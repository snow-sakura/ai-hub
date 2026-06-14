# 数据库版本变更日志

> 记录所有模块的数据库表变更，按时间倒序排列。

## 2026-06-14 — Phase 1 修正：清理错误生成模块

**清理原因**：上一轮错误优先实现了非核心模块，现按正确优先级清理。

### 已删除的模块（3个）

| 模块 | 删除的表 |
|------|---------|
| **api_testing** | `api_testing_environments`, `api_testing_environment_variables`, `api_testing_interface_projects`, `api_testing_interface_collections`, `api_testing_interfaces`, `api_testing_request_history`, `api_testing_mock_rules`, `api_testing_notification_config` |
| **ui_automation** | `ui_projects`, `ui_elements`, `ui_test_environments`, `ui_test_cases`, `ui_test_case_steps`, `ui_test_suites`, `ui_suite_cases`, `ui_test_scripts`, `ui_executions`, `ui_execution_steps`, `ui_devices`, `ui_scheduled_tasks`, `ui_notification_config` |
| **app_automation** | 无（从未创建过表） |

**变更内容**：
- 删除 `backend/app/modules/api_testing/`、`ui_automation/`、`app_automation/` 目录
- main.py 移除对应模块的 import 和 init 调用
- router.py 移除对应模块的路由注册

---

## 2026-06-14 — Phase 1 重构（错误生成，已废弃）

### 配置中心模块（新建）

新表：`backend/app/modules/config_center/database.py`

| 表名 | 说明 | 迁移版本 |
|------|------|---------|
| `config_models` | AI 模型供应商配置 | v1 |
| `config_prompts` | 提示词模板配置 | v1 |
| `config_behaviors` | 生成行为配置 | v1 |
| `config_chat` | AI 聊天室配置 | v1 |
| `config_ui_env` | UI 自动化环境配置 | v1 |
| `config_app_env` | APP 自动化环境配置 | v1 |

### API 测试模块 — 表定义统一

**变更**：废弃 ai_testing 模块 v13-v14 迁移中的 API 测试表创建，统一由 `api_testing/database.py` 管理。

受影响表：

| 表名 | 原有双路径 | 现归属 |
|------|-----------|--------|
| `api_testing_environments` | ai_testing + api_testing | api_testing |
| `api_testing_environment_variables` | ai_testing + api_testing | api_testing |
| `api_testing_interface_projects` | ai_testing + api_testing | api_testing |
| `api_testing_interface_collections` | ai_testing + api_testing | api_testing |
| `api_testing_interfaces` | ai_testing + api_testing | api_testing |
| `api_testing_request_history` | ai_testing + api_testing | api_testing |
| `api_testing_mock_rules` | ai_testing + api_testing | api_testing |
| `api_testing_notification_config` | ai_testing + api_testing | api_testing |

---

## 初始化表结构（Phase 1 已有）

### 共享表 — `backend/app/common/core/database.py`

| 表名 | 说明 |
|------|------|
| `conversations` | 聊天会话 |
| `messages` | 聊天消息 |
| `users` | 系统用户 |
| `knowledge_docs` | 知识库文档 |
| `langgraph_checkpoints` | LangGraph 检查点 |

### AI 测试模块 — `backend/app/modules/ai_testing/database.py`

22 张表，含 15 个版本迁移（v1-v15）。

| 表名 | 版本 | 说明 |
|------|------|------|
| `testing_projects` | v1 | 项目表 |
| `testing_project_members` | v1 | 项目成员 |
| `testing_project_member_links` | v11 | 多对多关联 |
| `testing_cases` | v1 | 测试用例 |
| `testing_generation_tasks` | v1 | 生成任务 |
| `testing_generation_results` | v1 | 阶段结果 |
| `testing_config` | v1 | 配置 |
| `testing_case_attachments` | v1 | 用例附件 |
| `testing_case_comments` | v1 | 用例评论 |
| `testing_operation_logs` | v1 | 操作日志 |
| `testing_project_versions` | v1 | 项目版本 |
| `testing_task_generated_cases` | v6 | 任务-用例桥接 |
| `testing_reviews` | v8 | 评审主表 |
| `testing_review_cases` | v8 | 评审用例关联 |
| `testing_review_reviewers` | v8 | 评审人关联 |
| `testing_ai_tester_sessions` | v8 | AI 评测师会话 |
| `testing_ai_tester_messages` | v8 | AI 评测师消息 |
| `testing_generated_case_items` | v6 | 候选用例项 |
| `testing_scheduled_tasks` | v12 | 定时任务 |
| `testing_scheduled_task_logs` | v12 | 任务执行日志 |
| `testing_schema_version` | — | 版本追踪 |

> ~~API 测试模块 `app/modules/api_testing/database.py`（8 张表）—— 已在 2026-06-14 Phase 1 修正中删除~~

### 哄哄模拟器 — `backend/app/modules/comfort/database.py`

4 张表：

| 表名 | 说明 |
|------|------|
| `comfort_scenes` | 场景 |
| `comfort_characters` | 角色 |
| `comfort_memories` | 记忆 |
| `emotion_statistics` | 情绪统计 |

### 系统管理 — `backend/app/modules/system/database.py`

5 张表：

| 表名 | 说明 |
|------|------|
| `system_roles` | 角色定义 |
| `system_user_profiles` | 用户档案 |
| `system_user_roles` | 用户-角色关联 |
| `system_audit_logs` | 审计日志 |
| `system_settings` | 系统设置 |
