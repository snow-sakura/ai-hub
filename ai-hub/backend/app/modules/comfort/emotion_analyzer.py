"""LLM 情绪分析器 - 结构化输出分析用户情绪"""

import json
from langchain_core.messages import SystemMessage, HumanMessage

from app.common.core.llm_factory import LLMFactory
from app.modules.comfort.domain import EmotionResult


EMOTION_ANALYSIS_PROMPT = """你是一个专业的情绪分析助手。请分析用户最新消息中的情绪状态。

## 分析维度
- **情绪类型**: anger(愤怒) / sadness(悲伤) / anxiety(焦虑) / fatigue(疲惫) / calm(平静) / joy(喜悦) / fear(恐惧)
- **情绪强度**: 0.0 ~ 1.0 之间的浮点数
- **原因**: 简短说明判断依据（一句话）

## 输出格式
请严格按照以下 JSON 格式输出，不要包含任何其他文本：
```json
{
  "label": "情绪类型",
  "intensity": 0.0到1.0的数值,
  "reason": "判断依据"
}
```

## 分析原则
1. 关注用户消息中透露的真实情绪，而非字面含义
2. 如果消息包含多种情绪，选择最强烈的那种
3. 如果用户表现出质问、不满、攻击性语言，倾向于 anger
4. 如果用户表现出委屈、沮丧、低落，倾向于 sadness
5. 如果用户表现出紧张、担忧、不确定，倾向于 anxiety
6. 如果用户语气平和、接纳、理解，倾向于 calm
7. 如果用户表现出开心、释然、感激，倾向于 joy
"""


class EmotionAnalyzer:
  """情绪分析器"""

  @staticmethod
  async def analyze(
    user_message: str,
    context_messages: list[dict] | None = None,
    model_provider: str = "deepseek",
    model_name: str = "",
  ) -> EmotionResult:
    """分析用户消息的情绪"""
    try:
      llm = LLMFactory.create(model_provider, model_name)
      # 使用较低 temperature 提高分析一致性
      llm.temperature = 0.3

      messages = [SystemMessage(content=EMOTION_ANALYSIS_PROMPT)]

      # 如果有上下文消息，提供最近几轮作为参考
      if context_messages:
        recent = context_messages[-4:]  # 最近 2 轮
        context_text = "\n".join(
          f"{'用户' if m['role'] == 'user' else 'AI'}: {m['content'][:200]}"
          for m in recent
        )
        messages.append(HumanMessage(content=f"对话上下文:\n{context_text}\n\n请分析最新消息的情绪。"))

      messages.append(HumanMessage(content=f"请分析以下消息的情绪:\n\n{user_message}"))

      response = await llm.ainvoke(messages)
      content = response.content.strip()

      # 提取 JSON
      return EmotionAnalyzer._parse_response(content)
    except Exception as e:
      # 降级：返回中性情绪
      return EmotionResult(label="calm", intensity=0.3, reason=f"分析降级: {str(e)[:50]}")

  @staticmethod
  def _parse_response(content: str) -> EmotionResult:
    """解析 LLM 返回的 JSON"""
    # 尝试直接解析
    try:
      data = json.loads(content)
      return EmotionResult(
        label=data.get("label", "calm"),
        intensity=max(0.0, min(1.0, float(data.get("intensity", 0.5)))),
        reason=data.get("reason", ""),
      )
    except (json.JSONDecodeError, ValueError, TypeError):
      pass

    # 尝试提取 ```json ... ``` 块
    if "```" in content:
      start = content.find("{")
      end = content.rfind("}") + 1
      if start >= 0 and end > start:
        try:
          data = json.loads(content[start:end])
          return EmotionResult(
            label=data.get("label", "calm"),
            intensity=max(0.0, min(1.0, float(data.get("intensity", 0.5)))),
            reason=data.get("reason", ""),
          )
        except (json.JSONDecodeError, ValueError, TypeError):
          pass

    # 降级
    return EmotionResult(label="calm", intensity=0.3, reason="无法解析情绪分析结果")
