"""AI Testing SSE 流式生成 - 接入 LangGraph 工作流

SSE 事件类型：
  - testing_stage:    阶段切换 (analyze / write / review / revise / complete)
  - testing_token:    流式 token（带 stage 标签）
  - testing_review:   评审结果（结构化 JSON）
  - testing_progress: 进度更新
  - testing_done:     生成完成
  - testing_error:    错误信息

三段式架构：
  Phase 1: get_db_context() — 加载任务、更新状态
  Phase 2: 无 DB 连接 — 运行 LangGraph astream_events，产出 SSE 事件
  Phase 3: get_db_context() — 持久化结果、更新状态
"""

import json
import logging
import re
from typing import AsyncGenerator

from app.common.core.database import get_db_context
from app.common.domain.exceptions import GenerationTaskNotFoundError
from app.modules.ai_testing.graph import get_testing_graph
from app.modules.ai_testing.service import TestingService
from app.common.utils.sse_helper import format_sse_event

logger = logging.getLogger(__name__)

# 节点名 → 阶段标签（必须与 graph.py 中注册的节点名一致）
NODE_TO_STAGE = {
  "analyze": "analyze",
  "write": "write",
  "review": "review",
  "revise": "revise",
}

# 阶段顺序（用于进度百分比）
STAGE_ORDER = ["analyze", "write", "review", "revise"]

# 取消信号集：task_id 在此 set 中表示已请求取消
_cancelled_tasks: set[str] = set()


def _sse(event_type: str, data: dict) -> str:
  """快捷 SSE 格式化"""
  return format_sse_event(event_type, data)


def _parse_model_field(model_str: str) -> tuple[str, str]:
  """从任务 model 字段解析 (provider, model_name)"""
  if not model_str:
    return "deepseek", ""
  if ":" in model_str:
    parts = model_str.split(":", 1)
    return parts[0], parts[1]
  return "deepseek", model_str


def _count_generated_cases(content: str) -> int:
  """从最终内容中统计生成的用例数"""
  if not content:
    return 0
  case_blocks = re.split(r'\n-{3,}\n', content)
  count = 0
  for block in case_blocks:
    if '**标题**' in block or '**用例 ID**' in block:
      count += 1
  if count == 0:
    count = content.count("TC-")
  return count


# ── Phase 2 核心：LangGraph 流水线（产出 (event_type, data) 流） ──────


async def _run_pipeline_events(
    task_id: str, input_state: dict,
) -> AsyncGenerator[tuple[str, dict], None]:
  """运行 LangGraph 流水线，产出 (event_type, data) 事件元组

  事件类型：testing_stage / testing_token / testing_review / testing_progress / testing_error
  执行完后产出特殊的 _done / _error 事件携带最终结果。
  """
  graph = await get_testing_graph()
  config = {"configurable": {"thread_id": task_id}}

  current_stage = ""
  stage_contents: dict[str, str] = {}
  review_result: dict = {}

  # 预填充已有的阶段（用于修订时跳过 analyze/write）
  if input_state.get("existing_analysis"):
    stage_contents["analyze"] = input_state["existing_analysis"]
  if input_state.get("existing_draft"):
    stage_contents["write"] = input_state["existing_draft"]

  # 计算起始阶段
  if stage_contents.get("analyze") and stage_contents.get("write"):
    start_idx = 2  # 从 review 开始
  elif stage_contents.get("analyze"):
    start_idx = 1  # 从 write 开始
  else:
    start_idx = 0  # 从 analyze 开始

  yield ("testing_progress", {"current": start_idx, "total": 4, "message": "开始生成..."})

  try:
    async for event in graph.astream_events(input_state, config=config, version="v2"):
      kind = event.get("event", "")
      metadata = event.get("metadata", {})
      node_name = metadata.get("langgraph_node", "")

      # 取消检查
      if task_id in _cancelled_tasks:
        _cancelled_tasks.discard(task_id)
        yield ("testing_error", {"code": "CANCELLED", "message": "用户已停止生成"})
        yield ("_done", {"error": True, "cancelled": True, "err_msg": "用户已停止生成",
                         "stage_contents": {}, "review_result": {},
                         "final_content": "", "generated_count": 0})
        return

      # ── 节点级 chain 开始：阶段切换 ──────────────────────────────
      if kind == "on_chain_start" and node_name in NODE_TO_STAGE:
        stage = NODE_TO_STAGE[node_name]
        if stage in stage_contents and stage_contents[stage]:
          # 已有预填充内容，跳过此阶段的流式事件
          current_stage = stage
          continue
        if stage != current_stage:
          current_stage = stage
          stage_idx = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else 0
          yield ("testing_stage", {"stage": stage, "current": stage_idx + 1})
          stage_contents[stage] = ""

      # ── LLM 流式 token ──────────────────────────────────────────
      elif kind == "on_chat_model_stream":
        if node_name not in NODE_TO_STAGE:
          continue
        chunk = event.get("data", {}).get("chunk")
        if chunk and hasattr(chunk, "content") and chunk.content:
          token = chunk.content
          stage = NODE_TO_STAGE[node_name]
          if stage in stage_contents:
            stage_contents[stage] += token
          yield ("testing_token", {"stage": stage, "content": token})

      # ── 节点完成：捕获最终输出 ───────────────────────────────────
      elif kind == "on_chain_end" and node_name in NODE_TO_STAGE:
        output = event.get("data", {}).get("output")
        stage = NODE_TO_STAGE[node_name]

        if isinstance(output, dict):
          if "analysis_result" in output:
            stage_contents["analyze"] = output["analysis_result"]
          elif "test_cases_draft" in output:
            stage_contents["write"] = output["test_cases_draft"]
          elif "review_result" in output:
            review_result = output.get("review_result", {})
            stage_contents["review"] = json.dumps(review_result, ensure_ascii=False)
            yield ("testing_review", review_result)
          elif "final_test_cases" in output:
            final_content = output["final_test_cases"]
            stage_contents["revise"] = final_content

        stage_idx = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else 0
        yield ("testing_progress", {
          "current": stage_idx + 1, "total": 4, "message": f"阶段 {stage} 完成",
        })

  except Exception as e:
    err_msg = str(e)[:500]
    logger.error(f"[_run_pipeline_events] LangGraph 执行错误: {e}", exc_info=True)
    yield ("testing_error", {"code": "EXECUTION_ERROR", "message": "AI 生成过程中发生错误，请重试"})
    yield ("_done", {"error": True, "err_msg": err_msg,
                     "stage_contents": stage_contents, "review_result": review_result})
    return

  # 正常完成：确定最终输出
  final_content = stage_contents.get("revise") or stage_contents.get("write", "")
  generated_count = _count_generated_cases(final_content)
  yield ("_done", {
    "error": False,
    "stage_contents": stage_contents,
    "review_result": review_result,
    "final_content": final_content,
    "generated_count": generated_count,
  })


# ── Phase 3：持久化 ────────────────────────────────────────────────


async def _persist_and_finish(task_id: str, done_data: dict) -> list[str]:
  """持久化结果到数据库，返回 SSE 事件字符串列表"""
  events: list[str] = []
  try:
    async with get_db_context() as db:
      svc = TestingService(db)

      if done_data.get("error"):
        await svc.update_generation_task(
          task_id, status="failed",
          error_message=done_data.get("err_msg", ""),
        )
        return events

      if done_data.get("cancelled"):
        await svc.update_generation_task(task_id, status="cancelled")
        return events

      stage_contents = done_data.get("stage_contents", {})
      for stage, content in stage_contents.items():
        if content:
          await svc.save_generation_result(task_id, stage, content)

      final_content = done_data.get("final_content", "")
      if final_content:
        await svc.save_generation_result(task_id, "final", final_content)

      generated_count = done_data.get("generated_count", 0)
      review_result = done_data.get("review_result", {})
      await svc.update_generation_task(
        task_id, status="completed", generated_count=generated_count,
      )

    events.append(_sse("testing_save_progress", {
      "stage": "persist", "generated_count": generated_count,
    }))
    events.append(_sse("testing_done", {
      "task_id": task_id,
      "generated_count": generated_count,
      "review_passed": review_result.get("review_passed", False),
      "overall_score": review_result.get("overall_score", 0),
    }))
  except Exception as e:
    logger.error(f"[_persist_and_finish] 持久化失败: {e}", exc_info=True)
    events.append(_sse("testing_error", {
      "code": "SAVE_ERROR", "message": "保存生成结果失败，请重试",
    }))
  return events


# ── 公共入口：加载任务（Phase 1） ──────────────────────────────────────


async def _load_task(task_id: str) -> dict | None:
  """Phase 1：加载任务，返回 input_state 或 None（失败时）"""
  try:
    async with get_db_context() as db:
      service = TestingService(db)
      try:
        task = await service.get_generation_task(task_id)
      except GenerationTaskNotFoundError:
        logger.error("[_load_task] 任务 %s 不存在（可能创建后未提交或被删除）", task_id)
        return None

      await service.update_generation_task(task_id, status="running")
      provider, model_name = _parse_model_field(task.get("model", ""))
      project_context = ""
      project_id = task.get("project_id")
      if project_id:
        try:
          project = await service.get_project(project_id)
          if project:
            project_context = f"项目：{project.get('name', '')}\n{project.get('description', '')}"
        except Exception as e:
          logger.debug("加载项目上下文失败: %s", e)

      model_api_key = ""
      try:
        config_api_key = await service.get_config_value(f"api_key_{provider}")
        if config_api_key:
          model_api_key = config_api_key
      except Exception as e:
        logger.debug("加载自定义 API Key 失败: %s", e)

      return {
        "requirement_text": task.get("input_text", ""),
        "project_context": project_context,
        "model_provider": provider,
        "model_name": model_name,
        "model_api_key": model_api_key,
      }
  except Exception as e:
    logger.error(f"[_load_task] 加载任务 {task_id} 失败: {e}", exc_info=True)
    return None


# ── SSE 流式生成 ──────────────────────────────────────────────────────


async def stream_generation_task(
    task_id: str,
    custom_suggestions: list[str] | None = None,
) -> AsyncGenerator[str, None]:
  """SSE 流式推送 LangGraph 生成进度（三段式）"""

  # Phase 1: 加载任务
  input_state = await _load_task(task_id)
  if input_state is None:
    yield _sse("testing_error", {"code": "LOAD_ERROR", "message": f"任务 {task_id} 不存在或加载失败"})
    return

  if custom_suggestions:
    input_state["custom_suggestions"] = custom_suggestions

  # Phase 2: 流式执行 LangGraph，实时推送 SSE
  done_data = None
  async for event_type, data in _run_pipeline_events(task_id, input_state):
    if event_type == "_done":
      done_data = data
    else:
      yield _sse(event_type, data)

  # Phase 3: 持久化
  if done_data:
    events = await _persist_and_finish(task_id, done_data)
    for ev in events:
      yield ev


# ── 后台非流式执行（Complete 模式用） ──────────────────────────────────


async def execute_generation_task_background(task_id: str) -> None:
  """后台执行生成任务（无 SSE），供 complete 模式轮询使用"""
  logger.info("[execute_background] 开始执行任务 %s", task_id)

  try:
    input_state = await _load_task(task_id)
    if input_state is None:
      logger.error("[execute_background] 任务 %s 加载失败", task_id)
      return

    # Phase 2: 静默执行
    done_data = None
    async for event_type, data in _run_pipeline_events(task_id, input_state):
      if event_type == "_done":
        done_data = data
      # 静默模式下忽略其他事件

    # Phase 3: 持久化
    if done_data:
      await _persist_and_finish(task_id, done_data)

    logger.info("[execute_background] 任务 %s 完成", task_id)
  except Exception as e:
    logger.error(f"[execute_background] 任务 {task_id} 执行异常: {e}", exc_info=True)
    # 尝试将任务标记为失败
    try:
      async with get_db_context() as db:
        svc = TestingService(db)
        await svc.update_generation_task(task_id, status="failed", error_message=str(e)[:500])
    except Exception:
      pass
