"""文件上传安全校验工具

提供统一的文件类型验证、魔数检测、文件名安全检查。
消除 chat/api.py 和 knowledge/api.py 中的重复魔数验证函数。
"""

from pathlib import Path


# ===== 文件魔数验证 =====

def validate_file_magic(content: bytes, ext: str) -> bool:
  """通过文件头字节（魔数）验证文件真实类型

  校验规则：
  - JPEG: FF D8 FF（前3字节）
  - PNG: 89 50 4E 47（前4字节）
  - GIF: 47 49 46 38（前4字节）
  - PDF: 25 50 44 46（前4字节）
  - WebP: RIFF + WEBP（前4 + 第9-12字节）
  - SVG: 包含 <svg 标签
  - DOC: D0 CF 11 E0（OLE2，前4字节）
  - DOCX: PK（ZIP-based，前2字节）
  - TXT/MD: 文本文件，无法可靠验证，跳过
  """
  if len(content) < 4:
    # 空文件或极小文件，让后续业务逻辑处理
    return True

  if ext in ('jpg', 'jpeg'):
    return content[:3] == b'\xff\xd8\xff'
  elif ext == 'png':
    return content[:4] == b'\x89PNG'
  elif ext == 'gif':
    return content[:4] == b'GIF8'
  elif ext == 'pdf':
    return content[:4] == b'%PDF'
  elif ext == 'webp':
    return content[:4] == b'RIFF' and content[8:12] == b'WEBP'
  elif ext == 'svg':
    return _validate_svg(content)
  elif ext in ('doc',):
    return content[:4] == b'\xd0\xcf\x11\xe0'
  elif ext in ('docx',):
    return content[:2] == b'PK'
  elif ext in ('txt', 'md'):
    return True
  return False


def _validate_svg(content: bytes) -> bool:
  """验证是否为 SVG 文件：检查是否包含 <svg 标签"""
  try:
    return b'<svg' in content[:512].lower()
  except Exception:
    return False


# ===== 文件名安全检查 =====

def safe_filename(filename: str) -> str:
  """获取安全的文件名（去除路径遍历攻击风险）"""
  return Path(filename).name


def has_path_traversal(filename: str) -> bool:
  """检查文件名是否存在路径遍历风险"""
  return '..' in filename or '/' in filename or '\\' in filename


def sanitize_filename_component(name: str) -> str:
  """清理文件名中的特殊字符，只保留字母数字和 ._- 空格"""
  safe = "".join(c for c in name if c.isalnum() or c in '._- ')
  if not safe:
    safe = "unnamed_file"
  return safe
