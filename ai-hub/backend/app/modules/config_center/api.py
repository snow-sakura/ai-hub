"""配置中心模块路由"""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_db_dep
from app.common.api.schemas.common import ApiResponse
from app.common.core.database import MySQLConnection
from app.modules.config_center.schemas import (
    ModelConfigCreate, ModelConfigUpdate,
    PromptConfigCreate, PromptConfigUpdate,
    BehaviorConfigUpdate,
    ChatConfigUpdate,
    UiEnvConfigCreate, UiEnvConfigUpdate,
    AppEnvConfigCreate, AppEnvConfigUpdate,
)
from app.modules.config_center.service import ConfigCenterService

router = APIRouter()


def get_service(db: MySQLConnection = Depends(get_db_dep)) -> ConfigCenterService:
    return ConfigCenterService(db)


# ── AI 模型配置 ──────────────────────────────────────────────

@router.get("/models", response_model=ApiResponse)
async def list_models(svc: ConfigCenterService = Depends(get_service)):
    """获取 AI 模型配置列表"""
    data = await svc.list_models()
    return ApiResponse(code=200, data=data)


@router.get("/models/{model_id}", response_model=ApiResponse)
async def get_model(model_id: str, svc: ConfigCenterService = Depends(get_service)):
    """获取 AI 模型配置详情"""
    data = await svc.get_model(model_id)
    if not data:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    return ApiResponse(code=200, data=data)


@router.post("/models", response_model=ApiResponse)
async def create_model(body: ModelConfigCreate, svc: ConfigCenterService = Depends(get_service)):
    """创建 AI 模型配置"""
    data = await svc.create_model(body.model_dump())
    return ApiResponse(code=200, data=data)


@router.put("/models/{model_id}", response_model=ApiResponse)
async def update_model(model_id: str, body: ModelConfigUpdate, svc: ConfigCenterService = Depends(get_service)):
    """更新 AI 模型配置"""
    data = await svc.update_model(model_id, body.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    return ApiResponse(code=200, data=data)


@router.delete("/models/{model_id}", response_model=ApiResponse)
async def delete_model(model_id: str, svc: ConfigCenterService = Depends(get_service)):
    """删除 AI 模型配置"""
    await svc.delete_model(model_id)
    return ApiResponse(code=200, message="删除成功")


# ── 提示词配置 ──────────────────────────────────────────────

@router.get("/prompts", response_model=ApiResponse)
async def list_prompts(svc: ConfigCenterService = Depends(get_service)):
    """获取提示词配置列表"""
    data = await svc.list_prompts()
    return ApiResponse(code=200, data=data)


@router.get("/prompts/{prompt_id}", response_model=ApiResponse)
async def get_prompt(prompt_id: str, svc: ConfigCenterService = Depends(get_service)):
    """获取提示词配置详情"""
    data = await svc.get_prompt(prompt_id)
    if not data:
        raise HTTPException(status_code=404, detail="提示词不存在")
    return ApiResponse(code=200, data=data)


@router.post("/prompts", response_model=ApiResponse)
async def create_prompt(body: PromptConfigCreate, svc: ConfigCenterService = Depends(get_service)):
    """创建提示词配置"""
    data = await svc.create_prompt(body.model_dump())
    return ApiResponse(code=200, data=data)


@router.put("/prompts/{prompt_id}", response_model=ApiResponse)
async def update_prompt(prompt_id: str, body: PromptConfigUpdate, svc: ConfigCenterService = Depends(get_service)):
    """更新提示词配置"""
    data = await svc.update_prompt(prompt_id, body.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="提示词不存在")
    return ApiResponse(code=200, data=data)


@router.delete("/prompts/{prompt_id}", response_model=ApiResponse)
async def delete_prompt(prompt_id: str, svc: ConfigCenterService = Depends(get_service)):
    """删除提示词配置"""
    await svc.delete_prompt(prompt_id)
    return ApiResponse(code=200, message="删除成功")


# ── 生成行为配置 ──────────────────────────────────────────────

@router.get("/behaviors", response_model=ApiResponse)
async def list_behaviors(svc: ConfigCenterService = Depends(get_service)):
    """获取生成行为配置列表"""
    data = await svc.list_behaviors()
    return ApiResponse(code=200, data=data)


@router.put("/behaviors", response_model=ApiResponse)
async def upsert_behavior(body: BehaviorConfigUpdate, svc: ConfigCenterService = Depends(get_service)):
    """创建/更新生成行为配置"""
    data = await svc.upsert_behavior(body.key, body.value, body.description)
    return ApiResponse(code=200, data=data)


@router.delete("/behaviors/{key}", response_model=ApiResponse)
async def delete_behavior(key: str, svc: ConfigCenterService = Depends(get_service)):
    """删除生成行为配置"""
    await svc.delete_behavior(key)
    return ApiResponse(code=200, message="删除成功")


# ── AI 聊天室配置 ──────────────────────────────────────────────

@router.get("/chat", response_model=ApiResponse)
async def get_chat_config(svc: ConfigCenterService = Depends(get_service)):
    """获取 AI 聊天室配置"""
    data = await svc.get_chat_config()
    return ApiResponse(code=200, data=data)


@router.put("/chat", response_model=ApiResponse)
async def update_chat_config(body: ChatConfigUpdate, svc: ConfigCenterService = Depends(get_service)):
    """更新 AI 聊天室配置"""
    data = await svc.update_chat_config(body.model_dump(exclude_unset=True))
    return ApiResponse(code=200, data=data)


# ── UI 环境配置 ──────────────────────────────────────────────

@router.get("/ui-envs", response_model=ApiResponse)
async def list_ui_envs(svc: ConfigCenterService = Depends(get_service)):
    """获取 UI 测试环境列表"""
    data = await svc.list_ui_envs()
    return ApiResponse(code=200, data=data)


@router.get("/ui-envs/{env_id}", response_model=ApiResponse)
async def get_ui_env(env_id: str, svc: ConfigCenterService = Depends(get_service)):
    """获取 UI 测试环境详情"""
    data = await svc.get_ui_env(env_id)
    if not data:
        raise HTTPException(status_code=404, detail="环境不存在")
    return ApiResponse(code=200, data=data)


@router.post("/ui-envs", response_model=ApiResponse)
async def create_ui_env(body: UiEnvConfigCreate, svc: ConfigCenterService = Depends(get_service)):
    """创建 UI 测试环境"""
    data = await svc.create_ui_env(body.model_dump())
    return ApiResponse(code=200, data=data)


@router.put("/ui-envs/{env_id}", response_model=ApiResponse)
async def update_ui_env(env_id: str, body: UiEnvConfigUpdate, svc: ConfigCenterService = Depends(get_service)):
    """更新 UI 测试环境"""
    data = await svc.update_ui_env(env_id, body.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="环境不存在")
    return ApiResponse(code=200, data=data)


@router.delete("/ui-envs/{env_id}", response_model=ApiResponse)
async def delete_ui_env(env_id: str, svc: ConfigCenterService = Depends(get_service)):
    """删除 UI 测试环境"""
    await svc.delete_ui_env(env_id)
    return ApiResponse(code=200, message="删除成功")


# ── APP 环境配置 ──────────────────────────────────────────────

@router.get("/app-envs", response_model=ApiResponse)
async def list_app_envs(svc: ConfigCenterService = Depends(get_service)):
    """获取 APP 测试环境列表"""
    data = await svc.list_app_envs()
    return ApiResponse(code=200, data=data)


@router.get("/app-envs/{env_id}", response_model=ApiResponse)
async def get_app_env(env_id: str, svc: ConfigCenterService = Depends(get_service)):
    """获取 APP 测试环境详情"""
    data = await svc.get_app_env(env_id)
    if not data:
        raise HTTPException(status_code=404, detail="环境不存在")
    return ApiResponse(code=200, data=data)


@router.post("/app-envs", response_model=ApiResponse)
async def create_app_env(body: AppEnvConfigCreate, svc: ConfigCenterService = Depends(get_service)):
    """创建 APP 测试环境"""
    data = await svc.create_app_env(body.model_dump())
    return ApiResponse(code=200, data=data)


@router.put("/app-envs/{env_id}", response_model=ApiResponse)
async def update_app_env(env_id: str, body: AppEnvConfigUpdate, svc: ConfigCenterService = Depends(get_service)):
    """更新 APP 测试环境"""
    data = await svc.update_app_env(env_id, body.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="环境不存在")
    return ApiResponse(code=200, data=data)


@router.delete("/app-envs/{env_id}", response_model=ApiResponse)
async def delete_app_env(env_id: str, svc: ConfigCenterService = Depends(get_service)):
    """删除 APP 测试环境"""
    await svc.delete_app_env(env_id)
    return ApiResponse(code=200, message="删除成功")
