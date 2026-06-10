"""文本切分工具"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def split_text(
  text: str,
  chunk_size: int = DEFAULT_CHUNK_SIZE,
  chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
  """将文本切分为固定大小的块"""
  splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separators=["\n\n", "\n", "。", ".", " ", ""],
    length_function=len,
  )
  chunks = splitter.split_text(text)
  return [c.strip() for c in chunks if c.strip()]
