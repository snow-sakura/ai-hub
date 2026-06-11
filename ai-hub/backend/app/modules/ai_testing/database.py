"""AI Testing 模块数据库表 DDL（10 张表 — MySQL 版）"""

from app.shared.core.database import get_db, MySQLConnection


# ── 建表语句（独立语句，不含索引）────────────────────────────────────

CORE_TABLE_DDL: list[str] = [
    # 项目表
    """CREATE TABLE IF NOT EXISTS testing_projects (
      id VARCHAR(36) PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      description TEXT NOT NULL,
      status VARCHAR(20) NOT NULL DEFAULT 'active',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 项目成员表
    """CREATE TABLE IF NOT EXISTS testing_project_members (
      id VARCHAR(36) PRIMARY KEY,
      project_id VARCHAR(36) NOT NULL,
      name VARCHAR(255) NOT NULL,
      role VARCHAR(20) NOT NULL DEFAULT 'tester',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 测试用例表（含完整的 source 选项）
    """CREATE TABLE IF NOT EXISTS testing_cases (
      id VARCHAR(36) PRIMARY KEY,
      project_id VARCHAR(36),
      title VARCHAR(500) NOT NULL,
      version VARCHAR(50) NOT NULL DEFAULT '',
      priority VARCHAR(5) NOT NULL DEFAULT 'P2',
      case_type VARCHAR(50) NOT NULL DEFAULT 'functional',
      preconditions TEXT NOT NULL,
      steps TEXT NOT NULL,
      expected_results TEXT NOT NULL,
      tags TEXT,
      status VARCHAR(20) NOT NULL DEFAULT 'draft',
      source VARCHAR(20) NOT NULL DEFAULT 'manual',
      ai_task_id VARCHAR(36),
      author VARCHAR(100) NOT NULL DEFAULT '',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 生成任务表（含 requirement_title + 输出模式/自动化评审/超时列）
    """CREATE TABLE IF NOT EXISTS testing_generation_tasks (
      id VARCHAR(36) PRIMARY KEY,
      project_id VARCHAR(36),
      input_text TEXT NOT NULL,
      requirement_title VARCHAR(500) NOT NULL DEFAULT '',
      file_path TEXT,
      file_type VARCHAR(50),
      file_name VARCHAR(255),
      model VARCHAR(100) NOT NULL DEFAULT '',
      status VARCHAR(20) NOT NULL DEFAULT 'pending',
      generated_count INT NOT NULL DEFAULT 0,
      error_message TEXT,
      output_mode VARCHAR(20) DEFAULT 'stream',
      enable_auto_review TINYINT DEFAULT 1,
      review_timeout INT DEFAULT 120,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 生成阶段结果表
    """CREATE TABLE IF NOT EXISTS testing_generation_results (
      id VARCHAR(36) PRIMARY KEY,
      task_id VARCHAR(36) NOT NULL,
      stage VARCHAR(20) NOT NULL,
      content TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 配置表（category 含 model/prompt/behavior/secret）
    """CREATE TABLE IF NOT EXISTS testing_config (
      id VARCHAR(36) PRIMARY KEY,
      `key` VARCHAR(255) NOT NULL UNIQUE,
      value TEXT NOT NULL,
      category VARCHAR(20) NOT NULL DEFAULT 'model',
      description TEXT NOT NULL,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 用例附件表
    """CREATE TABLE IF NOT EXISTS testing_case_attachments (
      id VARCHAR(36) PRIMARY KEY,
      case_id VARCHAR(36) NOT NULL,
      file_name VARCHAR(255) NOT NULL,
      file_path TEXT NOT NULL,
      file_size INT NOT NULL DEFAULT 0,
      file_type VARCHAR(100) NOT NULL DEFAULT '',
      uploaded_by VARCHAR(100) NOT NULL DEFAULT '',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 用例评论表
    """CREATE TABLE IF NOT EXISTS testing_case_comments (
      id VARCHAR(36) PRIMARY KEY,
      case_id VARCHAR(36) NOT NULL,
      content TEXT NOT NULL,
      author VARCHAR(100) NOT NULL DEFAULT '',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 操作日志表
    """CREATE TABLE IF NOT EXISTS testing_operation_logs (
      id VARCHAR(36) PRIMARY KEY,
      entity_type VARCHAR(20) NOT NULL,
      entity_id VARCHAR(36) NOT NULL,
      action VARCHAR(100) NOT NULL,
      operator VARCHAR(100) NOT NULL DEFAULT '',
      detail TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 项目版本表
    """CREATE TABLE IF NOT EXISTS testing_project_versions (
      id VARCHAR(36) PRIMARY KEY,
      project_id VARCHAR(36) NOT NULL,
      name VARCHAR(255) NOT NULL,
      description TEXT NOT NULL,
      status VARCHAR(20) NOT NULL DEFAULT 'active',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 生成任务-用例桥接表
    """CREATE TABLE IF NOT EXISTS testing_task_generated_cases (
      id VARCHAR(36) PRIMARY KEY,
      task_id VARCHAR(36) NOT NULL,
      case_id VARCHAR(36) NOT NULL,
      status VARCHAR(20) DEFAULT 'adopted',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 生成候选用例项表（从 LLM 输出解析的单个用例）
    """CREATE TABLE IF NOT EXISTS testing_generated_case_items (
      id VARCHAR(36) PRIMARY KEY,
      task_id VARCHAR(36) NOT NULL,
      title VARCHAR(500) NOT NULL DEFAULT '',
      priority VARCHAR(10) NOT NULL DEFAULT 'P2',
      case_type VARCHAR(50) NOT NULL DEFAULT 'functional',
      preconditions TEXT,
      steps TEXT,
      expected_results TEXT,
      tags TEXT,
      status VARCHAR(20) NOT NULL DEFAULT 'pending',
      sort_order INT DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
]


# ── 索引（独立执行，容错已存在）────────────────────────────────────

TABLE_INDEXES: list[str] = [
    "CREATE INDEX idx_testing_projects_status ON testing_projects(status)",
    "CREATE INDEX idx_project_members_project ON testing_project_members(project_id)",
    "CREATE INDEX idx_testing_cases_project ON testing_cases(project_id)",
    "CREATE INDEX idx_testing_cases_priority ON testing_cases(priority)",
    "CREATE INDEX idx_testing_cases_status ON testing_cases(status)",
    "CREATE INDEX idx_generation_tasks_status ON testing_generation_tasks(status)",
    "CREATE INDEX idx_generation_results_task ON testing_generation_results(task_id)",
    "CREATE UNIQUE INDEX idx_testing_config_key ON testing_config(key)",
    "CREATE INDEX idx_case_attachments_case ON testing_case_attachments(case_id)",
    "CREATE INDEX idx_case_comments_case ON testing_case_comments(case_id)",
    "CREATE INDEX idx_operation_logs_entity ON testing_operation_logs(entity_type, entity_id)",
    "CREATE INDEX idx_project_versions_project ON testing_project_versions(project_id)",
    "CREATE INDEX idx_task_generated_cases_task ON testing_task_generated_cases(task_id)",
    "CREATE INDEX idx_task_generated_cases_case ON testing_task_generated_cases(case_id)",
    "CREATE INDEX idx_generated_case_items_task ON testing_generated_case_items(task_id)",
    "CREATE INDEX idx_generated_case_items_status ON testing_generated_case_items(status)",
]


async def init_testing_tables() -> None:
    """初始化 AI Testing 模块数据库表"""
    db = await get_db()
    try:
        await db.execute("SET SQL_NOTES = 0")
        await db.execute("SET FOREIGN_KEY_CHECKS = 0")
        # 逐条执行建表语句
        for stmt in CORE_TABLE_DDL:
            await db.execute(stmt)
        # 逐条建索引，对"已存在"错误容错
        for stmt in TABLE_INDEXES:
            try:
                await db.execute(stmt)
            except Exception:
                pass  # 索引已存在时忽略
        await _run_migrations(db)
        await db.execute("SET FOREIGN_KEY_CHECKS = 1")
        await db.execute("SET SQL_NOTES = 1")
        await db.commit()
    finally:
        await db.close()


async def _run_migrations(db: MySQLConnection) -> None:
    """执行数据库迁移（版本控制）

    v1-v4 已合并到基础 DDL 中，首次初始化时直接记录版本号。
    后续新迁移在此追加。
    """
    await db.execute(
        "CREATE TABLE IF NOT EXISTS testing_schema_version ("
        "  version INTEGER PRIMARY KEY,"
        "  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ")"
    )

    # 获取当前版本
    cursor = await db.execute(
        "SELECT MAX(version) as max_version FROM testing_schema_version"
    )
    row = await cursor.fetchone()
    current_version = row["max_version"] if row and row["max_version"] else 0

    # v1-v4 已合并到基础 DDL 中，首次运行时直接标记为已应用
    if current_version < 1:
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (1)")
    if current_version < 2:
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (2)")
    if current_version < 3:
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (3)")
    if current_version < 4:
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (4)")
    if current_version < 5:
        # v5: 新列 + 桥接表（已合并到基础 DDL）
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (5)")
    if current_version < 6:
        # v6: testing_generated_case_items 表（已合并到基础 DDL）
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (6)")
