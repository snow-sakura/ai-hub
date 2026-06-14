"""系统管理模块业务逻辑层"""

import uuid
import logging
from typing import Optional

from app.common.auth import hash_password, verify_password, create_access_token
from app.modules.system.repository import SystemRepository

logger = logging.getLogger(__name__)


class SystemService:
    """认证、用户管理、角色管理、审计日志"""

    def __init__(self, db):
        self.repo = SystemRepository(db)

    # ─── 认证 ──────────────────────────────────────────

    async def login(self, username: str, password: str) -> dict:
        """用户登录，返回 token"""
        user = await self.repo.get_user_by_username(username)
        if not user:
            raise ValueError("用户名或密码错误")
        if not user.get("is_active"):
            raise ValueError("账号已被禁用")
        if not verify_password(password, user["password_hash"]):
            raise ValueError("用户名或密码错误")

        token = create_access_token(
            user_id=user["id"],
            username=user["username"],
            role=user.get("role", "user"),
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400,
        }

    async def register(self, username: str, password: str) -> dict:
        """注册新用户"""
        existing = await self.repo.get_user_by_username(username)
        if existing:
            raise ValueError("用户名已存在")
        password_hash = hash_password(password)
        user = await self.repo.create_user(username, password_hash)
        token = create_access_token(
            user_id=user["id"],
            username=user["username"],
            role="user",
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400,
            "user": user,
        }

    async def get_profile(self, user_id: str) -> Optional[dict]:
        """获取用户完整档案"""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            return None
        profile = await self.repo.get_profile(user_id)
        roles = await self.repo.get_user_roles(user_id)
        return {
            "id": user["id"],
            "username": user["username"],
            "role": user.get("role", "user"),
            "is_active": bool(user.get("is_active", True)),
            "display_name": profile.get("display_name") if profile else None,
            "email": profile.get("email") if profile else None,
            "phone": profile.get("phone") if profile else None,
            "department": profile.get("department") if profile else None,
            "position": profile.get("position") if profile else None,
            "roles": [r["name"] for r in roles],
            "created_at": user["created_at"],
        }

    # ─── 用户管理 ──────────────────────────────────────

    async def list_users(self, page: int = 1, page_size: int = 20) -> dict:
        """获取用户列表"""
        users, total = await self.repo.list_users(page, page_size)
        return {"items": users, "total": total, "page": page, "page_size": page_size}

    async def create_user(self, username: str, password: str, **profile) -> dict:
        """创建用户（管理员）"""
        existing = await self.repo.get_user_by_username(username)
        if existing:
            raise ValueError("用户名已存在")
        password_hash = hash_password(password)
        user = await self.repo.create_user(username, password_hash)
        if profile.get("display_name") or profile.get("email"):
            await self.repo.upsert_profile(user["id"], **profile)
        return user

    async def update_user(self, user_id: str, **fields) -> bool:
        """更新用户"""
        return await self.repo.update_user(user_id, **fields)

    async def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        return await self.repo.delete_user(user_id)

    async def toggle_user_active(self, user_id: str, is_active: bool) -> None:
        """启用/禁用用户"""
        await self.repo.set_user_active(user_id, is_active)

    # ─── 角色管理 ──────────────────────────────────────

    async def list_roles(self) -> list[dict]:
        """获取角色列表"""
        return await self.repo.list_roles()

    async def create_role(self, name: str, description: str, permissions: list[str]) -> dict:
        """创建角色"""
        return await self.repo.create_role(name, description, permissions)

    async def update_role(self, role_id: str, **fields) -> bool:
        """更新角色"""
        return await self.repo.update_role(role_id, **fields)

    async def delete_role(self, role_id: str) -> bool:
        """删除角色（内置角色不可删除）"""
        role = await self.repo.get_role_by_id(role_id)
        if not role:
            raise ValueError("角色不存在")
        if role.get("is_builtin"):
            raise ValueError("内置角色不可删除")
        return await self.repo.delete_role(role_id)

    async def get_user_roles(self, user_id: str) -> list[dict]:
        """获取用户角色"""
        return await self.repo.get_user_roles(user_id)

    async def set_user_roles(self, user_id: str, role_ids: list[str]) -> None:
        """设置用户角色"""
        await self.repo.set_user_roles(user_id, role_ids)

    # ─── 审计日志 ──────────────────────────────────────

    async def create_audit_log(self, user_id: str, username: str, action: str,
                               resource_type: str = "", resource_id: str = "",
                               detail: str = "", ip: str = "") -> None:
        """创建审计日志"""
        import uuid
        await self.repo.create_audit_log({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "username": username,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "detail": detail,
            "ip": ip,
        })

    async def list_audit_logs(self, page: int = 1, page_size: int = 20,
                              user_id: Optional[str] = None,
                              action: Optional[str] = None) -> dict:
        """获取审计日志"""
        logs, total = await self.repo.list_audit_logs(page, page_size, user_id, action)
        return {"items": logs, "total": total, "page": page, "page_size": page_size}

    # ─── 系统统计 ──────────────────────────────────────

    async def get_stats(self) -> dict:
        """获取系统统计"""
        users, _ = await self.repo.list_users(page=1, page_size=1)
        roles = await self.repo.list_roles()
        audit_logs, audit_total = await self.repo.list_audit_logs(page=1, page_size=1)
        return {
            "user_count": len(users) if isinstance(users, list) else 0,
            "role_count": len(roles),
            "active_sessions": 0,
            "audit_log_count": audit_total,
        }

    # ─── 系统设置 ──────────────────────────────────────

    async def list_settings(self) -> list[dict]:
        """获取所有系统设置"""
        return await self.repo.list_settings()

    async def set_setting(self, key: str, value: str) -> None:
        """更新系统设置"""
        await self.repo.set_setting(key, value)
