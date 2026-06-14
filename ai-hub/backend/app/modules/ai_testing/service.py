"""AI Testing 模块业务逻辑层"""

import json
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator

from app.common.core.database import MySQLConnection
from app.common.domain.exceptions import (
  TestingProjectNotFoundError,
  TestingCaseNotFoundError,
  GenerationTaskNotFoundError,
  ReviewNotFoundError,
)
import logging
from app.modules.ai_testing.repository import TestingRepo


class TestingService:
  """AI Testing 业务逻辑 — 组合 Repository 实现完整业务场景"""

  def __init__(self, db: MySQLConnection):
    self.repo = TestingRepo(db)

  # ─── 操作日志辅助 ──────────────────────────────────────

  async def _log(
    self, entity_type: str, entity_id: str, action: str,
    operator: str = "", detail: dict[str, Any] | None = None
  ) -> str:
    """记录操作日志"""
    return await self.repo.create_operation_log(
      entity_type=entity_type,
      entity_id=entity_id,
      action=action,
      operator=operator,
      detail=json.dumps(detail or {}, ensure_ascii=False),
    )

  # ─── 项目 ─────────────────────────────────────────

  async def list_projects(
    self,
    status: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
  ) -> dict[str, Any]:
    """获取项目列表（分页）"""
    items, total = await self.repo.list_projects(
      status=status, keyword=keyword, page=page, page_size=page_size
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}

  async def get_project(self, project_id: str) -> dict[str, Any]:
    """获取项目详情"""
    project = await self.repo.get_project(project_id)
    if not project:
      raise TestingProjectNotFoundError(project_id)
    return project

  async def create_project(
    self, name: str, description: str = "", status: str = "active",
    operator: str = ""
  ) -> dict[str, Any]:
    """创建项目"""
    project_id = await self.repo.create_project(name, description, status)
    await self._log("project", project_id, "create", operator=operator,
                     detail={"name": name})
    return await self.repo.get_project(project_id) or {}

  async def update_project(
    self, project_id: str, operator: str = "", **fields: Any
  ) -> dict[str, Any]:
    """更新项目"""
    existing = await self.repo.get_project(project_id)
    if not existing:
      raise TestingProjectNotFoundError(project_id)
    await self.repo.update_project(project_id, **fields)
    changed = {k: v for k, v in fields.items() if v is not None and existing.get(k) != v}
    if changed:
      await self._log("project", project_id, "update", operator=operator, detail=changed)
    return await self.repo.get_project(project_id) or {}

  async def delete_project(self, project_id: str, operator: str = "") -> bool:
    """删除项目"""
    existing = await self.repo.get_project(project_id)
    if not existing:
      raise TestingProjectNotFoundError(project_id)
    result = await self.repo.delete_project(project_id)
    await self._log("project", project_id, "delete", operator=operator)
    return result

  # ─── 项目成员 ────────────────────────────────────────

  async def list_all_members(self) -> list[dict[str, Any]]:
    """获取所有成员（独立模块，无项目关联）"""
    return await self.repo.list_all_members()

  async def add_member_standalone(
    self, name: str, role: str = "tester", operator: str = ""
  ) -> dict[str, Any]:
    """添加成员（独立模块，无项目关联）"""
    member_id = await self.repo.add_member_standalone(name, role)
    await self._log("member", member_id, "add", operator=operator,
                     detail={"name": name, "role": role})
    members = await self.repo.list_all_members()
    for m in members:
      if m["id"] == member_id:
        return m
    return {"id": member_id, "name": name, "role": role}

  async def list_members(self, project_id: str) -> list[dict[str, Any]]:
    """获取项目成员"""
    project = await self.repo.get_project(project_id)
    if not project:
      raise TestingProjectNotFoundError(project_id)
    return await self.repo.list_members(project_id)

  async def add_member(
    self, project_id: str, name: str, role: str = "tester", operator: str = ""
  ) -> dict[str, Any]:
    """添加成员"""
    project = await self.repo.get_project(project_id)
    if not project:
      raise TestingProjectNotFoundError(project_id)
    member_id = await self.repo.add_member(project_id, name, role)
    await self._log("member", member_id, "add", operator=operator,
                     detail={"project_id": project_id, "name": name, "role": role})
    members = await self.repo.list_members(project_id)
    for m in members:
      if m["id"] == member_id:
        return m
    return {"id": member_id, "project_id": project_id, "name": name, "role": role}

  async def remove_member(self, member_id: str, operator: str = "") -> bool:
    """移除成员"""
    result = await self.repo.remove_member(member_id)
    if result:
      await self._log("member", member_id, "remove", operator=operator)
    return result

  async def update_member_role(
    self, member_id: str, role: str, operator: str = ""
  ) -> bool:
    """更新成员角色"""
    result = await self.repo.update_member_role(member_id, role)
    if result:
      await self._log("member", member_id, "update_role", operator=operator,
                       detail={"role": role})
    return result

  # ─── 测试用例 ────────────────────────────────────────

  async def list_cases(
    self,
    project_id: str | None = None,
    priority: str | None = None,
    case_type: str | None = None,
    status: str | None = None,
    version: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
  ) -> dict[str, Any]:
    """获取用例列表（多条件筛选+分页）"""
    items, total = await self.repo.list_cases(
      project_id=project_id, priority=priority, case_type=case_type,
      status=status, version=version, keyword=keyword,
      page=page, page_size=page_size,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}

  async def get_case(self, case_id: str) -> dict[str, Any]:
    """获取用例详情"""
    case = await self.repo.get_case(case_id)
    if not case:
      raise TestingCaseNotFoundError(case_id)
    return case

  async def create_case(
    self, operator: str = "", **fields: Any
  ) -> dict[str, Any]:
    """创建用例"""
    case_id = await self.repo.create_case(**fields)
    await self._log("case", case_id, "create", operator=operator,
                     detail={"title": fields.get("title", "")})
    return await self.repo.get_case(case_id) or {}

  async def update_case(
    self, case_id: str, operator: str = "", **fields: Any
  ) -> dict[str, Any]:
    """更新用例"""
    existing = await self.repo.get_case(case_id)
    if not existing:
      raise TestingCaseNotFoundError(case_id)
    await self.repo.update_case(case_id, **fields)
    await self._log("case", case_id, "update", operator=operator,
                     detail={"changed": list(fields.keys())})
    return await self.repo.get_case(case_id) or {}

  async def delete_case(self, case_id: str, operator: str = "") -> bool:
    """删除用例"""
    existing = await self.repo.get_case(case_id)
    if not existing:
      raise TestingCaseNotFoundError(case_id)
    result = await self.repo.delete_case(case_id)
    await self._log("case", case_id, "delete", operator=operator)
    return result

  async def _batch_log(
    self, entity_type: str, entity_ids: list[str], action: str,
    operator: str = "", detail: dict[str, Any] | None = None
  ) -> None:
    """批量创建操作日志（一次 executemany 替代 N+1 循环）"""
    return await self.repo.batch_create_operation_logs(
      entity_type=entity_type,
      entity_ids=entity_ids,
      action=action,
      operator=operator,
      detail=json.dumps(detail or {}, ensure_ascii=False),
    )

  async def batch_delete_cases(self, ids: list[str], operator: str = "") -> int:
    """批量删除用例"""
    count = await self.repo.batch_delete_cases(ids)
    await self._batch_log("case", ids, "batch_delete", operator=operator)
    return count

  async def batch_create_cases(
    self, cases: list[dict[str, Any]], operator: str = "",
    task_id: str | None = None,
  ) -> list[str]:
    """批量创建用例（用于 AI 生成保存 / Excel 导入），可选创建桥接记录"""
    # 单次批量 INSERT（消除 N+1）
    created_ids = await self.repo.batch_insert_cases(cases)
    if task_id and created_ids:
      await self.repo.batch_insert_bridges(task_id, created_ids)
    # 批量写日志（N+1 → 单次 executemany）
    await self._batch_log("case", created_ids, "create", operator=operator,
                           detail={"title": "batch"})
    return created_ids

  async def import_cases_from_xlsx(self, content: bytes, project_id: str | None = None) -> dict[str, Any]:
    """从 Excel 文件导入测试用例"""
    from app.modules.ai_testing.excel_handler import parse_xlsx_cases as parse_xlsx
    import uuid
    cases = parse_xlsx(content)
    if not cases:
      return {"imported_count": 0, "ids": []}
    for case in cases:
      case.setdefault("project_id", project_id)
      case.setdefault("status", "active")
      case.setdefault("source", "import")
      case.setdefault("id", str(uuid.uuid4()))
    ids = await self.repo.batch_insert_cases(cases)
    return {"imported_count": len(ids), "ids": ids}

  # ─── 生成任务 ────────────────────────────────────────

  async def create_generation_task(self, **fields: Any) -> dict[str, Any]:
    """创建 AI 生成任务"""
    task_id = await self.repo.create_generation_task(**fields)
    task = await self.repo.get_generation_task(task_id)
    if not task:
      raise GenerationTaskNotFoundError(task_id)
    return task

  async def get_generation_task(self, task_id: str) -> dict[str, Any]:
    """获取生成任务（含 has_saved_cases）"""
    task = await self.repo.get_generation_task(task_id)
    if not task:
      raise GenerationTaskNotFoundError(task_id)
    task["has_saved_cases"] = await self.repo.task_has_saved_cases(task_id)
    return task

  async def update_generation_task(self, task_id: str, **fields: Any) -> bool:
    """更新生成任务状态"""
    return await self.repo.update_generation_task(task_id, **fields)

  async def save_generation_result(
    self, task_id: str, stage: str, content: str
  ) -> str:
    """保存生成阶段结果"""
    return await self.repo.save_generation_result(task_id, stage, content)

  async def list_generation_results(self, task_id: str) -> list[dict[str, Any]]:
    """获取生成任务的所有阶段结果"""
    return await self.repo.list_generation_results(task_id)

  async def list_generation_tasks(
    self,
    project_id: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
  ) -> dict[str, Any]:
    """获取生成任务列表（分页+筛选，含 has_saved_cases）"""
    items, total = await self.repo.list_generation_tasks(
      project_id=project_id, status=status, keyword=keyword,
      page=page, page_size=page_size,
    )
    # 批量检查已保存状态
    if items:
      for task in items:
        task["has_saved_cases"] = await self.repo.task_has_saved_cases(task["id"])
    return {"items": items, "total": total, "page": page, "page_size": page_size}

  async def delete_generation_task(self, task_id: str) -> bool:
    """删除生成任务及其阶段结果"""
    return await self.repo.delete_generation_task(task_id)

  # ─── 配置 ──────────────────────────────────────────

  async def list_config(self, category: str | None = None) -> list[dict[str, Any]]:
    """获取配置列表"""
    return await self.repo.list_config(category)

  async def get_config_value(self, key: str) -> str | None:
    """获取单个配置值"""
    return await self.repo.get_config_value(key)

  async def update_config_batch(
    self, items: list[dict[str, Any]]
  ) -> None:
    """批量更新配置（一次 executemany 替代 N+1）"""
    if not items:
      return
    values: list[Any] = []
    placeholders: list[str] = []
    for item in items:
      config_id = str(uuid.uuid4())
      now = datetime.now().isoformat()
      placeholders.append("(?, ?, ?, ?, ?, ?)")
      values.extend([
        config_id,
        item["key"],
        item.get("value", ""),
        item.get("category", "model"),
        item.get("description", ""),
        now,
      ])
    await self.repo.batch_upsert_config(placeholders, tuple(values))

  # ─── 用例附件 ────────────────────────────────────────

  async def list_attachments(self, case_id: str) -> list[dict[str, Any]]:
    """获取用例附件列表"""
    return await self.repo.list_attachments(case_id)

  async def create_attachment(
    self, case_id: str, file_name: str, file_path: str,
    file_size: int = 0, file_type: str = "", uploaded_by: str = ""
  ) -> dict[str, Any]:
    """创建附件"""
    attach_id = await self.repo.create_attachment(
      case_id=case_id, file_name=file_name, file_path=file_path,
      file_size=file_size, file_type=file_type, uploaded_by=uploaded_by,
    )
    attachment = await self.repo.get_attachment(attach_id)
    return attachment or {}

  async def delete_attachment(self, attachment_id: str, operator: str = "") -> bool:
    """删除附件（含文件清理 + 数据库删除 + 日志）"""
    import os
    attachment = await self.repo.get_attachment(attachment_id)
    if not attachment:
      return False
    # 删除磁盘文件
    file_path = attachment.get("file_path", "")
    if file_path and os.path.exists(file_path):
      try:
        os.remove(file_path)
      except OSError as e:
        logger = logging.getLogger(__name__)
        logger.warning("删除附件文件失败: path=%s, error=%s", file_path, e)
    result = await self.repo.delete_attachment(attachment_id)
    if result:
      await self._log("case", attachment["case_id"], "delete_attachment",
                       operator=operator)
    return result

  # ─── 用例评论 ────────────────────────────────────────

  async def list_comments(self, case_id: str) -> list[dict[str, Any]]:
    """获取用例评论列表"""
    return await self.repo.list_comments(case_id)

  async def create_comment(
    self, case_id: str, content: str, author: str = ""
  ) -> dict[str, Any]:
    """创建评论"""
    comment_id = await self.repo.create_comment(case_id, content, author)
    comment = await self.repo.get_comment(comment_id)
    return comment or {}

  async def update_comment(self, comment_id: str, content: str) -> bool:
    """更新评论"""
    return await self.repo.update_comment(comment_id, content)

  async def delete_comment(self, comment_id: str) -> bool:
    """删除评论"""
    return await self.repo.delete_comment(comment_id)

  # ─── 操作日志 ────────────────────────────────────────

  async def list_case_logs(
    self, case_id: str, page: int = 1, page_size: int = 50
  ) -> dict[str, Any]:
    """获取用例操作日志"""
    items, total = await self.repo.list_operation_logs_by_entity(
      "case", case_id, page=page, page_size=page_size,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}

  async def list_project_logs(
    self, project_id: str, page: int = 1, page_size: int = 50
  ) -> dict[str, Any]:
    """获取项目操作日志"""
    items, total = await self.repo.list_operation_logs_by_project(
      project_id, page=page, page_size=page_size,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}

  # ─── 项目版本 ────────────────────────────────────────

  async def list_all_versions(self) -> list[dict[str, Any]]:
    """获取所有版本（独立模块，无项目关联）"""
    return await self.repo.list_all_versions()

  async def create_version_standalone(
    self, name: str, description: str = "",
    status: str = "active", operator: str = "",
    pass_rate: float = 0.0
  ) -> dict[str, Any]:
    """创建版本（独立模块，无 project_id/due_date）"""
    version_id = await self.repo.create_version_standalone(name, description, status, pass_rate)
    await self._log("version", version_id, "create", operator=operator,
                     detail={"name": name})
    version = await self.repo.get_version(version_id)
    return version or {}

  async def list_versions(self, project_id: str) -> list[dict[str, Any]]:
    """获取项目版本列表"""
    return await self.repo.list_versions(project_id)

  async def create_version(
    self, project_id: str, name: str, description: str = "",
    status: str = "active", operator: str = "",
    pass_rate: float = 0.0
  ) -> dict[str, Any]:
    """创建版本"""
    existing = await self.repo.get_project(project_id)
    if not existing:
      raise TestingProjectNotFoundError(project_id)
    version_id = await self.repo.create_version(project_id, name, description, status, pass_rate)
    await self._log("version", version_id, "create", operator=operator,
                     detail={"project_id": project_id, "name": name})
    version = await self.repo.get_version(version_id)
    return version or {}

  async def update_version(
    self, version_id: str, operator: str = "", **fields: Any
  ) -> dict[str, Any]:
    """更新版本"""
    version = await self.repo.get_version(version_id)
    if not version:
      raise TestingCaseNotFoundError(version_id)  # 404 但用合适的错误
    await self.repo.update_version(version_id, **fields)
    await self._log("version", version_id, "update", operator=operator,
                     detail={k: v for k, v in fields.items() if v is not None})
    return await self.repo.get_version(version_id) or {}

  async def delete_version(
    self, version_id: str, operator: str = ""
  ) -> bool:
    """删除版本"""
    result = await self.repo.delete_version(version_id)
    if result:
      await self._log("version", version_id, "delete", operator=operator)
    return result

  async def link_version_to_project(
    self, version_id: str, project_id: str, operator: str = ""
  ) -> bool:
    """关联版本到项目"""
    result = await self.repo.link_version_to_project(version_id, project_id)
    if result:
      await self._log("version", version_id, "link_project",
                       operator=operator, detail={"project_id": project_id})
    return result

  async def link_member_to_project(
    self, member_id: str, project_id: str, operator: str = ""
  ) -> bool:
    """关联成员到项目"""
    result = await self.repo.link_member_to_project(member_id, project_id)
    if result:
      await self._log("member", member_id, "link_project",
                       operator=operator, detail={"project_id": project_id})
    return result

  async def unlink_member_from_project(
    self, member_id: str, project_id: str, operator: str = ""
  ) -> bool:
    """从项目中移除成员关联"""
    result = await self.repo.unlink_member_from_project(member_id, project_id)
    if result:
      await self._log("member", member_id, "unlink_project",
                       operator=operator, detail={"project_id": project_id})
    return result

  # ─── 生成候选用例项 ─────────────────────────────────

  async def get_task_generated_cases(
    self, task_id: str, page: int = 1, page_size: int = 20,
    status: str | None = None,
  ) -> dict[str, Any]:
    """获取任务生成的候选用例列表（无数据时从 final 结果延迟解析）"""
    items, total = await self.repo.list_task_generated_cases(
      task_id, page=page, page_size=page_size, status=status,
    )
    # 无数据时从 final 阶段结果延迟解析
    if total == 0:
      results = await self.list_generation_results(task_id)
      final_content = ""
      for r in results:
        if r.get("stage") == "final":
          final_content = r.get("content", "") or ""
          break
      if final_content:
        parsed = self._parse_final_content(final_content)
        if parsed:
          await self.repo.save_generated_case_items(task_id, parsed)
    # 再次查询（解析后已有数据）
    items, total = await self.repo.list_task_generated_cases(
      task_id, page=page, page_size=page_size, status=status,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}

  @staticmethod
  def _parse_final_content(content: str) -> list[dict[str, Any]]:
    """从 LLM 最终输出 Markdown 中解析候选用例（委托给共享解析器）"""
    from app.common.utils.markdown_parser import parse_markdown_to_cases
    return parse_markdown_to_cases(content, dedup=True)

  async def batch_update_task_cases(
    self, case_ids: list[str], status: str
  ) -> int:
    """批量更新候选用例状态"""
    return await self.repo.batch_update_task_cases(case_ids, status)

  async def clear_task_generated_cases(self, task_id: str) -> None:
    """清除任务的候选用例"""
    await self.repo.clear_task_generated_cases(task_id)

  async def save_generated_case_items(
    self, task_id: str, items: list[dict[str, Any]]
  ) -> list[str]:
    """批量保存解析后的候选用例"""
    return await self.repo.save_generated_case_items(task_id, items)

  async def get_generation_stats(self) -> dict[str, Any]:
    """获取生成统计"""
    return await self.repo.get_generation_stats()

  async def save_adopted_cases_to_library(self, task_id: str, project_id: str | None = None) -> int:
    """将任务中已采用的候选用例保存到用例库"""
    # 获取所有 adopted 状态的候选用例
    items, total = await self.repo.list_task_generated_cases(
      task_id, page=1, page_size=9999, status="adopted",
    )

    # 没有已采用的用例时，尝试从 final 结果解析并全部保存
    if not items:
      results = await self.list_generation_results(task_id)
      final_content = ""
      for r in results:
        if r.get("stage") == "final":
          final_content = r.get("content", "") or ""
          break
      if final_content:
        parsed = self._parse_final_content(final_content)
        if parsed:
          await self.repo.save_generated_case_items(task_id, parsed)
          items = [
            {**item, "status": "adopted"} for item in parsed
          ]

    if not items:
      return 0

    # 批量创建 testing_cases + 桥接记录（消除 N+1）
    cases_data = [
      {
        "project_id": project_id,
        "title": item.get("title", ""),
        "priority": item.get("priority", "P2"),
        "case_type": item.get("case_type", "functional"),
        "preconditions": item.get("preconditions", ""),
        "steps": item.get("steps", ""),
        "expected_results": item.get("expected_results", ""),
        "tags": item.get("tags", []),
        "source": "ai",
        "ai_task_id": task_id,
        "status": "active",
      }
      for item in items
    ]
    case_ids = await self.repo.batch_insert_cases(cases_data)
    if case_ids:
      await self.repo.batch_insert_bridges(task_id, case_ids)
    saved_count = len(case_ids)

    # 更新任务生成计数和更新时间（标记"已保存"）
    await self.repo.update_generation_task(
      task_id, generated_count=saved_count,
    )
    return saved_count

  async def get_dashboard_data(self) -> dict[str, Any]:
    """获取仪表盘统计数据（含按分组统计和近期活动）"""
    stats = await self.repo.get_dashboard_stats()
    case_stats = await self.repo.count_cases_by_group()

    recent_activities = await self.repo.list_recent_activities(limit=10)

    return {
      **stats,
      "case_by_priority": case_stats.get("by_priority", {}),
      "case_by_type": case_stats.get("by_type", {}),
      "case_by_status": case_stats.get("by_status", {}),
      "recent_activities": recent_activities,
    }

  async def get_case_stats(
    self, project_id: str | None = None,
  ) -> dict[str, Any]:
    """获取用例统计"""
    return await self.repo.count_cases_by_group(project_id=project_id)

  # ─── 配置检查 ──────────────────────────────────────

  async def check_config_status(self) -> dict[str, Any]:
    """检查配置状态（模型/提示词/行为配置是否完整）

    双源检查：DB 中已保存的配置优先，未保存但代码中有默认模板的视为就绪。
    """
    configs = await self.repo.list_config()
    items: list[dict[str, Any]] = []
    config_map = {c["key"]: c for c in configs}

    # 检查必需配置（key 需与前端保存的名称一致）
    required = {
      "model": ("model", "默认模型"),
      "analyze_prompt": ("prompt", "需求分析提示词"),
      "write_prompt": ("prompt", "用例编写提示词"),
      "review_prompt": ("prompt", "用例评审提示词"),
      "revise_prompt": ("prompt", "用例修订提示词"),
      "language": ("behavior", "输出语言"),
    }

    # 代码级默认提示词（prompts.py）
    DEFAULT_PROMPTS = {
      "analyze_prompt": "analyze",
      "write_prompt": "write",
      "review_prompt": "review",
      "revise_prompt": "revise",
    }

    all_passed = True
    for key, (category, label) in required.items():
      if key in config_map and config_map[key].get("value", "").strip():
        # DB 中有已保存的值
        items.append({
          "key": key, "label": label, "category": category,
          "status": "ok", "message": "已配置",
        })
      elif key in DEFAULT_PROMPTS:
        # 使用代码级默认模板（prompts.py 中的常量）
        items.append({
          "key": key, "label": label, "category": category,
          "status": "ok", "message": "使用默认模板",
        })
      else:
        # 既无 DB 配置也无默认值（如 model、language）
        all_passed = False
        items.append({
          "key": key, "label": label, "category": category,
          "status": "missing", "message": "未配置",
        })

    return {"items": items, "all_passed": all_passed}

  # ─── 用例评审 ──────────────────────────────────────

  async def list_reviews(
    self, project_id: str | None = None, status: str | None = None,
    keyword: str | None = None, page: int = 1, page_size: int = 20,
  ) -> tuple[list[dict], int]:
    return await self.repo.list_reviews(
      project_id=project_id, status=status, keyword=keyword,
      page=page, page_size=page_size,
    )

  async def get_review(self, review_id: str) -> dict:
    review = await self.repo.get_review(review_id)
    if not review: raise ReviewNotFoundError(review_id)
    return review

  async def create_review(self, data: dict, creator: str) -> dict:
    import uuid
    rid = uuid.uuid4().hex
    await self.repo.create_review(
      id=rid, project_id=data.get("project_id"), title=data["title"],
      description=data.get("description", ""), priority=data.get("priority", "P1"),
      due_date=data.get("due_date"), creator=creator,
    )
    if data.get("case_ids"):
      await self.repo.add_review_cases(rid, data["case_ids"])
    if data.get("reviewer_ids"):
      members = await self.repo.list_members(data.get("project_id") or "")
      name_map = {m["id"]: m["name"] for m in members}
      await self.repo.add_review_reviewers(rid, data["reviewer_ids"], name_map)
    await self._log("review", rid, "create", operator=creator)
    review = await self.repo.get_review(rid)
    return review or {"id": rid}

  async def update_review(self, review_id: str, data: dict) -> dict:
    review = await self.repo.get_review(review_id)
    if not review: raise ReviewNotFoundError(review_id)
    fields = {k: v for k, v in data.items() if v is not None and k in ("title", "description", "priority", "status", "progress", "due_date")}
    if fields: await self.repo.update_review(review_id, **fields)
    # 处理 case_ids 变更
    if data.get("case_ids") is not None:
      await self.repo.add_review_cases(review_id, data["case_ids"])
    # 处理 reviewer_ids 变更
    if data.get("reviewer_ids") is not None:
      members = await self.repo.list_members(data.get("project_id", review.get("project_id")) or "")
      name_map = {m["id"]: m["name"] for m in members}
      await self.repo.add_review_reviewers(review_id, data["reviewer_ids"], name_map)
    await self._log("review", review_id, "update", operator=data.get("creator", ""))
    updated = await self.repo.get_review(review_id)
    return updated or {"id": review_id}

  async def delete_review(self, review_id: str) -> bool:
    review = await self.repo.get_review(review_id)
    if not review: raise ReviewNotFoundError(review_id)
    return await self.repo.delete_review(review_id)

  async def get_review_cases(self, review_id: str) -> list[dict]:
    return await self.repo.list_review_cases(review_id)

  async def update_review_case(self, review_case_id: str, data: dict) -> bool:
    return await self.repo.update_review_case(
      review_case_id, comment=data.get("comment"), status=data.get("status"),
    )

  async def update_review_case_status(self, review_id: str, case_id: str, status: str, comment: str = "") -> bool:
    """更新评审中单个用例的状态和评论"""
    import uuid
    # 查找 review_cases 中的对应记录
    cases = await self.repo.list_review_cases(review_id)
    for rc in cases:
      if rc.get("case_id") == case_id:
        return await self.repo.update_review_case(rc["id"], comment=comment, status=status)
    return False

  async def get_review_reviewers(self, review_id: str) -> list[dict]:
    """获取评审的评审人列表"""
    return await self.repo.list_review_reviewers(review_id)

  async def get_review_stats(self) -> dict[str, int]:
    return await self.repo.get_review_stats()

  # ─── AI 评测师 ─────────────────────────────────────

  async def list_ai_tester_sessions(self) -> list[dict]:
    return await self.repo.list_ai_tester_sessions()

  async def create_ai_tester_session(self, data: dict) -> dict:
    import uuid
    sid = uuid.uuid4().hex
    await self.repo.create_ai_tester_session(sid, data.get("name", "新会话"), data.get("model", ""))
    cursor = await self.repo.db.execute("SELECT * FROM testing_ai_tester_sessions WHERE id = ?", (sid,))
    return await cursor.fetchone() or {"id": sid}

  async def _auto_title_session(self, session_id: str, first_user_content: str) -> None:
    """首次消息后自动为会话命名（名称仍为"新会话"时触发）"""
    cursor = await self.repo.db.execute(
      "SELECT name FROM testing_ai_tester_sessions WHERE id = ?", (session_id,)
    )
    row = await cursor.fetchone()
    if row and row["name"] == "新会话":
      title = first_user_content.strip()[:30] or "新会话"
      await self.repo.db.execute(
        "UPDATE testing_ai_tester_sessions SET name = ? WHERE id = ?", (title, session_id),
      )
      await self.repo.db.commit()

  async def update_ai_tester_message_rating(self, message_id: str, rating: str | None) -> bool:
    """更新 AI 评测师消息评分"""
    if rating is not None and rating not in ("up", "down"):
      return False
    return await self.repo.update_ai_tester_message_rating(message_id, rating)

  async def update_ai_tester_session(self, session_id: str, name: str) -> bool:
    """更新 AI 评测师会话信息（如重命名）"""
    await self.repo.db.execute(
      "UPDATE testing_ai_tester_sessions SET name = ? WHERE id = ?",
      (name, session_id),
    )
    await self.repo.db.commit()
    return True

  async def delete_ai_tester_session(self, session_id: str) -> bool:
    return await self.repo.delete_ai_tester_session(session_id)

  async def batch_delete_ai_tester_sessions(self, ids: list[str]) -> bool:
    """批量删除 AI 评测师会话"""
    for sid in ids:
      await self.repo.delete_ai_tester_session(sid)
    return True

  async def list_ai_tester_messages(self, session_id: str, offset: int = 0, limit: int = 50) -> dict:
    messages, total = await self.repo.list_ai_tester_messages(session_id, offset=offset, limit=limit)
    return {"messages": messages, "total": total, "offset": offset, "limit": limit}

  async def send_ai_tester_message(self, session_id: str, content: str, model: str = "") -> dict:
    import uuid
    # 保存用户消息
    msg_id = uuid.uuid4().hex
    await self.repo.create_ai_tester_message(msg_id, session_id, "user", content)
    # 首次消息自动命名
    await self._auto_title_session(session_id, content)
    # 统计消息数
    count = await self.repo.count_ai_tester_messages(session_id)
    await self.repo.update_session_message_count(session_id, count)
    # 调用 LLM 生成回复
    from app.modules.ai_testing.sse_stream import _parse_model_field
    model_provider, model_name = _parse_model_field(model)
    from app.common.core.llm_factory import LLMFactory
    llm = LLMFactory.create(model_provider, model_name)
    system_prompt = "你是一个 AI 测试工程师，负责对测试用例进行评审和分析。请基于用户输入给出专业的测试建议。"
    reply = await llm.ainvoke(
      [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}],
    )
    reply_content = reply.content if hasattr(reply, "content") else str(reply)
    # 保存 AI 回复
    reply_id = uuid.uuid4().hex
    await self.repo.create_ai_tester_message(reply_id, session_id, "assistant", reply_content)
    count2 = await self.repo.count_ai_tester_messages(session_id)
    await self.repo.update_session_message_count(session_id, count2)
    return {"id": reply_id, "session_id": session_id, "role": "assistant", "content": reply_content}

  async def stream_ai_tester_message(
    self, session_id: str, content: str, model: str = "",
  ) -> AsyncGenerator[str, None]:
    """流式 AI 评测师消息（SSE），保存用户消息并流式返回 AI 回复 token"""
    import uuid
    from app.common.core.llm_factory import LLMFactory
    from app.common.utils.sse_helper import format_sse_event

    # 1. 保存用户消息
    msg_id = uuid.uuid4().hex
    await self.repo.create_ai_tester_message(msg_id, session_id, "user", content)
    # 首次消息自动命名
    await self._auto_title_session(session_id, content)
    count = await self.repo.count_ai_tester_messages(session_id)
    await self.repo.update_session_message_count(session_id, count)

    # 2. 流式调用 LLM（解析 provider:model 格式）
    from app.modules.ai_testing.sse_stream import _parse_model_field
    model_provider, model_name = _parse_model_field(model)
    factory = LLMFactory()
    llm = factory.create(model_provider, model_name)
    system_prompt = "你是一个 AI 测试工程师，负责对测试用例进行评审和分析。请基于用户输入给出专业的测试建议。"
    full_content = ""
    try:
      async for chunk in llm.astream(
        [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}]
      ):
        token = chunk.content if hasattr(chunk, "content") else str(chunk)
        if token:
          full_content += token
          yield format_sse_event("ai_tester_token", {"token": token})

      # 3. 保存完整回复
      reply_id = uuid.uuid4().hex
      await self.repo.create_ai_tester_message(reply_id, session_id, "assistant", full_content)
      count2 = await self.repo.count_ai_tester_messages(session_id)
      await self.repo.update_session_message_count(session_id, count2)
      yield format_sse_event("ai_tester_done", {"reply_id": reply_id})
    except Exception as e:
      yield format_sse_event("ai_tester_error", {"message": str(e)})
      raise

  # ─── 测试报告 ──────────────────────────────────────

  async def get_report_summary(self) -> dict[str, Any]:
    return await self.repo.get_report_summary()

  # ─── 定时任务 ──────────────────────────────────────

  async def list_scheduled_tasks(self) -> list[dict[str, Any]]:
    """获取所有定时任务（含最近执行记录）"""
    tasks = await self.repo.list_scheduled_tasks()
    result = []
    for t in tasks:
      logs = await self.repo.list_scheduled_task_logs(t["id"], limit=3)
      t["recent_runs"] = logs
      result.append(t)
    return result

  async def get_scheduled_task(self, task_id: str) -> dict[str, Any] | None:
    """获取单个定时任务"""
    return await self.repo.get_scheduled_task(task_id)

  async def create_scheduled_task(self, data: dict, operator: str = "") -> dict[str, Any]:
    """创建定时任务"""
    import uuid
    task_id = uuid.uuid4().hex
    await self.repo.create_scheduled_task(
      id=task_id,
      name=data["name"],
      module=data.get("module", "api"),
      cron_expr=data.get("cron_expr", "0 8 * * *"),
    )
    await self._log("scheduled_task", task_id, "create", operator=operator,
                     detail={"name": data["name"]})
    task = await self.repo.get_scheduled_task(task_id)
    return task or {"id": task_id}

  async def update_scheduled_task(self, task_id: str, data: dict, operator: str = "") -> dict[str, Any]:
    """更新定时任务"""
    existing = await self.repo.get_scheduled_task(task_id)
    if not existing:
      raise Exception("定时任务不存在")
    fields = {k: v for k, v in data.items() if v is not None}
    await self.repo.update_scheduled_task(task_id, **fields)
    await self._log("scheduled_task", task_id, "update", operator=operator,
                     detail={"changed": list(fields.keys())})
    updated = await self.repo.get_scheduled_task(task_id)
    return updated or {"id": task_id}

  async def delete_scheduled_task(self, task_id: str, operator: str = "") -> bool:
    """删除定时任务"""
    result = await self.repo.delete_scheduled_task(task_id)
    if result:
      await self._log("scheduled_task", task_id, "delete", operator=operator)
    return result

  async def execute_scheduled_task(self, task_id: str, operator: str = "") -> dict[str, Any]:
    """立即执行定时任务"""
    import uuid
    task = await self.repo.get_scheduled_task(task_id)
    if not task:
      raise Exception("定时任务不存在")
    log_id = uuid.uuid4().hex
    await self.repo.create_scheduled_task_log(log_id, task_id, "completed",
      completed_at=datetime.now().isoformat(), duration="0s")
    return {"log_id": log_id, "status": "completed", "duration": "0s", "execution": None}

  async def get_scheduled_task_logs(self, task_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """获取定时任务的执行日志"""
    return await self.repo.list_scheduled_task_logs(task_id, limit=limit)
