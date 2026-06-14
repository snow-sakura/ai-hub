"""会话管理 API 端点"""

from typing import Any, Optional

from fastapi import APIRouter, Query, Depends

from app.common.api.schemas.common import ApiResponse
from app.common.api.schemas.conversation import ConversationCreate, ConversationUpdate
from app.common.core.database import get_db
from app.common.service.conversation_service import ConversationService

router = APIRouter()


@router.get("")
async def list_conversations(
  type: Optional[str] = Query(None, description="按类型过滤"),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取会话列表"""
  db = await get_db()
  service = ConversationService(db)
  try:
    data = await service.list_all(conv_type=type)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("")
async def create_conversation(body: ConversationCreate) -> ApiResponse[dict[str, Any]]:
  """新建会话"""
  db = await get_db()
  service = ConversationService(db)
  try:
    data = await service.create(
      title=body.title,
      conv_type=body.type,
      metadata=body.metadata,
    )
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.patch("/{conv_id}")
async def rename_conversation(
  conv_id: str, body: ConversationUpdate) -> ApiResponse[dict[str, Any]]:
  """重命名会话（校验归属）"""
  db = await get_db()
  service = ConversationService(db)
  try:
    data = await service.rename(conv_id, body.title)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.delete("/{conv_id}")
async def delete_conversation(conv_id: str) -> ApiResponse[bool]:
  """删除会话（校验归属）"""
  db = await get_db()
  service = ConversationService(db)
  try:
    await service.delete(conv_id)
    return ApiResponse(data=True)
  finally:
    await db.close()


@router.get("/{conv_id}/messages")
async def get_messages(
  conv_id: str,
  page: int = Query(1, ge=1, description="页码"),
  page_size: int = Query(50, ge=1, le=200, description="每页条数"),
) -> ApiResponse[dict[str, Any]]:
  """分页获取会话的历史消息（校验归属）"""
  db = await get_db()
  service = ConversationService(db)
  try:
    data = await service.get_messages(conv_id, page=page, page_size=page_size)
    return ApiResponse(data=data)
  finally:
    await db.close()
