"""Agent 状态定义"""

from typing import Annotated, Any, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
  """LangGraph Agent 状态"""
  messages: Annotated[list[BaseMessage], add_messages]
  model_provider: str
  model_name: str
  rag_context: str | None
  knowledge_doc_ids: list[str] | None  # 知识库文档过滤
  attachment_contents: list[dict] | None  # 附件解析内容 [{filename, content}]
  thinking_steps: list[dict[str, str]]
  progress: dict[str, Any] | None
  current_tool_calls: list[dict[str, Any]]
  # 哄哄模拟器扩展字段
  emotion_result: dict[str, Any] | None       # 情绪分析结果
  forgiveness_result: dict[str, Any] | None   # 原谅值计算结果
  comfort_metadata: dict[str, Any] | None     # 哄哄会话元数据(场景/角色/原谅值等)
