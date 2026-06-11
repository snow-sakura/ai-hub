"""哄哄模拟器数据访问层"""

import json
import uuid
from datetime import datetime
from typing import Any

from app.shared.core.database import MySQLConnection
from app.modules.comfort.domain import (
  ComfortScene,
  ComfortCharacter,
  ComfortMemory,
  EmotionStatRecord,
)


class ComfortRepo:
  """哄哄模拟器 Repository"""

  def __init__(self, db: MySQLConnection):
    self.db = db

  # ─── 场景 ─────────────────────────────────────────

  async def list_scenes(self) -> list[dict[str, Any]]:
    """获取所有场景列表"""
    cursor = await self.db.execute(
      "SELECT id, name, description, icon, initial_prompt, difficulty_default, "
      "tags, sort_order, is_builtin, created_at "
      "FROM comfort_scenes ORDER BY sort_order ASC, created_at ASC"
    )
    rows = await cursor.fetchall()
    return [self._parse_scene_row(dict(r)) for r in rows]

  async def get_scene(self, scene_id: str) -> dict[str, Any] | None:
    """获取单个场景"""
    cursor = await self.db.execute(
      "SELECT id, name, description, icon, initial_prompt, difficulty_default, "
      "tags, sort_order, is_builtin, created_at "
      "FROM comfort_scenes WHERE id = ?",
      (scene_id,),
    )
    row = await cursor.fetchone()
    return self._parse_scene_row(dict(row)) if row else None

  async def create_scene(self, scene: ComfortScene) -> None:
    """创建场景"""
    await self.db.execute(
      "INSERT INTO comfort_scenes "
      "(id, name, description, icon, initial_prompt, difficulty_default, "
      "tags, sort_order, is_builtin, created_at) "
      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (
        scene.id, scene.name, scene.description, scene.icon,
        scene.initial_prompt, scene.difficulty_default,
        json.dumps(scene.tags, ensure_ascii=False),
        scene.sort_order, int(scene.is_builtin),
        datetime.now().isoformat(),
      ),
    )
    await self.db.commit()

  async def scene_exists(self, scene_id: str) -> bool:
    """检查场景是否存在"""
    cursor = await self.db.execute(
      "SELECT 1 FROM comfort_scenes WHERE id = ?", (scene_id,)
    )
    return await cursor.fetchone() is not None

  # ─── 角色 ─────────────────────────────────────────

  async def list_characters(self, scene_id: str | None = None) -> list[dict[str, Any]]:
    """获取角色列表，可按场景过滤"""
    if scene_id:
      cursor = await self.db.execute(
        "SELECT id, name, age, identity, personality_tags, speaking_style, "
        "avatar_emoji, backstory, scene_id, is_builtin, created_at "
        "FROM comfort_characters WHERE scene_id = ? ORDER BY is_builtin DESC, created_at ASC",
        (scene_id,),
      )
    else:
      cursor = await self.db.execute(
        "SELECT id, name, age, identity, personality_tags, speaking_style, "
        "avatar_emoji, backstory, scene_id, is_builtin, created_at "
        "FROM comfort_characters ORDER BY is_builtin DESC, created_at ASC"
      )
    rows = await cursor.fetchall()
    return [self._parse_character_row(dict(r)) for r in rows]

  async def get_character(self, char_id: str) -> dict[str, Any] | None:
    """获取单个角色"""
    cursor = await self.db.execute(
      "SELECT id, name, age, identity, personality_tags, speaking_style, "
      "avatar_emoji, backstory, scene_id, is_builtin, created_at "
      "FROM comfort_characters WHERE id = ?",
      (char_id,),
    )
    row = await cursor.fetchone()
    return self._parse_character_row(dict(row)) if row else None

  async def create_character(self, char: ComfortCharacter) -> None:
    """创建角色"""
    await self.db.execute(
      "INSERT INTO comfort_characters "
      "(id, name, age, identity, personality_tags, speaking_style, "
      "avatar_emoji, backstory, scene_id, is_builtin, created_at) "
      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (
        char.id, char.name, char.age, char.identity,
        json.dumps(char.personality_tags, ensure_ascii=False),
        char.speaking_style, char.avatar_emoji, char.backstory,
        char.scene_id, int(char.is_builtin),
        datetime.now().isoformat(),
      ),
    )
    await self.db.commit()

  async def update_character(self, char_id: str, **fields: Any) -> bool:
    """更新角色字段"""
    allowed = {"name", "age", "identity", "speaking_style",
               "avatar_emoji", "backstory", "scene_id"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
      return False
    # personality_tags 需要 JSON 序列化
    if "personality_tags" in fields:
      updates["personality_tags"] = json.dumps(
        fields["personality_tags"], ensure_ascii=False
      )
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [char_id]
    cursor = await self.db.execute(
      f"UPDATE comfort_characters SET {set_clause} WHERE id = ?", values
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def delete_character(self, char_id: str) -> bool:
    """删除角色"""
    cursor = await self.db.execute(
      "DELETE FROM comfort_characters WHERE id = ?", (char_id,)
    )
    await self.db.commit()
    return cursor.rowcount > 0

  # ─── 记忆 ─────────────────────────────────────────

  async def list_memories(self, conversation_id: str) -> list[dict[str, Any]]:
    """获取会话的记忆列表"""
    cursor = await self.db.execute(
      "SELECT id, conversation_id, content, memory_type, importance, created_at "
      "FROM comfort_memories WHERE conversation_id = ? "
      "ORDER BY importance DESC, created_at ASC",
      (conversation_id,),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  async def create_memory(self, mem: ComfortMemory) -> None:
    """创建记忆"""
    await self.db.execute(
      "INSERT INTO comfort_memories "
      "(id, conversation_id, content, memory_type, importance, created_at) "
      "VALUES (?, ?, ?, ?, ?, ?)",
      (
        mem.id, mem.conversation_id, mem.content,
        mem.memory_type, mem.importance,
        datetime.now().isoformat(),
      ),
    )
    await self.db.commit()

  async def update_memory(self, mem_id: str, content: str) -> bool:
    """更新记忆内容"""
    cursor = await self.db.execute(
      "UPDATE comfort_memories SET content = ? WHERE id = ?",
      (content, mem_id),
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def delete_memory(self, mem_id: str) -> bool:
    """删除记忆"""
    cursor = await self.db.execute(
      "DELETE FROM comfort_memories WHERE id = ?", (mem_id,)
    )
    await self.db.commit()
    return cursor.rowcount > 0

  # ─── 情绪统计 ───────────────────────────────────────

  async def upsert_emotion_stat(
    self,
    user_date: str,
    emotion_label: str,
    intensity: float,
    comfort_score: float | None = None,
  ) -> None:
    """插入或更新情绪统计（按日期+情绪类型聚合，原子操作避免竞态）"""
    await self.db.execute(
      "INSERT INTO emotion_statistics "
      "(id, user_date, emotion_label, avg_intensity, count, comfort_score, created_at) "
      "VALUES (?, ?, ?, ?, ?, ?, ?) "
      "ON DUPLICATE KEY UPDATE "
      "  avg_intensity = (avg_intensity * count + VALUES(avg_intensity)) / (count + 1), "
      "  count = count + 1, "
      "  comfort_score = COALESCE(VALUES(comfort_score), comfort_score)",
      (str(uuid.uuid4()), user_date, emotion_label, intensity, 1, comfort_score,
       datetime.now().isoformat()),
    )
    await self.db.commit()

  async def get_emotion_stats(
    self,
    start_date: str,
    end_date: str,
  ) -> list[dict[str, Any]]:
    """获取日期范围内的情绪统计"""
    cursor = await self.db.execute(
      "SELECT id, user_date, emotion_label, avg_intensity, count, "
      "comfort_score, created_at FROM emotion_statistics "
      "WHERE user_date BETWEEN ? AND ? ORDER BY user_date ASC",
      (start_date, end_date),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  # ─── 会话元数据 ─────────────────────────────────────

  async def update_conversation_metadata(
    self, conv_id: str, metadata: dict[str, Any]
  ) -> bool:
    """更新会话的 metadata JSON"""
    meta_json = json.dumps(metadata, ensure_ascii=False)
    now = datetime.now().isoformat()
    cursor = await self.db.execute(
      "UPDATE conversations SET metadata = ?, updated_at = ? WHERE id = ?",
      (meta_json, now, conv_id),
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def get_conversation_metadata(self, conv_id: str) -> dict[str, Any]:
    """获取会话的 metadata"""
    cursor = await self.db.execute(
      "SELECT metadata FROM conversations WHERE id = ?", (conv_id,)
    )
    row = await cursor.fetchone()
    if not row:
      return {}
    try:
      return json.loads(row["metadata"] or "{}")
    except (json.JSONDecodeError, TypeError):
      return {}

  # ─── 行解析辅助 ─────────────────────────────────────

  @staticmethod
  def _parse_scene_row(row: dict[str, Any]) -> dict[str, Any]:
    """解析场景行数据，JSON 反序列化 tags"""
    if "tags" in row and isinstance(row["tags"], str):
      try:
        row["tags"] = json.loads(row["tags"])
      except (json.JSONDecodeError, TypeError):
        row["tags"] = []
    return row

  @staticmethod
  def _parse_character_row(row: dict[str, Any]) -> dict[str, Any]:
    """解析角色行数据，JSON 反序列化 personality_tags"""
    if "personality_tags" in row and isinstance(row["personality_tags"], str):
      try:
        row["personality_tags"] = json.loads(row["personality_tags"])
      except (json.JSONDecodeError, TypeError):
        row["personality_tags"] = []
    return row
