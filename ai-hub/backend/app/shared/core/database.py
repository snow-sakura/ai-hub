"""SQLite 数据库连接管理模块（共享表：conversations, messages, knowledge_docs）"""

import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager
from app.config import get_settings


DB_PATH = Path(get_settings().sqlite_db_path)

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '新会话',
  type TEXT NOT NULL DEFAULT 'chat',
  metadata TEXT DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'tool', 'system')),
  content TEXT NOT NULL DEFAULT '',
  metadata TEXT DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS knowledge_docs (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  file_type TEXT NOT NULL,
  file_size INTEGER NOT NULL,
  chunk_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation
  ON messages(conversation_id, created_at);
"""


async def get_db() -> aiosqlite.Connection:
  """获取数据库连接（不推荐，建议使用 get_db_context）"""
  DB_PATH.parent.mkdir(parents=True, exist_ok=True)
  db = await aiosqlite.connect(str(DB_PATH))
  db.row_factory = aiosqlite.Row
  await db.execute("PRAGMA journal_mode=WAL")
  await db.execute("PRAGMA foreign_keys=ON")
  await db.execute("PRAGMA busy_timeout=5000")
  return db


@asynccontextmanager
async def get_db_context():
  """获取数据库连接的上下文管理器（推荐）

  用法：
    async with get_db_context() as db:
      await db.execute(...)
  """
  DB_PATH.parent.mkdir(parents=True, exist_ok=True)
  db = await aiosqlite.connect(str(DB_PATH))
  db.row_factory = aiosqlite.Row
  await db.execute("PRAGMA journal_mode=WAL")
  await db.execute("PRAGMA foreign_keys=ON")
  try:
    yield db
  finally:
    await db.close()


MIGRATIONS_SQL = """
-- v1 -> v2: conversations 新增 type/metadata 列
ALTER TABLE conversations ADD COLUMN type TEXT NOT NULL DEFAULT 'chat';
ALTER TABLE conversations ADD COLUMN metadata TEXT DEFAULT '{}';
"""


async def _run_migrations(db: aiosqlite.Connection) -> None:
  """执行增量迁移，兼容已有数据库的 schema 变更"""
  for sql in MIGRATIONS_SQL.split(";"):
    sql = sql.strip()
    if not sql:
      continue
    try:
      await db.execute(sql)
    except aiosqlite.OperationalError as e:
      # 忽略"重复列"等可接受的错误
      if "duplicate column" not in str(e).lower():
        raise


async def init_db() -> None:
  """初始化数据库共享表结构"""
  db = await get_db()
  try:
    await db.executescript(CREATE_TABLES_SQL)
    await _run_migrations(db)
    await db.commit()
  finally:
    await db.close()
