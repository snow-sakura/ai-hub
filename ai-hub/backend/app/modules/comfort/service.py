"""哄哄模拟器 Service 层"""

import uuid
import json
from typing import Any

from app.common.core.database import MySQLConnection
from app.common.domain.exceptions import (
  ComfortSceneNotFoundError,
  ComfortCharacterNotFoundError,
  ComfortMemoryNotFoundError,
)
from app.modules.comfort.repository import ComfortRepo
from app.modules.comfort.domain import ComfortCharacter, ComfortMemory
from app.common.service.conversation_service import ConversationService


class ComfortService:
  """哄哄模拟器业务逻辑"""

  def __init__(self, db: MySQLConnection):
    self.repo = ComfortRepo(db)

  # ─── 场景 ─────────────────────────────────────────

  async def list_scenes(self) -> list[dict[str, Any]]:
    """获取所有场景"""
    return await self.repo.list_scenes()

  async def get_scene(self, scene_id: str) -> dict[str, Any]:
    """获取单个场景"""
    scene = await self.repo.get_scene(scene_id)
    if not scene:
      raise ComfortSceneNotFoundError(scene_id)
    return scene

  # ─── 角色 ─────────────────────────────────────────

  async def list_characters(self, scene_id: str | None = None) -> list[dict[str, Any]]:
    """获取角色列表"""
    return await self.repo.list_characters(scene_id)

  async def get_character(self, char_id: str) -> dict[str, Any]:
    """获取单个角色"""
    char = await self.repo.get_character(char_id)
    if not char:
      raise ComfortCharacterNotFoundError(char_id)
    return char

  async def create_character(self, data: dict[str, Any]) -> dict[str, Any]:
    """创建自定义角色"""
    char_id = str(uuid.uuid4())
    char = ComfortCharacter(
      id=char_id,
      name=data["name"],
      age=data.get("age"),
      identity=data.get("identity", ""),
      personality_tags=data.get("personality_tags", []),
      speaking_style=data.get("speaking_style", ""),
      avatar_emoji=data.get("avatar_emoji", "😊"),
      backstory=data.get("backstory", ""),
      scene_id=data.get("scene_id"),
      is_builtin=False,
    )
    await self.repo.create_character(char)
    return await self.repo.get_character(char_id) or {}

  async def update_character(self, char_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """更新角色"""
    existing = await self.repo.get_character(char_id)
    if not existing:
      raise ComfortCharacterNotFoundError(char_id)
    success = await self.repo.update_character(char_id, **data)
    if not success:
      raise ComfortCharacterNotFoundError(char_id)
    return await self.repo.get_character(char_id) or {}

  async def delete_character(self, char_id: str) -> bool:
    """删除角色"""
    existing = await self.repo.get_character(char_id)
    if not existing:
      raise ComfortCharacterNotFoundError(char_id)
    await self.repo.delete_character(char_id)
    return True

  # ─── 记忆 ─────────────────────────────────────────

  async def list_memories(self, conversation_id: str) -> list[dict[str, Any]]:
    """获取会话的记忆列表"""
    return await self.repo.list_memories(conversation_id)

  async def create_memory(self, data: dict[str, Any]) -> dict[str, Any]:
    """创建记忆"""
    mem_id = str(uuid.uuid4())
    mem = ComfortMemory(
      id=mem_id,
      conversation_id=data["conversation_id"],
      content=data["content"],
      memory_type=data.get("memory_type", "fact"),
      importance=data.get("importance", 0.5),
    )
    await self.repo.create_memory(mem)
    memories = await self.repo.list_memories(data["conversation_id"])
    for m in memories:
      if m["id"] == mem_id:
        return m
    return {"id": mem_id, "content": data["content"]}

  async def update_memory(self, mem_id: str, content: str) -> bool:
    """更新记忆"""
    success = await self.repo.update_memory(mem_id, content)
    if not success:
      raise ComfortMemoryNotFoundError(mem_id)
    return True

  async def delete_memory(self, mem_id: str) -> bool:
    """删除记忆"""
    success = await self.repo.delete_memory(mem_id)
    if not success:
      raise ComfortMemoryNotFoundError(mem_id)
    return True

  # ─── 情绪统计 ───────────────────────────────────────

  async def get_emotion_stats(self, start_date: str, end_date: str) -> list[dict[str, Any]]:
    """获取情绪统计"""
    return await self.repo.get_emotion_stats(start_date, end_date)

  # ─── 哄哄会话创建 ───────────────────────────────────

  async def create_comfort_session(
    self,
    scene_id: str,
    character_id: str,
    difficulty: int = 3,
    title: str = "哄哄模拟器",
  ) -> dict[str, Any]:
    """创建哄哄模拟器会话，返回含会话ID和场景信息的完整数据"""
    scene = await self.repo.get_scene(scene_id)
    if not scene:
      raise ComfortSceneNotFoundError(scene_id)
    character = await self.repo.get_character(character_id)
    if not character:
      raise ComfortCharacterNotFoundError(character_id)

    metadata = {
      "scene_id": scene_id,
      "scene_name": scene["name"],
      "character_id": character_id,
      "character_name": character["name"],
      "difficulty": difficulty,
      "forgiveness": 50.0,
      "emotion_log": [],
      "turn_count": 0,
    }

    db = self.repo.db
    conv_service = ConversationService(db)
    conv = await conv_service.create(
      title=title,
      conv_type="comfort",
      metadata=metadata,
    )

    return {
      "conversation": conv,
      "scene": scene,
      "character": character,
      "metadata": metadata,
    }

  async def get_session_info(self, conv_id: str) -> dict[str, Any]:
    """获取哄哄会话的场景/角色/原谅值等完整信息"""
    meta = await self.repo.get_conversation_metadata(conv_id)
    if not meta or "scene_id" not in meta:
      return {"metadata": {}}

    scene = await self.repo.get_scene(meta.get("scene_id", ""))
    character = await self.repo.get_character(meta.get("character_id", ""))

    return {
      "metadata": meta,
      "scene": scene,
      "character": character,
    }
