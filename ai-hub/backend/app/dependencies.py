"""FastAPI 依赖注入模块"""

from typing import AsyncGenerator

from app.common.core.database import MySQLConnection, get_db


async def get_db_dep() -> AsyncGenerator[MySQLConnection, None]:
    """获取数据库连接依赖"""
    db = await get_db()
    try:
        yield db
    finally:
        await db.close()
