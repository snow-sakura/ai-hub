"""领域实体定义 - 纯数据类，无框架依赖"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Conversation:
  """会话实体"""
  id: str
  title: str = "新会话"
  created_at: datetime | None = None
  updated_at: datetime | None = None


@dataclass
class Message:
  """消息实体"""
  id: str
  conversation_id: str
  role: str  # user / assistant / tool / system
  content: str = ""
  metadata: dict[str, Any] = field(default_factory=dict)
  created_at: datetime | None = None


@dataclass
class KnowledgeDoc:
  """知识库文档实体"""
  id: str
  filename: str
  file_type: str
  file_size: int
  chunk_count: int = 0
  created_at: datetime | None = None


@dataclass
class ToolInfo:
  """工具信息实体"""
  name: str
  display_name: str
  description: str
  icon: str = "tool"
  category: str = "general"


@dataclass
class ModelConfig:
  """模型配置实体"""
  provider: str
  model: str
  api_key: str = ""
  base_url: str = ""
  display_name: str = ""
