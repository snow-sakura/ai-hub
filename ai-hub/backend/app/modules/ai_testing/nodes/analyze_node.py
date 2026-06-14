"""Step 1: 需求分析节点 - 提取功能点、边界条件、异常场景"""

from app.common.core.llm_factory import LLMFactory
from app.modules.ai_testing.prompts import analyze_prompt


async def analyze_node(state: dict) -> dict:
  """分析需求文档，提取测试要点（如已有分析结果则跳过）"""
  if state.get("existing_analysis"):
    return {"analysis_result": state["existing_analysis"]}

  llm = LLMFactory.create(
    state.get("model_provider", "deepseek"),
    state.get("model_name", ""),
    reasoning_effort="max",
    api_key=state.get("model_api_key") or None,
  )

  project_context = ""
  if state.get("project_context"):
    project_context = f"## 项目背景\n{state['project_context']}"

  chain = analyze_prompt | llm
  result = await chain.ainvoke({
    "requirement_text": state["requirement_text"],
    "project_context": project_context,
  })

  return {"analysis_result": result.content}
