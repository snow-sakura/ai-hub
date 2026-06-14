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


class MemberUpdate(BaseModel):
  """更新成员角色请求"""
  role: str = Field(pattern=r"^(owner|tester|viewer)$")


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
  """附件响应（不返回 file_path，防止服务端路径泄露）"""
  id: str
  case_id: str
  file_name: str
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
  """创建版本请求（独立模块，无 project_id）"""
  name: str = Field(min_length=1, max_length=200)
  description: str = ""
  status: str = Field(default="active", pattern=r"^(active|released|archived)$")
  pass_rate: float | None = None


class VersionUpdate(BaseModel):
  """更新版本请求"""
  name: str | None = Field(default=None, min_length=1, max_length=200)
  description: str | None = None
  status: str | None = Field(default=None, pattern=r"^(active|released|archived)$")
  pass_rate: float | None = None


class VersionResponse(BaseModel):
  """版本响应"""
  id: str
  name: str
  description: str = ""
  status: str = "active"
  pass_rate: float = 0.0
  created_at: str = ""
  updated_at: str = ""


class LinkProjectRequest(BaseModel):
  """关联项目请求"""
  project_id: str


class DashboardStatsResponse(BaseModel):
  """仪表盘统计数据"""
  project_count: int = 0
  total_cases: int = 0
  member_count: int = 0
  active_versions: int = 0
  case_by_priority: dict[str, int] = {}
  case_by_type: dict[str, int] = {}
  case_by_status: dict[str, int] = {}
  recent_activities: list[dict] = []


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
  has_saved_cases: bool = False
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
  base_urls: dict[str, str] = {}


class TestConnectionRequest(BaseModel):
  """测试连接请求"""
  provider: str
  model_name: str = ""
  api_key: str = ""
  base_url: str = ""


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


# ─── 用例评审 ────────────────────────────────────────

class ReviewCreate(BaseModel):
  """创建评审请求"""
  project_id: str | None = None
  title: str = Field(min_length=1, max_length=500)
  description: str = ""
  priority: str = Field(default="P1", pattern=r"^(P0|P1|P2|P3)$")
  due_date: str | None = None
  case_ids: list[str] = []
  reviewer_ids: list[str] = []


class ReviewUpdate(BaseModel):
  """更新评审请求"""
  title: str | None = Field(default=None, min_length=1, max_length=500)
  description: str | None = None
  priority: str | None = Field(default=None, pattern=r"^(P0|P1|P2|P3)$")
  status: str | None = Field(default=None, pattern=r"^(pending|in_progress|approved|rejected|cancelled)$")
  progress: int | None = Field(default=None, ge=0, le=100)
  due_date: str | None = None
  case_ids: list[str] | None = None
  reviewer_ids: list[str] | None = None


class ReviewResponse(BaseModel):
  """评审响应"""
  id: str
  project_id: str | None = None
  project_name: str | None = None
  title: str
  description: str = ""
  priority: str = "P1"
  status: str = "pending"
  progress: int = 0
  due_date: str = ""
  creator: str = ""
  case_count: int = 0
  reviewer_count: int = 0
  created_at: str = ""
  updated_at: str = ""


class ReviewListResponse(BaseModel):
  """评审列表分页响应"""
  items: list[ReviewResponse]
  total: int
  page: int
  page_size: int


class ReviewCaseUpdate(BaseModel):
  """更新评审用例状态请求"""
  status: str = Field(pattern=r"^(approved|rejected|pending)$")
  comment: str = ""


class ReviewStatsResponse(BaseModel):
  """评审统计响应"""
  pending: int = 0
  in_progress: int = 0
  approved: int = 0
  rejected: int = 0


# ─── AI 评测师 ──────────────────────────────────────

class AITesterSessionCreate(BaseModel):
  """创建会话请求"""
  name: str = "新会话"
  model: str = ""


class AITesterSessionUpdate(BaseModel):
  """更新会话名称请求"""
  name: str = Field(min_length=1, max_length=200)


class AITesterSessionResponse(BaseModel):
  """会话响应"""
  id: str
  name: str = ""
  model: str = ""
  message_count: int = 0
  created_at: str = ""
  updated_at: str = ""


class AITesterMessageSend(BaseModel):
  """发送消息请求"""
  session_id: str
  content: str = Field(min_length=1, max_length=10000)
  model: str = ""  # 选择的模型 provider，为空则使用默认 deepseek


class AITesterMessageBody(BaseModel):
  """发送消息请求体（session_id 来自路径参数）"""
  content: str = Field(min_length=1, max_length=10000)
  model: str = ""  # 选择的模型 provider，为空则使用默认 deepseek


class AITesterMessageResponse(BaseModel):
  """消息响应"""
  id: str
  session_id: str
  role: str
  content: str
  rating: str | None = None
  created_at: str = ""


class AITesterMessageRatingUpdate(BaseModel):
  """消息评分更新请求"""
  rating: str | None = Field(default=None, description="'up' 或 'down'，null 清除评分")


# ─── 测试报告 ────────────────────────────────────────

class ReportSummaryResponse(BaseModel):
  """报告摘要响应"""
  total_cases: int = 0
  total_suites: int = 0
  total_reviews: int = 0
  passed_cases: int = 0
  failed_cases: int = 0
  pass_rate: float = 0.0
  active_reviews: int = 0


# ─── 定时任务 ────────────────────────────────────────

class ScheduledTaskCreate(BaseModel):
  """创建定时任务请求"""
  name: str = Field(min_length=1, max_length=255)
  module: str = Field(default="api", pattern=r"^(api|ui|app)$")
  suite_id: str | None = None
  suite_name: str = ""
  cron_expr: str = Field(default="0 8 * * *", max_length=100)


class ScheduledTaskUpdate(BaseModel):
  """更新定时任务请求"""
  name: str | None = Field(default=None, min_length=1, max_length=255)
  module: str | None = Field(default=None, pattern=r"^(api|ui|app)$")
  suite_id: str | None = None
  suite_name: str | None = None
  cron_expr: str | None = Field(default=None, max_length=100)
  enabled: bool | None = None


# ─── 修订请求 ────────────────────────────────────────

class ReviseRequest(BaseModel):
  """修订生成请求：复用已有分析/草稿，仅重新执行评审+修订"""
  custom_suggestions: list[str] = Field(default_factory=list, description="用户选中的改进建议列表")
