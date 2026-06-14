"""LangGraph Agent 图构建"""

from typing import Literal
from langgraph.graph import StateGraph, START, END

from app.common.agent.state import AgentState
from app.common.agent.nodes.agent_node import agent_node
from app.common.agent.nodes.tool_node import tool_node
from app.common.agent.nodes.rag_node import rag_node
from app.common.core.managed_graph import ManagedGraphBase


def should_continue(state: AgentState) -> Literal["tool_node", END]:
  """根据最后一条消息判断是否需要继续执行工具"""
  messages = state["messages"]
  last_message = messages[-1]
  if hasattr(last_message, "tool_calls") and last_message.tool_calls:
    return "tool_node"
  return END


def should_rag(state: AgentState) -> Literal["rag_node", "agent"]:
  """判断是否需要 RAG 检索：无知识库文档时跳过，节省一次无用 ChromaDB 查询"""
  knowledge_doc_ids = state.get("knowledge_doc_ids")
  if knowledge_doc_ids and len(knowledge_doc_ids) > 0:
    return "rag_node"
  return "agent"


class ManagedAgentGraph(ManagedGraphBase):
  """管理 LangGraph Agent 图的生命周期（包括数据库连接）"""

  def __init__(self):
    super().__init__(db_suffix='_graph', use_mysql_checkpoint=True)

  def _build_graph(self) -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("tool_node", tool_node)
    builder.add_node("rag_node", rag_node)

    # START → 条件判断 → rag_node（有选中文档时检索）/ agent（无文档直接推理）
    builder.add_conditional_edges(START, should_rag, ["rag_node", "agent"])
    builder.add_edge("rag_node", "agent")
    # agent 根据是否有 tool_calls 决定走 tool_node 还是 END
    builder.add_conditional_edges("agent", should_continue, ["tool_node", END])
    # tool_node 执行完回到 agent
    builder.add_edge("tool_node", "agent")

    return builder


# 全局单例管理器
_agent_graph_manager = ManagedAgentGraph()


async def get_agent_graph():
  """获取 Agent 图单例"""
  return await _agent_graph_manager.initialize()


async def close_agent_graph():
  """关闭 Agent 图连接（应用 shutdown 时调用）"""
  await _agent_graph_manager.close()
