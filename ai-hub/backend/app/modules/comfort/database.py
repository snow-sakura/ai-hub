"""哄哄模拟器专用表 DDL（MySQL 版）"""

from app.shared.core.database import get_db


# ── 建表语句 ─────────────────────────────────────────────────────

COMFORT_TABLE_DDL: list[str] = [
    # 场景表
    """CREATE TABLE IF NOT EXISTS comfort_scenes (
      id VARCHAR(36) PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      description TEXT NOT NULL,
      icon VARCHAR(10) NOT NULL DEFAULT '🎭',
      initial_prompt TEXT NOT NULL,
      difficulty_default INT NOT NULL DEFAULT 3,
      tags TEXT,
      sort_order INT NOT NULL DEFAULT 0,
      is_builtin TINYINT NOT NULL DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 角色表
    """CREATE TABLE IF NOT EXISTS comfort_characters (
      id VARCHAR(36) PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      age INT,
      identity VARCHAR(255) NOT NULL DEFAULT '',
      personality_tags TEXT,
      speaking_style TEXT NOT NULL,
      avatar_emoji VARCHAR(10) NOT NULL DEFAULT '😊',
      backstory TEXT,
      scene_id VARCHAR(36),
      is_builtin TINYINT NOT NULL DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 记忆表
    """CREATE TABLE IF NOT EXISTS comfort_memories (
      id VARCHAR(36) PRIMARY KEY,
      conversation_id VARCHAR(36) NOT NULL,
      content TEXT NOT NULL,
      memory_type VARCHAR(20) NOT NULL DEFAULT 'fact',
      importance FLOAT NOT NULL DEFAULT 0.5,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 情绪统计数据表
    """CREATE TABLE IF NOT EXISTS emotion_statistics (
      id VARCHAR(36) PRIMARY KEY,
      user_date VARCHAR(10) NOT NULL,
      emotion_label VARCHAR(50) NOT NULL,
      avg_intensity FLOAT NOT NULL,
      count INT NOT NULL DEFAULT 1,
      comfort_score FLOAT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      UNIQUE KEY uk_emotion_daily (user_date, emotion_label)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
]


# ── 索引（独立执行，容错已存在）────────────────────────────────────

COMFORT_INDEXES: list[str] = [
    "CREATE INDEX idx_characters_scene ON comfort_characters(scene_id)",
    "CREATE INDEX idx_memories_conversation ON comfort_memories(conversation_id, created_at)",
]


async def init_comfort_tables() -> None:
    """初始化哄哄模拟器专用表"""
    db = await get_db()
    try:
        await db.execute("SET SQL_NOTES = 0")
        await db.execute("SET FOREIGN_KEY_CHECKS = 0")
        for stmt in COMFORT_TABLE_DDL:
            await db.execute(stmt)
        for stmt in COMFORT_INDEXES:
            try:
                await db.execute(stmt)
            except Exception:
                pass  # 索引已存在时忽略
        await db.execute("SET FOREIGN_KEY_CHECKS = 1")
        await db.execute("SET SQL_NOTES = 1")
        for stmt in COMFORT_INDEXES:
            try:
                await db.execute(stmt)
            except Exception:
                pass  # 索引已存在时忽略
        await db.commit()
    finally:
        await db.close()
