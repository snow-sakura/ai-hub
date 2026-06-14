"""会话相关 Schema"""

from typing import Any

from pydantic import BaseModel


class ConversationCreate(BaseModel):
  """创建会话请求"""
  title: str = "新会话"
  type: str = "chat"
  metadata: dict[str, Any] | None = None


class ConversationUpdate(BaseModel):
  """更新会话请求"""
  title: str


class ConversationResponse(BaseModel):
  """会话响应"""
  id: str
  user_id: str = ""
  title: str
  type: str = "chat"
  metadata: str = "{}"
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
