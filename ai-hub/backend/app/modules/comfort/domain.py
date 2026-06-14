"""哄哄模拟器领域实体 - 纯数据类，无框架依赖"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ComfortScene:
  """场景实体"""
  id: str
  name: str
  description: str
  icon: str = "🎭"
  initial_prompt: str = ""
  difficulty_default: int = 3
  tags: list[str] = field(default_factory=list)
  sort_order: int = 0
  is_builtin: bool = False
  created_at: datetime | None = None


@dataclass
class ComfortCharacter:
  """角色人设实体"""
  id: str
  name: str
  age: int | None = None
  identity: str = ""
  personality_tags: list[str] = field(default_factory=list)
  speaking_style: str = ""
  avatar_emoji: str = "😊"
  backstory: str = ""
  scene_id: str | None = None
  is_builtin: bool = False
  created_at: datetime | None = None


@dataclass
class ComfortMemory:
  """AI 记忆实体"""
  id: str
  conversation_id: str
  content: str
  user_id: str = ""
  memory_type: str = "fact"  # fact / preference / event
  importance: float = 0.5
  created_at: datetime | None = None


@dataclass
class EmotionResult:
  """情绪分析结果"""
  label: str  # anger / sadness / anxiety / fatigue / calm / joy / fear
  intensity: float  # 0.0 ~ 1.0
  reason: str = ""

  @property
  def emoji(self) -> str:
    """情绪对应的 emoji"""
    mapping = {
      "anger": "😡",
      "sadness": "😢",
      "anxiety": "😰",
      "fatigue": "😩",
      "calm": "😌",
      "joy": "😊",
      "fear": "😨",
    }
    return mapping.get(self.label, "😐")


@dataclass
class ForgivenessResult:
  """原谅值计算结果"""
  current: float  # 当前原谅值 0-100
  delta: float  # 本次变化量
  reason: str = ""
  trend: str = "stable"  # up / down / stable


@dataclass
class EmotionStatRecord:
  """情绪统计聚合记录"""
  id: str
  user_date: str  # YYYY-MM-DD
  emotion_label: str
  avg_intensity: float
  count: int = 1
  comfort_score: float | None = None
  created_at: datetime | None = None
