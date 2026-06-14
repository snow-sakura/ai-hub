"""哄哄模拟器 API 端点"""

from typing import Any, Optional

from fastapi import APIRouter, Query, Depends, HTTPException, Request

from app.common.api.schemas.common import ApiResponse
from app.modules.comfort.schemas import (
  CharacterCreate,
  CharacterUpdate,
  MemoryCreate,
  MemoryUpdate,
  ComfortSessionCreate,
)
from app.dependencies import get_db_dep
from app.common.core.database import MySQLConnection
from app.modules.comfort.service import ComfortService

router = APIRouter()


# ─── 场景 ─────────────────────────────────────────

@router.get("/scenes")
async def list_scenes(db: MySQLConnection = Depends(get_db_dep), ) -> ApiResponse[list[dict[str, Any]]]:
  """获取所有场景列表"""
  service = ComfortService(db)
  data = await service.list_scenes()
  return ApiResponse(data=data)


@router.get("/scenes/{scene_id}")
async def get_scene(scene_id: str, db: MySQLConnection = Depends(get_db_dep), ) -> ApiResponse[dict[str, Any]]:
  """获取单个场景详情"""
  service = ComfortService(db)
  data = await service.get_scene(scene_id)
  return ApiResponse(data=data)


# ─── 角色 ─────────────────────────────────────────

@router.get("/characters")
async def list_characters(
  scene_id: Optional[str] = Query(None, description="按场景过滤"),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取角色列表"""
  service = ComfortService(db)
  data = await service.list_characters(scene_id)
  return ApiResponse(data=data)


@router.get("/characters/{char_id}")
async def get_character(char_id: str, db: MySQLConnection = Depends(get_db_dep), ) -> ApiResponse[dict[str, Any]]:
  """获取单个角色详情"""
  service = ComfortService(db)
  data = await service.get_character(char_id)
  return ApiResponse(data=data)


@router.post("/characters")
async def create_character(
  request: Request,
  body: CharacterCreate, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[dict[str, Any]]:
  """创建自定义角色"""
  service = ComfortService(db)
  data = await service.create_character(body.model_dump())
  return ApiResponse(data=data)


@router.patch("/characters/{char_id}")
async def update_character(
  request: Request,
  char_id: str, body: CharacterUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """更新角色"""
  service = ComfortService(db)
  update_data = {k: v for k, v in body.model_dump().items() if v is not None}
  data = await service.update_character(char_id, update_data)
  return ApiResponse(data=data)


@router.delete("/characters/{char_id}")
async def delete_character(
  request: Request,
  char_id: str, db: MySQLConnection = Depends(get_db_dep), ) -> ApiResponse[bool]:
  """删除角色（禁止删除内置角色）"""
  service = ComfortService(db)
  char = await service.get_character(char_id)
  if char.get("is_builtin"):
    raise HTTPException(status_code=403, detail="无法删除内置角色")
  await service.delete_character(char_id)
  return ApiResponse(data=True)


# ─── 记忆 ─────────────────────────────────────────

@router.get("/memories/{conversation_id}")
async def list_memories(conversation_id: str, db: MySQLConnection = Depends(get_db_dep), ) -> ApiResponse[list[dict[str, Any]]]:
  """获取会话的记忆列表（校验归属）"""
  service = ComfortService(db)
  data = await service.list_memories(conversation_id)
  return ApiResponse(data=data)


@router.post("/memories")
async def create_memory(
  request: Request,
  body: MemoryCreate, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[dict[str, Any]]:
  """创建记忆"""
  service = ComfortService(db)
  data = await service.create_memory(body.model_dump())
  return ApiResponse(data=data)


@router.patch("/memories/{mem_id}")
async def update_memory(
  request: Request,
  mem_id: str, body: MemoryUpdate, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """更新记忆（校验归属）"""
  service = ComfortService(db)
  await service.update_memory(mem_id, body.content)
  return ApiResponse(data=True)


@router.delete("/memories/{mem_id}")
async def delete_memory(
  request: Request,
  mem_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """删除记忆（校验归属）"""
  service = ComfortService(db)
  await service.delete_memory(mem_id)
  return ApiResponse(data=True)


# ─── 情绪统计 ───────────────────────────────────────

@router.get("/stats")
async def get_emotion_stats(
  request: Request,
  start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
  end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取情绪统计（按用户过滤）"""
  service = ComfortService(db)
  data = await service.get_emotion_stats(start_date, end_date)
  return ApiResponse(data=data)


# ─── 哄哄会话 ───────────────────────────────────────

@router.post("/session")
async def create_comfort_session(
  request: Request,
  body: ComfortSessionCreate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """创建哄哄模拟器会话"""
  service = ComfortService(db)
  data = await service.create_comfort_session(
    scene_id=body.scene_id,
    character_id=body.character_id,
    difficulty=body.difficulty,
    title=body.title,
  )
  return ApiResponse(data=data)


@router.get("/session/{conv_id}")
async def get_comfort_session_info(
  conv_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """获取哄哄会话的场景/角色/原谅值信息（校验归属）"""
  service = ComfortService(db)
  data = await service.get_session_info(conv_id)
  return ApiResponse(data=data)
