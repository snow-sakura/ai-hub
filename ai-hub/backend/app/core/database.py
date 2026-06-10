"""SQLite 数据库连接管理模块"""

import aiosqlite
from pathlib import Path
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

CREATE TABLE IF NOT EXISTS comfort_scenes (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  icon TEXT NOT NULL DEFAULT '🎭',
  initial_prompt TEXT NOT NULL,
  difficulty_default INTEGER NOT NULL DEFAULT 3,
  tags TEXT DEFAULT '[]',
  sort_order INTEGER NOT NULL DEFAULT 0,
  is_builtin INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS comfort_characters (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  age INTEGER,
  identity TEXT NOT NULL DEFAULT '',
  personality_tags TEXT DEFAULT '[]',
  speaking_style TEXT NOT NULL DEFAULT '',
  avatar_emoji TEXT NOT NULL DEFAULT '😊',
  backstory TEXT DEFAULT '',
  scene_id TEXT,
  is_builtin INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (scene_id) REFERENCES comfort_scenes(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_characters_scene
  ON comfort_characters(scene_id);

CREATE TABLE IF NOT EXISTS comfort_memories (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  content TEXT NOT NULL,
  memory_type TEXT NOT NULL DEFAULT 'fact',
  importance REAL NOT NULL DEFAULT 0.5,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_memories_conversation
  ON comfort_memories(conversation_id, created_at);

CREATE TABLE IF NOT EXISTS emotion_statistics (
  id TEXT PRIMARY KEY,
  user_date TEXT NOT NULL,
  emotion_label TEXT NOT NULL,
  avg_intensity REAL NOT NULL,
  count INTEGER NOT NULL DEFAULT 1,
  comfort_score REAL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_emotion_daily
  ON emotion_statistics(user_date, emotion_label);
"""


async def get_db() -> aiosqlite.Connection:
  """获取数据库连接"""
  DB_PATH.parent.mkdir(parents=True, exist_ok=True)
  db = await aiosqlite.connect(str(DB_PATH))
  db.row_factory = aiosqlite.Row
  await db.execute("PRAGMA journal_mode=WAL")
  await db.execute("PRAGMA foreign_keys=ON")
  return db


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
  """初始化数据库表结构"""
  db = await get_db()
  try:
    await db.executescript(CREATE_TABLES_SQL)
    await _run_migrations(db)
    await db.commit()
  finally:
    await db.close()
