"""AI Testing 模块 API 端点（36+ 个端点）"""

import os
import stat
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote
import json
import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Query, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, Response, JSONResponse

from app.common.api.schemas.common import ApiResponse
from app.dependencies import get_db_dep
from app.common.core.database import MySQLConnection

from app.common.utils.file_validator import (
  validate_file_magic,
  has_path_traversal,
  safe_filename,
  sanitize_filename_component,
)
from langchain_openai import ChatOpenAI

from app.modules.ai_testing.schemas import (
  ProjectCreate,
  ProjectUpdate,
  MemberCreate,
  MemberUpdate,
  TestCaseCreate,
  TestCaseUpdate,
  BatchDeleteRequest,
  GenerateRequest,
  SaveCasesRequest,
  ConfigUpdateRequest,
  VersionCreate,
  VersionUpdate,
  CommentCreate,
  CommentUpdate,
  ConfigDefaultsResponse,
  TaskStatusUpdate,
  BatchUpdateCasesRequest,
  ReviewCreate,
  ReviewUpdate,
  ReviewCaseUpdate,
  TestConnectionRequest,
  AITesterSessionCreate,
  AITesterSessionUpdate,
  AITesterMessageSend,
  LinkProjectRequest,
)
from app.modules.ai_testing import prompts
from app.common.core.llm_factory import LLMFactory, PROVIDER_DEFAULT_URLS
from app.modules.ai_testing.service import TestingService
from app.modules.ai_testing import schemas

router = APIRouter()

# ─── 项目 CRUD ─────────────────────────────────────

@router.get("/projects")
async def list_projects(
  status: str | None = Query(default=None),
  keyword: str | None = Query(default=None),
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=20, ge=1, le=1000),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """获取项目列表（分页+筛选）"""
  service = TestingService(db)
  data = await service.list_projects(
    status=status, keyword=keyword, page=page, page_size=page_size
  )
  return ApiResponse(data=data)

@router.get("/projects/{project_id}")
async def get_project(project_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[dict[str, Any]]:
  """获取项目详情"""
  service = TestingService(db)
  data = await service.get_project(project_id)
  return ApiResponse(data=data)

@router.post("/projects")
async def create_project(body: ProjectCreate, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[dict[str, Any]]:
  """创建项目"""
  service = TestingService(db)
  data = await service.create_project(
    name=body.name,
    description=body.description,
    status=body.status,
  )
  return ApiResponse(data=data)

@router.put("/projects/{project_id}")
async def update_project(
  project_id: str, body: ProjectUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """更新项目"""
  service = TestingService(db)
  update_data = body.model_dump(exclude_none=True)
  data = await service.update_project(project_id, **update_data)
  return ApiResponse(data=data)

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """删除项目"""
  service = TestingService(db)
  result = await service.delete_project(project_id)
  return ApiResponse(data=result)

# ─── 项目成员 ────────────────────────────────────────

@router.get("/members")
async def list_all_members(
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取所有成员（独立模块，无项目关联）"""
  service = TestingService(db)
  data = await service.list_all_members()
  return ApiResponse(data=data)

@router.post("/members")
async def add_member_standalone(
  body: MemberCreate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """添加成员（独立模块，无项目关联）"""
  service = TestingService(db)
  data = await service.add_member_standalone(body.name, body.role)
  return ApiResponse(data=data)

@router.get("/projects/{project_id}/members")
async def list_members(project_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[list[dict[str, Any]]]:
  """获取项目成员列表"""
  service = TestingService(db)
  data = await service.list_members(project_id)
  return ApiResponse(data=data)

@router.post("/projects/{project_id}/members")
async def add_member(
  project_id: str, body: MemberCreate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """添加项目成员"""
  service = TestingService(db)
  data = await service.add_member(project_id, body.name, body.role)
  return ApiResponse(data=data)

@router.delete("/members/{member_id}")
async def remove_member(member_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """移除项目成员"""
  service = TestingService(db)
  result = await service.remove_member(member_id)
  return ApiResponse(data=result)

@router.put("/members/{member_id}")
async def update_member_role(
  member_id: str, body: MemberUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """更新成员角色"""
  service = TestingService(db)
  result = await service.update_member_role(member_id, body.role)
  return ApiResponse(data=result)

# ─── 测试用例 CRUD ──────────────────────────────────

@router.get("/cases")
async def list_cases(
  project_id: str | None = Query(default=None),
  priority: str | None = Query(default=None),
  case_type: str | None = Query(default=None),
  status: str | None = Query(default=None),
  version: str | None = Query(default=None),
  keyword: str | None = Query(default=None),
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=20, ge=1, le=1000),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """获取用例列表（多条件筛选+分页）"""
  service = TestingService(db)
  data = await service.list_cases(
    project_id=project_id, priority=priority, case_type=case_type,
    status=status, version=version, keyword=keyword,
    page=page, page_size=page_size,
  )
  return ApiResponse(data=data)

# 固定路径路由必须在参数化路由之前注册，避免 "stats"/"export" 被捕获为 case_id
@router.get("/cases/export")
async def export_cases(
  project_id: str | None = Query(default=None),
  ids: str | None = Query(default=None, description="逗号分隔的用例 ID"),
  db: MySQLConnection = Depends(get_db_dep),
) -> Response:
  """导出用例为 Excel 文件"""
  service = TestingService(db)
  from app.modules.ai_testing.excel_handler import export_cases_to_xlsx

  # 获取项目名称
  project_name = ""
  if project_id:
    try:
      proj = await service.get_project(project_id)
      project_name = proj.get("name", "")
    except Exception:
      pass

  # 获取用例数据
  result = await service.list_cases(
    project_id=project_id, page=1, page_size=9999
  )
  cases = result.get("items", [])

  # 如果指定了 ID 则过滤
  if ids:
    id_set = set(ids.split(","))
    cases = [c for c in cases if c.get("id") in id_set]

  file_bytes = export_cases_to_xlsx(cases, project_name=project_name)
  ts = datetime.now().strftime("%Y%m%d_%H%M%S")
  filename = f"test_cases_{ts}.xlsx"

  return Response(
    content=file_bytes,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition": f'attachment; filename="{filename}"'},
  )

@router.get("/cases/stats")
async def get_case_stats(
  project_id: str | None = Query(default=None),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """获取用例统计（按优先级/类型/状态分组）"""
  service = TestingService(db)
  data = await service.get_case_stats(project_id=project_id)
  return ApiResponse(data=data)

@router.get("/cases/{case_id}")
async def get_case(case_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[dict[str, Any]]:
  """获取用例详情"""
  service = TestingService(db)
  data = await service.get_case(case_id)
  return ApiResponse(data=data)

@router.post("/cases")
async def create_case(body: TestCaseCreate, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[dict[str, Any]]:
  """创建测试用例"""
  service = TestingService(db)
  fields = body.model_dump()
  data = await service.create_case(**fields)
  return ApiResponse(data=data)

@router.put("/cases/{case_id}")
async def update_case(
  case_id: str, body: TestCaseUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """更新测试用例"""
  service = TestingService(db)
  update_data = body.model_dump(exclude_none=True)
  data = await service.update_case(case_id, **update_data)
  return ApiResponse(data=data)

@router.delete("/cases/{case_id}")
async def delete_case(case_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """删除测试用例"""
  service = TestingService(db)
  result = await service.delete_case(case_id)
  return ApiResponse(data=result)

@router.post("/cases/batch-delete")
async def batch_delete_cases(body: BatchDeleteRequest, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[int]:
  """批量删除测试用例"""
  service = TestingService(db)
  count = await service.batch_delete_cases(body.ids)
  return ApiResponse(data=count)

@router.post("/cases/import")
async def import_cases(
  file: UploadFile = File(...),
  project_id: str | None = Query(default=None),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """从 Excel 文件导入测试用例"""
  if not file.filename:
    raise HTTPException(status_code=400, detail="文件名不能为空")
  ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
  if ext not in {"xlsx", "xls"}:
    raise HTTPException(status_code=400, detail="仅支持 .xlsx/.xls 文件")
  content = await file.read()
  if len(content) > 20 * 1024 * 1024:
    raise HTTPException(status_code=413, detail="文件过大（超过 20MB）")
  service = TestingService(db)
  result = await service.import_cases_from_xlsx(content, project_id=project_id)
  return ApiResponse(data=result)

# ─── AI 生成 ────────────────────────────────────────

@router.post("/generate")
async def create_generation_task(
  body: GenerateRequest,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """创建 AI 用例生成任务"""
  service = TestingService(db)
  fields = body.model_dump()
  data = await service.create_generation_task(**fields)
  return ApiResponse(data=data)

@router.get("/generate/tasks")
async def list_generation_tasks(
  project_id: str | None = Query(default=None),
  status: str | None = Query(default=None),
  keyword: str | None = Query(default=None),
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=20, ge=1, le=1000),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """获取生成任务列表（分页+筛选）"""
  service = TestingService(db)
  data = await service.list_generation_tasks(
    project_id=project_id, status=status, keyword=keyword,
    page=page, page_size=page_size,
  )
  return ApiResponse(data=data)

@router.get("/generate/tasks/{task_id}/generated-cases")
async def get_task_generated_cases(
  task_id: str,
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=20, ge=1, le=1000),
  status: str | None = Query(default=None),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """获取任务生成的候选用例列表（分页+状态筛选）"""
  service = TestingService(db)
  data = await service.get_task_generated_cases(
    task_id, page=page, page_size=page_size, status=status,
  )
  return ApiResponse(data=data)

@router.post("/generate/tasks/{task_id}/batch-update-cases")
async def batch_update_task_cases(
  task_id: str, body: BatchUpdateCasesRequest,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """批量更新候选用例状态（adopted/discarded）"""
  service = TestingService(db)
  updated = await service.batch_update_task_cases(body.case_ids, body.status)
  return ApiResponse(data={"updated": updated})

@router.get("/generate/stats")
async def get_generation_stats(db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[dict[str, Any]]:
  """获取生成统计（总任务数/已完成/总用例数）"""
  service = TestingService(db)
  data = await service.get_generation_stats()
  return ApiResponse(data=data)

@router.get("/generate/{task_id}")
async def get_generation_task(task_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[dict[str, Any]]:
  """获取生成任务状态"""
  service = TestingService(db)
  data = await service.get_generation_task(task_id)
  return ApiResponse(data=data)

@router.post("/generate/{task_id}/cancel")
async def cancel_generation_task(task_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """取消生成任务"""
  from app.modules.ai_testing.sse_stream import _cancelled_tasks
  _cancelled_tasks.add(task_id)  # 设置取消信号，LangGraph 流中检测后停止
  service = TestingService(db)
  result = await service.update_generation_task(task_id, status="cancelled")
  return ApiResponse(data=result)

@router.post("/generate/{task_id}/revise")
async def revise_generation_task(
  task_id: str,
  body: schemas.ReviseRequest,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """修订生成：复用已有分析/草稿阶段结果，仅重新执行评审+修订"""
  service = TestingService(db)

  # 1. 检查任务是否存在且已完成
  task = await service.get_generation_task(task_id)
  if not task:
    return ApiResponse(code=404, message=f"任务 {task_id} 不存在")
  if task.get("status") not in ("completed",):
    return ApiResponse(code=400, message=f"任务状态为 {task.get('status')}，不可修订", data=task)

  # 2. 加载已有阶段结果
  results = await service.list_generation_results(task_id)
  existing_analysis = ""
  existing_draft = ""
  for r in results:
    stage = r.get("stage", "")
    content = r.get("content", "") or ""
    if stage == "analyze":
      existing_analysis = content
    elif stage in ("write", "draft"):
      existing_draft = content

  if not existing_draft:
    return ApiResponse(code=400, message="无已有用例草稿可修订")

  # 3. 获取任务原始输入，补充 existing_analysis/existing_draft
  from app.modules.ai_testing.sse_stream import _parse_model_field, _run_pipeline_events
  provider, model_name = _parse_model_field(task.get("model", ""))
  project_id = task.get("project_id")
  if project_id:
    try:
      project = await service.get_project(project_id)
      if project:
        project_context = f"项目：{project.get('name', '')}\n{project.get('description', '')}"
    except Exception:
      pass

  model_api_key = ""
  try:
    config_api_key = await service.get_config_value(f"api_key_{provider}")
    if config_api_key:
      model_api_key = config_api_key
  except Exception:
    pass

  input_state = {
    "requirement_text": task.get("input_text", ""),
    "project_context": project_context,
    "model_provider": provider,
    "model_name": model_name,
    "model_api_key": model_api_key,
    "existing_analysis": existing_analysis,
    "existing_draft": existing_draft,
    "custom_suggestions": body.custom_suggestions,
  }

  # 4. 后台静默执行流水线（仅 review+revise）
  from app.modules.ai_testing.sse_stream import _persist_and_finish
  done_data = None
  async for event_type, data in _run_pipeline_events(task_id, input_state):
    if event_type == "_done":
      done_data = data

  # 5. 持久化结果
  if done_data:
    await _persist_and_finish(task_id, done_data)

  return ApiResponse(data={
    "task_id": task_id,
    "status": "completed",
    "generated_count": done_data.get("generated_count", 0) if done_data else 0,
  })


@router.post("/generate/{task_id}/execute")
async def execute_generation_task(
  task_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """非流式执行生成任务（用于 complete 模式），后台运行，立即返回"""
  from app.modules.ai_testing.sse_stream import execute_generation_task_background
  asyncio.create_task(execute_generation_task_background(task_id))
  return ApiResponse(data={"task_id": task_id, "status": "started"})

@router.get("/generate/{task_id}/results")
async def get_generation_results(
  task_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取生成任务的所有阶段结果"""
  service = TestingService(db)
  data = await service.list_generation_results(task_id)
  return ApiResponse(data=data)

@router.get("/generate/{task_id}/stream")
async def stream_generation(
    task_id: str,
    custom_suggestions: str | None = Query(default=None, description="JSON 编码的用户选中改进建议列表"),
) -> StreamingResponse:

  suggestions = []
  if custom_suggestions:
    try:
      suggestions = json.loads(custom_suggestions)
    except Exception:
      pass

  return StreamingResponse(
    stream_generation_task(task_id, custom_suggestions=suggestions),
    media_type="text/event-stream",
    headers={
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "X-Accel-Buffering": "no",
    },
  )

@router.get("/generate/{task_id}/export")
async def export_generated_cases(task_id: str, db: MySQLConnection = Depends(get_db_dep)) -> Response:
  """导出 AI 生成用例为 Excel"""
  service = TestingService(db)
  from app.modules.ai_testing.excel_handler import (
    export_cases_to_xlsx,
    parse_markdown_cases,
  )

  # 获取 final 阶段结果
  results = await service.list_generation_results(task_id)
  final_content = ""
  for r in results:
    if r.get("stage") == "final":
      final_content = r.get("content", "") or ""
      break

  if not final_content:
    return Response(
      status_code=404,
      content="未找到生成结果",
      media_type="text/plain",
    )

  cases = parse_markdown_cases(final_content)
  file_bytes = export_cases_to_xlsx(cases)
  ts = datetime.now().strftime("%Y%m%d_%H%M%S")
  filename = f"ai_generated_cases_{ts}.xlsx"

  return Response(
    content=file_bytes,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition": f'attachment; filename="{filename}"'},
  )

@router.post("/generate/tasks/{task_id}/save-cases")
async def save_task_cases(
  task_id: str, body: SaveCasesRequest | None = None,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """将任务中已采用的候选用例保存到用例库"""
  service = TestingService(db)
  project_id = body.project_id if body else None
  saved_count = await service.save_adopted_cases_to_library(task_id, project_id)
  return ApiResponse(data={"saved_count": saved_count})

@router.delete("/generate/tasks/{task_id}")
async def delete_generation_task(task_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """删除生成任务（含阶段结果）"""
  service = TestingService(db)
  result = await service.delete_generation_task(task_id)
  return ApiResponse(data=result)

@router.put("/generate/tasks/{task_id}/status")
async def update_generation_task_status(
  task_id: str, body: TaskStatusUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """更新生成任务状态"""
  service = TestingService(db)
  result = await service.update_generation_task(task_id, status=body.status)
  return ApiResponse(data=result)

@router.post("/generate/save-cases")
async def save_generated_cases(
  body: SaveCasesRequest,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """将 AI 生成的用例保存到用例库（含字段校验）"""
  service = TestingService(db)

  VALID_CASE_TYPES = {"functional", "performance", "security", "compatibility", "ui", "api"}

  cases_data: list[dict[str, Any]] = []
  errors: list[dict[str, Any]] = []

  for i, case in enumerate(body.cases):
    title = (case.get("title") or "").strip()
    priority = (case.get("priority") or "P2").strip().upper()
    case_type = (case.get("case_type") or "functional").strip().lower()

    # 标题校验（必填）
    if not title or len(title) > 500:
      errors.append({
        "index": i, "field": "title",
        "message": "标题不能为空且不超过 500 字符",
        "title_preview": title[:50] if title else "(空)",
      })
      continue

    # 优先级校验
    if priority not in ("P0", "P1", "P2", "P3"):
      priority = "P2"

    # 用例类型校验
    if case_type not in VALID_CASE_TYPES:
      case_type = "functional"

    # 标签处理
    tags = case.get("tags") or []
    if isinstance(tags, list):
      tags = list(dict.fromkeys(t for t in tags if t))  # 去重+去空
    else:
      tags = ["ai-generated"]
    if not tags:
      tags = ["ai-generated"]

    cases_data.append({
      "title": title,
      "priority": priority,
      "case_type": case_type,
      "preconditions": (case.get("preconditions") or "").strip()[:5000],
      "steps": (case.get("steps") or "").strip()[:5000],
      "expected_results": (case.get("expected_results") or "").strip()[:5000],
      "tags": tags,
      "project_id": body.project_id,
      "source": "ai",
      "ai_task_id": body.task_id,
    })

  if not cases_data:
    return ApiResponse(data={
      "saved_count": 0, "ids": [], "failed_count": len(errors), "errors": errors,
    })

  ids = await service.batch_create_cases(cases_data, task_id=body.task_id)
  await service.update_generation_task(
    body.task_id, generated_count=len(ids)
  )
  return ApiResponse(data={
    "saved_count": len(ids), "ids": ids,
    "failed_count": len(errors), "errors": errors,
  })

# ─── 配置 ──────────────────────────────────────────

@router.get("/config")
async def list_config(
  category: str | None = Query(default=None),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取配置列表"""
  service = TestingService(db)
  data = await service.list_config(category)
  return ApiResponse(data=data)

@router.put("/config")
async def update_config(body: ConfigUpdateRequest, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """批量更新配置"""
  service = TestingService(db)
  items = [item.model_dump() for item in body.items]
  await service.update_config_batch(items)
  return ApiResponse(data=True)

@router.get("/config/defaults")
async def get_config_defaults(db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[ConfigDefaultsResponse]:
  """获取配置默认值（默认提示词模板 + 可用模型列表 + 默认 Base URL）"""
  data = ConfigDefaultsResponse(
    prompts={
      "analyze": prompts.ANALYZE_SYSTEM,
      "write": prompts.WRITE_SYSTEM,
      "review": prompts.REVIEW_SYSTEM,
      "revise": prompts.REVISE_SYSTEM,
    },
    models=LLMFactory.get_available_models(),
    base_urls=PROVIDER_DEFAULT_URLS,
  )
  return ApiResponse(data=data)


@router.post("/config/test-connection")
async def test_connection(
  body: TestConnectionRequest,
) -> ApiResponse[dict[str, Any]]:
  """测试 LLM 连接：使用指定参数创建模型实例并发送测试请求"""
  try:
    from langchain_core.messages import HumanMessage
    from app.config import get_settings
    settings = get_settings()

    # 根据 provider 创建 ChatOpenAI 实例（支持通过 base_url 自定义端点）
    if body.provider == "deepseek":
      llm = ChatOpenAI(
        model=body.model_name or "deepseek-chat",
        api_key=body.api_key or settings.deepseek_api_key,
        base_url=body.base_url or settings.deepseek_base_url,
        temperature=0.1, timeout=15, max_retries=0,
      )
    elif body.provider == "openai":
      llm = ChatOpenAI(
        model=body.model_name or "gpt-4o-mini",
        api_key=body.api_key or settings.openai_api_key,
        base_url=body.base_url or settings.openai_base_url,
        temperature=0.1, timeout=15, max_retries=0,
      )
    elif body.provider == "qwen":
      llm = ChatOpenAI(
        model=body.model_name or "qwen-plus",
        api_key=body.api_key or settings.qwen_api_key,
        base_url=body.base_url or settings.qwen_base_url,
        temperature=0.1, timeout=15, max_retries=0,
      )
    elif body.provider == "zhipu":
      llm = ChatOpenAI(
        model=body.model_name or "glm-4-flash",
        api_key=body.api_key or settings.zhipu_api_key,
        base_url=body.base_url or settings.zhipu_base_url,
        temperature=0.1, timeout=15, max_retries=0,
      )
    elif body.provider == "ollama":
      from langchain_ollama import ChatOllama
      llm = ChatOllama(
        model=body.model_name or "qwen2.5",
        base_url=body.base_url or settings.ollama_base_url or "http://localhost:11434",
        temperature=0.1, num_predict=50,
      )
    else:
      return ApiResponse(code=400, message=f"不支持的 provider: {body.provider}")

    result = llm.invoke([HumanMessage(content="回复『连接测试成功』即可，不要回复其他内容")])
    reply = result.content.strip() if result.content else ""
    return ApiResponse(data={"reply": reply, "success": True})
  except Exception as e:
    logger.warning(f"连接测试失败 [{body.provider}]: {e}")
    return ApiResponse(code=400, message=f"连接测试失败: {str(e)}")


# ─── 仪表盘统计 ─────────────────────────────────────

@router.get("/dashboard/stats")
async def get_dashboard_stats(
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """获取仪表盘统计数据"""
  service = TestingService(db)
  data = await service.get_dashboard_data()
  return ApiResponse(data=data)

# ─── 项目版本 ────────────────────────────────────────

@router.get("/versions")
async def list_all_versions(
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取所有版本（独立模块，无项目关联）"""
  service = TestingService(db)
  data = await service.list_all_versions()
  return ApiResponse(data=data)

@router.post("/versions")
async def create_version_standalone(
  body: VersionCreate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """创建版本（独立模块，无项目关联）"""
  service = TestingService(db)
  data = await service.create_version_standalone(
    name=body.name,
    description=body.description,
    status=body.status,
    pass_rate=body.pass_rate if body.pass_rate is not None else 0.0,
  )
  return ApiResponse(data=data)

@router.get("/projects/{project_id}/versions")
async def list_versions(project_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[list[dict[str, Any]]]:
  """获取项目版本列表"""
  service = TestingService(db)
  data = await service.list_versions(project_id)
  return ApiResponse(data=data)

@router.post("/projects/{project_id}/versions")
async def create_version(
  project_id: str, body: VersionCreate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """创建项目版本"""
  service = TestingService(db)
  data = await service.create_version(
    project_id=project_id,
    name=body.name,
    description=body.description,
    status=body.status,
    pass_rate=body.pass_rate if body.pass_rate is not None else 0.0,
  )
  return ApiResponse(data=data)

@router.put("/versions/{version_id}")
async def update_version(
  version_id: str, body: VersionUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """更新版本"""
  service = TestingService(db)
  update_data = body.model_dump(exclude_none=True)
  data = await service.update_version(version_id, **update_data)
  return ApiResponse(data=data)

@router.delete("/versions/{version_id}")
async def delete_version(version_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """删除版本"""
  service = TestingService(db)
  result = await service.delete_version(version_id)
  return ApiResponse(data=result)

@router.put("/versions/{version_id}/link-project")
async def link_version_to_project(
  version_id: str, body: LinkProjectRequest,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """关联已有版本到项目"""
  service = TestingService(db)
  result = await service.link_version_to_project(version_id, body.project_id)
  return ApiResponse(data=result)

@router.put("/members/{member_id}/link-project")
async def link_member_to_project(
  member_id: str, body: LinkProjectRequest,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """关联已有成员到项目"""
  service = TestingService(db)
  result = await service.link_member_to_project(member_id, body.project_id)
  return ApiResponse(data=result)

@router.delete("/members/{member_id}/unlink-project")
async def unlink_member_from_project(
  member_id: str, project_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """从项目中移除成员关联（多对多）"""
  service = TestingService(db)
  result = await service.unlink_member_from_project(member_id, project_id)
  return ApiResponse(data=result)

# ─── 用例附件 ────────────────────────────────────────

# 附件上传安全配置
ATTACHMENT_MAX_SIZE = 50 * 1024 * 1024  # 50MB
ATTACHMENT_ALLOWED_EXTS = {
  'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',
  'pdf', 'txt', 'md', 'doc', 'docx', 'xls', 'xlsx',
  'csv', 'json', 'xml', 'zip', 'tar', 'gz',
}

@router.post("/cases/{case_id}/attachments")
async def upload_attachment(
  request: Request,
  case_id: str,
  file: UploadFile = File(...),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """上传用例附件"""
  from app.config import get_settings

  # 1. 文件名检查
  if not file.filename:
    raise HTTPException(status_code=400, detail="文件名不能为空")
  raw_name = safe_filename(file.filename)
  if not raw_name or has_path_traversal(raw_name):
    raise HTTPException(status_code=400, detail="非法的文件名")

  # 2. 扩展名白名单
  ext = raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else ""
  if ext not in ATTACHMENT_ALLOWED_EXTS:
    raise HTTPException(
      status_code=400,
      detail=f"不支持的文件类型: {ext}",
    )

  # 3. 先检查 Content-Length 头部（快速拒绝超大文件）
  content_length = file.size
  if content_length is not None and content_length > ATTACHMENT_MAX_SIZE:
    raise HTTPException(
      status_code=413,
      detail=f"文件过大（{content_length / 1024 / 1024:.1f}MB）",
    )

  # 4. 读取文件内容并检查实际大小
  content = await file.read()
  if len(content) > ATTACHMENT_MAX_SIZE:
    raise HTTPException(
      status_code=413,
      detail=f"文件过大（{len(content) / 1024 / 1024:.1f}MB）",
    )

  # 5. 魔数验证
  if ext and not validate_file_magic(content, ext):
    raise HTTPException(status_code=400, detail="文件内容与扩展名不符")

  # 6. 安全保存
  settings = get_settings()
  upload_dir = Path(settings.upload_dir) / "case_attachments"
  upload_dir.mkdir(parents=True, exist_ok=True)

  safe_name = sanitize_filename_component(raw_name)
  file_path = upload_dir / f"{uuid.uuid4().hex}_{safe_name}"
  file_path.write_bytes(content)
  os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

  service = TestingService(db)
  data = await service.create_attachment(
    case_id=case_id,
    file_name=raw_name,
    file_path=str(file_path),
    file_size=len(content),
    file_type=file.content_type or "",
  )
  return ApiResponse(data=data)

@router.get("/cases/{case_id}/attachments")
async def list_attachments(case_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[list[dict[str, Any]]]:
  """获取用例附件列表"""
  service = TestingService(db)
  data = await service.list_attachments(case_id)
  return ApiResponse(data=data)

@router.delete("/attachments/{attachment_id}")
async def delete_attachment(attachment_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """删除附件（文件清理由 Service 层处理）"""
  service = TestingService(db)
  result = await service.delete_attachment(attachment_id)
  return ApiResponse(data=result)

@router.get("/attachments/{attachment_id}/download")
async def download_attachment(attachment_id: str, db: MySQLConnection = Depends(get_db_dep)) -> StreamingResponse:
  """下载附件文件（流式传输 + 路径安全校验）"""
  from app.config import get_settings

  service = TestingService(db)
  attachment = await service.repo.get_attachment(attachment_id)
  if not attachment:
    raise HTTPException(status_code=404, detail="附件不存在")

  file_path = attachment.get("file_path", "")
  if not file_path:
    raise HTTPException(status_code=404, detail="附件路径为空")

  # 路径安全校验：确保文件在 upload 目录内
  settings = get_settings()
  upload_base = Path(settings.upload_dir).resolve()
  resolved = Path(file_path).resolve()
  if not str(resolved).startswith(str(upload_base)):
    raise HTTPException(status_code=403, detail="非法的文件路径")

  if not resolved.is_file():
    raise HTTPException(status_code=404, detail="文件已丢失")

  # 真正的流式下载（分块迭代，避免全部加载到内存）
  def file_iterator(path: str, chunk_size: int = 64 * 1024):
    with open(path, "rb") as f:
      while chunk := f.read(chunk_size):
        yield chunk

  file_name = attachment.get("file_name", "download")
  return StreamingResponse(
    file_iterator(str(resolved)),
    media_type=attachment.get("file_type", "application/octet-stream"),
    headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
  )

# ─── 用例评论 ────────────────────────────────────────

@router.get("/cases/{case_id}/comments")
async def list_comments(case_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[list[dict[str, Any]]]:
  """获取用例评论列表"""
  service = TestingService(db)
  data = await service.list_comments(case_id)
  return ApiResponse(data=data)

@router.post("/cases/{case_id}/comments")
async def create_comment(
  case_id: str, body: CommentCreate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """创建用例评论"""
  service = TestingService(db)
  data = await service.create_comment(
    case_id=case_id,
    content=body.content,
    author=body.author,
  )
  return ApiResponse(data=data)

@router.put("/comments/{comment_id}")
async def update_comment(
  comment_id: str, body: CommentUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """更新评论"""
  service = TestingService(db)
  result = await service.update_comment(comment_id, body.content)
  return ApiResponse(data=result)

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[bool]:
  """删除评论"""
  service = TestingService(db)
  result = await service.delete_comment(comment_id)
  return ApiResponse(data=result)

# ─── 操作日志 ────────────────────────────────────────

@router.get("/cases/{case_id}/logs")
async def get_case_logs(
  case_id: str,
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=50, ge=1, le=200),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """获取用例操作日志"""
  service = TestingService(db)
  data = await service.list_case_logs(case_id, page=page, page_size=page_size)
  return ApiResponse(data=data)

@router.get("/projects/{project_id}/logs")
async def get_project_logs(
  project_id: str,
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=50, ge=1, le=200),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """获取项目操作日志"""
  service = TestingService(db)
  data = await service.list_project_logs(project_id, page=page, page_size=page_size)
  return ApiResponse(data=data)

# ─── 文档上传解析 ────────────────────────────────────

# 文档上传安全配置
DOC_MAX_SIZE = 20 * 1024 * 1024  # 20MB
DOC_ALLOWED_EXTS = {'pdf', 'doc', 'docx', 'txt', 'md'}

@router.post("/generate/upload-doc")
async def upload_document(
  request: Request,
  file: UploadFile = File(...),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, str]]:
  """上传文档并解析内容（PDF/Word/TXT/MD）"""
  from app.config import get_settings
  from app.common.utils.file_parser import parse_file

  # 1. 文件名检查
  if not file.filename:
    raise HTTPException(status_code=400, detail="文件名不能为空")
  raw_name = safe_filename(file.filename)
  if not raw_name or has_path_traversal(raw_name):
    raise HTTPException(status_code=400, detail="非法的文件名")

  # 2. 扩展名白名单
  ext = raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else "txt"
  if ext not in DOC_ALLOWED_EXTS:
    raise HTTPException(
      status_code=400,
      detail=f"不支持的文件类型: {ext}。允许: {', '.join(sorted(DOC_ALLOWED_EXTS))}",
    )

  # 3. 先检查 Content-Length 头部
  content_length = file.size
  if content_length is not None and content_length > DOC_MAX_SIZE:
    raise HTTPException(
      status_code=413,
      detail=f"文件过大（{content_length / 1024 / 1024:.1f}MB）",
    )

  # 4. 读取并检查实际大小
  content = await file.read()
  if len(content) > DOC_MAX_SIZE:
    raise HTTPException(
      status_code=413,
      detail=f"文件过大（{len(content) / 1024 / 1024:.1f}MB）",
    )

  # 5. 魔数验证
  if not validate_file_magic(content, ext):
    raise HTTPException(status_code=400, detail="文件内容与扩展名不符")

  # 6. 安全保存
  settings = get_settings()
  upload_dir = Path(settings.upload_dir) / "testing_docs"
  upload_dir.mkdir(parents=True, exist_ok=True)
  safe_name = sanitize_filename_component(raw_name)
  save_path = upload_dir / f"{uuid.uuid4().hex}_{safe_name}"
  save_path.write_bytes(content)
  os.chmod(save_path, stat.S_IRUSR | stat.S_IWUSR)

  # 解析文本
  text = parse_file(content, ext)

  return ApiResponse(data={
    "text": text,
    "file_name": raw_name,
    "file_type": ext,
    "file_path": str(save_path),
  })

# ─── 配置检查 ─────────────────────────────────────────

@router.get("/config/check")
async def check_config(db: MySQLConnection = Depends(get_db_dep)) -> ApiResponse[dict[str, Any]]:
  """检查 AI 生成必需配置是否完整"""
  service = TestingService(db)
  data = await service.check_config_status()
  return ApiResponse(data=data)


# ─── 用例评审 ─────────────────────────────────────────

@router.get("/reviews")
async def list_reviews(
  project_id: str | None = Query(None), status: str | None = Query(None),
  keyword: str | None = Query(None), page: int = Query(1, ge=1),
  page_size: int = Query(20, ge=1, le=1000),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  service = TestingService(db)
  items, total = await service.list_reviews(
    project_id=project_id, status=status, keyword=keyword,
    page=page, page_size=page_size,
  )
  return ApiResponse(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.get("/reviews/stats")
async def get_review_stats(
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, int]]:
  service = TestingService(db)
  stats = await service.get_review_stats()
  return ApiResponse(data=stats)


@router.post("/reviews")
async def create_review(
  body: schemas.ReviewCreate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  service = TestingService(db)
  review = await service.create_review(body.model_dump(), creator=current_user.get("username", ""))
  return ApiResponse(data=review)


@router.get("/reviews/{review_id}")
async def get_review(
  review_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  service = TestingService(db)
  review = await service.get_review(review_id)
  return ApiResponse(data=review)


@router.put("/reviews/{review_id}")
async def update_review(
  review_id: str, body: schemas.ReviewUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  service = TestingService(db)
  review = await service.update_review(review_id, body.model_dump(exclude_none=True))
  return ApiResponse(data=review)


@router.delete("/reviews/{review_id}")
async def delete_review(
  review_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  service = TestingService(db)
  result = await service.delete_review(review_id)
  return ApiResponse(data=result)


@router.get("/reviews/{review_id}/cases")
async def list_review_cases(
  review_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict]]:
  service = TestingService(db)
  cases = await service.get_review_cases(review_id)
  return ApiResponse(data=cases)


@router.put("/reviews/{review_id}/cases/{case_id}")
async def update_review_case(
  review_id: str, case_id: str, body: ReviewCaseUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """更新评审中单个用例的状态和评论"""
  service = TestingService(db)
  result = await service.update_review_case_status(review_id, case_id, body.status, body.comment)
  return ApiResponse(data=result)


@router.get("/reviews/{review_id}/reviewers")
async def list_review_reviewers(
  review_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict]]:
  """获取评审的评审人列表"""
  service = TestingService(db)
  reviewers = await service.get_review_reviewers(review_id)
  return ApiResponse(data=reviewers)


# ─── AI 评测师 ────────────────────────────────────────

@router.get("/ai-tester/sessions")
async def list_ai_tester_sessions(
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict]]:
  service = TestingService(db)
  sessions = await service.list_ai_tester_sessions()
  return ApiResponse(data=sessions)


@router.put("/ai-tester/sessions/{session_id}")
async def update_ai_tester_session(
  session_id: str, body: AITesterSessionUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """更新 AI 评测师会话（如重命名）"""
  service = TestingService(db)
  result = await service.update_ai_tester_session(session_id, name=body.name)
  return ApiResponse(data=result)


@router.post("/ai-tester/sessions/batch-delete")
async def batch_delete_ai_tester_sessions(
  body: BatchDeleteRequest,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """批量删除 AI 评测师会话"""
  service = TestingService(db)
  result = await service.batch_delete_ai_tester_sessions(body.ids)
  return ApiResponse(data=result)


@router.post("/ai-tester/sessions")
async def create_ai_tester_session(
  body: schemas.AITesterSessionCreate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  service = TestingService(db)
  session = await service.create_ai_tester_session(body.model_dump())
  return ApiResponse(data=session)


@router.delete("/ai-tester/sessions/{session_id}")
async def delete_ai_tester_session(
  session_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  service = TestingService(db)
  result = await service.delete_ai_tester_session(session_id)
  return ApiResponse(data=result)


@router.get("/ai-tester/sessions/{session_id}/messages")
async def list_ai_tester_messages(
  session_id: str,
  offset: int = Query(0, ge=0),
  limit: int = Query(50, ge=1, le=200),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict]:
  service = TestingService(db)
  result = await service.list_ai_tester_messages(session_id, offset=offset, limit=limit)
  return ApiResponse(data=result)


@router.post("/ai-tester/sessions/messages", status_code=400)
async def send_ai_tester_message_missing_session():
  """兜底路由：缺少 session_id 时返回清晰错误"""
  return JSONResponse(status_code=400, content={"code": 400, "message": "缺少会话 ID，请在路径中指定 session_id，如 /ai-tester/sessions/{session_id}/messages"})


@router.post("/ai-tester/sessions/{session_id}/messages")
async def send_ai_tester_message(
  session_id: str, body: schemas.AITesterMessageBody,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  service = TestingService(db)
  reply = await service.send_ai_tester_message(session_id, body.content, model=body.model)
  return ApiResponse(data=reply)


@router.post("/ai-tester/sessions/{session_id}/messages/stream")
async def stream_ai_tester_message(
  session_id: str, body: schemas.AITesterMessageBody,
  db: MySQLConnection = Depends(get_db_dep),
) -> StreamingResponse:
  """流式 AI 评测师消息（SSE），逐 token 返回 AI 回复"""
  service = TestingService(db)
  return StreamingResponse(
    service.stream_ai_tester_message(session_id, body.content, model=body.model),
    media_type="text/event-stream",
    headers={
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "X-Accel-Buffering": "no",
    },
  )


@router.put("/ai-tester/messages/{message_id}/rating")
async def rate_ai_tester_message(
  message_id: str, body: schemas.AITesterMessageRatingUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """给 AI 评测师消息评分（up/down/null 清除评分）"""
  service = TestingService(db)
  result = await service.update_ai_tester_message_rating(message_id, body.rating)
  return ApiResponse(data=result)


# ─── 测试报告 ─────────────────────────────────────────

@router.get("/reports/summary")
async def get_report_summary(
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  service = TestingService(db)
  summary = await service.get_report_summary()
  return ApiResponse(data=summary)


@router.get("/reports/export")
async def export_report(
  db: MySQLConnection = Depends(get_db_dep),
) -> Response:
  """导出测试报告为 Excel 文件"""
  from app.modules.ai_testing.excel_handler import export_cases_to_xlsx
  service = TestingService(db)
  summary = await service.get_report_summary()
  # 获取全部用例作为报告数据
  result = await service.list_cases(page=1, page_size=9999)
  cases = result.get("items", [])
  file_bytes = export_cases_to_xlsx(cases, project_name="全量报告")
  ts = datetime.now().strftime("%Y%m%d_%H%M%S")
  filename = f"test_report_{ts}.xlsx"
  return Response(
    content=file_bytes,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition": f'attachment; filename="{filename}"'},
  )


# ─── 定时任务 ─────────────────────────────────────────

@router.get("/scheduled-tasks")
async def list_scheduled_tasks(
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取所有定时任务（含最近执行记录）"""
  service = TestingService(db)
  tasks = await service.list_scheduled_tasks()
  return ApiResponse(data=tasks)


@router.get("/scheduled-tasks/{task_id}")
async def get_scheduled_task(
  task_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """获取单个定时任务"""
  service = TestingService(db)
  task = await service.get_scheduled_task(task_id)
  return ApiResponse(data=task)


@router.post("/scheduled-tasks")
async def create_scheduled_task(
  body: schemas.ScheduledTaskCreate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """创建定时任务"""
  service = TestingService(db)
  task = await service.create_scheduled_task(body.model_dump(), operator=current_user.get("username", ""))
  return ApiResponse(data=task)


@router.put("/scheduled-tasks/{task_id}")
async def update_scheduled_task(
  task_id: str, body: schemas.ScheduledTaskUpdate,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """更新定时任务"""
  service = TestingService(db)
  task = await service.update_scheduled_task(task_id, body.model_dump(exclude_none=True),
    operator=current_user.get("username", ""))
  return ApiResponse(data=task)


@router.delete("/scheduled-tasks/{task_id}")
async def delete_scheduled_task(
  task_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[bool]:
  """删除定时任务"""
  service = TestingService(db)
  result = await service.delete_scheduled_task(task_id, operator=current_user.get("username", ""))
  return ApiResponse(data=result)


@router.post("/scheduled-tasks/{task_id}/execute")
async def execute_scheduled_task(
  task_id: str,
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[dict[str, Any]]:
  """立即执行定时任务"""
  service = TestingService(db)
  result = await service.execute_scheduled_task(task_id, operator=current_user.get("username", ""))
  return ApiResponse(data=result)


@router.get("/scheduled-tasks/{task_id}/logs")
async def list_scheduled_task_logs(
  task_id: str, limit: int = Query(default=10, ge=1, le=50),
  db: MySQLConnection = Depends(get_db_dep),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取定时任务的执行日志"""
  service = TestingService(db)
  logs = await service.get_scheduled_task_logs(task_id, limit=limit)
  return ApiResponse(data=logs)
