"""知识库相关 Schema"""

from pydantic import BaseModel


class KnowledgeUploadResponse(BaseModel):
  """上传响应"""
  id: str
  filename: str
  file_type: str
  file_size: int
  chunk_count: int


class KnowledgeItemResponse(BaseModel):
  """知识库文档响应"""
  id: str
  filename: str
  file_type: str
  file_size: int
  chunk_count: int
  created_at: str
