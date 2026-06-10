"""LangGraph 图生命周期管理基类"""

import os
import aiosqlite
from abc import ABC, abstractmethod
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.config import get_settings


class ManagedGraphBase(ABC):
  """LangGraph 图生命周期管理基类

  子类需实现 _build_graph() 返回已构建（未编译）的 StateGraph，
  initialize() 由基类处理守卫检查、checkpointer 设置和编译。
  """

  def __init__(self, db_suffix: str = '_graph.db'):
    self._conn = None
    self._graph = None
    self._db_suffix = db_suffix

  @abstractmethod
  def _build_graph(self) -> StateGraph:
    """子类实现此方法返回已构建好节点和边的 StateGraph"""
    ...

  async def initialize(self):
    """初始化图和连接（模板方法：守卫 → _build_graph → checkpointer → 编译）"""
    if self._graph is not None:
      return self._graph
    builder = self._build_graph()
    checkpointer = await self._setup_checkpointer()
    self._graph = builder.compile(checkpointer=checkpointer)
    return self._graph

  async def _setup_checkpointer(self) -> AsyncSqliteSaver:
    """创建数据库连接和 checkpointer"""
    settings = get_settings()
    db_dir = os.path.dirname(settings.sqlite_db_path)
    os.makedirs(db_dir, exist_ok=True)
    base, _ = os.path.splitext(settings.sqlite_db_path)
    graph_db_path = base + self._db_suffix
    self._conn = await aiosqlite.connect(graph_db_path)
    return AsyncSqliteSaver(self._conn)

  async def close(self):
    """关闭数据库连接"""
    if self._conn:
      await self._conn.close()
      self._conn = None
      self._graph = None
