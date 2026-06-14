"""AI Testing 模块数据库表 DDL（10 张表 — MySQL 版）"""

from app.config import get_settings
from app.common.core.database import get_db, MySQLConnection


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
      project_id VARCHAR(36),
      name VARCHAR(255) NOT NULL,
      role VARCHAR(20) NOT NULL DEFAULT 'tester',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 项目-成员关联表（多对多）
    """CREATE TABLE IF NOT EXISTS testing_project_member_links (
      project_id VARCHAR(36) NOT NULL,
      member_id VARCHAR(36) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (project_id, member_id)
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
      project_id VARCHAR(36),
      name VARCHAR(255) NOT NULL,
      description TEXT NOT NULL,
      status VARCHAR(20) NOT NULL DEFAULT 'active',
      pass_rate DECIMAL(5,2) DEFAULT 0.00,
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

    # 评审主表
    """CREATE TABLE IF NOT EXISTS testing_reviews (
      id VARCHAR(36) PRIMARY KEY,
      project_id VARCHAR(36),
      title VARCHAR(500) NOT NULL,
      description TEXT,
      priority VARCHAR(5) NOT NULL DEFAULT 'P1',
      status VARCHAR(20) NOT NULL DEFAULT 'pending',
      progress INT NOT NULL DEFAULT 0,
      due_date TIMESTAMP NULL,
      creator VARCHAR(100) NOT NULL DEFAULT '',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 评审-用例关联表
    """CREATE TABLE IF NOT EXISTS testing_review_cases (
      id VARCHAR(36) PRIMARY KEY,
      review_id VARCHAR(36) NOT NULL,
      case_id VARCHAR(36) NOT NULL,
      comment TEXT,
      status VARCHAR(20) NOT NULL DEFAULT 'pending',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # 评审-评审人关联表
    """CREATE TABLE IF NOT EXISTS testing_review_reviewers (
      id VARCHAR(36) PRIMARY KEY,
      review_id VARCHAR(36) NOT NULL,
      member_id VARCHAR(36) NOT NULL,
      name VARCHAR(100) NOT NULL DEFAULT '',
      status VARCHAR(20) NOT NULL DEFAULT 'pending',
      progress INT NOT NULL DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # AI 评测师会话表
    """CREATE TABLE IF NOT EXISTS testing_ai_tester_sessions (
      id VARCHAR(36) PRIMARY KEY,
      name VARCHAR(255) NOT NULL DEFAULT '',
      model VARCHAR(100) NOT NULL DEFAULT '',
      message_count INT NOT NULL DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",

    # AI 评测师消息表
    """CREATE TABLE IF NOT EXISTS testing_ai_tester_messages (
      id VARCHAR(36) PRIMARY KEY,
      session_id VARCHAR(36) NOT NULL,
      role VARCHAR(10) NOT NULL,
      content TEXT NOT NULL,
      rating VARCHAR(10) DEFAULT NULL COMMENT '用户评分: up/down/null',
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
    "CREATE INDEX idx_project_member_links_member ON testing_project_member_links(member_id)",
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
    "CREATE INDEX idx_reviews_project ON testing_reviews(project_id)",
    "CREATE INDEX idx_reviews_status ON testing_reviews(status)",
    "CREATE INDEX idx_review_cases_review ON testing_review_cases(review_id)",
    "CREATE INDEX idx_review_cases_case ON testing_review_cases(case_id)",
    "CREATE INDEX idx_review_reviewers_review ON testing_review_reviewers(review_id)",
    "CREATE INDEX idx_ai_tester_messages_session ON testing_ai_tester_messages(session_id)",
]


async def init_testing_tables() -> None:
    """初始化 AI Testing 模块数据库表"""
    db = await get_db()
    try:
        await db.execute("SET sql_notes = 0")
        await db.execute("SET FOREIGN_KEY_CHECKS = 0")
        try:
            # 逐条执行建表语句
            for stmt in CORE_TABLE_DDL:
                await db.execute(stmt)
            # 逐条建索引，对"已存在"错误容错
            for stmt in TABLE_INDEXES:
                try:
                    await db.execute(stmt)
                except Exception as idx_err:
                    import logging
                    logging.getLogger(__name__).debug(f"索引创建跳过（可能已存在）: {idx_err}")
        finally:
            await db.execute("SET FOREIGN_KEY_CHECKS = 1")
        await _run_migrations(db)
        await db.execute("SET sql_notes = 1")
        await db.commit()
    finally:
        await db.close()


async def _column_exists(db: MySQLConnection, table: str, column: str) -> bool:
    """使用 INFORMATION_SCHEMA 检查列是否存在"""
    settings = get_settings()
    cursor = await db.execute(
        "SELECT COUNT(*) as cnt FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (settings.mysql_database, table, column),
    )
    row = await cursor.fetchone()
    return row["cnt"] > 0 if row else False


async def _run_migrations(db: MySQLConnection) -> None:
    """执行数据库迁移（版本控制）

    v1-v4 已合并到基础 DDL 中，首次初始化时直接记录版本号。
    v5: ALTER TABLE testing_generation_tasks 添加4个新列
    v6: 创建 testing_task_generated_cases / testing_generated_case_items 表
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
        # v5: 实际执行 ALTER TABLE 添加4个新列（幂等：先检查列是否存在）
        import logging
        _logger = logging.getLogger(__name__)

        v5_columns = {
            "requirement_title": "VARCHAR(500) NOT NULL DEFAULT ''",
            "output_mode": "VARCHAR(20) DEFAULT 'stream'",
            "enable_auto_review": "TINYINT DEFAULT 1",
            "review_timeout": "INT DEFAULT 120",
        }
        for col_name, col_def in v5_columns.items():
            if not await _column_exists(db, "testing_generation_tasks", col_name):
                await db.execute(
                    f"ALTER TABLE testing_generation_tasks ADD COLUMN {col_name} {col_def}"
                )
                _logger.info("v5 迁移: 添加列 testing_generation_tasks.%s", col_name)

        await db.execute("INSERT INTO testing_schema_version (version) VALUES (5)")

    if current_version < 6:
        # v6: 创建 testing_generated_case_items 表（IF NOT EXISTS 保证幂等）
        await db.execute(
            "CREATE TABLE IF NOT EXISTS testing_generated_case_items ("
            "  id VARCHAR(36) PRIMARY KEY,"
            "  task_id VARCHAR(36) NOT NULL,"
            "  title VARCHAR(500) NOT NULL DEFAULT '',"
            "  priority VARCHAR(10) NOT NULL DEFAULT 'P2',"
            "  case_type VARCHAR(50) NOT NULL DEFAULT 'functional',"
            "  preconditions TEXT,"
            "  steps TEXT,"
            "  expected_results TEXT,"
            "  tags TEXT,"
            "  status VARCHAR(20) NOT NULL DEFAULT 'pending',"
            "  sort_order INT DEFAULT 0,"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS testing_task_generated_cases ("
            "  id VARCHAR(36) PRIMARY KEY,"
            "  task_id VARCHAR(36) NOT NULL,"
            "  case_id VARCHAR(36) NOT NULL,"
            "  status VARCHAR(20) DEFAULT 'adopted',"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        # 创建索引（容错已存在）
        for idx_stmt in [
            "CREATE INDEX idx_task_generated_cases_task ON testing_task_generated_cases(task_id)",
            "CREATE INDEX idx_task_generated_cases_case ON testing_task_generated_cases(case_id)",
            "CREATE INDEX idx_generated_case_items_task ON testing_generated_case_items(task_id)",
            "CREATE INDEX idx_generated_case_items_status ON testing_generated_case_items(status)",
        ]:
            try:
                await db.execute(idx_stmt)
            except Exception:
                pass
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (6)")

    if current_version < 7:
        # v7: testing_project_versions 增加 due_date 和 pass_rate 列
        if not await _column_exists(db, "testing_project_versions", "due_date"):
            await db.execute(
                "ALTER TABLE testing_project_versions ADD COLUMN due_date TIMESTAMP NULL"
            )
        if not await _column_exists(db, "testing_project_versions", "pass_rate"):
            await db.execute(
                "ALTER TABLE testing_project_versions ADD COLUMN pass_rate DECIMAL(5,2) DEFAULT 0.00"
            )
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (7)")

    if current_version < 9:
        # v9: testing_project_versions 和 testing_project_members 的 project_id 改为可空（独立模块无项目关联）
        await db.execute("ALTER TABLE testing_project_versions MODIFY COLUMN project_id VARCHAR(36)")
        await db.execute("ALTER TABLE testing_project_members MODIFY COLUMN project_id VARCHAR(36)")
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (9)")

    if current_version < 10:
        # v10: 删除 testing_project_versions 中不再使用的 due_date 列
        if await _column_exists(db, "testing_project_versions", "due_date"):
            await db.execute("ALTER TABLE testing_project_versions DROP COLUMN due_date")
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (10)")

    if current_version < 11:
        # v11: 创建项目-成员多对多关联表，迁移已有 project_id 数据
        await db.execute(
            "CREATE TABLE IF NOT EXISTS testing_project_member_links ("
            "  project_id VARCHAR(36) NOT NULL,"
            "  member_id VARCHAR(36) NOT NULL,"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  PRIMARY KEY (project_id, member_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        # 迁移已有关联：将 project_id 非空的成员插入关联表
        await db.execute(
            "INSERT IGNORE INTO testing_project_member_links (project_id, member_id) "
            "SELECT project_id, id FROM testing_project_members WHERE project_id IS NOT NULL"
        )
        # 清空成员表的 project_id（改为纯成员池 + 关联表方式）
        await db.execute("UPDATE testing_project_members SET project_id = NULL")
        # 建索引
        try:
            await db.execute(
                "CREATE INDEX idx_project_member_links_member "
                "ON testing_project_member_links(member_id)"
            )
        except Exception:
            pass
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (11)")

    if current_version < 8:
        # v8: 新增 8 张表（评审、测试套件、AI 评测师）
        v8_tables = [
            # testing_reviews
            """CREATE TABLE IF NOT EXISTS testing_reviews (
              id VARCHAR(36) PRIMARY KEY,
              project_id VARCHAR(36),
              title VARCHAR(500) NOT NULL,
              description TEXT,
              priority VARCHAR(5) NOT NULL DEFAULT 'P1',
              status VARCHAR(20) NOT NULL DEFAULT 'pending',
              progress INT NOT NULL DEFAULT 0,
              due_date TIMESTAMP NULL,
              creator VARCHAR(100) NOT NULL DEFAULT '',
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
            # testing_review_cases
            """CREATE TABLE IF NOT EXISTS testing_review_cases (
              id VARCHAR(36) PRIMARY KEY,
              review_id VARCHAR(36) NOT NULL,
              case_id VARCHAR(36) NOT NULL,
              comment TEXT,
              status VARCHAR(20) NOT NULL DEFAULT 'pending',
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
            # testing_review_reviewers
            """CREATE TABLE IF NOT EXISTS testing_review_reviewers (
              id VARCHAR(36) PRIMARY KEY,
              review_id VARCHAR(36) NOT NULL,
              member_id VARCHAR(36) NOT NULL,
              name VARCHAR(100) NOT NULL DEFAULT '',
              status VARCHAR(20) NOT NULL DEFAULT 'pending',
              progress INT NOT NULL DEFAULT 0,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
            # testing_ai_tester_sessions
            """CREATE TABLE IF NOT EXISTS testing_ai_tester_sessions (
              id VARCHAR(36) PRIMARY KEY,
              name VARCHAR(255) NOT NULL DEFAULT '',
              model VARCHAR(100) NOT NULL DEFAULT '',
              message_count INT NOT NULL DEFAULT 0,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
            # testing_ai_tester_messages
            """CREATE TABLE IF NOT EXISTS testing_ai_tester_messages (
              id VARCHAR(36) PRIMARY KEY,
              session_id VARCHAR(36) NOT NULL,
              role VARCHAR(10) NOT NULL,
              content TEXT NOT NULL,
              rating VARCHAR(10) DEFAULT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
        ]
        for stmt in v8_tables:
            await db.execute(stmt)
        # v8 索引
        v8_indexes = [
            "CREATE INDEX idx_reviews_project ON testing_reviews(project_id)",
            "CREATE INDEX idx_reviews_status ON testing_reviews(status)",
            "CREATE INDEX idx_review_cases_review ON testing_review_cases(review_id)",
            "CREATE INDEX idx_review_cases_case ON testing_review_cases(case_id)",
            "CREATE INDEX idx_review_reviewers_review ON testing_review_reviewers(review_id)",
            "CREATE INDEX idx_ai_tester_messages_session ON testing_ai_tester_messages(session_id)",
        ]
        for idx_stmt in v8_indexes:
            try:
                await db.execute(idx_stmt)
            except Exception:
                pass
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (8)")

    if current_version < 12:
        # v12: 定时任务配置表 + 执行日志表
        await db.execute(
            "CREATE TABLE IF NOT EXISTS testing_scheduled_tasks ("
            "  id VARCHAR(36) PRIMARY KEY,"
            "  name VARCHAR(255) NOT NULL,"
            "  module VARCHAR(20) NOT NULL DEFAULT 'api',"
            "  suite_id VARCHAR(36),"
            "  suite_name VARCHAR(255) DEFAULT '',"
            "  cron_expr VARCHAR(100) NOT NULL DEFAULT '0 8 * * *',"
            "  enabled TINYINT DEFAULT 1,"
            "  last_run_at TIMESTAMP NULL,"
            "  next_run_at TIMESTAMP NULL,"
            "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS testing_scheduled_task_logs ("
            "  id VARCHAR(36) PRIMARY KEY,"
            "  task_id VARCHAR(36) NOT NULL,"
            "  status VARCHAR(20) NOT NULL DEFAULT 'running',"
            "  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  completed_at TIMESTAMP NULL,"
            "  duration VARCHAR(50) DEFAULT ''"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        try:
            await db.execute("CREATE INDEX idx_scheduled_task_logs_task ON testing_scheduled_task_logs(task_id)")
        except Exception:
            pass
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (12)")

    if current_version < 13:
        # [已删除] api_testing 系列表 — 模块已在 Phase 1 修正中清理
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (13)")

    # ── v14: Mock 服务 + 通知配置 ──────────────────────────────
    if current_version < 14:
        # [已删除] api_testing_mock_rules/notification_config — 模块已清理
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (14)")

    if current_version < 15:
        # v15: testing_ai_tester_messages 增加 rating 字段（AI 评测师消息评分）
        if not await _column_exists(db, "testing_ai_tester_messages", "rating"):
            await db.execute(
                "ALTER TABLE testing_ai_tester_messages "
                "ADD COLUMN rating VARCHAR(10) DEFAULT NULL COMMENT '用户评分: up/down/null'"
            )
        await db.execute("INSERT INTO testing_schema_version (version) VALUES (15)")
