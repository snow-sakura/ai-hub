"""情绪分析节点 - 分析用户最新消息的情绪"""

from app.shared.agent.state import AgentState
from app.modules.comfort.emotion_analyzer import EmotionAnalyzer


async def emotion_node(state: AgentState) -> dict:
  """分析用户消息中的情绪，将结果存入状态"""
  messages = state["messages"]
  if not messages:
    return {"emotion_result": None}

  # 获取最后一条用户消息
  last_user_msg = None
  for msg in reversed(messages):
    if hasattr(msg, "type") and msg.type == "human":
      last_user_msg = msg.content
      break

  if not last_user_msg:
    return {"emotion_result": None}

  # 构建上下文（最近的消息）
  context_messages = []
  for msg in messages[-6:]:
    if hasattr(msg, "type"):
      role = "user" if msg.type == "human" else "assistant"
      context_messages.append({"role": role, "content": msg.content})

  provider = state.get("model_provider", "deepseek")
  model_name = state.get("model_name", "")

  result = await EmotionAnalyzer.analyze(
    user_message=last_user_msg,
    context_messages=context_messages,
    model_provider=provider,
    model_name=model_name,
  )

  return {"emotion_result": {
    "label": result.label,
    "intensity": result.intensity,
    "reason": result.reason,
    "emoji": result.emoji,
  }}
