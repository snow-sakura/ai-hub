"""终端执行工具 - 增强安全控制"""

import re
import logging
import subprocess
from langchain_core.tools import tool
from app.config import get_settings

logger = logging.getLogger(__name__)

# 危险命令模式（正则匹配，覆盖面更广）
DANGEROUS_PATTERNS = [
  r"rm\s+(-rf|rf)\s+/",
  r"mkfs(\.|$)",
  r"dd\s+if=/dev/zero",
  r":\(\)\s*\{",
  r"chmod\s+-R\s+777\s+/",
  r"curl\s.*\|\s*(sh|bash)",
  r"wget\s.*\|\s*(sh|bash)",
  r"fork\s*bomb",
  r">\s*/dev/sda",
  r"mv\s+.*\s+/dev/null",
  r"sudo\s+",
  r"su\s+-",
  r"passwd",
  r"visudo",
  r"crontab\s+-e",
  r"systemctl\s+(start|stop|restart|disable|enable)",
  r"iptables",
  r"shutdown|reboot|halt|poweroff",
]

# 安全命令白名单前缀
SAFE_PREFIXES = [
  "ls", "cat", "head", "tail", "wc", "grep", "find", "echo",
  "pwd", "whoami", "date", "uname", "df", "du", "free",
  "ps", "top", "env", "which", "whereis", "type",
  "mkdir", "cp", "mv", "touch", "stat", "file",
  "python", "python3", "pip", "node", "npm", "npx",
  "git", "curl", "wget", "jq",
  "tree", "sort", "uniq", "cut", "awk", "sed",
  "tar", "zip", "unzip", "gzip", "gunzip",
]


@tool
def terminal_exec(command: str, timeout: int = 30) -> str:
  """在终端执行命令并返回输出。
  命令在工作目录中执行，有超时限制和权限控制。

  Args:
    command: 要执行的终端命令
    timeout: 超时时间（秒），默认 30 秒
  """
  settings = get_settings()
  workspace = settings.workspace_dir

  # 审计日志
  logger.info(f"[TERMINAL_AUDIT] 命令请求: {command}")

  # 1. 检查危险命令模式
  for pattern in DANGEROUS_PATTERNS:
    if re.search(pattern, command, re.IGNORECASE):
      logger.warning(f"[TERMINAL_BLOCKED] 危险命令被拦截: {command}")
      return f"⚠️ 安全拦截：检测到危险命令 `{command[:50]}...`，已拒绝执行。"

  # 2. 检查白名单
  first_word = command.strip().split()[0] if command.strip() else ""
  is_safe = any(first_word.startswith(prefix) for prefix in SAFE_PREFIXES)
  if not is_safe:
    logger.warning(f"[TERMINAL_UNSAFE] 非白名单命令: {command}")
    return f"⚠️ 安全拦截：命令 `{first_word}` 不在允许列表中。仅支持读取、编译、运行等安全命令。"

  # 3. 限制超时时间
  timeout = min(max(timeout, 5), 120)

  try:
    result = subprocess.run(
      command,
      shell=True,
      cwd=workspace,
      capture_output=True,
      text=True,
      timeout=timeout,
      env={
        "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": workspace,
        "LANG": "en_US.UTF-8",
      },
    )
    output = ""
    if result.stdout:
      output += f"**标准输出:**\n```\n{result.stdout[:5000]}\n```\n"
    if result.stderr:
      output += f"**标准错误:**\n```\n{result.stderr[:2000]}\n```\n"
    if result.returncode != 0:
      output += f"\n**退出码**: {result.returncode}"

    logger.info(f"[TERMINAL_AUDIT] 命令完成: {command}, exit={result.returncode}")
    return output or "命令执行完成，无输出。"
  except subprocess.TimeoutExpired:
    logger.warning(f"[TERMINAL_TIMEOUT] 命令超时: {command}")
    return f"⏱️ 命令执行超时（{timeout}秒），已终止。"
  except Exception as e:
    logger.error(f"[TERMINAL_ERROR] 命令异常: {command}, error={e}")
    return f"命令执行失败: {str(e)}"
