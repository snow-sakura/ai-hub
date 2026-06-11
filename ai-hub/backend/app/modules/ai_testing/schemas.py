"""AI Testing 模块 Pydantic 请求/响应 Schema"""

from typing import Any
from pydantic import BaseModel, Field


# ─── 项目 ──────────────────────────────────────────

class ProjectCreate(BaseModel):
  """创建项目请求"""
  name: str = Field(min_length=2, max_length=200)
  description: str = ""
  status: str = Field(default="active", pattern=r"^(active|paused|completed|archived)$")


class ProjectUpdate(BaseModel):
  """更新项目请求"""
  name: str | None = Field(default=None, min_length=2, max_length=200)
  description: str | None = None
  status: str | None = Field(default=None, pattern=r"^(active|paused|completed|archived)$")


class ProjectResponse(BaseModel):
  """项目响应"""
  id: str
  name: str
  description: str = ""
  status: str = "active"
  case_count: int = 0
  member_count: int = 0
  created_at: str = ""
  updated_at: str = ""


class ProjectListResponse(BaseModel):
  """项目列表分页响应"""
  items: list[ProjectResponse]
  total: int
  page: int
  page_size: int


# ─── 项目成员 ────────────────────────────────────────

class MemberCreate(BaseModel):
  """添加成员请求"""
  name: str = Field(min_length=1, max_length=100)
  role: str = Field(default="tester", pattern=r"^(owner|tester|viewer)$")


class MemberResponse(BaseModel):
  """成员响应"""
  id: str
  project_id: str
  name: str
  role: str = "tester"
  created_at: str = ""


# ─── 测试用例 ────────────────────────────────────────

class TestCaseCreate(BaseModel):
  """创建测试用例请求"""
  project_id: str | None = None
  title: str = Field(min_length=1, max_length=500)
  version: str = ""
  priority: str = Field(default="P2", pattern=r"^(P0|P1|P2|P3)$")
  case_type: str = "functional"
  preconditions: str = ""
  steps: str = ""
  expected_results: str = ""
  tags: list[str] = []
  status: str = Field(default="draft", pattern=r"^(draft|active|deprecated)$")
  author: str = ""


class TestCaseUpdate(BaseModel):
  """更新测试用例请求"""
  project_id: str | None = None
  title: str | None = Field(default=None, min_length=1, max_length=500)
  version: str | None = None
  priority: str | None = Field(default=None, pattern=r"^(P0|P1|P2|P3)$")
  case_type: str | None = None
  preconditions: str | None = None
  steps: str | None = None
  expected_results: str | None = None
  tags: list[str] | None = None
  status: str | None = Field(default=None, pattern=r"^(draft|active|deprecated)$")


class TestCaseResponse(BaseModel):
  """测试用例响应"""
  id: str
  project_id: str | None = None
  project_name: str | None = None
  title: str
  version: str = ""
  priority: str = "P2"
  case_type: str = "functional"
  preconditions: str = ""
  steps: str = ""
  expected_results: str = ""
  tags: list[str] = []
  status: str = "draft"
  source: str = "manual"
  ai_task_id: str | None = None
  author: str = ""
  created_at: str = ""
  updated_at: str = ""


class TestCaseListResponse(BaseModel):
  """用例列表分页响应"""
  items: list[TestCaseResponse]
  total: int
  page: int
  page_size: int


class TestCaseFilter(BaseModel):
  """用例筛选参数"""
  project_id: str | None = None
  priority: str | None = None
  case_type: str | None = None
  status: str | None = None
  version: str | None = None
  keyword: str | None = None
  page: int = 1
  page_size: int = 20


class BatchDeleteRequest(BaseModel):
  """批量删除请求"""
  ids: list[str] = Field(min_length=1)


# ─── 生成任务 ────────────────────────────────────────

class GenerateRequest(BaseModel):
  """发起 AI 生成请求"""
  project_id: str | None = None
  requirement_title: str = ""
  input_text: str = ""
  file_path: str | None = None
  file_type: str | None = None
  file_name: str | None = None
  model: str = ""
  output_mode: str = Field(default="stream", pattern=r"^(stream|complete)$")
  custom_suggestions: list[str] = []  # 用户选中的改进建议，用于按需重新生成


class DocumentUploadResponse(BaseModel):
  """文档上传解析响应"""
  text: str = ""
  file_name: str = ""
  file_type: str = ""
  file_path: str = ""


# ─── 用例附件 ───────────────────────────────────────

class AttachmentResponse(BaseModel):
  """附件响应"""
  id: str
  case_id: str
  file_name: str
  file_path: str
  file_size: int = 0
  file_type: str = ""
  uploaded_by: str = ""
  created_at: str = ""


# ─── 用例评论 ────────────────────────────────────────

class CommentCreate(BaseModel):
  """创建评论请求"""
  content: str = Field(min_length=1, max_length=5000)
  author: str = ""


class CommentUpdate(BaseModel):
  """更新评论请求"""
  content: str = Field(min_length=1, max_length=5000)


class CommentResponse(BaseModel):
  """评论响应"""
  id: str
  case_id: str
  content: str
  author: str = ""
  created_at: str = ""
  updated_at: str = ""


# ─── 操作日志 ────────────────────────────────────────

class OperationLogResponse(BaseModel):
  """操作日志响应"""
  id: str
  entity_type: str
  entity_id: str
  action: str
  operator: str = ""
  detail: str = "{}"
  created_at: str = ""


# ─── 项目版本 ────────────────────────────────────────

class VersionCreate(BaseModel):
  """创建版本请求"""
  name: str = Field(min_length=1, max_length=200)
  description: str = ""
  status: str = Field(default="active", pattern=r"^(active|released|archived)$")


class VersionUpdate(BaseModel):
  """更新版本请求"""
  name: str | None = Field(default=None, min_length=1, max_length=200)
  description: str | None = None
  status: str | None = Field(default=None, pattern=r"^(active|released|archived)$")


class VersionResponse(BaseModel):
  """版本响应"""
  id: str
  project_id: str
  name: str
  description: str = ""
  status: str = "active"
  created_at: str = ""
  updated_at: str = ""


# ─── 配置检查 ─────────────────────────────────────────

class ConfigCheckItem(BaseModel):
  """配置检查项"""
  key: str
  label: str = ""
  category: str = ""
  status: str = "ok"
  message: str = ""


class ConfigCheckResponse(BaseModel):
  """配置检查响应"""
  items: list[ConfigCheckItem] = []
  all_passed: bool = True


class GenerateTaskResponse(BaseModel):
  """生成任务响应"""
  id: str
  project_id: str | None = None
  input_text: str = ""
  file_name: str | None = None
  file_type: str | None = None
  model: str = ""
  status: str = "pending"
  generated_count: int = 0
  error_message: str | None = None
  created_at: str = ""
  updated_at: str = ""


class GenerateResultResponse(BaseModel):
  """生成结果响应"""
  id: str
  task_id: str
  stage: str
  content: str = ""
  created_at: str = ""


class SaveCasesRequest(BaseModel):
  """将生成结果保存到用例库"""
  task_id: str
  project_id: str | None = None
  cases: list[dict[str, Any]] = []


# ─── 配置 ──────────────────────────────────────────

class ConfigItem(BaseModel):
  """配置项"""
  key: str
  value: str = ""
  category: str = "model"
  description: str = ""


class ConfigUpdateRequest(BaseModel):
  """更新配置请求"""
  items: list[ConfigItem] = []


class ConfigResponse(BaseModel):
  """配置列表响应"""
  items: list[ConfigItem]


class TaskStatusUpdate(BaseModel):
  """任务状态更新请求"""
  status: str = ""


class ConfigDefaultsResponse(BaseModel):
  """配置默认值响应"""
  prompts: dict[str, str] = {}
  models: list[dict[str, str]] = []


# ─── 生成用例项 ─────────────────────────────────────────

class GeneratedCaseItem(BaseModel):
  """生成任务中的单个候选用例项"""
  id: str
  task_id: str
  title: str = ""
  priority: str = "P2"
  case_type: str = "functional"
  preconditions: str = ""
  steps: str = ""
  expected_results: str = ""
  tags: list[str] = []
  status: str = "pending"
  sort_order: int = 0
  created_at: str = ""


class BatchUpdateCasesRequest(BaseModel):
  """批量更新用例状态请求"""
  case_ids: list[str] = Field(min_length=1)
  status: str = Field(pattern=r"^(adopted|discarded|pending)$")


class GenerationStatsResponse(BaseModel):
  """生成统计响应"""
  total_tasks: int = 0
  completed_tasks: int = 0
  total_cases: int = 0
  avg_score: float = 0.0
