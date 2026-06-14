"""Step 2: 用例编写节点 - 根据分析结果编写结构化测试用例"""

from app.common.core.llm_factory import LLMFactory
from app.modules.ai_testing.prompts import write_prompt


async def write_node(state: dict) -> dict:
  """根据需求分析结果编写测试用例（如已有草稿则跳过）"""
  if state.get("existing_draft"):
    return {"test_cases_draft": state["existing_draft"]}

  llm = LLMFactory.create(
    state.get("model_provider", "deepseek"),
    state.get("model_name", ""),
    reasoning_effort="high",
    api_key=state.get("model_api_key") or None,
  )

  project_context = ""
  if state.get("project_context"):
    project_context = f"## 项目背景\n{state['project_context']}"

  chain = write_prompt | llm
  result = await chain.ainvoke({
    "requirement_text": state["requirement_text"],
    "analysis_result": state["analysis_result"],
    "project_context": project_context,
  })

  return {"test_cases_draft": result.content}
