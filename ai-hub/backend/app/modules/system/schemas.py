"""系统管理模块数据模型"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ─── 认证 ──────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = None
    email: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400


class RefreshRequest(BaseModel):
    access_token: str


# ─── 用户 ──────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    password: str
    role_ids: Optional[list[str]] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None


class UserProfileResponse(BaseModel):
    id: str
    username: str
    role: str
    is_active: bool
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    roles: list[str] = []
    created_at: datetime


class UserListItem(BaseModel):
    id: str
    username: str
    role: str
    is_active: bool
    display_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    created_at: datetime


# ─── 角色 ──────────────────────────────────────────

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: list[str] = []


class RoleUpdate(BaseModel):
    description: Optional[str] = None
    permissions: Optional[list[str]] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: list[str] = []
    is_builtin: bool
    user_count: int = 0
    created_at: datetime


# ─── 审计日志 ──────────────────────────────────────

class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    detail: Optional[str] = None
    ip: Optional[str] = None
    created_at: datetime


# ─── 系统设置 ──────────────────────────────────────

class SystemSettingResponse(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SystemSettingUpdate(BaseModel):
    value: str


# ─── 通用响应 ──────────────────────────────────────

class SystemStatsResponse(BaseModel):
    user_count: int
    role_count: int
    active_sessions: int
    audit_log_count: int
