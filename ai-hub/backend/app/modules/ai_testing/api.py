"""AI Testing 模块 API 端点（36+ 个端点）"""

import uuid
from typing import Any

from fastapi import APIRouter, Query, UploadFile, File
from fastapi.responses import StreamingResponse, Response

from app.shared.api.schemas.common import ApiResponse
from app.shared.core.database import get_db
from app.modules.ai_testing.schemas import (
  ProjectCreate,
  ProjectUpdate,
  MemberCreate,
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
)
from app.modules.ai_testing import prompts
from app.shared.core.llm_factory import LLMFactory
from app.modules.ai_testing.service import TestingService

router = APIRouter()


# ─── 项目 CRUD ─────────────────────────────────────

@router.get("/projects")
async def list_projects(
  status: str | None = Query(default=None),
  keyword: str | None = Query(default=None),
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[dict[str, Any]]:
  """获取项目列表（分页+筛选）"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_projects(
      status=status, keyword=keyword, page=page, page_size=page_size
    )
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/projects/{project_id}")
async def get_project(project_id: str) -> ApiResponse[dict[str, Any]]:
  """获取项目详情"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.get_project(project_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("/projects")
async def create_project(body: ProjectCreate) -> ApiResponse[dict[str, Any]]:
  """创建项目"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.create_project(
      name=body.name,
      description=body.description,
      status=body.status,
    )
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.put("/projects/{project_id}")
async def update_project(
  project_id: str, body: ProjectUpdate
) -> ApiResponse[dict[str, Any]]:
  """更新项目"""
  db = await get_db()
  service = TestingService(db)
  try:
    update_data = body.model_dump(exclude_none=True)
    data = await service.update_project(project_id, **update_data)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str) -> ApiResponse[bool]:
  """删除项目"""
  db = await get_db()
  service = TestingService(db)
  try:
    result = await service.delete_project(project_id)
    return ApiResponse(data=result)
  finally:
    await db.close()


# ─── 项目成员 ────────────────────────────────────────

@router.get("/projects/{project_id}/members")
async def list_members(project_id: str) -> ApiResponse[list[dict[str, Any]]]:
  """获取项目成员列表"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_members(project_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("/projects/{project_id}/members")
async def add_member(
  project_id: str, body: MemberCreate
) -> ApiResponse[dict[str, Any]]:
  """添加项目成员"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.add_member(project_id, body.name, body.role)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.delete("/members/{member_id}")
async def remove_member(member_id: str) -> ApiResponse[bool]:
  """移除项目成员"""
  db = await get_db()
  service = TestingService(db)
  try:
    result = await service.remove_member(member_id)
    return ApiResponse(data=result)
  finally:
    await db.close()


@router.put("/members/{member_id}")
async def update_member_role(
  member_id: str, body: MemberCreate
) -> ApiResponse[bool]:
  """更新成员角色"""
  db = await get_db()
  service = TestingService(db)
  try:
    result = await service.update_member_role(member_id, body.role)
    return ApiResponse(data=result)
  finally:
    await db.close()


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
  page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[dict[str, Any]]:
  """获取用例列表（多条件筛选+分页）"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_cases(
      project_id=project_id, priority=priority, case_type=case_type,
      status=status, version=version, keyword=keyword,
      page=page, page_size=page_size,
    )
    return ApiResponse(data=data)
  finally:
    await db.close()


# 固定路径路由必须在参数化路由之前注册，避免 "stats"/"export" 被捕获为 case_id
@router.get("/cases/export")
async def export_cases(
  project_id: str | None = Query(default=None),
  ids: str | None = Query(default=None, description="逗号分隔的用例 ID"),
) -> Response:
  """导出用例为 Excel 文件"""
  db = await get_db()
  service = TestingService(db)
  try:
    from app.modules.ai_testing.excel_handler import export_cases_to_xlsx
    from datetime import datetime

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
  finally:
    await db.close()


@router.get("/cases/stats")
async def get_case_stats(
  project_id: str | None = Query(default=None),
) -> ApiResponse[dict[str, Any]]:
  """获取用例统计（按优先级/类型/状态分组）"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.get_case_stats(project_id=project_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/cases/{case_id}")
async def get_case(case_id: str) -> ApiResponse[dict[str, Any]]:
  """获取用例详情"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.get_case(case_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("/cases")
async def create_case(body: TestCaseCreate) -> ApiResponse[dict[str, Any]]:
  """创建测试用例"""
  db = await get_db()
  service = TestingService(db)
  try:
    fields = body.model_dump()
    data = await service.create_case(**fields)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.put("/cases/{case_id}")
async def update_case(
  case_id: str, body: TestCaseUpdate
) -> ApiResponse[dict[str, Any]]:
  """更新测试用例"""
  db = await get_db()
  service = TestingService(db)
  try:
    update_data = body.model_dump(exclude_none=True)
    data = await service.update_case(case_id, **update_data)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.delete("/cases/{case_id}")
async def delete_case(case_id: str) -> ApiResponse[bool]:
  """删除测试用例"""
  db = await get_db()
  service = TestingService(db)
  try:
    result = await service.delete_case(case_id)
    return ApiResponse(data=result)
  finally:
    await db.close()


@router.post("/cases/batch-delete")
async def batch_delete_cases(body: BatchDeleteRequest) -> ApiResponse[int]:
  """批量删除测试用例"""
  db = await get_db()
  service = TestingService(db)
  try:
    count = await service.batch_delete_cases(body.ids)
    return ApiResponse(data=count)
  finally:
    await db.close()


# ─── AI 生成 ────────────────────────────────────────

@router.post("/generate")
async def create_generation_task(
  body: GenerateRequest,
) -> ApiResponse[dict[str, Any]]:
  """创建 AI 用例生成任务"""
  db = await get_db()
  service = TestingService(db)
  try:
    fields = body.model_dump()
    data = await service.create_generation_task(**fields)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/generate/tasks")
async def list_generation_tasks(
  project_id: str | None = Query(default=None),
  status: str | None = Query(default=None),
  keyword: str | None = Query(default=None),
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[dict[str, Any]]:
  """获取生成任务列表（分页+筛选）"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_generation_tasks(
      project_id=project_id, status=status, keyword=keyword,
      page=page, page_size=page_size,
    )
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/generate/tasks/{task_id}/generated-cases")
async def get_task_generated_cases(
  task_id: str,
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=20, ge=1, le=100),
  status: str | None = Query(default=None),
) -> ApiResponse[dict[str, Any]]:
  """获取任务生成的候选用例列表（分页+状态筛选）"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.get_task_generated_cases(
      task_id, page=page, page_size=page_size, status=status,
    )
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("/generate/tasks/{task_id}/batch-update-cases")
async def batch_update_task_cases(
  task_id: str, body: BatchUpdateCasesRequest,
) -> ApiResponse[dict[str, Any]]:
  """批量更新候选用例状态（adopted/discarded）"""
  db = await get_db()
  service = TestingService(db)
  try:
    updated = await service.batch_update_task_cases(body.case_ids, body.status)
    return ApiResponse(data={"updated": updated})
  finally:
    await db.close()


@router.get("/generate/stats")
async def get_generation_stats() -> ApiResponse[dict[str, Any]]:
  """获取生成统计（总任务数/已完成/总用例数）"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.get_generation_stats()
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/generate/{task_id}")
async def get_generation_task(task_id: str) -> ApiResponse[dict[str, Any]]:
  """获取生成任务状态"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.get_generation_task(task_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("/generate/{task_id}/cancel")
async def cancel_generation_task(task_id: str) -> ApiResponse[bool]:
  """取消生成任务"""
  db = await get_db()
  service = TestingService(db)
  try:
    result = await service.update_generation_task(task_id, status="cancelled")
    return ApiResponse(data=result)
  finally:
    await db.close()


@router.get("/generate/{task_id}/results")
async def get_generation_results(
  task_id: str,
) -> ApiResponse[list[dict[str, Any]]]:
  """获取生成任务的所有阶段结果"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_generation_results(task_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/generate/{task_id}/stream")
async def stream_generation(
    task_id: str,
    custom_suggestions: str | None = Query(default=None, description="JSON 编码的用户选中改进建议列表"),
) -> StreamingResponse:
  """SSE 流式获取生成进度（Phase 4 实现）"""
  from app.modules.ai_testing.sse_stream import stream_generation_task
  import json

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
async def export_generated_cases(task_id: str) -> Response:
  """导出 AI 生成用例为 Excel"""
  db = await get_db()
  service = TestingService(db)
  try:
    from app.modules.ai_testing.excel_handler import (
      export_cases_to_xlsx,
      parse_markdown_cases,
    )
    from datetime import datetime

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
  finally:
    await db.close()


@router.post("/generate/tasks/{task_id}/save-cases")
async def save_task_cases(
  task_id: str, body: SaveCasesRequest | None = None,
) -> ApiResponse[dict[str, Any]]:
  """将任务中已采用的候选用例保存到用例库"""
  db = await get_db()
  service = TestingService(db)
  try:
    project_id = body.project_id if body else None
    saved_count = await service.save_adopted_cases_to_library(task_id, project_id)
    return ApiResponse(data={"saved_count": saved_count})
  finally:
    await db.close()


@router.delete("/generate/tasks/{task_id}")
async def delete_generation_task(task_id: str) -> ApiResponse[bool]:
  """删除生成任务（含阶段结果）"""
  db = await get_db()
  service = TestingService(db)
  try:
    result = await service.delete_generation_task(task_id)
    return ApiResponse(data=result)
  finally:
    await db.close()


@router.put("/generate/tasks/{task_id}/status")
async def update_generation_task_status(
  task_id: str, body: TaskStatusUpdate
) -> ApiResponse[bool]:
  """更新生成任务状态"""
  db = await get_db()
  service = TestingService(db)
  try:
    result = await service.update_generation_task(task_id, status=body.status)
    return ApiResponse(data=result)
  finally:
    await db.close()


@router.post("/generate/save-cases")
async def save_generated_cases(
  body: SaveCasesRequest,
) -> ApiResponse[dict[str, Any]]:
  """将 AI 生成的用例保存到用例库"""
  db = await get_db()
  service = TestingService(db)
  try:
    cases_data = []
    for case in body.cases:
      cases_data.append({
        **case,
        "project_id": body.project_id,
        "source": "ai",
        "ai_task_id": body.task_id,
      })
    ids = await service.batch_create_cases(cases_data, task_id=body.task_id)
    # 更新任务的生成数量
    await service.update_generation_task(
      body.task_id, generated_count=len(ids)
    )
    return ApiResponse(data={"saved_count": len(ids), "ids": ids})
  finally:
    await db.close()


# ─── 配置 ──────────────────────────────────────────

@router.get("/config")
async def list_config(
  category: str | None = Query(default=None),
) -> ApiResponse[list[dict[str, Any]]]:
  """获取配置列表"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_config(category)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.put("/config")
async def update_config(body: ConfigUpdateRequest) -> ApiResponse[bool]:
  """批量更新配置"""
  db = await get_db()
  service = TestingService(db)
  try:
    items = [item.model_dump() for item in body.items]
    await service.update_config_batch(items)
    return ApiResponse(data=True)
  finally:
    await db.close()


@router.get("/config/defaults")
async def get_config_defaults() -> ApiResponse[ConfigDefaultsResponse]:
  """获取配置默认值（默认提示词模板 + 可用模型列表）"""
  data = ConfigDefaultsResponse(
    prompts={
      "analyze": prompts.ANALYZE_SYSTEM,
      "write": prompts.WRITE_SYSTEM,
      "review": prompts.REVIEW_SYSTEM,
      "revise": prompts.REVISE_SYSTEM,
    },
    models=LLMFactory.get_available_models(),
  )
  return ApiResponse(data=data)


# ─── 项目版本 ────────────────────────────────────────

@router.get("/projects/{project_id}/versions")
async def list_versions(project_id: str) -> ApiResponse[list[dict[str, Any]]]:
  """获取项目版本列表"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_versions(project_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("/projects/{project_id}/versions")
async def create_version(
  project_id: str, body: VersionCreate
) -> ApiResponse[dict[str, Any]]:
  """创建项目版本"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.create_version(
      project_id=project_id,
      name=body.name,
      description=body.description,
      status=body.status,
    )
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.put("/versions/{version_id}")
async def update_version(
  version_id: str, body: VersionUpdate
) -> ApiResponse[dict[str, Any]]:
  """更新版本"""
  db = await get_db()
  service = TestingService(db)
  try:
    update_data = body.model_dump(exclude_none=True)
    data = await service.update_version(version_id, **update_data)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.delete("/versions/{version_id}")
async def delete_version(version_id: str) -> ApiResponse[bool]:
  """删除版本"""
  db = await get_db()
  service = TestingService(db)
  try:
    result = await service.delete_version(version_id)
    return ApiResponse(data=result)
  finally:
    await db.close()


# ─── 用例附件 ────────────────────────────────────────

@router.post("/cases/{case_id}/attachments")
async def upload_attachment(
  case_id: str,
  file: UploadFile = File(...),
) -> ApiResponse[dict[str, Any]]:
  """上传用例附件"""
  import os
  from pathlib import Path
  from app.config import get_settings

  settings = get_settings()
  upload_dir = Path(settings.upload_dir) / "case_attachments"
  upload_dir.mkdir(parents=True, exist_ok=True)

  safe_name = f"{uuid.uuid4().hex}_{file.filename}"
  file_path = upload_dir / safe_name
  content = await file.read()
  file_path.write_bytes(content)

  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.create_attachment(
      case_id=case_id,
      file_name=file.filename or "unknown",
      file_path=str(file_path),
      file_size=len(content),
      file_type=file.content_type or "",
    )
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/cases/{case_id}/attachments")
async def list_attachments(case_id: str) -> ApiResponse[list[dict[str, Any]]]:
  """获取用例附件列表"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_attachments(case_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.delete("/attachments/{attachment_id}")
async def delete_attachment(attachment_id: str) -> ApiResponse[bool]:
  """删除附件"""
  import os
  db = await get_db()
  service = TestingService(db)
  try:
    attachment = await service.repo.get_attachment(attachment_id)
    if attachment and os.path.exists(attachment.get("file_path", "")):
      os.remove(attachment["file_path"])
    result = await service.delete_attachment(attachment_id)
    return ApiResponse(data=result)
  finally:
    await db.close()


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(attachment_id: str) -> StreamingResponse:
  """下载附件文件"""
  from pathlib import Path
  db = await get_db()
  service = TestingService(db)
  try:
    attachment = await service.repo.get_attachment(attachment_id)
    if not attachment:
      return StreamingResponse(
        content="附件不存在",
        status_code=404,
        media_type="text/plain",
      )
    file_path = attachment.get("file_path", "")
    if not Path(file_path).exists():
      return StreamingResponse(
        content="文件已丢失",
        status_code=404,
        media_type="text/plain",
      )
    file_bytes = Path(file_path).read_bytes()
    return StreamingResponse(
      iter([file_bytes]),
      media_type=attachment.get("file_type", "application/octet-stream"),
      headers={"Content-Disposition": f'attachment; filename="{attachment["file_name"]}"'},
    )
  finally:
    await db.close()


# ─── 用例评论 ────────────────────────────────────────

@router.get("/cases/{case_id}/comments")
async def list_comments(case_id: str) -> ApiResponse[list[dict[str, Any]]]:
  """获取用例评论列表"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_comments(case_id)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.post("/cases/{case_id}/comments")
async def create_comment(
  case_id: str, body: CommentCreate
) -> ApiResponse[dict[str, Any]]:
  """创建用例评论"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.create_comment(
      case_id=case_id,
      content=body.content,
      author=body.author,
    )
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.put("/comments/{comment_id}")
async def update_comment(
  comment_id: str, body: CommentUpdate
) -> ApiResponse[bool]:
  """更新评论"""
  db = await get_db()
  service = TestingService(db)
  try:
    result = await service.update_comment(comment_id, body.content)
    return ApiResponse(data=result)
  finally:
    await db.close()


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str) -> ApiResponse[bool]:
  """删除评论"""
  db = await get_db()
  service = TestingService(db)
  try:
    result = await service.delete_comment(comment_id)
    return ApiResponse(data=result)
  finally:
    await db.close()


# ─── 操作日志 ────────────────────────────────────────

@router.get("/cases/{case_id}/logs")
async def get_case_logs(
  case_id: str,
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=50, ge=1, le=200),
) -> ApiResponse[dict[str, Any]]:
  """获取用例操作日志"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_case_logs(case_id, page=page, page_size=page_size)
    return ApiResponse(data=data)
  finally:
    await db.close()


@router.get("/projects/{project_id}/logs")
async def get_project_logs(
  project_id: str,
  page: int = Query(default=1, ge=1),
  page_size: int = Query(default=50, ge=1, le=200),
) -> ApiResponse[dict[str, Any]]:
  """获取项目操作日志"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.list_project_logs(project_id, page=page, page_size=page_size)
    return ApiResponse(data=data)
  finally:
    await db.close()


# ─── 文档上传解析 ────────────────────────────────────

@router.post("/generate/upload-doc")
async def upload_document(
  file: UploadFile = File(...),
) -> ApiResponse[dict[str, str]]:
  """上传文档并解析内容（PDF/Word/TXT/MD）"""
  from app.shared.utils.file_parser import parse_file
  from app.config import get_settings
  from pathlib import Path

  content = await file.read()
  filename = file.filename or "unknown"
  ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

  # 安全保存原始文件
  settings = get_settings()
  upload_dir = Path(settings.upload_dir) / "testing_docs"
  upload_dir.mkdir(parents=True, exist_ok=True)
  safe_name = f"{uuid.uuid4().hex}_{filename}"
  save_path = upload_dir / safe_name
  save_path.write_bytes(content)

  # 解析文本
  text = parse_file(content, ext)

  return ApiResponse(data={
    "text": text,
    "file_name": filename,
    "file_type": ext,
    "file_path": str(save_path),
  })


# ─── 配置检查 ─────────────────────────────────────────

@router.get("/config/check")
async def check_config() -> ApiResponse[dict[str, Any]]:
  """检查 AI 生成必需配置是否完整"""
  db = await get_db()
  service = TestingService(db)
  try:
    data = await service.check_config_status()
    return ApiResponse(data=data)
  finally:
    await db.close()
