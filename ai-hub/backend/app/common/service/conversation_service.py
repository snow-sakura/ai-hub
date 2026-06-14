"""会话管理 Service 层"""

from datetime import datetime
from typing import Any

from app.common.core.database import MySQLConnection
from app.common.domain.exceptions import ConversationNotFoundError
from app.common.repository.conversation_repo import ConversationRepo


class ConversationService:
  """会话业务逻辑"""

  def __init__(self, db: MySQLConnection):
    self.repo = ConversationRepo(db)

  async def create(
    self,
    title: str = "新会话",
    conv_type: str = "chat",
    metadata: dict[str, Any] | None = None,
  ) -> dict[str, Any]:
    """创建新会话"""
    conv = await self.repo.create_conversation(title, conv_type, metadata)
    now = datetime.now().isoformat()
    return {
      "id": conv.id,
      "title": conv.title,
      "type": conv_type,
      "metadata": metadata or {},
      "created_at": now,
      "updated_at": now,
    }

  async def list_all(self, conv_type: str | None = None) -> list[dict[str, Any]]:
    """获取会话列表"""
    return await self.repo.list_conversations(conv_type)

  async def get(self, conv_id: str) -> dict[str, Any]:
    """获取会话详情"""
    conv = await self.repo.get_conversation(conv_id)
    if not conv:
      raise ConversationNotFoundError(conv_id)
    return conv

  async def rename(self, conv_id: str, title: str) -> dict[str, Any]:
    """重命名会话"""
    success = await self.repo.update_conversation_title(conv_id, title)
    if not success:
      raise ConversationNotFoundError(conv_id)
    return {
      "id": conv_id,
      "title": title,
      "updated_at": datetime.now().isoformat(),
    }

  async def delete(self, conv_id: str) -> bool:
    """删除会话"""
    success = await self.repo.delete_conversation(conv_id)
    if not success:
      raise ConversationNotFoundError(conv_id)
    return True

  async def get_messages(
    self, conv_id: str, page: int = 1, page_size: int = 50,
  ) -> dict[str, Any]:
    """分页获取会话消息"""
    conv = await self.repo.get_conversation(conv_id)
    if not conv:
      raise ConversationNotFoundError(conv_id)

    offset = (page - 1) * page_size
    items = await self.repo.list_messages(conv_id, limit=page_size, offset=offset)
    total = await self.repo.count_messages(conv_id)
    return {"items": items, "total": total}

  async def save_message(self, conv_id: str, role: str, content: str,
                         metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """保存消息"""
    conv = await self.repo.get_conversation(conv_id)
    if not conv:
      raise ConversationNotFoundError(conv_id)
    msg = await self.repo.add_message(conv_id, role, content, metadata)
    return {
      "id": msg.id,
      "conversation_id": msg.conversation_id,
      "role": msg.role,
      "content": msg.content,
      "metadata": msg.metadata,
    }
