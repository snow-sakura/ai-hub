"""Step 4: 用例修订节点 - 根据评审反馈修订测试用例"""

from app.common.core.llm_factory import LLMFactory
from app.modules.ai_testing.prompts import revise_prompt


async def revise_node(state: dict) -> dict:
  """根据评审反馈修订测试用例"""
  llm = LLMFactory.create(
    state.get("model_provider", "deepseek"),
    state.get("model_name", ""),
    reasoning_effort="high",
    api_key=state.get("model_api_key") or None,
  )

  review_result = state.get("review_result", {})

  # 格式化问题列表
  issues_text = ""
  for issue in review_result.get("issues", []):
    severity = issue.get("severity", "unknown")
    desc = issue.get("description", "")
    affected = ", ".join(issue.get("affected_cases", []))
    issues_text += f"- [{severity}] {desc}"
    if affected:
      issues_text += f"（涉及: {affected}）"
    issues_text += "\n"
  if not issues_text:
    issues_text = "- 无具体问题\n"

  # 格式化改进建议（优先使用用户选中的自定义建议）
  custom_suggestions = state.get("custom_suggestions", [])
  if custom_suggestions:
    suggestions_text = "\n".join(f"- {s}" for s in custom_suggestions)
  else:
    suggestions_text = "\n".join(
      f"- {s}" for s in review_result.get("improvement_suggestions", [])
    )
  if not suggestions_text:
    suggestions_text = "- 无改进建议\n"

  # 自定义建议提示（用于提示 LLM 优先参考用户选中的建议）
  custom_suggestions_hint = (
    "本次修订使用用户选中的自定义建议，优先参考自定义建议。"
    if custom_suggestions
    else "本次修订使用 LLM 生成的改进建议，可选择性采纳。"
  )

  chain = revise_prompt | llm
  result = await chain.ainvoke({
    "requirement_text": state["requirement_text"],
    "test_cases": state["test_cases_draft"],
    "review_score": review_result.get("overall_score", 5),
    "issues": issues_text,
    "suggestions": suggestions_text,
    "custom_suggestions_hint": custom_suggestions_hint,
  })

  return {"final_test_cases": result.content}
