"""文件读写工具"""

import os
from pathlib import Path
from langchain_core.tools import tool
from app.config import get_settings


@tool
def file_read(file_path: str) -> str:
  """读取指定路径的文件内容。

  Args:
    file_path: 文件路径（相对于工作目录）
  """
  settings = get_settings()
  workspace = Path(settings.workspace_dir).resolve()
  target = (workspace / file_path).resolve()

  if not str(target).startswith(str(workspace)):
    return "错误：不允许访问工作目录之外的文件"
  if not target.exists():
    return f"错误：文件 {file_path} 不存在"

  try:
    content = target.read_text(encoding="utf-8")
    if len(content) > 10000:
      return content[:10000] + f"\n\n... (文件过大，已截断，共 {len(content)} 字符)"
    return content
  except Exception as e:
    return f"读取文件失败: {str(e)}"


@tool
def file_write(file_path: str, content: str) -> str:
  """将内容写入指定路径的文件。

  Args:
    file_path: 文件路径（相对于工作目录）
    content: 要写入的内容
  """
  settings = get_settings()
  workspace = Path(settings.workspace_dir).resolve()
  target = (workspace / file_path).resolve()

  if not str(target).startswith(str(workspace)):
    return "错误：不允许在工作目录之外写入文件"

  try:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"文件已成功写入: {file_path} ({len(content)} 字符)"
  except Exception as e:
    return f"写入文件失败: {str(e)}"
