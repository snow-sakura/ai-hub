"""资源下载工具（含 SSRF 防护）"""

import httpx
from pathlib import Path
from urllib.parse import urlparse
from langchain_core.tools import tool
from app.config import get_settings
from urllib.parse import urljoin
from app.common.utils.url_validator import is_safe_url


@tool
def download_resource(url: str, filename: str = "") -> str:
  """从 URL 下载资源文件到工作目录。

  Args:
    url: 资源下载链接
    filename: 保存文件名（可选，默认从 URL 推断）
  """
  settings = get_settings()
  workspace = Path(settings.workspace_dir).resolve()
  workspace.mkdir(parents=True, exist_ok=True)

  if not filename:
    parsed = urlparse(url)
    filename = Path(parsed.path).name or "downloaded_file"

  target = (workspace / filename).resolve()
  if not str(target).startswith(str(workspace)):
    return "错误：不允许在工作目录之外保存文件"

  # SSRF 防护：校验 URL 是否指向内网
  if not is_safe_url(url):
    return "错误：不允许访问内网地址或不安全的 URL"

  try:
    headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }
    # 禁用自动重定向，手动逐跳验证防止 SSRF 重定向绕过
    with httpx.Client(timeout=60.0, follow_redirects=False) as client:
      # Content-Length 预检：拒绝超大文件
      head_resp = client.head(url, headers=headers, follow_redirects=True)
      content_length = head_resp.headers.get("Content-Length")
      if content_length and int(content_length) > 50 * 1024 * 1024:
        return f"错误：文件过大 (>{50}MB)，拒绝下载"
      resp = client.get(url, headers=headers)
      max_redirects = 5
      for _ in range(max_redirects):
        if resp.is_redirect:
          next_url = resp.headers.get("Location", "")
          if not next_url:
            return "错误：空重定向地址"
          # 解析相对 URL
          next_url = urljoin(str(resp.url), next_url)
          if not is_safe_url(next_url):
            return "错误：重定向到不安全的地址"
          resp = client.get(next_url, headers=headers)
        else:
          break
      resp.raise_for_status()
      target.write_bytes(resp.content)

    size_kb = len(resp.content) / 1024
    return f"文件已下载: {filename} ({size_kb:.1f} KB)"
  except Exception as e:
    return "下载失败，请检查 URL 和网络连接"
