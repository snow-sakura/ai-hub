"""会话管理 API 端点"""

from typing import Any

from fastapi import APIRouter, Depends
import aiosqlite

from app.api.schemas.common import ApiResponse
from app.api.schemas.conversation import ConversationCreate, ConversationUpdate
from app.core.database import get_db
from app.service.conversation_service import ConversationService

router = APIRouter()


async def get_conv_service() -> ConversationService:
  """获取会话 Service"""
  db = await get_db()
  return ConversationService(db)


@router.get("")
async def list_conversations() -> ApiResponse[list[dict[str, Any]]]:
  """获取会话列表"""
  db = await get_db()
  service = ConversationService(db)
  try:
    data = await service.list_all()
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("")
async def create_conversation(body: ConversationCreate) -> ApiResponse[dict[str, Any]]:
  """新建会话"""
  db = await get_db()
  service = ConversationService(db)
  try:
    data = await service.create(body.title)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.patch("/{conv_id}")
async def rename_conversation(
  conv_id: str, body: ConversationUpdate
) -> ApiResponse[dict[str, Any]]:
  """重命名会话"""
  db = await get_db()
  service = ConversationService(db)
  try:
    data = await service.rename(conv_id, body.title)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.delete("/{conv_id}")
async def delete_conversation(conv_id: str) -> ApiResponse[bool]:
  """删除会话"""
  db = await get_db()
  service = ConversationService(db)
  try:
    await service.delete(conv_id)
    return ApiResponse(data=True)
  finally:
    await db.close()


@router.get("/{conv_id}/messages")
async def get_messages(conv_id: str) -> ApiResponse[list[dict[str, Any]]]:
  """获取会话的历史消息"""
  db = await get_db()
  service = ConversationService(db)
  try:
    data = await service.get_messages(conv_id)
    return ApiResponse(data=data)
  finally:
    await db.close()
