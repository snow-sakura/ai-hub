"""文件解析工具 - 支持 PDF/Word/TXT"""

from app.common.domain.exceptions import FileParseError


def parse_file(content: bytes, file_type: str) -> str:
  """根据文件类型解析文件内容"""
  if file_type == "pdf":
    return _parse_pdf(content)
  elif file_type in ("docx", "doc"):
    return _parse_docx(content)
  elif file_type == "txt":
    return _parse_txt(content)
  else:
    return _parse_txt(content)


def _parse_pdf(content: bytes) -> str:
  """解析 PDF 文件"""
  try:
    import fitz
    doc = fitz.open(stream=content, filetype="pdf")
    text_parts = []
    for page in doc:
      text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts)
  except Exception as e:
    raise FileParseError("PDF", str(e))


def _parse_docx(content: bytes) -> str:
  """解析 Word 文件（支持 .docx 和 .doc）"""
  # .doc 是 OLE 二进制格式，.docx 是 ZIP 格式
  # 通过魔数判断：.docx 以 PK (0x50 0x4B) 开头
  is_old_doc = len(content) > 2 and content[0] == 0xD0 and content[1] == 0xCF

  if is_old_doc:
    return _parse_doc(content)
  return _parse_docx_inner(content)


def _parse_docx_inner(content: bytes) -> str:
  """解析 .docx 文件（ZIP 格式）"""
  try:
    import io
    from docx import Document
    doc = Document(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
  except Exception as e:
    raise FileParseError("Word", str(e))


def _parse_doc(content: bytes) -> str:
  """解析旧版 .doc 文件（OLE 二进制格式）"""
  # 优先使用 macOS 内置 textutil
  try:
    import subprocess, tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as tmp:
      tmp.write(content)
      tmp_path = tmp.name
    try:
      result = subprocess.run(
        ["textutil", "-convert", "txt", "-stdout", tmp_path],
        capture_output=True, timeout=30,
      )
      if result.returncode == 0:
        text = result.stdout.decode("utf-8", errors="replace").strip()
        if text:
          return text
    finally:
      os.unlink(tmp_path)
  except FileNotFoundError:
    pass  # textutil 不可用（非 macOS）
  except Exception:
    pass

  # fallback: 尝试用 olefile 提取纯文本
  try:
    import olefile
    ole = olefile.OleFileIO(content)
    # 尝试常见的文本流
    for stream_name in ["WordDocument", "1Table", "0Table"]:
      if ole.exists(stream_name):
        data = ole.openstream(stream_name).read()
        # 提取可读 ASCII/UTF-8 文本
        text = data.decode("utf-8", errors="replace")
        # 过滤掉不可见字符
        import re
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
        if cleaned.strip():
          ole.close()
          return cleaned.strip()
    ole.close()
  except ImportError:
    pass  # olefile 未安装
  except Exception:
    pass

  raise FileParseError(
    "Word",
    "不支持旧版 .doc 格式，请转换为 .docx 后重试。"
  )


def _parse_txt(content: bytes) -> str:
  """解析纯文本文件"""
  try:
    return content.decode("utf-8")
  except UnicodeDecodeError:
    return content.decode("gbk", errors="replace")
