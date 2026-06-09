"""会话相关 Schema"""

from pydantic import BaseModel


class ConversationCreate(BaseModel):
  """创建会话请求"""
  title: str = "新会话"


class ConversationUpdate(BaseModel):
  """更新会话请求"""
  title: str


class ConversationResponse(BaseModel):
  """会话响应"""
  id: str
  title: str
  created_at: str
  updated_at: str


class MessageResponse(BaseModel):
  """消息响应"""
  id: str
  conversation_id: str
  role: str
  content: str
  metadata: str
  created_at: str
