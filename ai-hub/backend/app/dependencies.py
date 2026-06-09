"""FastAPI 依赖注入模块"""

from typing import AsyncGenerator

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.config import Settings, get_settings
from app.core.database import get_db


async def get_settings_dep() -> Settings:
  """获取配置依赖"""
  return get_settings()


async def get_db_dep() -> AsyncGenerator[aiosqlite.Connection, None]:
  """获取数据库连接依赖"""
  db = await get_db()
  try:
    yield db
  finally:
    await db.close()


_checkpointer: AsyncSqliteSaver | None = None


async def get_checkpointer() -> AsyncSqliteSaver:
  """获取 LangGraph SQLite checkpointer 单例"""
  global _checkpointer
  if _checkpointer is None:
    settings = get_settings()
    db_path = settings.sqlite_db_path.replace("app.db", "checkpoints.db")
    _checkpointer = AsyncSqliteSaver.from_conn_string(db_path)
  return _checkpointer
