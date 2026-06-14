"""哄哄模拟器 LangGraph 图构建"""

from typing import Literal
from langgraph.graph import StateGraph, START, END

from app.common.agent.state import AgentState
from app.common.agent.nodes.tool_node import tool_node
from app.common.agent.nodes.rag_node import rag_node
from app.modules.comfort.nodes.emotion_node import emotion_node
from app.modules.comfort.nodes.forgiveness_node import forgiveness_node
from app.modules.comfort.nodes.comfort_agent_node import comfort_agent_node
from app.common.core.managed_graph import ManagedGraphBase


def should_continue(state: AgentState) -> Literal["tool_node", "forgiveness_node"]:
  """判断是否需要执行工具，还是直接到原谅值计算"""
  messages = state["messages"]
  last_message = messages[-1]
  if hasattr(last_message, "tool_calls") and last_message.tool_calls:
    return "tool_node"
  return "forgiveness_node"


class ManagedComfortGraph(ManagedGraphBase):
  """管理哄哄模拟器 LangGraph 图的生命周期（包括数据库连接）"""

  def __init__(self):
    super().__init__(db_suffix='_comfort_graph', use_mysql_checkpoint=True)

  def _build_graph(self) -> StateGraph:
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

    return builder


# 全局单例管理器
_comfort_graph_manager = ManagedComfortGraph()


async def get_comfort_graph():
  """获取哄哄模拟器图单例"""
  return await _comfort_graph_manager.initialize()


async def close_comfort_graph():
  """关闭哄哄模拟器图连接（应用 shutdown 时调用）"""
  await _comfort_graph_manager.close()
