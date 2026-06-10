"""哄哄模拟器 LangGraph 图构建"""

import os
import aiosqlite
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.shared.agent.state import AgentState
from app.shared.agent.nodes.tool_node import tool_node
from app.shared.agent.nodes.rag_node import rag_node
from app.modules.comfort.nodes.emotion_node import emotion_node
from app.modules.comfort.nodes.forgiveness_node import forgiveness_node
from app.modules.comfort.nodes.comfort_agent_node import comfort_agent_node
from app.config import get_settings


def should_continue(state: AgentState) -> Literal["tool_node", "forgiveness_node"]:
  """判断是否需要执行工具，还是直接到原谅值计算"""
  messages = state["messages"]
  last_message = messages[-1]
  if hasattr(last_message, "tool_calls") and last_message.tool_calls:
    return "tool_node"
  return "forgiveness_node"


async def build_comfort_graph():
  """构建并编译哄哄模拟器图

  图结构:
  START → emotion_node → rag_node → comfort_agent_node ↔ tool_node → forgiveness_node → END
  """
  builder = StateGraph(AgentState)

  builder.add_node("emotion_node", emotion_node)
  builder.add_node("rag_node", rag_node)
  builder.add_node("comfort_agent", comfort_agent_node)
  builder.add_node("tool_node", tool_node)
  builder.add_node("forgiveness_node", forgiveness_node)

  # 流程编排
  builder.add_edge(START, "emotion_node")
  builder.add_edge("emotion_node", "rag_node")
  builder.add_edge("rag_node", "comfort_agent")
  # comfort_agent 判断是否需要工具
  builder.add_conditional_edges("comfort_agent", should_continue, ["tool_node", "forgiveness_node"])
  # tool_node 执行完回到 comfort_agent
  builder.add_edge("tool_node", "comfort_agent")
  # forgiveness_node 是终点
  builder.add_edge("forgiveness_node", END)

  # 持久化 checkpointer
  settings = get_settings()
  db_dir = os.path.dirname(settings.sqlite_db_path)
  os.makedirs(db_dir, exist_ok=True)
  graph_db_path = settings.sqlite_db_path.replace('.db', '_comfort_graph.db')
  conn = await aiosqlite.connect(graph_db_path)
  checkpointer = AsyncSqliteSaver(conn)

  graph = builder.compile(checkpointer=checkpointer)
  return graph


_comfort_graph = None


async def get_comfort_graph():
  """获取哄哄模拟器图单例"""
  global _comfort_graph
  if _comfort_graph is None:
    _comfort_graph = await build_comfort_graph()
  return _comfort_graph
