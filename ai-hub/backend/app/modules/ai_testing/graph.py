"""AI Testing LangGraph 图构建

流程:
  START → analyze_node → write_node → review_node
    → [review_passed=True → END]
    → [review_passed=False → revise_node → END]

State 字段:
  - requirement_text:    需求文本（入参）
  - project_context:     项目背景（入参，可选）
  - model_provider:      LLM provider（入参）
  - model_name:          LLM model（入参）
  - analysis_result:     Step1 分析结果
  - test_cases_draft:    Step2 用例草稿
  - review_result:       Step3 评审结果（dict）
  - review_passed:       评审是否通过（条件路由）
  - final_test_cases:    Step4 最终用例（通过后 = test_cases_draft，未通过 = 修订后）
  - review_round:        评审轮次（保留字段，未来支持多轮）
"""

import logging

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

from app.common.core.managed_graph import ManagedGraphBase
from app.modules.ai_testing.nodes import (
  analyze_node,
  write_node,
  review_node,
  revise_node,
)

logger = logging.getLogger(__name__)


# ── State 定义 ────────────────────────────────────────────────────────────────
class TestCaseGenState(TypedDict, total=False):
  requirement_text: str        # 入参：需求文本
  project_context: str         # 入参：项目背景（可选）
  model_provider: str          # 入参：LLM provider
  model_name: str              # 入参：LLM model
  model_api_key: str           # 入参：模块级自定义 API Key（可选）
  custom_suggestions: list     # 入参：用户选中的改进建议（可选）
  existing_analysis: str       # 入参：已有的分析结果（修订时跳过 analyze）
  existing_draft: str          # 入参：已有的用例草稿（修订时跳过 write）
  analysis_result: str         # Step1 输出
  test_cases_draft: str        # Step2 输出
  review_result: dict          # Step3 输出
  review_passed: bool          # Step3 输出（路由判断用）
  final_test_cases: str        # 最终用例
  review_round: int            # 评审轮次


# ── 条件路由 ──────────────────────────────────────────────────────────────────
def _route_after_review(state: dict) -> str:
  """评审后路由：通过则直接结束，未通过则进入修订"""
  if state.get("review_passed", False):
    return "end"
  return "revise"


def _pass_through(state: dict) -> dict:
  """评审通过时：将草稿直接作为最终用例"""
  return {"final_test_cases": state.get("test_cases_draft", "")}


# ── 图构建 ────────────────────────────────────────────────────────────────────
def build_testing_graph() -> StateGraph:
  """构建测试用例生成工作流图（未编译）"""
  builder = StateGraph(TestCaseGenState)

  # 添加节点
  builder.add_node("analyze", analyze_node)
  builder.add_node("write", write_node)
  builder.add_node("review", review_node)
  builder.add_node("revise", revise_node)
  builder.add_node("pass_through", _pass_through)

  # 线性边: START → analyze → write → review
  builder.add_edge(START, "analyze")
  builder.add_edge("analyze", "write")
  builder.add_edge("write", "review")

  # 条件边: review → [passed → pass_through → END | failed → revise → END]
  builder.add_conditional_edges(
    "review",
    _route_after_review,
    {"end": "pass_through", "revise": "revise"},
  )
  builder.add_edge("pass_through", END)
  builder.add_edge("revise", END)

  return builder


# ── 托管图实例 ────────────────────────────────────────────────────────────────
class ManagedTestingGraph(ManagedGraphBase):
  """AI Testing 托管图，带 MySQL checkpointer（SQLite 回退）"""

  def __init__(self):
    super().__init__(db_suffix='_testing_graph', use_mysql_checkpoint=True)

  def _build_graph(self) -> StateGraph:
    return build_testing_graph()


# ── 模块级单例 ────────────────────────────────────────────────────────────────
_managed_graph = ManagedTestingGraph()


async def get_testing_graph():
  """获取已编译的 LangGraph 实例（懒初始化）"""
  return await _managed_graph.initialize()


async def close_testing_graph():
  """关闭图连接（应用关闭时调用）"""
  await _managed_graph.close()
