"""LangGraph 图生命周期管理基类"""

import os
import logging
import aiosqlite
from abc import ABC, abstractmethod
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.config import get_settings

logger = logging.getLogger(__name__)


class ManagedGraphBase(ABC):
  """LangGraph 图生命周期管理基类

  子类需实现 _build_graph() 返回已构建（未编译）的 StateGraph，
  initialize() 由基类处理守卫检查、checkpointer 设置和编译。
  """

  def __init__(self, db_suffix: str = '_graph', use_mysql_checkpoint: bool = True):
    self._conn = None
    self._saver = None
    self._graph = None
    self._db_suffix = db_suffix
    self._use_mysql_checkpoint = use_mysql_checkpoint

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

  async def _setup_checkpointer(self):
    """根据配置创建 checkpointer（MySQL 或 SQLite 回退）"""
    settings = get_settings()

    if self._use_mysql_checkpoint and settings.langgraph_checkpoint_backend == "mysql":
      try:
        from app.common.core.mysql_saver import MySQLSaver
        saver = MySQLSaver()
        self._saver = saver
        logger.info("LangGraph checkpoint 后端: MySQL (thread-safe)")
        return saver
      except Exception as e:
        logger.warning(
          "MySQL checkpoint 初始化失败 (%s)，回退到 SQLite", str(e)
        )

    # SQLite 回退
    db_dir = os.path.dirname(settings.sqlite_db_path)
    os.makedirs(db_dir, exist_ok=True)
    base, _ = os.path.splitext(settings.sqlite_db_path)
    graph_db_path = base + self._db_suffix + '.db'
    self._conn = await aiosqlite.connect(graph_db_path)
    saver = AsyncSqliteSaver(self._conn)
    self._saver = saver
    logger.info("LangGraph checkpoint 后端: SQLite (%s)", graph_db_path)
    return saver

  async def close(self):
    """关闭数据库连接"""
    if self._saver:
      try:
        await self._saver.aclose()
      except Exception as e:
        logger.warning("关闭 saver 失败: %s", e)
      self._saver = None
    if self._conn:
      await self._conn.close()
      self._conn = None
    self._graph = None
