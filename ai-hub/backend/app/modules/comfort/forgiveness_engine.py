"""原谅值计算引擎 - 基于情绪分析结果计算原谅值变化"""

from app.modules.comfort.domain import EmotionResult, ForgivenessResult


# 难度 → 难度系数映射 (1-5 星)
DIFFICULTY_FACTORS: dict[int, float] = {
  1: 0.4,  # 简单 - 容易获得原谅
  2: 0.7,
  3: 1.0,  # 中等
  4: 1.3,
  5: 1.6,  # 困难 - 很难获得原谅
}

# 情绪 → 基础变化量映射
# 正值 = 原谅值上升（用户安慰有效），负值 = 下降
EMOTION_BASE_DELTA: dict[str, float] = {
  "joy": 8.0,      # 用户让对方开心了 → 大幅上升
  "calm": 5.0,     # 用户让对方平静了 → 上升
  "fatigue": -2.0, # 疲惫 → 小幅下降
  "sadness": -4.0, # 悲伤 → 下降
  "anxiety": -3.0, # 焦虑 → 下降
  "fear": -3.0,    # 恐惧 → 下降
  "anger": -6.0,   # 愤怒 → 大幅下降
}

# 情绪强度阈值：高强度负面情绪更难挽回
INTENSITY_THRESHOLD = 0.7


def calculate_forgiveness(
  current: float,
  emotion: EmotionResult,
  difficulty: int = 3,
  turn_count: int = 0,
) -> ForgivenessResult:
  """计算原谅值变化

  Args:
    current: 当前原谅值 (0-100)
    emotion: 本轮情绪分析结果
    difficulty: 难度等级 (1-5)
    turn_count: 当前对话轮次（用于衰减计算）

  Returns:
    ForgivenessResult: 包含新值、变化量、原因和趋势
  """
  # 1. 基础变化量
  base_delta = EMOTION_BASE_DELTA.get(emotion.label, 0.0)

  # 2. 情绪强度调节（高强度负面情绪变化更剧烈）
  intensity_factor = 1.0
  if emotion.intensity > INTENSITY_THRESHOLD:
    if base_delta < 0:
      intensity_factor = 1.0 + (emotion.intensity - INTENSITY_THRESHOLD) * 1.5
    else:
      intensity_factor = 1.0 + (emotion.intensity - INTENSITY_THRESHOLD) * 0.5

  # 3. 难度系数
  diff_factor = DIFFICULTY_FACTORS.get(difficulty, 1.0)

  # 4. 轮次衰减（前几轮变化快，后期趋缓）
  turn_decay = 1.0 / (1.0 + turn_count * 0.05)

  # 5. 计算最终变化量
  raw_delta = base_delta * intensity_factor * diff_factor * turn_decay

  # 6. 边界附近的变化抑制（接近 0 或 100 时变化放缓）
  if current + raw_delta > 100:
    raw_delta = (100 - current) * 0.3
  elif current + raw_delta < 0:
    raw_delta = -(current) * 0.3

  # 取整
  delta = round(raw_delta, 1)
  new_value = max(0.0, min(100.0, current + delta))

  # 7. 生成原因说明
  reason = _generate_reason(emotion, delta, difficulty)

  # 8. 趋势判断
  if delta > 0.5:
    trend = "up"
  elif delta < -0.5:
    trend = "down"
  else:
    trend = "stable"

  return ForgivenessResult(
    current=round(new_value, 1),
    delta=delta,
    reason=reason,
    trend=trend,
  )


def _generate_reason(emotion: EmotionResult, delta: float, difficulty: int) -> str:
  """生成原谅值变化的原因说明"""
  emotion_names = {
    "anger": "愤怒", "sadness": "悲伤", "anxiety": "焦虑",
    "fatigue": "疲惫", "calm": "平静", "joy": "喜悦", "fear": "恐惧",
  }
  emotion_name = emotion_names.get(emotion.label, "未知")

  if delta > 3:
    return f"对方感受到你的真诚，情绪从{emotion_name}转为开心，原谅值大幅上升"
  elif delta > 0:
    return f"你的安慰有些效果，对方情绪略有缓和，原谅值小幅上升"
  elif delta > -3:
    return f"对方还在{emotion_name}中，你的安慰效果一般"
  else:
    return f"对方更加{emotion_name}了，可能需要换个方式安慰"
