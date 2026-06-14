"""哄哄模拟器专用表 DDL（MySQL 版）"""

from app.common.core.database import get_db, MySQLConnection
import logging


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
      user_id VARCHAR(36),
      content TEXT NOT NULL,
      memory_type VARCHAR(20) NOT NULL DEFAULT 'fact',
      importance FLOAT NOT NULL DEFAULT 0.5,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_memories_user_conv (conversation_id, user_id, created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 情绪统计数据表
    """CREATE TABLE IF NOT EXISTS emotion_statistics (
      id VARCHAR(36) PRIMARY KEY,
      user_id VARCHAR(36),
      user_date VARCHAR(10) NOT NULL,
      emotion_label VARCHAR(50) NOT NULL,
      avg_intensity FLOAT NOT NULL,
      count INT NOT NULL DEFAULT 1,
      comfort_score FLOAT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      UNIQUE KEY uk_emotion_daily (user_id, user_date, emotion_label),
      INDEX idx_emotion_user (user_id)
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
        await db.execute("SET sql_notes = 0")
        await db.execute("SET FOREIGN_KEY_CHECKS = 0")
        try:
            for stmt in COMFORT_TABLE_DDL:
                await db.execute(stmt)
            for stmt in COMFORT_INDEXES:
                try:
                    await db.execute(stmt)
                except Exception:
                    _logger = logging.getLogger(__name__)
                    _logger.debug("索引创建跳过（可能已存在）")
        finally:
            await db.execute("SET FOREIGN_KEY_CHECKS = 1")
        await _run_comfort_migrations(db)
        await db.execute("SET sql_notes = 1")
        await db.commit()
    finally:
        await db.close()


async def _run_comfort_migrations(db: MySQLConnection) -> None:
    """执行哄哄模拟器模块数据库迁移（版本控制）"""
    import logging
    _logger = logging.getLogger(__name__)

    await db.execute(
        "CREATE TABLE IF NOT EXISTS comfort_schema_version ("
        "  version INTEGER PRIMARY KEY,"
        "  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ")"
    )

    cursor = await db.execute(
        "SELECT MAX(version) as max_version FROM comfort_schema_version"
    )
    row = await cursor.fetchone()
    current_version = row["max_version"] if row and row["max_version"] else 0

    # v1: 基础表（comfort_scenes, comfort_characters, comfort_memories, emotion_statistics）
    if current_version < 1:
        await db.execute("INSERT INTO comfort_schema_version (version) VALUES (1)")
        _logger.info("comfort schema v1 迁移完成")

    # v2: comfort_memories 添加 user_id 列 + 索引（IDOR 归属校验）
    if current_version < 2:
        cursor = await db.execute("SHOW COLUMNS FROM comfort_memories LIKE 'user_id'")
        if not await cursor.fetchone():
            await db.execute("ALTER TABLE comfort_memories ADD COLUMN user_id VARCHAR(36) AFTER conversation_id")
            await db.execute("ALTER TABLE comfort_memories ADD INDEX idx_memories_user (user_id)")
        await db.execute("INSERT INTO comfort_schema_version (version) VALUES (2)")
        _logger.info("comfort schema v2 迁移完成：comfort_memories 添加 user_id 列")

    # v3: emotion_statistics 添加 user_id 列（情绪统计用户隔离）
    if current_version < 3:
        cursor = await db.execute("SHOW COLUMNS FROM emotion_statistics LIKE 'user_id'")
        if not await cursor.fetchone():
            await db.execute("ALTER TABLE emotion_statistics ADD COLUMN user_id VARCHAR(36) AFTER id")
            await db.execute("ALTER TABLE emotion_statistics ADD INDEX idx_emotion_user (user_id)")
        await db.execute("INSERT INTO comfort_schema_version (version) VALUES (3)")
        _logger.info("comfort schema v3 迁移完成：emotion_statistics 添加 user_id 列")

    # v4: emotion_statistics 唯一约束加 user_id（防止跨用户合并）
    if current_version < 4:
        await db.execute(
            "ALTER TABLE emotion_statistics DROP INDEX uk_emotion_daily"
        )
        await db.execute(
            "ALTER TABLE emotion_statistics ADD UNIQUE KEY uk_emotion_daily (user_id, user_date, emotion_label)"
        )
        await db.execute("INSERT INTO comfort_schema_version (version) VALUES (4)")
        _logger.info("comfort schema v4 迁移完成：emotion_statistics 唯一约束添加 user_id")
