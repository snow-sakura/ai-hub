"""系统管理模块数据库表定义"""


SYSTEM_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS system_roles (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  description VARCHAR(500),
  permissions JSON,
  is_builtin TINYINT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS system_user_profiles (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL UNIQUE,
  display_name VARCHAR(100),
  avatar VARCHAR(500),
  email VARCHAR(255),
  phone VARCHAR(50),
  department VARCHAR(200),
  position VARCHAR(200),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_sys_profile_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS system_user_roles (
  user_id VARCHAR(36) NOT NULL,
  role_id VARCHAR(36) NOT NULL,
  PRIMARY KEY (user_id, role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS system_audit_logs (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36),
  username VARCHAR(100),
  action VARCHAR(50) NOT NULL,
  resource_type VARCHAR(50),
  resource_id VARCHAR(255),
  detail TEXT,
  ip VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_audit_user (user_id),
  INDEX idx_audit_action (action),
  INDEX idx_audit_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS system_settings (
  `key` VARCHAR(100) PRIMARY KEY,
  `value` TEXT,
  description VARCHAR(500),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


async def init_system_tables(db) -> None:
    """初始化系统管理表"""
    await db.execute("SET sql_notes = 0")
    await db.execute("SET FOREIGN_KEY_CHECKS = 0")
    try:
        await db.executescript(SYSTEM_TABLES_SQL)
        await _seed_default_roles(db)
        await _seed_default_admin(db)
    finally:
        await db.execute("SET FOREIGN_KEY_CHECKS = 1")
    await db.execute("SET sql_notes = 1")
    await db.commit()


async def _seed_default_roles(db) -> None:
    """初始化默认角色"""
    import uuid
    cursor = await db.execute("SELECT COUNT(*) as cnt FROM system_roles")
    row = await cursor.fetchone()
    if row and row["cnt"] > 0:
        return

    default_roles = [
        {
            "id": str(uuid.uuid4()),
            "name": "admin",
            "description": "系统管理员，拥有全部权限",
            "permissions": '["*"]',
            "is_builtin": 1,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "project_admin",
            "description": "项目管理员，可管理项目内所有资源",
            "permissions": '["project:*"]',
            "is_builtin": 1,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "tester",
            "description": "测试工程师，可执行测试和查看报告",
            "permissions": '["project:view", "case:*", "execution:*", "report:*"]',
            "is_builtin": 1,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "viewer",
            "description": "只读用户，仅可查看项目和报告",
            "permissions": '["project:view", "report:view"]',
            "is_builtin": 1,
        },
    ]
    for role in default_roles:
        await db.execute(
            "INSERT INTO system_roles (id, name, description, permissions, is_builtin) VALUES (%s, %s, %s, %s, %s)",
            (role["id"], role["name"], role["description"], role["permissions"], role["is_builtin"]),
        )


async def _seed_default_admin(db) -> None:
    """初始化默认管理员账号（首次启动时创建）"""
    import uuid
    import logging
    from app.common.auth import hash_password

    _logger = logging.getLogger(__name__)

    # 默认管理员凭据（通过 .env 可覆盖）
    admin_username = "admin"
    admin_password = "admin123"

    # 检查是否已存在 admin 用户
    cursor = await db.execute(
        "SELECT COUNT(*) as cnt FROM users WHERE username = %s",
        (admin_username,),
    )
    row = await cursor.fetchone()
    if row and row["cnt"] > 0:
        return  # 已有管理员账号，跳过

    # 创建管理员用户
    user_id = str(uuid.uuid4())
    password_hash = hash_password(admin_password)
    await db.execute(
        "INSERT INTO users (id, username, password_hash, role, is_active) VALUES (%s, %s, %s, %s, %s)",
        (user_id, admin_username, password_hash, "admin", 1),
    )

    # 创建管理员用户档案
    await db.execute(
        "INSERT INTO system_user_profiles (id, user_id, display_name, email) VALUES (%s, %s, %s, %s)",
        (str(uuid.uuid4()), user_id, "系统管理员", "admin@ai-hub.local"),
    )

    # 关联 admin 角色
    cursor = await db.execute(
        "SELECT id FROM system_roles WHERE name = %s",
        (admin_username,),
    )
    role_row = await cursor.fetchone()
    if role_row:
        await db.execute(
            "INSERT INTO system_user_roles (user_id, role_id) VALUES (%s, %s)",
            (user_id, role_row["id"]),
        )

    _logger.info(
        "默认管理员账号已创建 — 用户名: %s, 密码: %s (请尽快修改密码)",
        admin_username,
        admin_password,
    )
