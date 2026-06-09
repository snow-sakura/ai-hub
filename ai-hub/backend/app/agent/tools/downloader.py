"""资源下载工具"""

import httpx
from pathlib import Path
from urllib.parse import urlparse
from langchain_core.tools import tool
from app.config import get_settings


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

  try:
    headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
      resp = client.get(url, headers=headers)
      resp.raise_for_status()
      target.write_bytes(resp.content)

    size_kb = len(resp.content) / 1024
    return f"文件已下载: {filename} ({size_kb:.1f} KB)"
  except Exception as e:
    return f"下载失败: {str(e)}"
