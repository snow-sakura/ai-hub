"""Step 3: AI 评审节点 - 对测试用例进行质量评审与评分"""

import json
import logging

from pydantic import BaseModel, Field

from app.common.core.llm_factory import LLMFactory
from app.modules.ai_testing.prompts import review_prompt

logger = logging.getLogger(__name__)


# ── 结构化输出模型 ────────────────────────────────────────────────────────────
class DimensionScore(BaseModel):
  score: int = Field(ge=1, le=10)
  comment: str = ""


class ReviewIssue(BaseModel):
  severity: str  # critical | major | minor
  description: str
  affected_cases: list[str] = Field(default_factory=list)


class TestCaseReview(BaseModel):
  overall_score: int = Field(ge=1, le=10)
  review_passed: bool
  dimensions: dict[str, DimensionScore] = Field(default_factory=dict)
  issues: list[ReviewIssue] = Field(default_factory=list)
  improvement_suggestions: list[str] = Field(default_factory=list)
  summary: str = ""


def _default_review() -> dict:
  """默认评审结果（无法解析时使用）"""
  return {
    "overall_score": 5,
    "review_passed": False,
    "dimensions": {},
    "issues": [],
    "improvement_suggestions": ["无法解析 LLM 评审结果，建议重试"],
    "summary": "评审结果解析失败",
  }


def _parse_review_json(text: str) -> dict:
  """从 LLM 文本中提取 JSON（支持 markdown 代码块包裹）"""
  text = text.strip()
  # 去掉 ```json ... ```
  if text.startswith("```"):
    lines = text.split("\n")
    # 去掉首尾的 ``` 行
    lines = [l for l in lines if not l.strip().startswith("```")]
    text = "\n".join(lines).strip()
  return json.loads(text)


async def review_node(state: dict) -> dict:
  """对测试用例进行 AI 评审，输出评分和改进建议"""
  llm = LLMFactory.create(
    state.get("model_provider", "deepseek"),
    state.get("model_name", ""),
    reasoning_effort="high",
    api_key=state.get("model_api_key") or None,
  )

  chain = review_prompt | llm
  messages = review_prompt.invoke({
    "requirement_text": state["requirement_text"],
    "test_cases": state["test_cases_draft"],
  })

  # 优先尝试结构化输出（部分模型支持）
  review_data = None
  try:
    structured_llm = llm.with_structured_output(TestCaseReview)
    review_data = await structured_llm.ainvoke(messages)
    if hasattr(review_data, "model_dump"):
      review_data = review_data.model_dump()
    elif hasattr(review_data, "dict"):
      review_data = review_data.dict()
  except Exception as e:
    logger.debug(f"[review_node] 结构化输出失败，降级为 JSON 解析: {e}")
    review_data = None

  # 降级：普通调用 + 手动解析 JSON
  if review_data is None:
    try:
      result = await chain.ainvoke({
        "requirement_text": state["requirement_text"],
        "test_cases": state["test_cases_draft"],
      })
      review_data = _parse_review_json(result.content)
    except Exception as e:
      logger.warning(f"[review_node] JSON 解析失败: {e}")
      review_data = _default_review()

  # 安全校验：确保关键字段存在
  review_data.setdefault("overall_score", 5)
  review_data.setdefault("review_passed", False)
  review_data.setdefault("issues", [])
  review_data.setdefault("improvement_suggestions", [])
  review_data.setdefault("summary", "")

  return {
    "review_result": review_data,
    "review_passed": bool(review_data.get("review_passed", False)),
  }
