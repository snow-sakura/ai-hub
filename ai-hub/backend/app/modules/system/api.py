"""系统管理 & 认证 API 端点"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request

from app.dependencies import get_db_dep
from app.common.core.database import MySQLConnection
from app.common.auth import get_current_user
from app.modules.system.service import SystemService
from app.modules.system.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserCreate,
    UserUpdate,
    UserProfileResponse,
    UserListItem,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
)

logger = logging.getLogger(__name__)

# 使用两个独立的路由器：认证路由和系统管理路由
auth_router = APIRouter()
system_router = APIRouter()


def get_system_service(db: MySQLConnection = Depends(get_db_dep)) -> SystemService:
    """获取系统服务实例"""
    return SystemService(db)


# ════════════════════════════════════════════════════════
# 认证 API (/auth/*)
# ════════════════════════════════════════════════════════


@auth_router.post("/login", response_model=dict)
async def login(req: LoginRequest, svc: SystemService = Depends(get_system_service)):
    """用户登录"""
    try:
        result = await svc.login(req.username, req.password)
        return {"code": 200, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@auth_router.post("/register", response_model=dict)
async def register(req: RegisterRequest, svc: SystemService = Depends(get_system_service)):
    """用户注册"""
    try:
        result = await svc.register(req.username, req.password)
        return {"code": 200, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.get("/me", response_model=dict)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: MySQLConnection = Depends(get_db_dep),
):
    """获取当前用户信息"""
    svc = SystemService(db)
    profile = await svc.get_profile(current_user["user_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"code": 200, "data": profile}


@auth_router.post("/logout", response_model=dict)
async def logout(
    current_user: dict = Depends(get_current_user),
):
    """退出登录（前端需清除 token）"""
    return {"code": 200, "message": "退出成功"}


@auth_router.post("/refresh", response_model=dict)
async def refresh_token(
    current_user: dict = Depends(get_current_user),
):
    """刷新 token"""
    from app.common.auth import create_access_token
    token = create_access_token(
        user_id=current_user["user_id"],
        username=current_user["username"],
        role=current_user["role"],
    )
    return {"code": 200, "data": {"access_token": token, "token_type": "bearer", "expires_in": 86400}}


# ════════════════════════════════════════════════════════
# 系统管理 API (/system/*)
# ════════════════════════════════════════════════════════


@system_router.get("/stats")
async def system_stats(
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """获取系统运行统计"""
    stats = await svc.get_stats()
    return {"code": 200, "data": stats}


@system_router.get("/users")
async def list_users(
    page: int = 1,
    page_size: int = 20,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """获取用户列表"""
    result = await svc.list_users(page, page_size)
    return {"code": 200, "data": result}


@system_router.post("/users")
async def create_user(
    req: UserCreate,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """创建用户"""
    try:
        user = await svc.create_user(
            req.username, req.password,
            display_name=req.display_name,
            email=req.email,
        )
        if req.role_ids:
            await svc.set_user_roles(user["id"], req.role_ids)
        return {"code": 200, "data": user, "message": "用户创建成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@system_router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """获取用户详情"""
    profile = await svc.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"code": 200, "data": profile}


@system_router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    req: UserUpdate,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """更新用户"""
    fields = req.model_dump(exclude_none=True)
    if fields:
        await svc.update_user(user_id, **fields)
    return {"code": 200, "message": "用户更新成功"}


@system_router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """删除用户"""
    await svc.delete_user(user_id)
    return {"code": 200, "message": "用户删除成功"}


@system_router.post("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: str,
    is_active: bool = True,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """启用/禁用用户"""
    await svc.toggle_user_active(user_id, is_active)
    return {"code": 200, "message": "状态更新成功"}


@system_router.get("/users/{user_id}/roles")
async def get_user_roles(
    user_id: str,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """获取用户角色"""
    roles = await svc.get_user_roles(user_id)
    return {"code": 200, "data": roles}


@system_router.put("/users/{user_id}/roles")
async def set_user_roles(
    user_id: str,
    role_ids: list[str],
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """设置用户角色"""
    await svc.set_user_roles(user_id, role_ids)
    return {"code": 200, "message": "角色设置成功"}


# ─── 角色管理 ──────────────────────────────────────


@system_router.get("/roles")
async def list_roles(
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """获取角色列表"""
    roles = await svc.list_roles()
    return {"code": 200, "data": roles}


@system_router.post("/roles")
async def create_role(
    req: RoleCreate,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """创建角色"""
    role = await svc.create_role(req.name, req.description or "", req.permissions)
    return {"code": 200, "data": role, "message": "角色创建成功"}


@system_router.put("/roles/{role_id}")
async def update_role(
    role_id: str,
    req: RoleUpdate,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """更新角色"""
    fields = req.model_dump(exclude_none=True)
    if fields:
        await svc.update_role(role_id, **fields)
    return {"code": 200, "message": "角色更新成功"}


@system_router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """删除角色（内置角色不可删除）"""
    try:
        await svc.delete_role(role_id)
        return {"code": 200, "message": "角色删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── 审计日志 ──────────────────────────────────────


@system_router.get("/audit-logs")
async def list_audit_logs(
    page: int = 1,
    page_size: int = 20,
    user_id: str = None,
    action: str = None,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """获取审计日志"""
    result = await svc.list_audit_logs(page, page_size, user_id, action)
    return {"code": 200, "data": result}


# ─── 操作日志（文件系统） ──────────────────────────


@system_router.get("/operation-logs")
async def list_operation_logs(
    module: str = None,
    action: str = None,
    resource_type: str = None,
    user_id: str = None,
    keyword: str = None,
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """查询操作日志（文件系统）"""
    from app.common.logs.operation_logger import OperationLogger
    result = OperationLogger.query_logs(
        module=module, action=action, resource_type=resource_type,
        user_id=user_id, keyword=keyword, page=page, page_size=page_size,
    )
    return {"code": 200, "data": result}


# ─── 系统设置 ──────────────────────────────────────


@system_router.get("/settings")
async def list_settings(
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """获取所有系统设置"""
    settings = await svc.list_settings()
    return {"code": 200, "data": settings}


@system_router.put("/settings/{key}")
async def update_setting(
    key: str,
    value: str,
    svc: SystemService = Depends(get_system_service),
    current_user: dict = Depends(get_current_user),
):
    """更新系统设置"""
    await svc.set_setting(key, value)
    return {"code": 200, "message": "设置更新成功"}
