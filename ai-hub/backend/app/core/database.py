"""SQLite 数据库连接管理模块"""

import aiosqlite
from pathlib import Path
from app.config import get_settings


DB_PATH = Path(get_settings().sqlite_db_path)

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '新会话',
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
  """获取数据库连接"""
  DB_PATH.parent.mkdir(parents=True, exist_ok=True)
  db = await aiosqlite.connect(str(DB_PATH))
  db.row_factory = aiosqlite.Row
  await db.execute("PRAGMA journal_mode=WAL")
  await db.execute("PRAGMA foreign_keys=ON")
  return db


async def init_db() -> None:
  """初始化数据库表结构"""
  db = await get_db()
  try:
    await db.executescript(CREATE_TABLES_SQL)
    await db.commit()
  finally:
    await db.close()
