"""会话/消息数据访问层"""

import json
import uuid
from datetime import datetime
from typing import Any

from app.common.core.database import MySQLConnection
from app.common.domain.entities import Conversation, Message


class ConversationRepo:
  """会话 Repository"""

  def __init__(self, db: MySQLConnection):
    self.db = db

  async def create_conversation(
    self,
    title: str = "新会话",
    conv_type: str = "chat",
    metadata: dict[str, Any] | None = None,
  ) -> Conversation:
    """创建新会话"""
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    meta_json = json.dumps(metadata or {}, ensure_ascii=False)
    await self.db.execute(
      "INSERT INTO conversations (id, title, type, metadata, created_at, updated_at) "
      "VALUES (?, ?, ?, ?, ?, ?)",
      (conv_id, title, conv_type, meta_json, now, now),
    )
    await self.db.commit()
    return Conversation(id=conv_id, title=title)

  async def list_conversations(
    self, conv_type: str | None = None, page: int = 1, page_size: int = 20,
  ) -> list[dict[str, Any]]:
    """获取会话列表，可按 type 过滤，支持分页"""
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size
    select_cols = "id, title, type, metadata, created_at, updated_at"
    if conv_type:
      cursor = await self.db.execute(
        f"SELECT {select_cols} FROM conversations WHERE type = ? "
        "ORDER BY updated_at DESC LIMIT ? OFFSET ?",
        (conv_type, page_size, offset),
      )
    else:
      cursor = await self.db.execute(
        f"SELECT {select_cols} FROM conversations ORDER BY updated_at DESC LIMIT ? OFFSET ?",
        (page_size, offset),
      )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]

  async def get_conversation(self, conv_id: str) -> dict[str, Any] | None:
    """获取单个会话"""
    cursor = await self.db.execute(
      "SELECT id, title, type, metadata, created_at, updated_at "
      "FROM conversations WHERE id = ?",
      (conv_id,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None

  async def update_conversation_title(self, conv_id: str, title: str) -> bool:
    """更新会话标题"""
    now = datetime.now().isoformat()
    cursor = await self.db.execute(
      "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
      (title, now, conv_id),
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def delete_conversation(self, conv_id: str) -> bool:
    """删除会话及其消息"""
    cursor = await self.db.execute(
      "DELETE FROM conversations WHERE id = ?", (conv_id,)
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def add_message(self, conversation_id: str, role: str,
                        content: str, metadata: dict[str, Any] | None = None) -> Message:
    """添加消息"""
    msg_id = str(uuid.uuid4())
    meta_json = json.dumps(metadata or {}, ensure_ascii=False)
    now = datetime.now().isoformat()
    await self.db.execute(
      "INSERT INTO messages (id, conversation_id, role, content, metadata, created_at) "
      "VALUES (?, ?, ?, ?, ?, ?)",
      (msg_id, conversation_id, role, content, meta_json, now),
    )
    await self.db.execute(
      "UPDATE conversations SET updated_at = ? WHERE id = ?",
      (now, conversation_id),
    )
    await self.db.commit()
    return Message(
      id=msg_id, conversation_id=conversation_id,
      role=role, content=content, metadata=metadata or {},
    )

  async def list_messages(
    self, conversation_id: str, limit: int = 50, offset: int = 0,
  ) -> list[dict[str, Any]]:
    """分页获取会话消息，按时间倒序（最新在前）"""
    cursor = await self.db.execute(
      "SELECT id, conversation_id, role, content, metadata, created_at "
      "FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
      (conversation_id, limit, offset),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]

  async def count_messages(self, conversation_id: str) -> int:
    """统计会话消息总数"""
    cursor = await self.db.execute(
      "SELECT COUNT(*) as cnt FROM messages WHERE conversation_id = ?",
      (conversation_id,),
    )
    row = await cursor.fetchone()
    return row["cnt"] if row else 0
