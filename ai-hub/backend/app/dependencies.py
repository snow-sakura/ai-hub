"""FastAPI 依赖注入模块"""

from typing import AsyncGenerator

import aiosqlite

from app.config import Settings, get_settings
from app.shared.core.database import get_db


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
