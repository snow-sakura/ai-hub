"""哄哄模拟器 API 端点"""

from typing import Any, Optional

from fastapi import APIRouter, Query
import aiosqlite

from app.shared.api.schemas.common import ApiResponse
from app.modules.comfort.schemas import (
  CharacterCreate,
  CharacterUpdate,
  MemoryCreate,
  MemoryUpdate,
  ComfortSessionCreate,
)
from app.shared.core.database import get_db
from app.modules.comfort.service import ComfortService

router = APIRouter()


# ─── 场景 ─────────────────────────────────────────

@router.get("/scenes")
async def list_scenes() -> ApiResponse[list[dict[str, Any]]]:
  """获取所有场景列表"""
  db = await get_db()
  service = ComfortService(db)
  try:
    data = await service.list_scenes()
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/scenes/{scene_id}")
async def get_scene(scene_id: str) -> ApiResponse[dict[str, Any]]:
  """获取单个场景详情"""
  db = await get_db()
  service = ComfortService(db)
  try:
    data = await service.get_scene(scene_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


# ─── 角色 ─────────────────────────────────────────

@router.get("/characters")
async def list_characters(
  scene_id: Optional[str] = Query(None, description="按场景过滤"),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取角色列表"""
  db = await get_db()
  service = ComfortService(db)
  try:
    data = await service.list_characters(scene_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/characters/{char_id}")
async def get_character(char_id: str) -> ApiResponse[dict[str, Any]]:
  """获取单个角色详情"""
  db = await get_db()
  service = ComfortService(db)
  try:
    data = await service.get_character(char_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("/characters")
async def create_character(body: CharacterCreate) -> ApiResponse[dict[str, Any]]:
  """创建自定义角色"""
  db = await get_db()
  service = ComfortService(db)
  try:
    data = await service.create_character(body.model_dump())
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.patch("/characters/{char_id}")
async def update_character(
  char_id: str, body: CharacterUpdate
) -> ApiResponse[dict[str, Any]]:
  """更新角色"""
  db = await get_db()
  service = ComfortService(db)
  try:
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    data = await service.update_character(char_id, update_data)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.delete("/characters/{char_id}")
async def delete_character(char_id: str) -> ApiResponse[bool]:
  """删除角色"""
  db = await get_db()
  service = ComfortService(db)
  try:
    await service.delete_character(char_id)
    return ApiResponse(data=True)
  finally:
    await db.close()


# ─── 记忆 ─────────────────────────────────────────

@router.get("/memories/{conversation_id}")
async def list_memories(conversation_id: str) -> ApiResponse[list[dict[str, Any]]]:
  """获取会话的记忆列表"""
  db = await get_db()
  service = ComfortService(db)
  try:
    data = await service.list_memories(conversation_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("/memories")
async def create_memory(body: MemoryCreate) -> ApiResponse[dict[str, Any]]:
  """创建记忆"""
  db = await get_db()
  service = ComfortService(db)
  try:
    data = await service.create_memory(body.model_dump())
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.patch("/memories/{mem_id}")
async def update_memory(mem_id: str, body: MemoryUpdate) -> ApiResponse[bool]:
  """更新记忆"""
  db = await get_db()
  service = ComfortService(db)
  try:
    await service.update_memory(mem_id, body.content)
    return ApiResponse(data=True)
  finally:
    await db.close()


@router.delete("/memories/{mem_id}")
async def delete_memory(mem_id: str) -> ApiResponse[bool]:
  """删除记忆"""
  db = await get_db()
  service = ComfortService(db)
  try:
    await service.delete_memory(mem_id)
    return ApiResponse(data=True)
  finally:
    await db.close()


# ─── 情绪统计 ───────────────────────────────────────

@router.get("/stats")
async def get_emotion_stats(
  start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
  end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取情绪统计"""
  db = await get_db()
  service = ComfortService(db)
  try:
    data = await service.get_emotion_stats(start_date, end_date)
    return ApiResponse(data=data)
  finally:
    await db.close()


# ─── 哄哄会话 ───────────────────────────────────────

@router.post("/session")
async def create_comfort_session(
  body: ComfortSessionCreate,
) -> ApiResponse[dict[str, Any]]:
  """创建哄哄模拟器会话"""
  db = await get_db()
  service = ComfortService(db)
  try:
    data = await service.create_comfort_session(
      scene_id=body.scene_id,
      character_id=body.character_id,
      difficulty=body.difficulty,
      title=body.title,
    )
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/session/{conv_id}")
async def get_comfort_session_info(
  conv_id: str,
) -> ApiResponse[dict[str, Any]]:
  """获取哄哄会话的场景/角色/原谅值信息"""
  db = await get_db()
  service = ComfortService(db)
  try:
    data = await service.get_session_info(conv_id)
    return ApiResponse(data=data)
  finally:
    await db.close()
