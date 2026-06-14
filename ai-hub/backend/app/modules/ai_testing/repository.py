"""AI Testing 模块数据访问层"""

import json
import uuid
from datetime import datetime
from typing import Any

from app.common.core.database import MySQLConnection


class TestingRepo:
  """AI Testing Repository — 项目/成员/用例/生成任务/配置的 CRUD"""

  def __init__(self, db: MySQLConnection):
    self.db = db

  # ─── 项目 ─────────────────────────────────────────

  async def list_projects(
    self,
    status: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
  ) -> tuple[list[dict[str, Any]], int]:
    """获取项目列表（含用例数/成员数），返回 (items, total)"""
    where_parts: list[str] = []
    params: list[Any] = []

    if status:
      where_parts.append("p.status = ?")
      params.append(status)
    if keyword:
      where_parts.append("p.name LIKE ?")
      params.append(f"%{keyword}%")

    where_clause = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
    offset = (page - 1) * page_size

    count_sql = (
      f"SELECT COUNT(*) as cnt FROM testing_projects p {where_clause}"
    )
    cursor = await self.db.execute(count_sql, params)
    row = await cursor.fetchone()
    total = row["cnt"] if row else 0

    list_sql = (
      "SELECT p.id, p.name, p.description, p.status, p.created_at, p.updated_at, "
      "(SELECT COUNT(*) FROM testing_cases c WHERE c.project_id = p.id) as case_count, "
      "(SELECT COUNT(*) FROM testing_project_member_links l WHERE l.project_id = p.id) as member_count "
      f"FROM testing_projects p {where_clause} "
      "ORDER BY p.updated_at DESC LIMIT ? OFFSET ?"
    )
    cursor = await self.db.execute(list_sql, params + [page_size, offset])
    rows = await cursor.fetchall()
    return [dict(r) for r in rows], total

  async def get_project(self, project_id: str) -> dict[str, Any] | None:
    """获取单个项目详情"""
    cursor = await self.db.execute(
      "SELECT p.id, p.name, p.description, p.status, p.created_at, p.updated_at, "
      "(SELECT COUNT(*) FROM testing_cases c WHERE c.project_id = p.id) as case_count, "
      "(SELECT COUNT(*) FROM testing_project_member_links l WHERE l.project_id = p.id) as member_count "
      "FROM testing_projects p WHERE p.id = ?",
      (project_id,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None

  async def create_project(self, name: str, description: str, status: str) -> str:
    """创建项目，返回新 ID"""
    project_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await self.db.execute(
      "INSERT INTO testing_projects (id, name, description, status, created_at, updated_at) "
      "VALUES (?, ?, ?, ?, ?, ?)",
      (project_id, name, description, status, now, now),
    )
    await self.db.commit()
    return project_id

  async def update_project(self, project_id: str, **fields: Any) -> bool:
    """更新项目字段"""
    allowed = {"name", "description", "status"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
      return False
    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [project_id]
    cursor = await self.db.execute(
      f"UPDATE testing_projects SET {set_clause} WHERE id = ?", values
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def delete_project(self, project_id: str) -> bool:
    """删除项目"""
    cursor = await self.db.execute(
      "DELETE FROM testing_projects WHERE id = ?", (project_id,)
    )
    await self.db.commit()
    return cursor.rowcount > 0

  # ─── 项目成员 ────────────────────────────────────────

  async def list_all_members(self) -> list[dict[str, Any]]:
    """获取所有成员（独立模块，无项目关联）"""
    cursor = await self.db.execute(
      "SELECT id, name, role, created_at "
      "FROM testing_project_members ORDER BY created_at ASC"
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  async def add_member_standalone(self, name: str, role: str) -> str:
    """添加成员（独立模块，无项目关联），返回新 ID"""
    member_id = str(uuid.uuid4())
    await self.db.execute(
      "INSERT INTO testing_project_members (id, name, role, created_at) "
      "VALUES (?, ?, ?, ?)",
      (member_id, name, role, datetime.now().isoformat()),
    )
    await self.db.commit()
    return member_id

  async def list_members(self, project_id: str) -> list[dict[str, Any]]:
    """获取项目成员列表（多对多关联表）"""
    cursor = await self.db.execute(
      "SELECT m.id, m.name, m.role, m.created_at, m.project_id "
      "FROM testing_project_members m "
      "INNER JOIN testing_project_member_links l ON l.member_id = m.id "
      "WHERE l.project_id = ? ORDER BY m.created_at ASC",
      (project_id,),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  async def add_member(self, project_id: str, name: str, role: str) -> str:
    """添加成员到项目，返回新 ID（成员池 + 关联表）"""
    member_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    # 插入成员池（project_id 始终为 NULL）
    await self.db.execute(
      "INSERT INTO testing_project_members (id, name, role, created_at) "
      "VALUES (?, ?, ?, ?)",
      (member_id, name, role, now),
    )
    # 插入关联表
    await self.db.execute(
      "INSERT INTO testing_project_member_links (project_id, member_id, created_at) "
      "VALUES (?, ?, ?)",
      (project_id, member_id, now),
    )
    await self.db.commit()
    return member_id

  async def remove_member(self, member_id: str) -> bool:
    """移除成员（同时清理关联表）"""
    await self.db.execute(
      "DELETE FROM testing_project_member_links WHERE member_id = ?", (member_id,)
    )
    cursor = await self.db.execute(
      "DELETE FROM testing_project_members WHERE id = ?", (member_id,)
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def update_member_role(self, member_id: str, role: str) -> bool:
    """更新成员角色"""
    cursor = await self.db.execute(
      "UPDATE testing_project_members SET role = ? WHERE id = ?",
      (role, member_id),
    )
    await self.db.commit()
    return cursor.rowcount > 0

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
  ) -> tuple[list[dict[str, Any]], int]:
    """获取用例列表（支持多条件筛选+分页），返回 (items, total)"""
    where_parts: list[str] = []
    params: list[Any] = []

    if project_id:
      where_parts.append("tc.project_id = ?")
      params.append(project_id)
    if priority:
      where_parts.append("tc.priority = ?")
      params.append(priority)
    if case_type:
      where_parts.append("tc.case_type = ?")
      params.append(case_type)
    if status:
      where_parts.append("tc.status = ?")
      params.append(status)
    if version:
      where_parts.append("tc.version = ?")
      params.append(version)
    if keyword:
      where_parts.append("tc.title LIKE ?")
      params.append(f"%{keyword}%")

    where_clause = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
    offset = (page - 1) * page_size

    count_sql = (
      f"SELECT COUNT(*) as cnt FROM testing_cases tc {where_clause}"
    )
    cursor = await self.db.execute(count_sql, params)
    row = await cursor.fetchone()
    total = row["cnt"] if row else 0

    list_sql = (
      "SELECT tc.id, tc.project_id, p.name as project_name, "
      "tc.title, tc.version, tc.priority, tc.case_type, "
      "tc.preconditions, tc.steps, tc.expected_results, "
      "tc.tags, tc.status, tc.source, tc.ai_task_id, tc.author, "
      "tc.created_at, tc.updated_at "
      "FROM testing_cases tc "
      "LEFT JOIN testing_projects p ON tc.project_id = p.id "
      f"{where_clause} "
      "ORDER BY tc.updated_at DESC LIMIT ? OFFSET ?"
    )
    cursor = await self.db.execute(list_sql, params + [page_size, offset])
    rows = await cursor.fetchall()
    return [self._parse_case_row(dict(r)) for r in rows], total

  async def get_case(self, case_id: str) -> dict[str, Any] | None:
    """获取单个用例详情"""
    cursor = await self.db.execute(
      "SELECT tc.id, tc.project_id, p.name as project_name, "
      "tc.title, tc.version, tc.priority, tc.case_type, "
      "tc.preconditions, tc.steps, tc.expected_results, "
      "tc.tags, tc.status, tc.source, tc.ai_task_id, tc.author, "
      "tc.created_at, tc.updated_at "
      "FROM testing_cases tc "
      "LEFT JOIN testing_projects p ON tc.project_id = p.id "
      "WHERE tc.id = ?",
      (case_id,),
    )
    row = await cursor.fetchone()
    return self._parse_case_row(dict(row)) if row else None

  async def batch_insert_cases(self, cases: list[dict[str, Any]]) -> list[str]:
    """批量插入测试用例（单次 INSERT，消除 N+1）"""
    if not cases:
      return []
    ids, values, phs = [], [], []
    now = datetime.now().isoformat()
    for case in cases:
      cid = str(uuid.uuid4())
      ids.append(cid)
      phs.append("(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
      values.extend([cid, case.get("project_id"), case.get("title",""),
        case.get("version",""), case.get("priority","P2"),
        case.get("case_type","functional"), case.get("preconditions",""),
        case.get("steps",""), case.get("expected_results",""),
        json.dumps(case.get("tags",[]),ensure_ascii=False),
        case.get("status","draft"), case.get("source","manual"),
        case.get("ai_task_id"), case.get("author",""), now, now])
    sql = ("INSERT INTO testing_cases "
      "(id,project_id,title,version,priority,case_type,"
      "preconditions,steps,expected_results,tags,status,"
      "source,ai_task_id,author,created_at,updated_at) VALUES "
      + ",".join(phs))
    await self.db.execute(sql, tuple(values))
    await self.db.commit()
    return ids

  async def batch_insert_bridges(self, task_id: str, case_ids: list[str]) -> None:
    """批量创建任务-用例桥接记录（单次 INSERT）"""
    if not case_ids:
      return
    values, phs = [], []
    now = datetime.now().isoformat()
    for cid in case_ids:
      phs.append("(?,?,?,?,?)")
      values.extend([str(uuid.uuid4()), task_id, cid, "adopted", now])
    sql = ("INSERT INTO testing_task_generated_cases "
      "(id,task_id,case_id,status,created_at) VALUES " + ",".join(phs))
    await self.db.execute(sql, tuple(values))
    await self.db.commit()

  async def create_case(self, **fields: Any) -> str:
    """创建测试用例，返回新 ID"""
    case_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    tags_json = json.dumps(fields.get("tags", []), ensure_ascii=False)

    await self.db.execute(
      "INSERT INTO testing_cases "
      "(id, project_id, title, version, priority, case_type, "
      "preconditions, steps, expected_results, tags, status, "
      "source, ai_task_id, author, created_at, updated_at) "
      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (
        case_id,
        fields.get("project_id"),
        fields.get("title", ""),
        fields.get("version", ""),
        fields.get("priority", "P2"),
        fields.get("case_type", "functional"),
        fields.get("preconditions", ""),
        fields.get("steps", ""),
        fields.get("expected_results", ""),
        tags_json,
        fields.get("status", "draft"),
        fields.get("source", "manual"),
        fields.get("ai_task_id"),
        fields.get("author", ""),
        now,
        now,
      ),
    )
    await self.db.commit()
    return case_id

  async def update_case(self, case_id: str, **fields: Any) -> bool:
    """更新测试用例"""
    allowed = {
      "project_id", "title", "version", "priority", "case_type",
      "preconditions", "steps", "expected_results", "status", "author",
    }
    updates: dict[str, Any] = {}
    for k, v in fields.items():
      if k in allowed and v is not None:
        updates[k] = v
    if "tags" in fields and fields["tags"] is not None:
      updates["tags"] = json.dumps(fields["tags"], ensure_ascii=False)

    if not updates:
      return False

    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [case_id]
    cursor = await self.db.execute(
      f"UPDATE testing_cases SET {set_clause} WHERE id = ?", values
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def delete_case(self, case_id: str) -> bool:
    """删除用例"""
    cursor = await self.db.execute(
      "DELETE FROM testing_cases WHERE id = ?", (case_id,)
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def batch_delete_cases(self, ids: list[str]) -> int:
    """批量删除用例，返回删除数"""
    if not ids:
      return 0
    placeholders = ", ".join("?" for _ in ids)
    cursor = await self.db.execute(
      f"DELETE FROM testing_cases WHERE id IN ({placeholders})", ids
    )
    await self.db.commit()
    return cursor.rowcount

  # ─── 生成任务 ────────────────────────────────────────

  async def create_generation_task(self, **fields: Any) -> str:
    """创建生成任务，返回新 ID"""
    task_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await self.db.execute(
      "INSERT INTO testing_generation_tasks "
      "(id, project_id, input_text, requirement_title, file_path, file_type, file_name, "
      "model, status, generated_count, created_at, updated_at) "
      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (
        task_id,
        fields.get("project_id"),
        fields.get("input_text", ""),
        fields.get("requirement_title", ""),
        fields.get("file_path"),
        fields.get("file_type"),
        fields.get("file_name"),
        fields.get("model", ""),
        "pending",
        0,
        now,
        now,
      ),
    )
    await self.db.commit()
    return task_id

  async def get_generation_task(self, task_id: str) -> dict[str, Any] | None:
    """获取生成任务"""
    cursor = await self.db.execute(
      "SELECT id, project_id, input_text, requirement_title, file_path, file_type, file_name, "
      "model, status, generated_count, error_message, created_at, updated_at "
      "FROM testing_generation_tasks WHERE id = ?",
      (task_id,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None

  async def update_generation_task(
    self, task_id: str, **fields: Any
  ) -> bool:
    """更新生成任务"""
    allowed = {"status", "generated_count", "error_message"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
      return False
    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [task_id]
    cursor = await self.db.execute(
      f"UPDATE testing_generation_tasks SET {set_clause} WHERE id = ?",
      values,
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def list_generation_tasks(
    self,
    project_id: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
  ) -> tuple[list[dict[str, Any]], int]:
    """获取生成任务列表（支持筛选+分页），返回 (items, total)"""
    where_parts: list[str] = []
    params: list[Any] = []

    if project_id:
      where_parts.append("t.project_id = ?")
      params.append(project_id)
    if status:
      where_parts.append("t.status = ?")
      params.append(status)
    if keyword:
      where_parts.append("(t.requirement_title LIKE ? OR t.input_text LIKE ?)")
      params.append(f"%{keyword}%")
      params.append(f"%{keyword}%")

    where_clause = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
    offset = (page - 1) * page_size

    count_sql = f"SELECT COUNT(*) as cnt FROM testing_generation_tasks t {where_clause}"
    cursor = await self.db.execute(count_sql, params)
    row = await cursor.fetchone()
    total = row["cnt"] if row else 0

    list_sql = (
      "SELECT t.id, t.project_id, p.name as project_name, "
      "t.requirement_title, t.input_text, t.file_name, t.file_type, "
      "t.model, t.status, t.generated_count, t.error_message, "
      "t.created_at, t.updated_at "
      "FROM testing_generation_tasks t "
      "LEFT JOIN testing_projects p ON t.project_id = p.id "
      f"{where_clause} ORDER BY t.created_at DESC LIMIT ? OFFSET ?"
    )
    cursor = await self.db.execute(list_sql, params + [page_size, offset])
    rows = await cursor.fetchall()
    return [dict(r) for r in rows], total

  async def delete_generation_task(self, task_id: str) -> bool:
    """删除生成任务及其所有阶段结果"""
    await self.db.execute(
      "DELETE FROM testing_generation_results WHERE task_id = ?",
      (task_id,),
    )
    cursor = await self.db.execute(
      "DELETE FROM testing_generation_tasks WHERE id = ?",
      (task_id,),
    )
    await self.db.commit()
    return cursor.rowcount > 0

  # ─── 生成结果 ────────────────────────────────────────

  async def save_generation_result(
    self, task_id: str, stage: str, content: str
  ) -> str:
    """保存生成阶段结果，返回新 ID"""
    result_id = str(uuid.uuid4())
    await self.db.execute(
      "INSERT INTO testing_generation_results "
      "(id, task_id, stage, content, created_at) VALUES (?, ?, ?, ?, ?)",
      (result_id, task_id, stage, content, datetime.now().isoformat()),
    )
    await self.db.commit()
    return result_id

  async def list_generation_results(
    self, task_id: str
  ) -> list[dict[str, Any]]:
    """获取任务的所有阶段结果"""
    cursor = await self.db.execute(
      "SELECT id, task_id, stage, content, created_at "
      "FROM testing_generation_results WHERE task_id = ? "
      "ORDER BY created_at ASC",
      (task_id,),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  # ─── 生成候选用例项 ──────────────────────────────────

  async def save_generated_case_items(
    self, task_id: str, items: list[dict[str, Any]]
  ) -> list[str]:
    """批量保存解析后的候选用例项，先清空旧数据再插入"""
    # 清空旧数据
    await self.db.execute(
      "DELETE FROM testing_generated_case_items WHERE task_id = ?", (task_id,)
    )
    # 批量插入（一次 executemany 替代 N+1）
    if not items:
      return []
    ids: list[str] = []
    values: list[Any] = []
    placeholders: list[str] = []
    for i, item in enumerate(items):
      case_id = str(uuid.uuid4())
      ids.append(case_id)
      tags_json = json.dumps(item.get("tags", []), ensure_ascii=False)
      now = datetime.now().isoformat()
      placeholders.append(
        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
      )
      values.extend([
        case_id, task_id,
        item.get("title", ""),
        item.get("priority", "P2"),
        item.get("case_type", "functional"),
        item.get("preconditions", ""),
        item.get("steps", ""),
        item.get("expected_results", ""),
        tags_json,
        item.get("status", "pending"),
        i,
        now,
      ])
    await self.db.execute(
      "INSERT INTO testing_generated_case_items "
      "(id, task_id, title, priority, case_type, preconditions, steps, "
      "expected_results, tags, status, sort_order, created_at) "
      "VALUES " + ",".join(placeholders),
      tuple(values),
    )
    await self.db.commit()
    return ids

  async def list_task_generated_cases(
    self, task_id: str,
    page: int = 1, page_size: int = 20,
    status: str | None = None,
  ) -> tuple[list[dict[str, Any]], int]:
    """获取任务生成的候选用例列表（分页+状态筛选）"""
    where_parts: list[str] = ["task_id = ?"]
    params: list[Any] = [task_id]
    if status:
      where_parts.append("status = ?")
      params.append(status)
    where_clause = f"WHERE {' AND '.join(where_parts)}"
    offset = (page - 1) * page_size

    count_cursor = await self.db.execute(
      f"SELECT COUNT(*) as cnt FROM testing_generated_case_items {where_clause}",
      params,
    )
    row = await count_cursor.fetchone()
    total = row["cnt"] if row else 0

    cursor = await self.db.execute(
      f"SELECT id, task_id, title, priority, case_type, preconditions, steps, "
      f"expected_results, tags, status, sort_order, created_at "
      f"FROM testing_generated_case_items {where_clause} "
      f"ORDER BY sort_order ASC LIMIT ? OFFSET ?",
      params + [page_size, offset],
    )
    rows = await cursor.fetchall()
    return [self._parse_case_item_row(dict(r)) for r in rows], total

  async def batch_update_task_cases(
    self, case_ids: list[str], status: str
  ) -> int:
    """批量更新候选用例状态（adopted/discarded/pending）"""
    if not case_ids:
      return 0
    placeholders = ", ".join("?" for _ in case_ids)
    cursor = await self.db.execute(
      f"UPDATE testing_generated_case_items SET status = ? "
      f"WHERE id IN ({placeholders})",
      [status] + case_ids,
    )
    await self.db.commit()
    return cursor.rowcount

  async def clear_task_generated_cases(self, task_id: str) -> None:
    """清除任务的候选用例（重新解析前调用）"""
    await self.db.execute(
      "DELETE FROM testing_generated_case_items WHERE task_id = ?",
      (task_id,),
    )
    await self.db.commit()

  async def create_task_case_bridge(
    self, task_id: str, case_id: str, status: str = "adopted"
  ) -> str:
    """创建任务-用例桥接记录，返回新 ID"""
    bridge_id = str(uuid.uuid4())
    await self.db.execute(
      "INSERT INTO testing_task_generated_cases "
      "(id, task_id, case_id, status, created_at) VALUES (?, ?, ?, ?, ?)",
      (bridge_id, task_id, case_id, status, datetime.now().isoformat()),
    )
    await self.db.commit()
    return bridge_id

  async def list_task_case_bridges(
    self, task_id: str, case_ids: list[str] | None = None
  ) -> list[dict[str, Any]]:
    """获取任务-用例桥接记录"""
    if case_ids:
      placeholders = ", ".join("?" for _ in case_ids)
      cursor = await self.db.execute(
        f"SELECT id, task_id, case_id, status, created_at "
        f"FROM testing_task_generated_cases "
        f"WHERE task_id = ? AND case_id IN ({placeholders})",
        [task_id] + case_ids,
      )
    else:
      cursor = await self.db.execute(
        "SELECT id, task_id, case_id, status, created_at "
        "FROM testing_task_generated_cases WHERE task_id = ?",
        (task_id,),
      )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  async def task_has_saved_cases(self, task_id: str) -> bool:
    """检查任务是否已保存过用例"""
    cursor = await self.db.execute(
      "SELECT COUNT(*) as cnt FROM testing_task_generated_cases WHERE task_id = ?",
      (task_id,),
    )
    row = await cursor.fetchone()
    return bool(row and row.get("cnt", 0) > 0)

  async def get_generation_stats(self) -> dict[str, Any]:
    """获取生成统计"""
    cursor = await self.db.execute(
      "SELECT "
      "COUNT(*) as total_tasks, "
      "COALESCE(CAST(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS SIGNED), 0) as completed_tasks, "
      "COALESCE(CAST(SUM(generated_count) AS SIGNED), 0) as total_cases "
      "FROM testing_generation_tasks"
    )
    row = await cursor.fetchone()
    return {
      "total_tasks": int(row["total_tasks"]) if row else 0,
      "completed_tasks": int(row["completed_tasks"]) if row else 0,
      "total_cases": int(row["total_cases"]) if row else 0,
    }

  # ─── 配置 ──────────────────────────────────────────

  async def list_config(
    self, category: str | None = None
  ) -> list[dict[str, Any]]:
    """获取配置列表"""
    if category:
      cursor = await self.db.execute(
        "SELECT id, `key`, value, category, description, updated_at "
        "FROM testing_config WHERE category = ? ORDER BY `key` ASC",
        (category,),
      )
    else:
      cursor = await self.db.execute(
        "SELECT id, `key`, value, category, description, updated_at "
        "FROM testing_config ORDER BY category ASC, `key` ASC"
      )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  async def get_config_value(self, key: str) -> str | None:
    """获取单个配置值"""
    cursor = await self.db.execute(
      "SELECT value FROM testing_config WHERE `key` = ?", (key,)
    )
    row = await cursor.fetchone()
    return row["value"] if row else None

  async def upsert_config(
    self, key: str, value: str, category: str, description: str = ""
  ) -> None:
    """插入或更新配置项"""
    config_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await self.db.execute(
      "INSERT INTO testing_config (id, `key`, value, category, description, updated_at) "
      "VALUES (?, ?, ?, ?, ?, ?) AS new "
      "ON DUPLICATE KEY UPDATE "
      "  value = new.value, "
      "  category = new.category, "
      "  description = new.description, "
      "  updated_at = new.updated_at",
      (config_id, key, value, category, description, now),
    )
    await self.db.commit()

  async def batch_upsert_config(
    self, placeholders: list[str], values: tuple
  ) -> None:
    """批量 upsert 配置（一次 executemany 替代 N+1）"""
    await self.db.execute(
      "INSERT INTO testing_config (id, `key`, value, category, description, updated_at) "
      "VALUES " + ",".join(placeholders) + " AS new "
      "ON DUPLICATE KEY UPDATE "
      "  value = new.value, "
      "  category = new.category, "
      "  description = new.description, "
      "  updated_at = new.updated_at",
      values,
    )
    await self.db.commit()

  async def create_attachment(
    self, case_id: str, file_name: str, file_path: str,
    file_size: int = 0, file_type: str = "", uploaded_by: str = ""
  ) -> str:
    """创建附件，返回新 ID"""
    attach_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await self.db.execute(
      "INSERT INTO testing_case_attachments "
      "(id, case_id, file_name, file_path, file_size, file_type, uploaded_by, created_at) "
      "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
      (attach_id, case_id, file_name, file_path, file_size, file_type, uploaded_by, now),
    )
    await self.db.commit()
    return attach_id

  async def get_attachment(self, attachment_id: str) -> dict[str, Any] | None:
    """获取附件详情"""
    cursor = await self.db.execute(
      "SELECT id, case_id, file_name, file_path, file_size, file_type, uploaded_by, created_at "
      "FROM testing_case_attachments WHERE id = ?",
      (attachment_id,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None

  async def list_attachments(self, case_id: str) -> list[dict[str, Any]]:
    """获取用例的附件列表"""
    cursor = await self.db.execute(
      "SELECT id, case_id, file_name, file_path, file_size, file_type, uploaded_by, created_at "
      "FROM testing_case_attachments WHERE case_id = ? ORDER BY created_at ASC",
      (case_id,),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  async def delete_attachment(self, attachment_id: str) -> bool:
    """删除附件"""
    cursor = await self.db.execute(
      "DELETE FROM testing_case_attachments WHERE id = ?", (attachment_id,)
    )
    await self.db.commit()
    return cursor.rowcount > 0

  # ─── 用例评论 ────────────────────────────────────────

  async def create_comment(
    self, case_id: str, content: str, author: str = ""
  ) -> str:
    """创建评论，返回新 ID"""
    comment_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await self.db.execute(
      "INSERT INTO testing_case_comments "
      "(id, case_id, content, author, created_at, updated_at) "
      "VALUES (?, ?, ?, ?, ?, ?)",
      (comment_id, case_id, content, author, now, now),
    )
    await self.db.commit()
    return comment_id

  async def get_comment(self, comment_id: str) -> dict[str, Any] | None:
    """获取评论详情"""
    cursor = await self.db.execute(
      "SELECT id, case_id, content, author, created_at, updated_at "
      "FROM testing_case_comments WHERE id = ?",
      (comment_id,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None

  async def list_comments(self, case_id: str) -> list[dict[str, Any]]:
    """获取用例的评论列表"""
    cursor = await self.db.execute(
      "SELECT id, case_id, content, author, created_at, updated_at "
      "FROM testing_case_comments WHERE case_id = ? ORDER BY created_at ASC",
      (case_id,),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  async def update_comment(self, comment_id: str, content: str) -> bool:
    """更新评论内容"""
    now = datetime.now().isoformat()
    cursor = await self.db.execute(
      "UPDATE testing_case_comments SET content = ?, updated_at = ? WHERE id = ?",
      (content, now, comment_id),
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def delete_comment(self, comment_id: str) -> bool:
    """删除评论"""
    cursor = await self.db.execute(
      "DELETE FROM testing_case_comments WHERE id = ?", (comment_id,)
    )
    await self.db.commit()
    return cursor.rowcount > 0

  # ─── 操作日志 ────────────────────────────────────────

  async def create_operation_log(
    self, entity_type: str, entity_id: str, action: str,
    operator: str = "", detail: str = "{}"
  ) -> str:
    """创建操作日志，返回新 ID"""
    log_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await self.db.execute(
      "INSERT INTO testing_operation_logs "
      "(id, entity_type, entity_id, action, operator, detail, created_at) "
      "VALUES (?, ?, ?, ?, ?, ?, ?)",
      (log_id, entity_type, entity_id, action, operator, detail, now),
    )
    await self.db.commit()
    return log_id

  async def batch_create_operation_logs(
    self, entity_type: str, entity_ids: list[str], action: str,
    operator: str = "", detail: str = "{}"
  ) -> None:
    """批量创建操作日志（一次 INSERT 替代 N+1）"""
    if not entity_ids:
      return
    values, phs = [], []
    now = datetime.now().isoformat()
    for eid in entity_ids:
      phs.append("(?,?,?,?,?,?,?)")
      values.extend([str(uuid.uuid4()), entity_type, eid, action, operator, detail, now])
    sql = ("INSERT INTO testing_operation_logs "
      "(id, entity_type, entity_id, action, operator, detail, created_at) VALUES " + ",".join(phs))
    await self.db.execute(sql, tuple(values))
    await self.db.commit()

  async def list_operation_logs_by_entity(
    self, entity_type: str, entity_id: str,
    page: int = 1, page_size: int = 50,
  ) -> tuple[list[dict[str, Any]], int]:
    """获取实体的操作日志列表"""
    offset = (page - 1) * page_size
    count_cursor = await self.db.execute(
      "SELECT COUNT(*) as cnt FROM testing_operation_logs "
      "WHERE entity_type = ? AND entity_id = ?",
      (entity_type, entity_id),
    )
    row = await count_cursor.fetchone()
    total = row["cnt"] if row else 0

    cursor = await self.db.execute(
      "SELECT id, entity_type, entity_id, action, operator, detail, created_at "
      "FROM testing_operation_logs WHERE entity_type = ? AND entity_id = ? "
      "ORDER BY created_at DESC LIMIT ? OFFSET ?",
      (entity_type, entity_id, page_size, offset),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows], total

  async def list_recent_activities(self, limit: int = 10) -> list[dict[str, Any]]:
    """获取全局近期活动"""
    cursor = await self.db.execute(
      "SELECT id, entity_type, entity_id, action, operator, detail, created_at "
      "FROM testing_operation_logs ORDER BY created_at DESC LIMIT ?",
      (limit,),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  async def list_operation_logs_by_project(
    self, project_id: str, page: int = 1, page_size: int = 50
  ) -> tuple[list[dict[str, Any]], int]:
    """获取项目的所有操作日志"""
    offset = (page - 1) * page_size
    count_cursor = await self.db.execute(
      "SELECT COUNT(*) as cnt FROM testing_operation_logs "
      "WHERE entity_id = ?",
      (project_id,),
    )
    row = await count_cursor.fetchone()
    total = row["cnt"] if row else 0

    cursor = await self.db.execute(
      "SELECT id, entity_type, entity_id, action, operator, detail, created_at "
      "FROM testing_operation_logs WHERE entity_id = ? "
      "ORDER BY created_at DESC LIMIT ? OFFSET ?",
      (project_id, page_size, offset),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows], total

  # ─── 项目版本 ────────────────────────────────────────

  async def list_all_versions(self) -> list[dict[str, Any]]:
    """获取所有版本（独立模块，无项目关联）"""
    cursor = await self.db.execute(
      "SELECT id, name, description, status, pass_rate, created_at, updated_at "
      "FROM testing_project_versions ORDER BY created_at DESC"
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  async def create_version_standalone(
    self, name: str, description: str = "",
    status: str = "active", pass_rate: float = 0.0
  ) -> str:
    """创建版本（独立模块，无 project_id/due_date），返回新 ID"""
    version_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await self.db.execute(
      "INSERT INTO testing_project_versions "
      "(id, name, description, status, pass_rate, created_at, updated_at) "
      "VALUES (?, ?, ?, ?, ?, ?, ?)",
      (version_id, name, description, status, pass_rate, now, now),
    )
    await self.db.commit()
    return version_id

  async def create_version(
    self, project_id: str, name: str, description: str = "",
    status: str = "active", pass_rate: float = 0.0
  ) -> str:
    """创建版本，返回新 ID"""
    version_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await self.db.execute(
      "INSERT INTO testing_project_versions "
      "(id, project_id, name, description, status, pass_rate, created_at, updated_at) "
      "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
      (version_id, project_id, name, description, status, pass_rate, now, now),
    )
    await self.db.commit()
    return version_id

  async def get_version(self, version_id: str) -> dict[str, Any] | None:
    """获取版本详情"""
    cursor = await self.db.execute(
      "SELECT id, project_id, name, description, status, pass_rate, created_at, updated_at "
      "FROM testing_project_versions WHERE id = ?",
      (version_id,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None

  async def list_versions(self, project_id: str) -> list[dict[str, Any]]:
    """获取项目的版本列表"""
    cursor = await self.db.execute(
      "SELECT id, project_id, name, description, status, pass_rate, created_at, updated_at "
      "FROM testing_project_versions WHERE project_id = ? ORDER BY created_at DESC",
      (project_id,),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]

  async def update_version(self, version_id: str, **fields: Any) -> bool:
    """更新版本"""
    allowed = {"name", "description", "status", "pass_rate"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
      return False
    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [version_id]
    cursor = await self.db.execute(
      f"UPDATE testing_project_versions SET {set_clause} WHERE id = ?", values
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def delete_version(self, version_id: str) -> bool:
    """删除版本"""
    cursor = await self.db.execute(
      "DELETE FROM testing_project_versions WHERE id = ?", (version_id,)
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def link_version_to_project(self, version_id: str, project_id: str) -> bool:
    """关联版本到项目（设置 project_id）"""
    cursor = await self.db.execute(
      "UPDATE testing_project_versions SET project_id = ? WHERE id = ?",
      (project_id, version_id),
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def link_member_to_project(self, member_id: str, project_id: str) -> bool:
    """关联成员到项目（多对多关联表）"""
    try:
      await self.db.execute(
        "INSERT INTO testing_project_member_links (project_id, member_id) VALUES (?, ?)",
        (project_id, member_id),
      )
      await self.db.commit()
      return True
    except Exception:
      return False

  async def unlink_member_from_project(self, member_id: str, project_id: str) -> bool:
    """从项目中移除成员关联"""
    cursor = await self.db.execute(
      "DELETE FROM testing_project_member_links WHERE project_id = ? AND member_id = ?",
      (project_id, member_id),
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def get_dashboard_stats(self) -> dict[str, Any]:
    """获取仪表盘统计数据"""
    # 项目数、用例数、成员数
    cursor = await self.db.execute(
      "SELECT "
      "COUNT(DISTINCT p.id) as project_count, "
      "COALESCE(CAST(SUM(c.case_count) AS SIGNED), 0) as total_cases, "
      "COALESCE(CAST(SUM(m.member_count) AS SIGNED), 0) as member_count "
      "FROM testing_projects p "
      "LEFT JOIN (SELECT project_id, COUNT(*) as case_count FROM testing_cases GROUP BY project_id) c ON p.id = c.project_id "
      "LEFT JOIN (SELECT project_id, COUNT(*) as member_count FROM testing_project_member_links GROUP BY project_id) m ON p.id = m.project_id"
    )
    row = await cursor.fetchone()
    project_count = int(row["project_count"]) if row else 0
    total_cases = int(row["total_cases"]) if row else 0
    member_count = int(row["member_count"]) if row else 0

    # 进行中的版本数
    cursor = await self.db.execute(
      "SELECT COUNT(*) as cnt FROM testing_project_versions WHERE status = 'active'"
    )
    ver_row = await cursor.fetchone()
    active_versions = int(ver_row["cnt"]) if ver_row else 0

    return {
      "project_count": project_count,
      "total_cases": total_cases,
      "member_count": member_count,
      "active_versions": active_versions,
    }

  # ─── 行解析辅助 ─────────────────────────────────────

  @staticmethod
  def _parse_case_row(row: dict[str, Any]) -> dict[str, Any]:
    """解析用例行数据，JSON 反序列化 tags"""
    if "tags" in row and isinstance(row["tags"], str):
      try:
        row["tags"] = json.loads(row["tags"])
      except (json.JSONDecodeError, TypeError):
        row["tags"] = []
    return row

  @staticmethod
  def _parse_case_item_row(row: dict[str, Any]) -> dict[str, Any]:
    """解析生成候选用例行，JSON 反序列化 tags"""
    if "tags" in row and isinstance(row["tags"], str):
      try:
        row["tags"] = json.loads(row["tags"])
      except (json.JSONDecodeError, TypeError):
        row["tags"] = []
    return row

  # ─── 统计 ─────────────────────────────────────────────

  async def count_cases_by_group(
    self, project_id: str | None = None,
  ) -> dict[str, Any]:
    """按分组统计用例数量（合并查询，减少 DB 往返）"""
    where = ""
    params: list[Any] = []
    if project_id:
      where = "WHERE project_id = ?"
      params.append(project_id)

    # 单次查询：总数 + 按优先级统计
    cursor = await self.db.execute(
      f"""SELECT COUNT(*) as total,
        SUM(CASE WHEN priority='P0' THEN 1 ELSE 0 END) as p0,
        SUM(CASE WHEN priority='P1' THEN 1 ELSE 0 END) as p1,
        SUM(CASE WHEN priority='P2' THEN 1 ELSE 0 END) as p2,
        SUM(CASE WHEN priority='P3' THEN 1 ELSE 0 END) as p3
      FROM testing_cases {where}""", params
    )
    row = await cursor.fetchone() or {}
    total = row.get('total', 0)
    by_priority = {}
    for p in ('P0','P1','P2','P3'):
      c = row.get(p.lower(), 0) or 0
      if c: by_priority[p] = c

    # 按类型统计
    cursor = await self.db.execute(
      f"SELECT case_type, COUNT(*) as cnt FROM testing_cases {where} GROUP BY case_type",
      params,
    )
    rows = await cursor.fetchall()
    by_type = {r["case_type"]: r["cnt"] for r in rows}

    # 按状态统计
    cursor = await self.db.execute(
      f"SELECT status, COUNT(*) as cnt FROM testing_cases {where} GROUP BY status",
      params,
    )
    rows = await cursor.fetchall()
    by_status = {r["status"]: r["cnt"] for r in rows}

    return {
      "total": total,
      "by_priority": by_priority,
      "by_type": by_type,
      "by_status": by_status,
    }

  # ─── 用例评审 ──────────────────────────────────────

  async def list_reviews(
    self, project_id: str | None = None, status: str | None = None,
    keyword: str | None = None, page: int = 1, page_size: int = 20,
  ) -> tuple[list[dict], int]:
    conditions = []
    params: list[str | int] = []
    if project_id:
      conditions.append("r.project_id = ?"); params.append(project_id)
    if status:
      conditions.append("r.status = ?"); params.append(status)
    if keyword:
      conditions.append("r.title LIKE ?"); params.append(f"%{keyword}%")
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    cursor = await self.db.execute(f"SELECT COUNT(*) as cnt FROM testing_reviews r {where}", params)
    total = (await cursor.fetchone() or {}).get("cnt", 0)

    cursor = await self.db.execute(
      f"""SELECT r.*, (SELECT COUNT(*) FROM testing_review_cases rc WHERE rc.review_id = r.id) as case_count,
         (SELECT COUNT(*) FROM testing_review_reviewers rv WHERE rv.review_id = r.id) as reviewer_count
      FROM testing_reviews r {where} ORDER BY r.created_at DESC LIMIT ? OFFSET ?""",
      params + [page_size, (page - 1) * page_size],
    )
    items = await cursor.fetchall() or []
    return items, total

  async def get_review(self, review_id: str) -> dict | None:
    cursor = await self.db.execute(
      "SELECT r.*, (SELECT COUNT(*) FROM testing_review_cases rc WHERE rc.review_id = r.id) as case_count FROM testing_reviews r WHERE r.id = ?",
      (review_id,),
    )
    return await cursor.fetchone()

  async def create_review(self, id: str, project_id: str | None, title: str, description: str, priority: str, due_date: str | None, creator: str) -> str:
    await self.db.execute(
      "INSERT INTO testing_reviews (id, project_id, title, description, priority, due_date, creator) VALUES (?, ?, ?, ?, ?, ?, ?)",
      (id, project_id, title, description, priority, due_date, creator),
    )
    return id

  async def update_review(self, review_id: str, **fields: Any) -> bool:
    if not fields: return False
    pairs = [f"{k} = ?" for k in fields]
    vals = list(fields.values()) + [review_id]
    await self.db.execute(f"UPDATE testing_reviews SET {', '.join(pairs)} WHERE id = ?", vals)
    return True

  async def delete_review(self, review_id: str) -> bool:
    await self.db.execute("DELETE FROM testing_reviews WHERE id = ?", (review_id,))
    await self.db.execute("DELETE FROM testing_review_cases WHERE review_id = ?", (review_id,))
    await self.db.execute("DELETE FROM testing_review_reviewers WHERE review_id = ?", (review_id,))
    return True

  async def add_review_cases(self, review_id: str, case_ids: list[str]) -> None:
    import uuid
    for cid in case_ids:
      await self.db.execute(
        "INSERT IGNORE INTO testing_review_cases (id, review_id, case_id) VALUES (?, ?, ?)",
        (uuid.uuid4().hex, review_id, cid),
      )

  async def list_review_cases(self, review_id: str) -> list[dict]:
    cursor = await self.db.execute(
      "SELECT rc.*, c.title as case_title, c.priority as case_priority, "
      "c.preconditions, c.steps, c.expected_results, c.case_type "
      "FROM testing_review_cases rc LEFT JOIN testing_cases c ON rc.case_id = c.id "
      "WHERE rc.review_id = ? ORDER BY rc.created_at",
      (review_id,),
    )
    return await cursor.fetchall() or []

  async def update_review_case(self, review_case_id: str, comment: str | None = None, status: str | None = None) -> bool:
    fields = {}
    if comment is not None: fields["comment"] = comment
    if status is not None: fields["status"] = status
    if not fields: return False
    pairs = [f"{k} = ?" for k in fields]
    vals = list(fields.values()) + [review_case_id]
    await self.db.execute(f"UPDATE testing_review_cases SET {', '.join(pairs)} WHERE id = ?", vals)
    return True

  async def add_review_reviewers(self, review_id: str, reviewer_ids: list[str], member_names: dict[str, str]) -> None:
    import uuid
    for mid in reviewer_ids:
      name = member_names.get(mid, "")
      await self.db.execute(
        "INSERT IGNORE INTO testing_review_reviewers (id, review_id, member_id, name) VALUES (?, ?, ?, ?)",
        (uuid.uuid4().hex, review_id, mid, name),
      )

  async def list_review_reviewers(self, review_id: str) -> list[dict]:
    cursor = await self.db.execute(
      "SELECT * FROM testing_review_reviewers WHERE review_id = ? ORDER BY created_at",
      (review_id,),
    )
    return await cursor.fetchall() or []

  async def get_review_stats(self) -> dict[str, int]:
    cursor = await self.db.execute(
      "SELECT status, COUNT(*) as cnt FROM testing_reviews GROUP BY status"
    )
    rows = await cursor.fetchall() or []
    return {r["status"]: r["cnt"] for r in rows}

  # ─── AI 评测师 ─────────────────────────────────────

  async def create_ai_tester_session(self, id: str, name: str, model: str) -> str:
    await self.db.execute(
      "INSERT INTO testing_ai_tester_sessions (id, name, model) VALUES (?, ?, ?)",
      (id, name, model),
    )
    await self.db.commit()
    return id

  async def list_ai_tester_sessions(self) -> list[dict]:
    cursor = await self.db.execute(
      "SELECT * FROM testing_ai_tester_sessions ORDER BY updated_at DESC",
    )
    return await cursor.fetchall() or []

  async def delete_ai_tester_session(self, session_id: str) -> bool:
    await self.db.execute("DELETE FROM testing_ai_tester_sessions WHERE id = ?", (session_id,))
    await self.db.execute("DELETE FROM testing_ai_tester_messages WHERE session_id = ?", (session_id,))
    await self.db.commit()
    return True

  async def create_ai_tester_message(self, id: str, session_id: str, role: str, content: str) -> str:
    await self.db.execute(
      "INSERT INTO testing_ai_tester_messages (id, session_id, role, content) VALUES (?, ?, ?, ?)",
      (id, session_id, role, content),
    )
    await self.db.commit()
    return id

  async def list_ai_tester_messages(self, session_id: str, offset: int = 0, limit: int = 50) -> tuple[list[dict], int]:
    """获取消息列表（分页），返回 (消息列表, 总条数)"""
    cursor = await self.db.execute(
      "SELECT COUNT(*) as cnt FROM testing_ai_tester_messages WHERE session_id = ?",
      (session_id,),
    )
    row = await cursor.fetchone()
    total = row["cnt"] if row else 0

    cursor = await self.db.execute(
      "SELECT * FROM testing_ai_tester_messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
      (session_id, limit, offset),
    )
    rows = await cursor.fetchall() or []
    # 逆序变时间正序，前端直接追加/前置显示
    rows.reverse()
    return rows, total

  async def update_ai_tester_message_rating(self, message_id: str, rating: str | None) -> bool:
    """更新 AI 评测师消息评分"""
    cursor = await self.db.execute(
      "UPDATE testing_ai_tester_messages SET rating = ? WHERE id = ?",
      (rating, message_id),
    )
    await self.db.commit()
    return cursor.rowcount > 0

  async def count_ai_tester_messages(self, session_id: str) -> int:
    cursor = await self.db.execute(
      "SELECT COUNT(*) as cnt FROM testing_ai_tester_messages WHERE session_id = ?",
      (session_id,),
    )
    row = await cursor.fetchone()
    return row["cnt"] if row else 0

  async def update_session_message_count(self, session_id: str, count: int) -> None:
    await self.db.execute(
      "UPDATE testing_ai_tester_sessions SET message_count = ? WHERE id = ?", (count, session_id),
    )
    await self.db.commit()

  # ─── 测试报告 ──────────────────────────────────────

  async def get_report_summary(self) -> dict[str, Any]:
    cursor = await self.db.execute("SELECT COUNT(*) as cnt FROM testing_cases")
    total_cases = (await cursor.fetchone() or {}).get("cnt", 0)
    total_suites = 0
    cursor = await self.db.execute("SELECT COUNT(*) as cnt FROM testing_reviews")
    total_reviews = (await cursor.fetchone() or {}).get("cnt", 0)
    cursor = await self.db.execute("SELECT COUNT(*) as cnt FROM testing_cases WHERE status = 'active'")
    passed = (await cursor.fetchone() or {}).get("cnt", 0)
    cursor = await self.db.execute("SELECT COUNT(*) as cnt FROM testing_cases WHERE status = 'deprecated'")
    failed = (await cursor.fetchone() or {}).get("cnt", 0)
    cursor = await self.db.execute("SELECT COUNT(*) as cnt FROM testing_reviews WHERE status = 'pending'")
    active_reviews = (await cursor.fetchone() or {}).get("cnt", 0)
    pass_rate = (passed / total_cases * 100) if total_cases > 0 else 0.0
    return {
      "total_cases": total_cases, "total_suites": total_suites,
      "total_reviews": total_reviews, "passed_cases": passed,
      "failed_cases": failed, "pass_rate": round(pass_rate, 1),
      "active_reviews": active_reviews,
    }

  # ─── 定时任务 ──────────────────────────────────────

  async def list_scheduled_tasks(self) -> list[dict[str, Any]]:
    """获取所有定时任务"""
    cursor = await self.db.execute(
      "SELECT * FROM testing_scheduled_tasks ORDER BY created_at DESC"
    )
    return await cursor.fetchall() or []

  async def get_scheduled_task(self, task_id: str) -> dict[str, Any] | None:
    """获取单个定时任务"""
    cursor = await self.db.execute(
      "SELECT * FROM testing_scheduled_tasks WHERE id = ?", (task_id,)
    )
    return await cursor.fetchone()

  async def create_scheduled_task(self, id: str, name: str, module: str,
    cron_expr: str, suite_id: str | None = None, suite_name: str = "") -> str:
    """创建定时任务，返回新 ID"""
    await self.db.execute(
      "INSERT INTO testing_scheduled_tasks (id, name, module, suite_id, suite_name, cron_expr, enabled) "
      "VALUES (?, ?, ?, ?, ?, ?, 1)",
      (id, name, module, suite_id, suite_name, cron_expr),
    )
    return id

  async def update_scheduled_task(self, task_id: str, **fields: Any) -> bool:
    """更新定时任务"""
    allowed = {"name", "module", "suite_id", "suite_name", "cron_expr", "enabled", "last_run_at", "next_run_at"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
      return False
    updates["updated_at"] = datetime.now().isoformat()
    pairs = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [task_id]
    cursor = await self.db.execute(f"UPDATE testing_scheduled_tasks SET {pairs} WHERE id = ?", vals)
    return cursor.rowcount > 0

  async def delete_scheduled_task(self, task_id: str) -> bool:
    """删除定时任务"""
    await self.db.execute("DELETE FROM testing_scheduled_task_logs WHERE task_id = ?", (task_id,))
    cursor = await self.db.execute("DELETE FROM testing_scheduled_tasks WHERE id = ?", (task_id,))
    return cursor.rowcount > 0

  async def create_scheduled_task_log(self, id: str, task_id: str, status: str = "running") -> str:
    """创建定时任务执行日志"""
    await self.db.execute(
      "INSERT INTO testing_scheduled_task_logs (id, task_id, status) VALUES (?, ?, ?)",
      (id, task_id, status),
    )
    return id

  async def update_scheduled_task_log(self, log_id: str, **fields: Any) -> bool:
    """更新执行日志（完成时间、时长、状态）"""
    if not fields:
      return False
    pairs = ", ".join(f"{k} = ?" for k in fields)
    vals = list(fields.values()) + [log_id]
    cursor = await self.db.execute(f"UPDATE testing_scheduled_task_logs SET {pairs} WHERE id = ?", vals)
    return cursor.rowcount > 0

  async def list_scheduled_task_logs(self, task_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """获取最近的执行日志"""
    cursor = await self.db.execute(
      "SELECT * FROM testing_scheduled_task_logs WHERE task_id = ? ORDER BY started_at DESC LIMIT ?",
      (task_id, limit),
    )
    return await cursor.fetchall() or []
