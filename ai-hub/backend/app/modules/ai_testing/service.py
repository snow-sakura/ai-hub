"""AI Testing 模块业务逻辑层"""

import json
from typing import Any

from app.shared.core.database import MySQLConnection
from app.shared.domain.exceptions import (
  TestingProjectNotFoundError,
  TestingCaseNotFoundError,
  GenerationTaskNotFoundError,
)
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
    # 查询成员详情用于日志
    members = []
    # 无法直接查 member，但我们可以执行删除
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

  async def batch_delete_cases(self, ids: list[str], operator: str = "") -> int:
    """批量删除用例"""
    count = await self.repo.batch_delete_cases(ids)
    for case_id in ids:
      await self._log("case", case_id, "batch_delete", operator=operator)
    return count

  async def batch_create_cases(
    self, cases: list[dict[str, Any]], operator: str = "",
    task_id: str | None = None,
  ) -> list[str]:
    """批量创建用例（用于 AI 生成保存 / Excel 导入），可选创建桥接记录"""
    created_ids: list[str] = []
    for case_data in cases:
      case_id = await self.repo.create_case(**case_data)
      created_ids.append(case_id)
      if task_id:
        await self.repo.create_task_case_bridge(task_id, case_id)
    for case_id in created_ids:
      await self._log("case", case_id, "create", operator=operator,
                       detail={"title": "batch"})
    return created_ids

  # ─── 生成任务 ────────────────────────────────────────

  async def create_generation_task(self, **fields: Any) -> dict[str, Any]:
    """创建 AI 生成任务"""
    task_id = await self.repo.create_generation_task(**fields)
    return await self.repo.get_generation_task(task_id) or {}

  async def get_generation_task(self, task_id: str) -> dict[str, Any]:
    """获取生成任务"""
    task = await self.repo.get_generation_task(task_id)
    if not task:
      raise GenerationTaskNotFoundError(task_id)
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
    """获取生成任务列表（分页+筛选）"""
    items, total = await self.repo.list_generation_tasks(
      project_id=project_id, status=status, keyword=keyword,
      page=page, page_size=page_size,
    )
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
    """批量更新配置"""
    for item in items:
      await self.repo.upsert_config(
        key=item["key"],
        value=item.get("value", ""),
        category=item.get("category", "model"),
        description=item.get("description", ""),
      )

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
    """删除附件"""
    attachment = await self.repo.get_attachment(attachment_id)
    if not attachment:
      return False
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

  async def list_versions(self, project_id: str) -> list[dict[str, Any]]:
    """获取项目版本列表"""
    return await self.repo.list_versions(project_id)

  async def create_version(
    self, project_id: str, name: str, description: str = "",
    status: str = "active", operator: str = ""
  ) -> dict[str, Any]:
    """创建版本"""
    existing = await self.repo.get_project(project_id)
    if not existing:
      raise TestingProjectNotFoundError(project_id)
    version_id = await self.repo.create_version(project_id, name, description, status)
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
    """从 LLM 最终输出 Markdown 中解析候选用例"""
    import re
    cases: list[dict[str, Any]] = []
    blocks = re.split(r'\n-{3,}\n', content)
    seen_titles: set[str] = set()
    for block in blocks:
      if not block.strip():
        continue
      title_match = re.search(r'\*\*标题\*\*\s*:\s*(.+)', block)
      if not title_match:
        continue
      title = title_match.group(1).strip()
      if not title or title in seen_titles:
        continue
      seen_titles.add(title)
      priority_raw = re.search(r'\*\*优先级\*\*\s*:\s*(.+)', block)
      priority = priority_raw.group(1).strip().upper() if priority_raw else 'P2'
      if priority not in ('P0', 'P1', 'P2', 'P3'):
        priority = 'P2'
      type_match = re.search(r'\*\*用例类型\*\*\s*:\s*(.+)', block)
      case_type = type_match.group(1).strip() if type_match else 'functional'
      pre_match = re.search(r'\*\*前置条件\*\*\s*:\s*(.*?)(?=\n\*\*|$)', block, re.DOTALL)
      steps_match = re.search(r'\*\*测试步骤\*\*\s*:\s*([\s\S]*?)(?=\n\*\*|$)', block)
      er_match = re.search(r'\*\*预期结果\*\*\s*:\s*([\s\S]*?)(?=\n\*\*|$)', block)
      tags_match = re.search(r'\*\*标签\*\*\s*:\s*(.+)', block)
      tags = [t.strip() for t in tags_match.group(1).split(',') if t.strip()] if tags_match else ['ai-generated']
      cases.append({
        'title': title,
        'priority': priority,
        'case_type': case_type,
        'preconditions': (pre_match.group(1).strip() if pre_match else ''),
        'steps': (steps_match.group(1).strip() if steps_match else ''),
        'expected_results': (er_match.group(1).strip() if er_match else ''),
        'tags': tags,
        'status': 'pending',
      })
    return cases

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

    # 创建 testing_cases 记录 + 桥接记录
    saved_count = 0
    for item in items:
      case_data = {
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
      case_id = await self.repo.create_case(**case_data)
      await self.repo.create_task_case_bridge(task_id, case_id)
      saved_count += 1

    # 更新任务生成计数
    await self.repo.update_generation_task(task_id, generated_count=saved_count)
    return saved_count

  async def get_case_stats(
    self, project_id: str | None = None,
  ) -> dict[str, Any]:
    """获取用例统计"""
    return await self.repo.count_cases_by_group(project_id=project_id)

  # ─── 配置检查 ──────────────────────────────────────

  async def check_config_status(self) -> dict[str, Any]:
    """检查配置状态（模型/提示词/行为配置是否完整）"""
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
    all_passed = True
    for key, (category, label) in required.items():
      if key in config_map and config_map[key].get("value", "").strip():
        items.append({
          "key": key, "label": label, "category": category,
          "status": "ok", "message": "已配置",
        })
      else:
        all_passed = False
        items.append({
          "key": key, "label": label, "category": category,
          "status": "missing", "message": "未配置",
        })

    return {"items": items, "all_passed": all_passed}
