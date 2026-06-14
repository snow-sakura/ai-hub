"""MySQL 数据库连接管理模块（主数据存储）

共享表：conversations, messages, users, knowledge_docs
LangGraph checkpoint 表：langgraph_checkpoints, langgraph_checkpoint_writes
"""

import asyncio
import aiomysql
import logging
import re
from contextlib import asynccontextmanager
from app.config import get_settings

logger = logging.getLogger(__name__)


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
    使用持久化游标模式，避免 'Command Out of Sync' 错误。
    """

    def __init__(self, conn, pool=None):
        self._conn = conn
        self._pool = pool  # 持有池引用，close 时归还而非物理关闭
        self._cursor = None  # 持久化游标，复用避免冲突

    async def _get_cursor(self):
        """获取（或创建）持久化游标"""
        if self._cursor is None or self._cursor._cursor is None:
            c = await self._conn.cursor(aiomysql.DictCursor)
            self._cursor = _CursorProxy(c)
        return self._cursor

    async def execute(self, sql, params=None):
        # 兼容 SQLite 的 ? 占位符 → 转为 MySQL 的 %s
        if params is not None and "?" in sql:
            sql = re.sub(r"(?<!')\?(?!')", "%s", sql)
        cursor = await self._get_cursor()
        await cursor._cursor.execute(sql, params or ())
        return cursor

    async def executescript(self, script):
        statements = [s.strip() for s in script.split(";") if s.strip()]
        for stmt in statements:
            if stmt:
                await self.execute(stmt)

    async def commit(self):
        # 确保提交前连接状态清洁：如果有未消费结果，先清理
        if hasattr(self._conn, '_result') and self._conn._result is not None:
            try:
                if self._conn._result.unbuffered_active:
                    await self._conn._result._finish_unbuffered_query()
                while self._conn._result.has_next:
                    await self._conn.next_result()
            except Exception:
                pass
            self._conn._result = None
        await self._conn.commit()

    async def close(self):
        # 安全回滚：确保归还连接前无未提交事务，防止连接状态泄漏到池中
        try:
            await self._conn.rollback()
        except Exception:
            pass
        if self._cursor and self._cursor._cursor:
            try:
                await self._cursor._cursor.close()
            except Exception:
                pass
            self._cursor = None
        # 归还连接到池（而非物理关闭），否则池会快速耗尽
        if self._pool and self._conn:
            self._pool.release(self._conn)
            self._conn = None

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
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls):
        if cls._instance is not None:
            return cls._instance
        async with cls._lock:
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
            maxsize=settings.mysql_pool_size,
            minsize=2,
            pool_recycle=settings.mysql_pool_recycle,
            connect_timeout=10,
            autocommit=False,
        )

    async def get_connection(self):
        if self._pool is None:
            await self._create_pool()
        raw = await self._pool.acquire()
        return MySQLConnection(raw, pool=self._pool)

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
  user_id VARCHAR(36),
  title VARCHAR(500) NOT NULL DEFAULT '新会话',
  type VARCHAR(50) NOT NULL DEFAULT 'chat',
  INDEX idx_conversations_type (type),
  INDEX idx_conversations_user (user_id),
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


CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(36) PRIMARY KEY,
  username VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  is_active TINYINT NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS knowledge_docs (
  id VARCHAR(36) PRIMARY KEY,
  filename VARCHAR(500) NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  file_size INT NOT NULL,
  chunk_count INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS langgraph_checkpoints (
  thread_id VARCHAR(255) NOT NULL,
  checkpoint_id VARCHAR(255) NOT NULL,
  parent_checkpoint_id VARCHAR(255),
  type VARCHAR(255),
  checkpoint LONGTEXT NOT NULL,
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (thread_id, checkpoint_id),
  INDEX idx_lg_checkpoints_thread (thread_id),
  INDEX idx_lg_checkpoints_parent (parent_checkpoint_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS langgraph_checkpoint_writes (
  thread_id VARCHAR(255) NOT NULL,
  checkpoint_id VARCHAR(255) NOT NULL,
  task_id VARCHAR(255) NOT NULL,
  idx INT NOT NULL DEFAULT 0,
  channel VARCHAR(255) NOT NULL,
  type VARCHAR(255),
  value LONGTEXT,
  PRIMARY KEY (thread_id, checkpoint_id, task_id, idx),
  INDEX idx_lg_writes_thread (thread_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS shared_schema_version (
  version INTEGER PRIMARY KEY,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


async def init_db() -> None:
    """初始化数据库共享表结构 + 运行迁移"""
    db = await get_db()
    try:
        await db.execute("SET sql_notes = 0")
        await db.execute("SET FOREIGN_KEY_CHECKS = 0")
        try:
            await db.executescript(CREATE_TABLES_SQL)
        finally:
            await db.execute("SET FOREIGN_KEY_CHECKS = 1")
        await _run_shared_migrations(db)
        await db.execute("SET sql_notes = 1")
        await db.commit()
    finally:
        await db.close()


async def _run_shared_migrations(db: MySQLConnection) -> None:
    """执行共享层数据库迁移（版本控制）

    使用 INFORMATION_SCHEMA 检查列存在性，确保幂等。
    """
    import logging
    _logger = logging.getLogger(__name__)

    # 确保版本表存在（已在 CREATE_TABLES_SQL 中创建，此处仅作双保险）
    await db.execute(
        "CREATE TABLE IF NOT EXISTS shared_schema_version ("
        "  version INTEGER PRIMARY KEY,"
        "  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ")"
    )

    cursor = await db.execute(
        "SELECT MAX(version) as max_version FROM shared_schema_version"
    )
    row = await cursor.fetchone()
    current_version = row["max_version"] if row and row["max_version"] else 0

    # v1: 基础表（conversations, messages, knowledge_docs, users, checkpoint 表）
    if current_version < 1:
        await db.execute("INSERT INTO shared_schema_version (version) VALUES (1)")
        _logger.info("shared schema v1 迁移完成")

    # v2: conversations 表添加 user_id 列（IDOR 归属校验）
    if current_version < 2:
        cursor = await db.execute("SHOW COLUMNS FROM conversations LIKE 'user_id'")
        if not await cursor.fetchone():
            await db.execute("ALTER TABLE conversations ADD COLUMN user_id VARCHAR(36) AFTER id")
            await db.execute("ALTER TABLE conversations ADD INDEX idx_conversations_user (user_id)")
        await db.execute("INSERT INTO shared_schema_version (version) VALUES (2)")
        _logger.info("shared schema v2 迁移完成：conversations 添加 user_id 列")
