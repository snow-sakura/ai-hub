"""哄哄模拟器相关 Schema"""

from typing import Any
from pydantic import BaseModel, Field


# ─── 场景 ──────────────────────────────────────────

class SceneResponse(BaseModel):
  """场景响应"""
  id: str
  name: str
  description: str
  icon: str = "🎭"
  initial_prompt: str = ""
  difficulty_default: int = 3
  tags: list[str] = []
  sort_order: int = 0
  is_builtin: bool = False


# ─── 角色 ──────────────────────────────────────────

class CharacterCreate(BaseModel):
  """创建角色请求"""
  name: str
  age: int | None = None
  identity: str = ""
  personality_tags: list[str] = []
  speaking_style: str = ""
  avatar_emoji: str = "😊"
  backstory: str = ""
  scene_id: str | None = None


class CharacterUpdate(BaseModel):
  """更新角色请求"""
  name: str | None = None
  age: int | None = None
  identity: str | None = None
  personality_tags: list[str] | None = None
  speaking_style: str | None = None
  avatar_emoji: str | None = None
  backstory: str | None = None
  scene_id: str | None = None


class CharacterResponse(BaseModel):
  """角色响应"""
  id: str
  name: str
  age: int | None = None
  identity: str = ""
  personality_tags: list[str] = []
  speaking_style: str = ""
  avatar_emoji: str = "😊"
  backstory: str = ""
  scene_id: str | None = None
  is_builtin: bool = False


# ─── 记忆 ──────────────────────────────────────────

class MemoryCreate(BaseModel):
  """创建记忆请求"""
  conversation_id: str
  content: str
  memory_type: str = "fact"
  importance: float = Field(default=0.5, ge=0, le=1)


class MemoryUpdate(BaseModel):
  """更新记忆请求"""
  content: str


class MemoryResponse(BaseModel):
  """记忆响应"""
  id: str
  conversation_id: str
  content: str
  memory_type: str = "fact"
  importance: float = 0.5
  created_at: str = ""


# ─── 情绪统计 ────────────────────────────────────────

class EmotionStatResponse(BaseModel):
  """情绪统计响应"""
  id: str
  user_date: str
  emotion_label: str
  avg_intensity: float
  count: int = 1
  comfort_score: float | None = None


class EmotionStatsQuery(BaseModel):
  """情绪统计查询参数"""
  start_date: str  # YYYY-MM-DD
  end_date: str    # YYYY-MM-DD


# ─── 哄哄会话创建 ────────────────────────────────────

class ComfortSessionCreate(BaseModel):
  """创建哄哄模拟器会话"""
  scene_id: str
  character_id: str
  difficulty: int = Field(default=3, ge=1, le=5)
  title: str = "哄哄模拟器"


# ─── 情绪 / 原谅值 SSE 事件 ──────────────────────────

class EmotionEvent(BaseModel):
  """情绪 SSE 事件"""
  label: str
  intensity: float
  emoji: str
  message_index: int = 0


class ForgivenessEvent(BaseModel):
  """原谅值 SSE 事件"""
  current: float
  delta: float
  reason: str = ""
  trend: str = "stable"
