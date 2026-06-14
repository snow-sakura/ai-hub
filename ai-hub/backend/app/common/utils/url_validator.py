"""URL 安全校验工具 - 防止 SSRF 攻击"""

import asyncio
import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# DNS 解析超时（秒）
_DNS_TIMEOUT = 3

# 内网 / 保留地址段（SSRF 黑名单）
_BLOCKED_NETWORKS = [
  ipaddress.ip_network("10.0.0.0/8"),
  ipaddress.ip_network("172.16.0.0/12"),
  ipaddress.ip_network("192.168.0.0/16"),
  ipaddress.ip_network("169.254.0.0/16"),  # AWS metadata / link-local
  ipaddress.ip_network("127.0.0.0/8"),
  ipaddress.ip_network("0.0.0.0/8"),
  ipaddress.ip_network("100.64.0.0/10"),   # CGNAT (RFC 6598)
  ipaddress.ip_network("224.0.0.0/4"),     # Multicast
  ipaddress.ip_network("240.0.0.0/4"),     # Reserved (Class E / future)
  ipaddress.ip_network("198.18.0.0/15"),   # Benchmarking (RFC 2544)
  ipaddress.ip_network("::1/128"),
  ipaddress.ip_network("fc00::/7"),        # IPv6 unique-local
  ipaddress.ip_network("fe80::/10"),       # IPv6 link-local
  ipaddress.ip_network("ff00::/8"),        # IPv6 multicast
]


def _resolve_hostname(hostname: str) -> str:
  """同步 DNS 解析，带超时控制

  注意：使用 socket.setdefaulttimeout 修改全局状态，
  在多线程并发场景下存在竞态条件。仅在 LangGraph executor
  隔离线程池（单线程执行 tool）中使用。
  """
  original_timeout = socket.getdefaulttimeout()
  try:
    socket.setdefaulttimeout(_DNS_TIMEOUT)
    return socket.gethostbyname(hostname)
  finally:
    socket.setdefaulttimeout(original_timeout)


def _resolve_hostname_all(hostname: str) -> list[str]:
  """同步 DNS 解析，返回所有解析到的 IP 地址（多 A 记录）"""
  original_timeout = socket.getdefaulttimeout()
  try:
    socket.setdefaulttimeout(_DNS_TIMEOUT)
    addrinfo = socket.getaddrinfo(hostname, None)
    ips = []
    for info in addrinfo:
      ip = info[4][0]
      if ip not in ips:
        ips.append(ip)
    return ips
  except (socket.gaierror, socket.timeout, OSError):
    return []
  finally:
    socket.setdefaulttimeout(original_timeout)


def is_safe_url(url: str) -> bool:
  """
  验证 URL 是否安全（防止 SSRF）— 同步版本

  - 仅允许 http / https scheme
  - 禁止内网 / 保留 IP 地址
  - DNS 解析后二次校验（防 DNS rebinding）
  - DNS 解析超时控制（default: 3s）

  注意: 此函数包含同步 DNS 解析 (socket.gethostbyname)，
  在 async 上下文中请使用 is_safe_url_async()，在 LangGraph executor
  线程池中（如 tool 函数）可直接使用此版本。
  """
  try:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
      return False
    hostname = parsed.hostname
    if not hostname:
      return False
    # 校验所有解析到的 IP，防止 DNS 多IP 绕过
    ips = _resolve_hostname_all(hostname)
    if not ips:
      return False
    for ip_str in ips:
      ip = ipaddress.ip_address(ip_str)
      if any(ip in net for net in _BLOCKED_NETWORKS):
        return False
    return True
  except (socket.gaierror, socket.timeout, ValueError, OSError):
    return False


async def is_safe_url_async(url: str) -> bool:
  """
  验证 URL 是否安全（防止 SSRF）— 异步版本

  使用 loop.getaddrinfo 原生异步 DNS 解析，避免线程池竞态条件。
  """
  try:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
      return False
    hostname = parsed.hostname
    if not hostname:
      return False
    loop = asyncio.get_running_loop()
    # 使用原生异步 getaddrinfo，避免 run_in_executor 线程池竞态
    addrinfo = await asyncio.wait_for(
      loop.getaddrinfo(hostname, None),
      timeout=_DNS_TIMEOUT,
    )
    # getaddrinfo 返回 [(family, type, proto, canonname, sockaddr), ...]
    # 校验所有解析到的 IP，防止 DNS 多IP 绕过
    for info in addrinfo:
      ip_str = info[4][0]
      ip = ipaddress.ip_address(ip_str)
      if any(ip in net for net in _BLOCKED_NETWORKS):
        return False
    return True
  except (socket.gaierror, socket.timeout, ValueError, OSError, asyncio.TimeoutError):
    return False
