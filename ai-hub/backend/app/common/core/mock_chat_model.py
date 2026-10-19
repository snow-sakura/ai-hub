"""Mock 演示模型 — 离线确定性流式 LLM

用途：
  1. 无 API Key 环境下完整走通 AI 测试助手 4 步工作流（演示 / E2E 验证 / CI）
  2. GitHub Pages 静态 Demo 的行为参照（demo 数据由同套模板生成）
  3. 序列调度（免费串行 / 付费并行）的可观测验证

特性：
  - 真流式：_stream 按小块产出，触发 astream_events 的 on_chat_model_stream
  - 确定性：输出内容随需求文本哈希种子变化（用例数 3~5），可重复断言
  - 4 步感知：按提示词特征识别 analyze / write / review / revise 阶段
"""

import hashlib
import json
import time
from typing import Any, Iterator

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult

_CASE_TITLES = [
  ("使用有效输入完成{kw}核心流程（基本流）", "functional", "P0", "等价类划分 + 场景法", "§1.1"),
  ("{kw}输入达到边界上限时的处理", "boundary", "P1", "边界值分析", "§1.2"),
  ("{kw}输入非法/空值时的容错校验", "exception", "P0", "错误推测 + 等价类划分（无效等价类）", "§1.3"),
  ("无权限用户访问{kw}功能被正确拦截", "functional", "P1", "判定表", "§1.4"),
  ("并发场景下{kw}数据一致性验证", "exception", "P2", "错误推测", "§1.5"),
]

_STAGE_MARKERS = [
  ("review", ("专业评审", "overall_score")),
  ("revise", ("根据评审反馈修订", "修订步骤")),
  ("analyze", ("结构化分析报告", "功能点分解")),
  ("write", ("编写完整、可执行的测试用例", "用例格式要求")),
]


def _extract_keyword(messages: list) -> str:
  """从需求原文提取一个简短关键词用于内容拼装"""
  for msg in reversed(messages):
    text = msg.content if isinstance(msg.content, str) else str(msg.content)
    if "需求" not in text and "评审" not in text:
      continue
    for line in text.splitlines():
      line = line.strip("#- *0123456789.、:： ").strip()
      # 取需求正文中最长的一行中文作为关键词来源
      if len(line) >= 6 and any("\u4e00" <= c <= "\u9fff" for c in line):
        head = line.replace("需求内容", "").replace("需求原文", "").strip()
        return head[:8] if head else "被测功能"
  return "被测功能"


def _seed_of(text: str) -> int:
  return int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)


class MockChatModel(BaseChatModel):
  """离线确定性演示模型（provider = mock）"""

  chunk_size: int = 14
  delay: float = 0.012

  @property
  def _llm_type(self) -> str:
    return "mock"

  # ── 内容生成 ──────────────────────────────────────────────

  def _detect_stage(self, all_text: str) -> str:
    for stage, markers in _STAGE_MARKERS:
      if any(m in all_text for m in markers):
        return stage
    return "write"

  def _compose(self, messages: list) -> str:
    joined = "\n".join(
      m.content if isinstance(m.content, str) else str(m.content) for m in messages
    )
    stage = self._detect_stage(joined)
    kw = _extract_keyword(messages)
    seed = _seed_of(joined)

    if stage == "analyze":
      return self._analysis(kw, seed)
    if stage == "review":
      return self._review(seed)
    if stage == "revise":
      return self._cases(kw, seed, revised=True)
    return self._cases(kw, seed, revised=False)

  def _analysis(self, kw: str, seed: int) -> str:
    return (
      f"### 1. 功能点分解\n"
      f"- §1.1 {kw}基本流程 — 高风险（P0）\n"
      f"- §1.2 {kw}输入边界 — 中风险（P1）\n"
      f"- §1.3 非法输入与容错 — 高风险（P0）\n"
      f"- §1.4 权限控制 — 中风险（P1）\n"
      f"- §1.5 并发与数据一致性 — 低风险（P2）\n\n"
      f"### 2. 边界条件\n数值输入覆盖最小值/最大值/超限值/空值；流程覆盖基本流 + 2 个备选流。\n\n"
      f"### 3. 异常场景\n网络中断、重复提交、越权访问、数据不一致（错误推测法）。\n\n"
      f"### 4. 前置依赖\n测试账号、干净数据集、可控网络环境。\n\n"
      f"### 5. 测试范围建议\nP0×2, P1×2, P2×1，共 {3 + seed % 3} 条用例。\n"
      f"\n（mock 演示输出 · 种子 {seed % 1000}）"
    )

  def _case_block(self, kw: str, idx: int, revised: bool) -> str:
    title_tpl, ctype, prio, method, trace = _CASE_TITLES[idx % len(_CASE_TITLES)]
    tc = f"TC-{idx + 1:03d}"
    note = "**修订说明**: [major] 预期结果补充可验证断言 → 已更新" if revised else ""
    note_line = f"\n{note}" if revised else ""
    return (
      f"\n---\n"
      f"**用例 ID**: {tc}\n"
      f"**标题**: {title_tpl.format(kw=kw)}\n"
      f"**优先级**: {prio}\n"
      f"**用例类型**: {ctype}\n"
      f"**测试设计方法**: {method}\n"
      f"**需求追溯**: {trace}\n"
      f"**前置条件**:\n1. 测试环境已部署且服务健康\n2. 已准备该场景专用测试数据\n"
      f"**测试步骤**:\n1. 以符合前置条件的账号登录系统\n"
      f"2. 进入「{kw}」功能入口并按场景提交输入\n3. 观察系统响应与数据落库结果\n"
      f"**预期结果**:\n1. 接口返回码与提示语与设计一致\n"
      f"2. 数据库中状态字段更新为预期值\n3. 无错误日志产生\n"
      f"**标签**: [{method.split(' ')[0]}, {kw}, {ctype}]{note_line}\n---\n"
    )

  def _cases(self, kw: str, seed: int, revised: bool) -> str:
    n = 3 + seed % 3
    return f"## 测试用例集（{n} 条）\n" + "".join(
      self._case_block(kw, i, revised) for i in range(n)
    )

  def _review(self, seed: int) -> str:
    score = 6 if seed % 2 == 0 else 7
    payload = {
      "overall_score": score,
      # 首轮固定 passed=False，保证演示与 E2E 覆盖 4 步全链路
      "review_passed": False,
      "dimensions": {
        "coverage": {"score": 6, "comment": "主流程覆盖完整，异常场景略少"},
        "completeness": {"score": 7, "comment": "前置/步骤/预期基本齐备"},
        "accuracy": {"score": 6, "comment": "部分预期结果可验证性不足"},
        "priority": {"score": 7, "comment": "优先级与风险基本匹配"},
        "edge_cases": {"score": 5, "comment": "边界值类型覆盖偏少"},
        "clarity": {"score": 7, "comment": "表达清晰，个别步骤可再具体"},
        "maintainability": {"score": 8, "comment": "用例相互独立"},
        "traceability": {"score": 7, "comment": "追溯编号齐全"},
        "test_design_method": {"score": 6, "comment": "方法合理但未覆盖判定表场景"},
      },
      "issues": [
        {"severity": "major", "description": "预期结果含模糊描述，需补充可验证断言", "affected_cases": ["TC-002"]},
        {"severity": "minor", "description": "边界类用例数量不足，建议补充超限值场景", "affected_cases": ["TC-003"]},
      ],
      "improvement_suggestions": [
        "将『返回正常』类预期改写为具体断言（状态码、字段值、提示文案）",
        "为数值输入补充超限值与特殊字符用例",
      ],
      "summary": "用例结构完整、可追溯性良好；主要短板在预期结果可验证性与边界覆盖，修订后可达通过线。",
    }
    return json.dumps(payload, ensure_ascii=False)

  # ── LangChain 接口 ────────────────────────────────────────

  def _stream(
    self,
    messages: list,
    stop: list[str] | None = None,
    run_manager: CallbackManagerForLLMRun | None = None,
    **kwargs: Any,
  ) -> Iterator[ChatGenerationChunk]:
    text = self._compose(messages)
    for i in range(0, len(text), self.chunk_size):
      piece = text[i:i + self.chunk_size]
      chunk = ChatGenerationChunk(message=AIMessageChunk(content=piece))
      if run_manager:
        run_manager.on_llm_new_token(piece, chunk=chunk)
      yield chunk
      if self.delay:
        time.sleep(self.delay)

  def _generate(
    self,
    messages: list,
    stop: list[str] | None = None,
    run_manager: CallbackManagerForLLMRun | None = None,
    **kwargs: Any,
  ) -> ChatResult:
    text = self._compose(messages)
    return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])
