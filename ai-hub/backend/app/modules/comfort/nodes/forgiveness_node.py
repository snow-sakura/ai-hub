"""原谅值计算节点 - 基于情绪分析结果更新原谅值"""

from app.shared.agent.state import AgentState
from app.modules.comfort.domain import EmotionResult
from app.modules.comfort.forgiveness_engine import calculate_forgiveness


def forgiveness_node(state: AgentState) -> dict:
  """根据情绪分析结果计算原谅值变化"""
  emotion_data = state.get("emotion_result")
  comfort_meta = state.get("comfort_metadata", {})

  if not emotion_data:
    return {"forgiveness_result": None}

  # 构建 EmotionResult
  emotion = EmotionResult(
    label=emotion_data.get("label", "calm"),
    intensity=emotion_data.get("intensity", 0.5),
    reason=emotion_data.get("reason", ""),
  )

  # 从 comfort_metadata 获取当前状态
  current_forgiveness = comfort_meta.get("forgiveness", 50.0)
  difficulty = comfort_meta.get("difficulty", 3)
  turn_count = comfort_meta.get("turn_count", 0)

  # 计算原谅值变化
  result = calculate_forgiveness(
    current=current_forgiveness,
    emotion=emotion,
    difficulty=difficulty,
    turn_count=turn_count,
  )

  return {"forgiveness_result": {
    "current": result.current,
    "delta": result.delta,
    "reason": result.reason,
    "trend": result.trend,
  }}
