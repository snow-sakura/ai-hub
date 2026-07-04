# 系统架构文档

> 最后更新：2026-07-04

## 项目概述

AI-HUB 智能测试平台 —— 基于 LangGraph 的全栈 AI 测试管理平台。
竞品参考：testhub（Django + Vue 3 + Element Plus）
原型设计：`aihub-pic/`（55 个 HTML 原型页面，暖色调）

## 技术栈

### 后端
| 组件 | 技术 | 说明 |
|------|------|------|
| 框架 | Python FastAPI | 异步原生 |
| AI 工作流 | LangGraph + LangChain | 流式 SSE + checkpoint |
| 数据库 | MySQL 8.0+ (aiomysql) | InnoDB, utf8mb4 |
| 认证 | JWT (PyJWT) + bcrypt | Bearer Token |
| 定时任务 | apscheduler | 替代 Celery（最小依赖） |
| 向量检索 | ChromaDB | 知识库文档语义搜索 |

### 前端
| 组件 | 技术 | 说明 |
|------|------|------|
| 框架 | Vue 3 + TypeScript + Vite | Composition API |
| UI | Naive UI | 暖色调主题覆盖 |
| 状态 | Pinia | 模块化 store |
| 路由 | Vue Router 4 | Hash 模式 |
| HTTP | Axios | baseURL: /api/v1 |
| SSE | fetch + ReadableStream | useSseStream composable |

## 目录结构

```
ai-hub/
├── backend/
│   ├── main.py                            # 应用入口
│   ├── app/
│   │   ├── config.py                      # Pydantic 配置
│   │   ├── dependencies.py                # FastAPI 依赖注入
│   │   ├── api/v1/router.py               # 路由汇总
│   │   ├── modules/                       # 6 个功能模块
│   │   │   ├── system/                    # 认证 + 系统管理
│   │   │   ├── chat/                      # AI 聊天室
│   │   │   ├── comfort/                   # 哄哄模拟器
│   │   │   ├── knowledge/                 # 知识库
│   │   │   ├── ai_testing/                # AI 智能测试
│   │   │   └── config_center/             # 配置中心
│   │   └── common/
│   │       ├── core/                      # 核心基础设施
│   │       │   ├── database.py            # MySQL 连接池 + 共享表
│   │       │   ├── llm_factory.py         # LLM 工厂
│   │       │   ├── embedding_factory.py   # Embedding 工厂
│   │       │   ├── logging.py             # 日志配置
│   │       │   ├── managed_graph.py       # LangGraph 图生命周期管理
│   │       │   └── mysql_saver.py         # MySQL checkpoint saver
│   │       ├── auth.py                    # JWT 认证（签发/验证/密码哈希）
│   │       ├── agent/                     # LangGraph Agent 基础设施
│   │       │   ├── state.py               # AgentState 定义
│   │       │   ├── prompts.py             # 系统提示词模板
│   │       │   ├── agent_utils.py         # Agent 工具函数
│   │       │   ├── nodes/                 # LLM 推理/检索/工具节点
│   │       │   └── tools/                 # 7 大工具（搜索/抓取/图片/PDF/文件/下载/终端）
│   │       ├── api/v1/                   # 共享 API 接口（models, modules, tools）
│   │       ├── api/schemas/              # 共享 Pydantic 模型
│   │       ├── logs/                      # 日志系统
│   │       │   ├── logger.py             # 应用日志
│   │       │   └── operation_logger.py   # 操作日志（文件系统 JSON Lines）
│   │       ├── service/                   # 共享服务
│   │       ├── repository/                # 共享数据访问
│   │       ├── domain/                    # 领域实体与异常
│   │       ├── tools/                     # 工具函数
│   │       ├── utils/                     # 工具类（sse_helper, file_parser, encryption）
│   │       └── docs/                      # 文档解析
│   └── data/                              # 运行时数据
├── frontend/
│   └── src/
│       ├── shared/                        # 公共模块
│       │   ├── api/                       # API 客户端
│       │   ├── stores/                    # 全局状态
│       │   ├── types/                     # 类型定义
│       │   ├── components/layout/         # AppHeader, AppSidebar
│       │   └── router/                    # 路由配置
│       └── modules/                       # 6 个功能模块
│           ├── system/
│           ├── chat/
│           ├── comfort/
│           ├── knowledge/
│           ├── ai_testing/
│           └── config_center/
└── docs/                                  # 技术文档
    ├── architecture.md                    # 本文件
    ├── database-design.md                 # 数据库设计
    ├── changelog.md                       # 版本更新
    └── dev-plan.md                        # 研发计划
└── todo.md                                # 待办事项（根目录）
```

## 模块清单

| # | 模块 | 原型 | 后端目录 | 状态 |
|---|------|------|---------|------|
| 01 | AI 智能测试 | `01-AI智能测试/` + `05-测试管理/` | `ai_testing/` | 已实现，需优化 |
| 02 | 配置中心 | `06-配置中心/` | `config_center/` | ✅ 完整 |
| 03 | AI 聊天室 | `07-AI聊天室/` | `chat/` | ✅ 完整 |
| 04 | 知识库 | `08-知识库/` | `knowledge/` | 基本完整 |
| 05 | 系统管理 | `09-系统管理/` | `system/` | ✅ 完整 |

## 后端分层设计

每个模块遵循 4 层架构：

```
┌─────────────────────────────────────────────────┐
│  API 层 (api.py)                                 │
│  FastAPI APIRouter + Pydantic 校验               │
├─────────────────────────────────────────────────┤
│  Service 层 (service.py)                         │
│  业务逻辑编排、跨模块协作                          │
├─────────────────────────────────────────────────┤
│  Repository 层 (repository.py)                   │
│  数据访问(CRUD)、SQL 查询                         │
├─────────────────────────────────────────────────┤
│  Domain 层 (domain.py)                           │
│  纯业务实体、值对象                                │
└─────────────────────────────────────────────────┘
```

## 认证流程

```
请求 → HTTPBearer → decode_access_token → get_current_user → 请求处理
                                                      │
                                                   用户信息
                                              {user_id, username, role}
```

- 登录：`POST /auth/login` → 验证密码 → 签发 JWT（24h 有效期）
- 注册：`POST /auth/register` → 创建用户 → 自动签发 JWT
- 刷新：`POST /auth/refresh` → 重新签发
- 获取当前用户：`GET /auth/me`

## 操作日志系统

```
Service 层操作 → OperationLogger.log() → 文件系统 (JSON Lines)
                                     logs/operations/{module}/{module}.log
                                     ↑ 每日轮转，保留 90 天
                                     
查询 API: GET /system/operation-logs?module=&action=&user_id=&keyword=
```

## 数据库连接管理

使用连接池模式（`MySQLDatabase` 单例）：

```
FastAPI startup  →  create_pool (min=2, max=10)
                    ↓
get_db_dep()     →  pool.acquire() → MySQLConnection
依赖注入            ↓
                  使用完毕 → pool.release()（归还连接池）
```

## 竞品代码适配策略

testhub (Django) → ai-hub (FastAPI) 映射：

| testhub | ai-hub |
|---------|--------|
| `models.py` (Django ORM) | `database.py` (DDL) + `schemas.py` (Pydantic) |
| `views.py` (ViewSet) | `api.py` (APIRouter) + `service.py` (业务) |
| `serializers.py` | `schemas.py` (请求/响应模型) |
| `admin.py` | 不迁移 |
| `tasks.py` (Celery) | LangGraph async / apscheduler |
| `urls.py` | 路由注册在 router.py |
