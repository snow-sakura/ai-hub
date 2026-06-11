"""AI Testing 模块纯业务实体（无框架依赖）"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TestingProject:
  """测试项目实体"""
  id: str
  name: str
  description: str = ""
  status: str = "active"
  created_at: str = ""
  updated_at: str = ""


@dataclass
class ProjectMember:
  """项目成员实体"""
  id: str
  project_id: str
  name: str
  role: str = "tester"
  created_at: str = ""


@dataclass
class TestingCase:
  """测试用例实体"""
  id: str
  project_id: str | None = None
  title: str = ""
  version: str = ""
  priority: str = "P2"
  case_type: str = "functional"
  preconditions: str = ""
  steps: str = ""
  expected_results: str = ""
  tags: list[str] = field(default_factory=list)
  status: str = "draft"
  source: str = "manual"
  ai_task_id: str | None = None
  author: str = ""
  created_at: str = ""
  updated_at: str = ""


@dataclass
class GenerationTask:
  """AI 生成任务实体"""
  id: str
  project_id: str | None = None
  input_text: str = ""
  requirement_title: str = ""
  file_path: str | None = None
  file_type: str | None = None
  file_name: str | None = None
  model: str = ""
  status: str = "pending"
  generated_count: int = 0
  error_message: str | None = None
  created_at: str = ""
  updated_at: str = ""


@dataclass
class CaseAttachment:
  """用例附件实体"""
  id: str
  case_id: str
  file_name: str
  file_path: str
  file_size: int = 0
  file_type: str = ""
  uploaded_by: str = ""
  created_at: str = ""


@dataclass
class CaseComment:
  """用例评论实体"""
  id: str
  case_id: str
  content: str
  author: str = ""
  created_at: str = ""
  updated_at: str = ""


@dataclass
class OperationLog:
  """操作日志实体"""
  id: str
  entity_type: str
  entity_id: str
  action: str
  operator: str = ""
  detail: str = "{}"
  created_at: str = ""


@dataclass
class ProjectVersion:
  """项目版本实体"""
  id: str
  project_id: str
  name: str
  description: str = ""
  status: str = "active"
  created_at: str = ""
  updated_at: str = ""


@dataclass
class GenerationResult:
  """AI 生成阶段结果实体"""
  id: str
  task_id: str
  stage: str = "analyze"
  content: str = ""
  created_at: str = ""


@dataclass
class TestingConfig:
  """配置项实体"""
  id: str
  key: str
  value: str = ""
  category: str = "model"
  description: str = ""
  updated_at: str = ""
