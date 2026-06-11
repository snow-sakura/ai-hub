"""AI Testing 模块数据库表 DDL（6 张表）"""

import aiosqlite
from app.shared.core.database import get_db


TESTING_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS testing_projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'active'
    CHECK(status IN ('active', 'paused', 'completed', 'archived')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_testing_projects_status
  ON testing_projects(status);

CREATE TABLE IF NOT EXISTS testing_project_members (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'tester'
    CHECK(role IN ('owner', 'tester', 'viewer')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES testing_projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_project_members_project
  ON testing_project_members(project_id);

CREATE TABLE IF NOT EXISTS testing_cases (
  id TEXT PRIMARY KEY,
  project_id TEXT,
  title TEXT NOT NULL,
  version TEXT NOT NULL DEFAULT '',
  priority TEXT NOT NULL DEFAULT 'P2'
    CHECK(priority IN ('P0', 'P1', 'P2', 'P3')),
  case_type TEXT NOT NULL DEFAULT 'functional',
  preconditions TEXT NOT NULL DEFAULT '',
  steps TEXT NOT NULL DEFAULT '',
  expected_results TEXT NOT NULL DEFAULT '',
  tags TEXT DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'draft'
    CHECK(status IN ('draft', 'active', 'deprecated')),
  source TEXT NOT NULL DEFAULT 'manual'
    CHECK(source IN ('manual', 'ai')),
  ai_task_id TEXT,
  author TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES testing_projects(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_testing_cases_project
  ON testing_cases(project_id);
CREATE INDEX IF NOT EXISTS idx_testing_cases_priority
  ON testing_cases(priority);
CREATE INDEX IF NOT EXISTS idx_testing_cases_status
  ON testing_cases(status);

CREATE TABLE IF NOT EXISTS testing_generation_tasks (
  id TEXT PRIMARY KEY,
  project_id TEXT,
  input_text TEXT NOT NULL DEFAULT '',
  file_path TEXT,
  file_type TEXT,
  file_name TEXT,
  model TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK(status IN ('pending', 'running', 'completed', 'failed')),
  generated_count INTEGER NOT NULL DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES testing_projects(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_generation_tasks_status
  ON testing_generation_tasks(status);

CREATE TABLE IF NOT EXISTS testing_generation_results (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  stage TEXT NOT NULL
    CHECK(stage IN ('analyze', 'write', 'review', 'revise', 'final')),
  content TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (task_id) REFERENCES testing_generation_tasks(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_generation_results_task
  ON testing_generation_results(task_id);

CREATE TABLE IF NOT EXISTS testing_config (
  id TEXT PRIMARY KEY,
  key TEXT NOT NULL UNIQUE,
  value TEXT NOT NULL DEFAULT '',
  category TEXT NOT NULL DEFAULT 'model'
    CHECK(category IN ('model', 'prompt', 'behavior')),
  description TEXT NOT NULL DEFAULT '',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_testing_config_key
  ON testing_config(key);
"""


async def init_testing_tables() -> None:
  """初始化 AI Testing 模块数据库表"""
  db = await get_db()
  try:
    await db.executescript(TESTING_TABLES_SQL)
    await db.commit()
  finally:
    await db.close()
