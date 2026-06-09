"""聊天相关 Schema"""

from typing import Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
  """聊天请求"""
  message: str
  conversation_id: str
  model_provider: str = "deepseek"
  model_name: str = ""
  attachments: list[str] | None = None  # 上传附件返回的 file_id 列表
  knowledge_doc_ids: list[str] | None = None  # 选中的知识库文档 ID 列表


class ChatTokenEvent(BaseModel):
  """流式 token 事件"""
  content: str


class ToolCallStartEvent(BaseModel):
  """工具调用开始事件"""
  tool_name: str
  display: str
  tool_call_id: str
  input: dict[str, Any] | None = None


class ToolCallResultEvent(BaseModel):
  """工具调用结果事件"""
  tool_name: str
  tool_call_id: str
  summary: str
  result: dict[str, Any] | None = None


class ThinkingEvent(BaseModel):
  """智能体思考过程事件"""
  step: str  # thought / action / observation
  content: str


class ProgressEvent(BaseModel):
  """长任务进度事件"""
  current: int
  total: int
  message: str


class ChatDoneEvent(BaseModel):
  """聊天完成事件"""
  message_id: str
