"""AI Testing SSE 流式生成 - 接入 LangGraph 工作流

SSE 事件类型：
  - testing_stage:    阶段切换 (analyze / write / review / revise / complete)
  - testing_token:    流式 token（带 stage 标签）
  - testing_review:   评审结果（结构化 JSON）
  - testing_progress: 进度更新
  - testing_done:     生成完成
  - testing_error:    错误信息
"""

import json
import logging
from typing import AsyncGenerator

from app.shared.core.database import get_db
from app.modules.ai_testing.graph import get_testing_graph
from app.modules.ai_testing.service import TestingService
from app.shared.utils.sse_helper import format_sse_event

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


def _sse(event_type: str, data: dict) -> str:
  """快捷 SSE 格式化"""
  return format_sse_event(event_type, data)


def _parse_model_field(model_str: str) -> tuple[str, str]:
  """从任务 model 字段解析 (provider, model_name)"""
  if not model_str:
    return "deepseek", ""
  # 支持 "provider:model" 或直接 "model"
  if ":" in model_str:
    parts = model_str.split(":", 1)
    return parts[0], parts[1]
  return "deepseek", model_str


async def stream_generation_task(
    task_id: str,
    custom_suggestions: list[str] | None = None,
) -> AsyncGenerator[str, None]:
  """SSE 流式推送 LangGraph 生成进度

  流程：
    1. 从 DB 加载任务
    2. 启动 LangGraph astream_events(v2)
    3. 按节点过滤 token，实时推送
    4. 完成后更新任务状态
  """
  db = None
  try:
    # ── 1. 加载任务 ──────────────────────────────────────────────────────────
    db = await get_db()
    service = TestingService(db)

    try:
      task = await service.get_generation_task(task_id)
    except Exception as e:
      yield _sse("testing_error", {"code": "NOT_FOUND", "message": str(e)})
      return

    if not task:
      yield _sse("testing_error", {"code": "NOT_FOUND", "message": f"任务 {task_id} 不存在"})
      return

    # 更新状态为 running
    await service.update_generation_task(task_id, status="running")

    # 解析模型配置
    provider, model_name = _parse_model_field(task.get("model", ""))

    # 获取项目背景（可选）
    project_context = ""
    project_id = task.get("project_id")
    if project_id:
      try:
        project = await service.get_project(project_id)
        if project:
          project_context = f"项目：{project.get('name', '')}\n{project.get('description', '')}"
      except Exception:
        pass

    # 加载模块级自定义 API Key（key 格式: api_key_{provider}）
    model_api_key = ""
    try:
      config_api_key = await service.get_config_value(f"api_key_{provider}")
      if config_api_key:
        model_api_key = config_api_key
    except Exception:
      pass

    # 流式执行期间暂不占用数据库连接，持久化时重新获取
    await db.close()
    db = None

    # ── 2. 构建输入 state ────────────────────────────────────────────────────
    input_state = {
      "requirement_text": task.get("input_text", ""),
      "project_context": project_context,
      "model_provider": provider,
      "model_name": model_name,
      "model_api_key": model_api_key,
    }

    # 注入用户选中的改进建议（按需重新生成时使用）
    if custom_suggestions:
      input_state["custom_suggestions"] = custom_suggestions

    # ── 3. 运行 LangGraph 流 ─────────────────────────────────────────────────
    graph = await get_testing_graph()
    config = {"configurable": {"thread_id": task_id}}

    # 状态追踪
    current_stage = ""
    stage_contents: dict[str, str] = {}   # stage → 完整内容
    review_result: dict = {}
    final_content = ""
    error_occurred = False

    yield _sse("testing_progress", {
      "current": 0, "total": 4, "message": "开始生成...",
    })

    try:
      async for event in graph.astream_events(input_state, config=config, version="v2"):
        kind = event.get("event", "")
        metadata = event.get("metadata", {})
        node_name = metadata.get("langgraph_node", "")

        # ── 节点级 chain 开始：阶段切换 ──────────────────────────────────────
        if kind == "on_chain_start" and node_name in NODE_TO_STAGE:
          stage = NODE_TO_STAGE[node_name]
          if stage != current_stage:
            current_stage = stage
            stage_idx = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else 0
            yield _sse("testing_stage", {"stage": stage, "current": stage_idx + 1})
            stage_contents[stage] = ""

        # ── LLM 流式 token ──────────────────────────────────────────────────
        elif kind == "on_chat_model_stream":
          if node_name not in NODE_TO_STAGE:
            continue
          chunk = event.get("data", {}).get("chunk")
          if chunk and hasattr(chunk, "content") and chunk.content:
            token = chunk.content
            stage = NODE_TO_STAGE[node_name]
            # 累积内容
            if stage in stage_contents:
              stage_contents[stage] += token
            yield _sse("testing_token", {"stage": stage, "content": token})

        # ── 节点完成：捕获最终输出 ───────────────────────────────────────────
        elif kind == "on_chain_end" and node_name in NODE_TO_STAGE:
          output = event.get("data", {}).get("output")
          stage = NODE_TO_STAGE[node_name]

          # 从节点输出字典中提取内容
          if isinstance(output, dict):
            if "analysis_result" in output:
              stage_contents["analyze"] = output["analysis_result"]
            elif "test_cases_draft" in output:
              stage_contents["write"] = output["test_cases_draft"]
            elif "review_result" in output:
              review_result = output.get("review_result", {})
              stage_contents["review"] = json.dumps(review_result, ensure_ascii=False)
              yield _sse("testing_review", review_result)
            elif "final_test_cases" in output:
              final_content = output["final_test_cases"]
              stage_contents["revise"] = final_content

          # 进度更新
          stage_idx = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else 0
          yield _sse("testing_progress", {
            "current": stage_idx + 1,
            "total": 4,
            "message": f"阶段 {stage} 完成",
          })

    except Exception as e:
      error_occurred = True
      err_msg = str(e)[:500]
      logger.error(f"[stream_generation_task] LangGraph 执行错误: {e}", exc_info=True)
      yield _sse("testing_error", {"code": "EXECUTION_ERROR", "message": err_msg})

    # ── 出错时持久化失败状态 ──────────────────────────────────────────────
    if error_occurred:
      try:
        db_err = await get_db()
        svc_err = TestingService(db_err)
        await svc_err.update_generation_task(task_id, status="failed", error_message=err_msg)
        await db_err.close()
      except Exception as persist_err:
        logger.error(f"[stream_generation_task] 持久化失败状态出错: {persist_err}")

    # ── 4. 确定最终输出 ──────────────────────────────────────────────────────
    if not error_occurred:
      # 评审通过：最终用例 = 草稿；评审未通过：最终用例 = 修订结果
      if not final_content:
        final_content = stage_contents.get("write", "")

      # ── 5. 持久化 ──────────────────────────────────────────────────────────
      try:
        db2 = await get_db()
        svc2 = TestingService(db2)

        # 保存各阶段结果
        for stage, content in stage_contents.items():
          if content:
            await svc2.save_generation_result(task_id, stage, content)

        # 保存 final 阶段
        if final_content:
          await svc2.save_generation_result(task_id, "final", final_content)

        # 统计生成的用例数：按 --- 分隔符分割，过滤含 **标题** 或 **用例 ID** 的段落
        generated_count = 0
        import re
        case_blocks = re.split(r'\n-{3,}\n', final_content)
        for block in case_blocks:
          if '**标题**' in block or '**用例 ID**' in block:
            generated_count += 1
        if generated_count == 0:
          generated_count = final_content.count("TC-")

        await svc2.update_generation_task(
          task_id,
          status="completed",
          generated_count=generated_count,
        )
        await db2.close()
      except Exception as e:
        logger.error(f"[stream_generation_task] 持久化失败: {e}", exc_info=True)
        yield _sse("testing_error", {"code": "SAVE_ERROR", "message": str(e)})

      # 发送保存完成事件
      yield _sse("testing_save_progress", {
        "stage": "persist",
        "generated_count": generated_count,
      })

      yield _sse("testing_done", {
        "task_id": task_id,
        "generated_count": generated_count,
        "review_passed": review_result.get("review_passed", False),
        "overall_score": review_result.get("overall_score", 0),
      })

  except Exception as e:
    logger.error(f"[stream_generation_task] 顶层错误: {e}", exc_info=True)
    yield _sse("testing_error", {"code": "UNKNOWN_ERROR", "message": str(e)[:500]})
    # 顶层异常也尝试更新任务状态为 failed
    try:
      if db:
        svc_top = TestingService(db)
        await svc_top.update_generation_task(
          task_id, status="failed", error_message=str(e)[:500],
        )
    except Exception:
      pass
  finally:
    if db:
      try:
        await db.close()
      except Exception:
        pass
