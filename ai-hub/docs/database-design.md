# 数据库设计文档

> 最后更新：2026-07-04

## 概述

使用 MySQL 8.0+，InnoDB 引擎，utf8mb4 字符集。
所有表名小写，单词间用下划线分隔。主键统一使用 VARCHAR(36) UUID。

## 版本管理

每个模块通过 `{module}_schema_version` 表管理数据库版本，启动时自动迁移：

```sql
CREATE TABLE shared_schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 公共层 (common/core/database.py)

由 `init_db()` 在应用启动时自动创建。

### users — 用户账号
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | UUID |
| `username` | VARCHAR(100) UNIQUE | 登录名 |
| `password_hash` | VARCHAR(255) | bcrypt 哈希 |
| `role` | VARCHAR(20) | 角色标识 (admin/user/…) |
| `is_active` | TINYINT(1) | 是否启用 |
| `created_at` | TIMESTAMP | |
| `updated_at` | TIMESTAMP | |

### conversations — 对话会话
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | UUID |
| `user_id` | VARCHAR(36) INDEX | 所属用户 |
| `title` | VARCHAR(500) | 标题 |
| `type` | VARCHAR(50) INDEX | chat / comfort / … |
| `metadata` | JSON | 扩展属性 |
| `created_at` / `updated_at` | TIMESTAMP | |

### messages — 聊天消息
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | |
| `conversation_id` | VARCHAR(36) FK | 所属会话 |
| `role` | VARCHAR(20) | user / assistant / system / tool |
| `content` | TEXT | 消息内容 |
| `metadata` | JSON | 扩展属性 |
| `created_at` | TIMESTAMP | |

### knowledge_docs — 知识库文档
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | |
| `filename` | VARCHAR(500) | 文件名 |
| `file_type` | VARCHAR(50) | pdf/docx/txt… |
| `file_size` | INT | 字节数 |
| `chunk_count` | INT | 分块数 |
| `created_at` | TIMESTAMP | |

### langgraph 检查点表
| 表名 | 说明 |
|------|------|
| `langgraph_checkpoints` | LangGraph 线程检查点 |
| `langgraph_checkpoint_writes` | LangGraph 写入记录 |

## 系统管理 (system/database.py)

由 `init_system_tables()` 创建。

### system_roles — 角色定义
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | |
| `name` | VARCHAR(100) UNIQUE | 角色名 (admin/tester/viewer…) |
| `description` | VARCHAR(500) | 角色描述 |
| `permissions` | JSON | 权限列表 ["case:*", "report:view"] |
| `is_builtin` | TINYINT(1) | 是否内置（不可删除） |
| `created_at` / `updated_at` | TIMESTAMP | |

默认内置角色：
- **admin**: 系统管理员，`["*"]`
- **project_admin**: 项目管理员，`["project:*"]`
- **tester**: 测试工程师，`["project:view", "case:*", "execution:*", "report:*"]`
- **viewer**: 只读用户，`["project:view", "report:view"]`

### system_user_profiles — 用户档案
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | |
| `user_id` | VARCHAR(36) UNIQUE FK → users.id | |
| `display_name` | VARCHAR(100) | 显示名 |
| `avatar` | VARCHAR(500) | 头像 URL |
| `email` | VARCHAR(255) | 邮箱 |
| `phone` | VARCHAR(50) | 电话 |
| `department` | VARCHAR(200) | 部门 |
| `position` | VARCHAR(200) | 职位 |

### system_user_roles — 用户角色关联
| 字段 | 说明 |
|------|------|
| `user_id` | VARCHAR(36) PK, FK → users.id |
| `role_id` | VARCHAR(36) PK, FK → system_roles.id |

### system_audit_logs — 审计日志
| 字段 | 说明 |
|------|------|
| `id` | VARCHAR(36) PK |
| `user_id` | VARCHAR(36) INDEX |
| `username` | VARCHAR(100) |
| `action` | VARCHAR(50) INDEX (login/create/delete/…) |
| `resource_type` | VARCHAR(50) |
| `resource_id` | VARCHAR(255) |
| `detail` | TEXT |
| `ip` | VARCHAR(50) |
| `created_at` | TIMESTAMP INDEX |

### system_settings — 系统设置（键值对）
| 字段 | 说明 |
|------|------|
| `key` | VARCHAR(100) PK |
| `value` | TEXT |
| `description` | VARCHAR(500) |
| `updated_at` | TIMESTAMP |

## 配置中心 (config_center/database.py)

### config_models — AI 模型供应商配置
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | |
| `provider` | VARCHAR(50) | 供应商: openai/deepseek/qwen/zhipu/ollama |
| `model_name` | VARCHAR(255) | 模型名称 |
| `api_key` | TEXT | API 密钥 |
| `api_base_url` | VARCHAR(500) | API 基础地址 |
| `temperature` | DECIMAL(3,2) | 温度参数 (0.0-2.0) |
| `max_tokens` | INT | 最大 Token 数 |
| `enabled` | TINYINT(1) | 是否启用 |
| `sort_order` | INT | 排序优先级 |
| `created_at` / `updated_at` | TIMESTAMP | |

### config_prompts — 提示词模板
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | |
| `name` | VARCHAR(255) | 提示词名称 |
| `stage` | VARCHAR(50) | 对应阶段: analyze/write/review/revise/general |
| `content` | TEXT | 提示词内容 |
| `enabled` | TINYINT(1) | 是否启用 |
| `description` | TEXT | 描述 |
| `created_at` / `updated_at` | TIMESTAMP | |

### config_behaviors — 生成行为配置
| 字段 | 类型 | 说明 |
|------|------|------|
| `key` | VARCHAR(100) PK | 配置键名 |
| `value` | TEXT | 配置值 |
| `description` | VARCHAR(500) | 描述 |
| `updated_at` | TIMESTAMP | |

### config_chat — AI 聊天室配置
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | |
| `model_provider` | VARCHAR(50) | 模型提供商 |
| `model_name` | VARCHAR(255) | 模型名称 |
| `system_prompt` | TEXT | 系统提示词 |
| `max_history` | INT | 最大历史消息数 |
| `enable_rag` | TINYINT(1) | RAG 知识库 |
| `rag_top_k` | INT | RAG 检索数量 |
| `enable_web_search` | TINYINT(1) | 联网搜索 |
| `temperature` | DECIMAL(3,2) | 温度参数 |
| `created_at` / `updated_at` | TIMESTAMP | |

### config_ui_env — UI 自动化环境配置
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | |
| `name` | VARCHAR(200) | 环境名称 |
| `browser_type` | VARCHAR(50) | 浏览器: chromium/firefox/edge/webkit |
| `base_url` | VARCHAR(500) | 基础 URL |
| `headless` | TINYINT(1) | 无头模式 |
| `viewport_width` | INT | 视口宽度 |
| `viewport_height` | INT | 视口高度 |
| `timeout_ms` | INT | 超时毫秒 |
| `screenshot_on_failure` | TINYINT(1) | 失败自动截图 |
| `created_at` / `updated_at` | TIMESTAMP | |

### config_app_env — APP 自动化环境配置
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) PK | |
| `name` | VARCHAR(200) | 环境名称 |
| `platform` | VARCHAR(50) | android / ios |
| `app_package` | VARCHAR(500) | 应用包名 |
| `app_activity` | VARCHAR(500) | 启动 Activity |
| `device_serial` | VARCHAR(200) | 设备序列号 |
| `appium_url` | VARCHAR(500) | Appium URL |
| `timeout_ms` | INT | 超时毫秒 |
| `screenshot_on_failure` | TINYINT(1) | 失败自动截图 |
| `created_at` / `updated_at` | TIMESTAMP | |

## AI 智能测试 (ai_testing/database.py)

完整的 22 张表清单见 ai_testing/database.py 的 `init_testing_tables()`。

核心表：
| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `testing_projects` | 测试项目 | name, description, status |
| `testing_cases` | 测试用例 | project_id, title, priority(P0-P3), status, tags JSON |
| `testing_generation_tasks` | AI 生成任务 | project_id, input_text, model, status |
| `testing_generation_results` | 生成阶段结果 | task_id, stage(analyze/write/review/revise), content |
| `testing_reviews` | 用例评审 | 评审流程记录 |
| `testing_project_versions` | 项目版本管理 | project_id, version_name |

## 哄哄模拟器 (comfort/database.py)

| 表名 | 说明 |
|------|------|
| `comfort_scenes` | 安抚场景 |
| `comfort_characters` | 角色定义 |
| `comfort_memories` | 对话记忆 |
| `emotion_statistics` | 情绪统计 |

## 数据库变更记录

### v4 (2026-07-04 — 文档完善)
- 完善配置中心表结构文档，补充完整字段定义
- 同步系统管理模块表结构更新
- 补充哄哄模拟器表结构详细定义

### v3 (2026-06-14 — Phase 1 修正)
- 新增 config_center 6 张表（config_models, config_prompts, config_behaviors, config_chat, config_ui_env, config_app_env）
- 删除 api_testing、ui_automation 模块及其对应表（参见 database-changelog.md）

### v2 (重构 v2.0 — 2026-06-14)
- 新增 `system_roles` — 角色定义 + 4 个默认角色
- 新增 `system_user_profiles` — 用户档案
- 新增 `system_user_roles` — 用户角色关联
- 新增 `system_audit_logs` — 审计日志
- 新增 `system_settings` — 系统设置
- 无破坏性变更

### v1 (初始)
- 创建共享层、ai_testing、comfort 的所有基础表
