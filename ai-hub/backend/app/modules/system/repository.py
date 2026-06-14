"""系统管理模块数据访问层"""

import uuid
import logging
from datetime import datetime
from typing import Optional

from app.common.core.database import MySQLConnection

logger = logging.getLogger(__name__)


class SystemRepository:
    """用户、角色、审计日志的数据库操作"""

    def __init__(self, db: MySQLConnection):
        self.db = db

    # ─── 用户 ──────────────────────────────────────────

    async def create_user(self, username: str, password_hash: str, role: str = "user") -> dict:
        """创建用户"""
        user_id = str(uuid.uuid4())
        now = datetime.now()
        await self.db.execute(
            "INSERT INTO users (id, username, password_hash, role, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, username, password_hash, role, now, now),
        )
        return {"id": user_id, "username": username, "role": role}

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """通过用户名查找用户"""
        cursor = await self.db.execute(
            "SELECT * FROM users WHERE username = %s", (username,)
        )
        return await cursor.fetchone()

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """通过 ID 查找用户"""
        cursor = await self.db.execute(
            "SELECT * FROM users WHERE id = %s", (user_id,)
        )
        return await cursor.fetchone()

    async def list_users(self, page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
        """获取用户列表（分页）"""
        offset = (page - 1) * page_size
        cursor = await self.db.execute("SELECT COUNT(*) as cnt FROM users")
        row = await cursor.fetchone()
        total = row["cnt"] if row else 0

        cursor = await self.db.execute(
            "SELECT id, username, role, is_active, created_at, updated_at "
            "FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (page_size, offset),
        )
        users = await cursor.fetchall() or []
        return users, total

    async def update_user(self, user_id: str, **fields) -> bool:
        """更新用户字段"""
        if not fields:
            return False
        sets = []
        values = []
        for key, val in fields.items():
            sets.append(f"{key} = %s")
            values.append(val)
        values.append(user_id)
        await self.db.execute(
            f"UPDATE users SET {', '.join(sets)} WHERE id = %s", values
        )
        return True

    async def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        await self.db.execute("DELETE FROM users WHERE id = %s", (user_id,))
        return True

    async def set_user_active(self, user_id: str, is_active: bool) -> None:
        """设置用户激活状态"""
        await self.db.execute(
            "UPDATE users SET is_active = %s WHERE id = %s", (1 if is_active else 0, user_id)
        )

    # ─── 用户档案 ──────────────────────────────────────

    async def upsert_profile(self, user_id: str, **fields) -> None:
        """创建或更新用户档案"""
        existing = await self.get_profile(user_id)
        if existing:
            sets = []
            values = []
            for key, val in fields.items():
                if val is not None:
                    sets.append(f"{key} = %s")
                    values.append(val)
            if not sets:
                return
            values.append(user_id)
            await self.db.execute(
                f"UPDATE system_user_profiles SET {', '.join(sets)} WHERE user_id = %s",
                values,
            )
        else:
            profile_id = str(uuid.uuid4())
            cols = ["id", "user_id"]
            vals = [profile_id, user_id]
            placeholders = ["%s", "%s"]
            for key, val in fields.items():
                if val is not None:
                    cols.append(key)
                    vals.append(val)
                    placeholders.append("%s")
            await self.db.execute(
                f"INSERT INTO system_user_profiles ({', '.join(cols)}) VALUES ({', '.join(placeholders)})",
                vals,
            )

    async def get_profile(self, user_id: str) -> Optional[dict]:
        """获取用户档案"""
        cursor = await self.db.execute(
            "SELECT * FROM system_user_profiles WHERE user_id = %s", (user_id,)
        )
        return await cursor.fetchone()

    # ─── 角色 ──────────────────────────────────────────

    async def list_roles(self) -> list[dict]:
        """获取角色列表"""
        cursor = await self.db.execute(
            "SELECT r.*, (SELECT COUNT(*) FROM system_user_roles ur WHERE ur.role_id = r.id) as user_count "
            "FROM system_roles r ORDER BY r.is_builtin DESC, r.name ASC"
        )
        rows = await cursor.fetchall() or []
        for row in rows:
            if isinstance(row.get("permissions"), str):
                import json
                row["permissions"] = json.loads(row["permissions"])
        return rows

    async def get_role_by_id(self, role_id: str) -> Optional[dict]:
        """获取角色"""
        cursor = await self.db.execute("SELECT * FROM system_roles WHERE id = %s", (role_id,))
        return await cursor.fetchone()

    async def create_role(self, name: str, description: str, permissions: list[str]) -> dict:
        """创建角色"""
        role_id = str(uuid.uuid4())
        import json
        await self.db.execute(
            "INSERT INTO system_roles (id, name, description, permissions) VALUES (%s, %s, %s, %s)",
            (role_id, name, description, json.dumps(permissions)),
        )
        return {"id": role_id, name: name}

    async def update_role(self, role_id: str, **fields) -> bool:
        """更新角色"""
        if not fields:
            return False
        sets = []
        values = []
        for key, val in fields.items():
            sets.append(f"{key} = %s")
            if key == "permissions" and isinstance(val, list):
                import json
                values.append(json.dumps(val))
            else:
                values.append(val)
        values.append(role_id)
        await self.db.execute(
            f"UPDATE system_roles SET {', '.join(sets)} WHERE id = %s", values
        )
        return True

    async def delete_role(self, role_id: str) -> bool:
        """删除角色"""
        await self.db.execute("DELETE FROM system_roles WHERE id = %s", (role_id,))
        return True

    async def get_user_roles(self, user_id: str) -> list[dict]:
        """获取用户角色列表"""
        cursor = await self.db.execute(
            "SELECT r.* FROM system_roles r "
            "JOIN system_user_roles ur ON r.id = ur.role_id "
            "WHERE ur.user_id = %s", (user_id,)
        )
        return await cursor.fetchall() or []

    async def set_user_roles(self, user_id: str, role_ids: list[str]) -> None:
        """设置用户角色"""
        await self.db.execute("DELETE FROM system_user_roles WHERE user_id = %s", (user_id,))
        for rid in role_ids:
            await self.db.execute(
                "INSERT INTO system_user_roles (user_id, role_id) VALUES (%s, %s)",
                (user_id, rid),
            )

    # ─── 审计日志 ──────────────────────────────────────

    async def create_audit_log(self, log_data: dict) -> None:
        """创建审计日志"""
        await self.db.execute(
            "INSERT INTO system_audit_logs "
            "(id, user_id, username, action, resource_type, resource_id, detail, ip, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                log_data.get("id"),
                log_data.get("user_id"),
                log_data.get("username"),
                log_data.get("action"),
                log_data.get("resource_type"),
                log_data.get("resource_id"),
                log_data.get("detail"),
                log_data.get("ip"),
                datetime.now(),
            ),
        )

    async def list_audit_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        """获取审计日志列表"""
        conditions = []
        params = []
        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)
        if action:
            conditions.append("action = %s")
            params.append(action)

        where = "WHERE " + " AND ".join(conditions) if conditions else ""

        cursor = await self.db.execute(f"SELECT COUNT(*) as cnt FROM system_audit_logs {where}", params)
        row = await cursor.fetchone()
        total = row["cnt"] if row else 0

        offset = (page - 1) * page_size
        cursor = await self.db.execute(
            f"SELECT * FROM system_audit_logs {where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
            params + [page_size, offset],
        )
        logs = await cursor.fetchall() or []
        return logs, total

    # ─── 系统设置 ──────────────────────────────────────

    async def get_setting(self, key: str) -> Optional[str]:
        """获取系统设置值"""
        cursor = await self.db.execute(
            "SELECT `value` FROM system_settings WHERE `key` = %s", (key,)
        )
        row = await cursor.fetchone()
        return row["value"] if row else None

    async def set_setting(self, key: str, value: str) -> None:
        """设置系统设置值"""
        await self.db.execute(
            "INSERT INTO system_settings (`key`, `value`) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE `value` = %s",
            (key, value, value),
        )

    async def list_settings(self) -> list[dict]:
        """获取所有系统设置"""
        cursor = await self.db.execute("SELECT * FROM system_settings ORDER BY `key`")
        return await cursor.fetchall() or []
