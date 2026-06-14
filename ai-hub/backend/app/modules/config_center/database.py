"""配置中心模块数据库表 DDL"""

from app.config import get_settings
from app.common.core.database import get_db, MySQLConnection


_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS config_models (
    id VARCHAR(36) PRIMARY KEY,
    provider VARCHAR(50) NOT NULL COMMENT '供应商: openai/deepseek/qwen/zhipu/ollama',
    model_name VARCHAR(255) NOT NULL DEFAULT '',
    api_key TEXT,
    api_base_url VARCHAR(500) DEFAULT '',
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INT DEFAULT 4096,
    enabled TINYINT DEFAULT 1,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS config_prompts (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT '提示词名称',
    stage VARCHAR(50) NOT NULL DEFAULT '' COMMENT '对应阶段: analyze/write/review/revise',
    content TEXT NOT NULL COMMENT '提示词内容',
    enabled TINYINT DEFAULT 1,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS config_behaviors (
    id VARCHAR(36) PRIMARY KEY,
    `key` VARCHAR(255) NOT NULL UNIQUE COMMENT '配置键',
    `value` TEXT NOT NULL COMMENT '配置值（JSON格式）',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS config_chat (
    id VARCHAR(36) PRIMARY KEY,
    model_provider VARCHAR(50) DEFAULT 'deepseek',
    model_name VARCHAR(255) DEFAULT '',
    system_prompt TEXT,
    max_history INT DEFAULT 20,
    enable_rag TINYINT DEFAULT 0,
    rag_top_k INT DEFAULT 3,
    enable_web_search TINYINT DEFAULT 0,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS config_ui_env (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    base_url VARCHAR(500) DEFAULT '',
    browser_type VARCHAR(20) DEFAULT 'chromium' COMMENT 'chromium/firefox/webkit',
    headless TINYINT DEFAULT 1,
    viewport_width INT DEFAULT 1280,
    viewport_height INT DEFAULT 720,
    timeout_ms INT DEFAULT 30000,
    screenshot_on_failure TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS config_app_env (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(20) DEFAULT 'android' COMMENT 'android/ios',
    app_package VARCHAR(255) DEFAULT '',
    app_activity VARCHAR(255) DEFAULT '',
    device_serial VARCHAR(255) DEFAULT '',
    appium_url VARCHAR(500) DEFAULT 'http://localhost:4723',
    timeout_ms INT DEFAULT 30000,
    screenshot_on_failure TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


async def init_config_tables() -> None:
    """初始化配置中心数据库表"""
    db = await get_db()
    try:
        await db.execute("SET sql_notes = 0")
        for statement in _TABLE_SQL.split(";"):
            stmt = statement.strip()
            if stmt:
                await db.execute(stmt)
        await db.execute("SET sql_notes = 1")
        await db.commit()
    finally:
        await db.close()
