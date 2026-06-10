"""哄哄模拟器专用表 DDL（comfort_scenes, comfort_characters, comfort_memories, emotion_statistics）"""

import aiosqlite
from app.shared.core.database import DB_PATH, get_db


COMFORT_TABLES_SQL = """
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


async def init_comfort_tables() -> None:
  """初始化哄哄模拟器专用表"""
  db = await get_db()
  try:
    await db.executescript(COMFORT_TABLES_SQL)
    await db.commit()
  finally:
    await db.close()
