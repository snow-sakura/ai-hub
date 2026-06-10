"""LangGraph Agent 图构建"""

import os
import aiosqlite
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.shared.agent.state import AgentState
from app.shared.agent.nodes.agent_node import agent_node
from app.shared.agent.nodes.tool_node import tool_node
from app.shared.agent.nodes.rag_node import rag_node
from app.config import get_settings


def should_continue(state: AgentState) -> Literal["tool_node", END]:
  """根据最后一条消息判断是否需要继续执行工具"""
  messages = state["messages"]
  last_message = messages[-1]
  if hasattr(last_message, "tool_calls") and last_message.tool_calls:
    return "tool_node"
  return END


def should_rag(state: AgentState) -> Literal["rag_node", "agent"]:
  """判断是否需要 RAG 检索"""
  rag_context = state.get("rag_context")
  if rag_context:
    return "agent"
  return "rag_node"


async def build_agent_graph():
  """构建并编译 Agent 图，使用持久化 checkpointer"""
  builder = StateGraph(AgentState)

  builder.add_node("agent", agent_node)
  builder.add_node("tool_node", tool_node)
  builder.add_node("rag_node", rag_node)

  # START → rag_node → agent（先检索知识库再推理）
  builder.add_edge(START, "rag_node")
  builder.add_edge("rag_node", "agent")
  # agent 根据是否有 tool_calls 决定走 tool_node 还是 END
  builder.add_conditional_edges("agent", should_continue, ["tool_node", END])
  # tool_node 执行完回到 agent
  builder.add_edge("tool_node", "agent")

  # 使用 AsyncSqliteSaver 持久化对话状态
  settings = get_settings()
  db_dir = os.path.dirname(settings.sqlite_db_path)
  os.makedirs(db_dir, exist_ok=True)
  graph_db_path = settings.sqlite_db_path.replace('.db', '_graph.db')
  conn = await aiosqlite.connect(graph_db_path)
  checkpointer = AsyncSqliteSaver(conn)

  graph = builder.compile(checkpointer=checkpointer)
  return graph


_agent_graph = None


async def get_agent_graph():
  """获取 Agent 图单例"""
  global _agent_graph
  if _agent_graph is None:
    _agent_graph = await build_agent_graph()
  return _agent_graph
