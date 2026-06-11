"""MySQL 数据库连接管理模块（主数据存储）

共享表：conversations, messages, knowledge_docs
LangGraph checkpoint 仍使用 SQLite，见 managed_graph.py
"""

import aiomysql
from contextlib import asynccontextmanager
from app.config import get_settings


class _CursorProxy:
    """代理 aiomysql 游标，提供与 aiosqlite 游标一致的接口"""

    def __init__(self, cursor):
        self._cursor = cursor

    async def fetchone(self):
        return await self._cursor.fetchone()

    async def fetchall(self):
        return await self._cursor.fetchall()

    @property
    def rowcount(self):
        return self._cursor.rowcount


class MySQLConnection:
    """包装 aiomysql 连接，提供与 aiosqlite.Connection 兼容的接口

    使现有 repository/service 代码无需大规模改写即可迁移到 MySQL。
    """

    def __init__(self, conn):
        self._conn = conn
        self._proxy = None

    async def execute(self, sql, params=None):
        # 兼容 SQLite 的 ? 占位符 → 转为 MySQL 的 %s
        if params is not None and "?" in sql:
            sql = sql.replace("?", "%s")
        cursor = await self._conn.cursor(aiomysql.DictCursor)
        await cursor.execute(sql, params or ())
        self._proxy = _CursorProxy(cursor)
        return self._proxy

    async def executescript(self, script):
        """模拟 executescript — 按 ; 分割逐条执行"""
        statements = [s.strip() for s in script.split(";") if s.strip()]
        for stmt in statements:
            if stmt:
                await self.execute(stmt)

    async def commit(self):
        await self._conn.commit()

    async def close(self):
        if self._proxy and self._proxy._cursor:
            await self._proxy._cursor.close()
        if self._conn and not self._conn.closed:
            self._conn.close()

    @property
    def row_factory(self):
        return None

    @row_factory.setter
    def row_factory(self, value):
        """DictCursor 已返回类 dict 对象，无需额外 row_factory"""
        pass


class MySQLDatabase:
    """MySQL 连接池管理器（单例）"""

    _instance = None
    _pool = None

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance._create_pool()
        return cls._instance

    async def _create_pool(self):
        settings = get_settings()
        self._pool = await aiomysql.create_pool(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            db=settings.mysql_database,
            charset="utf8mb4",
            maxsize=10,
            minsize=1,
            autocommit=False,
        )

    async def get_connection(self):
        if self._pool is None:
            await self._create_pool()
        raw = await self._pool.acquire()
        return MySQLConnection(raw)

    async def close(self):
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
            MySQLDatabase._instance = None


# ─── 便捷函数（保持与旧代码一致的接口） ──────────────────────────


async def get_db() -> MySQLConnection:
    """获取 MySQL 数据库连接（用完记得 close 归还连接池）"""
    mgr = await MySQLDatabase.get_instance()
    return await mgr.get_connection()


@asynccontextmanager
async def get_db_context():
    """获取数据库连接的上下文管理器"""
    db = await get_db()
    try:
        yield db
    finally:
        await db.close()


# ─── 共享表 DDL（MySQL 语法） ────────────────────────────────

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS conversations (
  id VARCHAR(36) PRIMARY KEY,
  title VARCHAR(500) NOT NULL DEFAULT '新会话',
  type VARCHAR(50) NOT NULL DEFAULT 'chat',
  INDEX idx_conversations_type (type),
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS messages (
  id VARCHAR(36) PRIMARY KEY,
  conversation_id VARCHAR(36) NOT NULL,
  role VARCHAR(20) NOT NULL,
  content TEXT NOT NULL,
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_messages_conversation (conversation_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS knowledge_docs (
  id VARCHAR(36) PRIMARY KEY,
  filename VARCHAR(500) NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  file_size INT NOT NULL,
  chunk_count INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


async def init_db() -> None:
    """初始化数据库共享表结构"""
    db = await get_db()
    try:
        await db.execute("SET SQL_NOTES = 0")
        await db.execute("SET FOREIGN_KEY_CHECKS = 0")
        await db.executescript(CREATE_TABLES_SQL)
        await db.execute("SET FOREIGN_KEY_CHECKS = 1")
        await db.execute("SET SQL_NOTES = 1")
        await db.commit()
    finally:
        await db.close()
