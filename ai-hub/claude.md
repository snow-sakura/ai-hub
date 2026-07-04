# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **重要**：研发实施前必须先阅读 `docs/project-rules.md`（项目专属规则），所有开发必须遵循其中的架构、编码、安全等约束。

## 项目概述

AI 测试平台（AI Test Platform）——基于 LangGraph 的全栈 AI 应用，包含三大模块：

- **AI 聊天室**：多模型对话 + RAG 知识库 + 工具调用
- **哄哄模拟器**：角色扮演情绪安抚场景 + 原谅值系统 + 情绪统计看板
- **AI 测试助手**：需求文档 → AI 4 步工作流（分析→编写→评审→修订）→ 测试用例 + 项目管理 + 用例全生命周期管理

## 技术栈

- **后端**：Python FastAPI + LangGraph + LangChain + MySQL + ChromaDB
- **前端**：Vue 3 + TypeScript + Vite + Naive UI + Pinia

## 常用命令

### 启动开发环境

```bash
# 方式一：Docker Compose
docker-compose up

# 方式二：独立启动后端
cd backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 方式三：独立启动前端
cd frontend
npm run dev        # 开发服务器，端口 5173
npm run build      # 生产构建（先执行 vue-tsc 类型检查）
npm run preview    # 预览生产构建
```

### 环境配置

```bash
cp backend/.env.example backend/.env
```

然后在 `.env` 中填入至少一个 LLM Provider 的 API Key（OpenAI / DeepSeek / Qwen / Zhipu / Ollama）。

## 后端架构

### 目录结构

```
backend/
├── app/
│   ├── modules/                  # 功能模块
│   │   ├── chat/                 # AI 聊天室
│   │   │   ├── api.py            # FastAPI 路由（SSE 端点）
│   │   │   ├── schemas.py        # ChatRequest（含 reasoning_effort/web_search/deep_thinking）
│   │   │   ├── graph.py          # LangGraph 图定义（recursion_limit=100）
│   │   │   └── service.py        # SSE 流式编排 + token 缓存 + 先思考后输出
│   │   ├── comfort/              # 哄哄模拟器
│   │   │   ├── graph.py          # 独立 LangGraph 图
│   │   │   ├── scene_seed.py     # 内置场景/角色种子数据
│   │   │   ├── emotion_analyzer.py
│   │   │   ├── forgiveness_engine.py
│   │   │   ├── comfort_prompts.py
│   │   │   └── nodes/
│   │   │       ├── emotion_node.py
│   │   │       ├── comfort_agent_node.py
│   │   │       └── forgiveness_node.py
│   │   ├── knowledge/            # 知识库管理（API 路由）
│   │   └── ai_testing/           # AI 测试助手
│   │       ├── api.py            # FastAPI 路由（24 个端点）
│   │       ├── schemas.py        # Pydantic 请求/响应模型
│   │       ├── service.py        # 业务逻辑层
│   │       ├── repository.py     # 数据访问层（全 CRUD）
│   │       ├── database.py       # 20 张表 DDL（含 15 个迁移版本）
│   │       ├── domain.py         # 纯业务实体
│   │       ├── graph.py          # LangGraph 图构建（4 步流水线）
│   │       ├── prompts.py        # 4 个 Prompt 模板
│   │       ├── sse_stream.py     # SSE 流式推送（astream_events v2）
│   │       ├── excel_handler.py  # Excel 导入/导出（openpyxl）
│   │       └── nodes/
│   │           ├── analyze_node.py   # Step1: 需求分析
│   │           ├── write_node.py     # Step2: 用例编写
│   │           ├── review_node.py    # Step3: AI 评审（JSON 输出）
│   │           └── revise_node.py    # Step4: 用例修订
│   ├── common/                   # 公共模块（原 shared/）
│   │   ├── agent/                # LangGraph Agent 基础设施
│   │   │   ├── state.py          # AgentState 定义
│   │   │   ├── prompts.py        # 系统提示词模板
│   │   │   ├── agent_utils.py    # Agent 工具函数
│   │   │   ├── nodes/
│   │   │   │   ├── agent_node.py     # LLM 推理节点（dispatch_custom_event）
│   │   │   │   ├── rag_node.py       # ChromaDB 检索节点
│   │   │   │   └── tool_node.py      # 工具并行执行节点
│   │   │   └── tools/
│   │   │       ├── web_search.py     # 联网搜索
│   │   │       ├── web_scraper.py    # 网页抓取
│   │   │       ├── image_search.py   # 图片搜索
│   │   │       ├── pdf_generator.py  # PDF 生成
│   │   │       ├── file_ops.py       # 文件读写
│   │   │       ├── downloader.py     # 资源下载
│   │   │       └── terminal.py       # 终端执行
│   │   ├── core/
│   │   │   ├── database.py       # MySQL 连接管理（连接池模式）
│   │   │   ├── llm_factory.py    # LLM 工厂（reasoning_effort + thinking mode）
│   │   │   ├── embedding_factory.py # Embedding 工厂
│   │   │   ├── logging.py        # 日志配置
│   │   │   ├── managed_graph.py  # LangGraph 图生命周期管理
│   │   │   └── mysql_saver.py    # MySQL checkpoint saver
│   │   ├── api/v1/               # 共享 API 接口
│   │   │   ├── __init__.py
│   │   │   ├── models.py         # 模型列表 API
│   │   │   ├── modules.py        # 模块信息 API
│   │   │   └── tools.py          # 工具列表 API
│   │   ├── api/schemas/          # 共享 Pydantic 模型
│   │   │   ├── __init__.py
│   │   │   └── common.py         # 通用响应模型
│   │   ├── auth.py               # JWT 认证（签发/验证/密码哈希）
│   │   ├── service/              # 共享服务
│   │   │   ├── __init__.py
│   │   │   └── conversation_service.py
│   │   ├── repository/           # 共享数据访问
│   │   │   ├── __init__.py
│   │   │   ├── conversation_repo.py
│   │   │   └── knowledge_repo.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities.py
│   │   │   ├── comfort_entities.py
│   │   │   └── exceptions.py
│   │   ├── logs/                 # 日志系统
│   │   │   ├── __init__.py
│   │   │   └── operation_logger.py  # 操作日志（文件系统 JSON Lines）
│   │   ├── tools/                # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── downloader.py
│   │   │   ├── file_ops.py
│   │   │   ├── image_search.py
│   │   │   ├── terminal.py
│   │   │   └── web_scraper.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── sse_helper.py     # SSE 事件格式化
│   │   │   ├── file_parser.py
│   │   │   └── encryption.py     # 加密工具
│   │   └── docs/                 # 文档解析
│   │       ├── __init__.py
│   │       └── parser.py
│   ├── config.py                 # Pydantic Settings 配置
│   └── main.py                   # FastAPI 应用入口
├── requirements.txt
└── .env.example
```

### 聊天 Agent 执行流

```
START → rag_node → agent → [conditional]
                            │
              有 tool_calls → tool_node → 回到 agent
              无 tool_calls → END
```

- **rag_node**：根据最后一条用户消息从 ChromaDB 检索相关知识片段，注入 `rag_context`。
- **agent_node**：调用 LLM 进行推理，LLM 可输出 `tool_calls`。通过 `dispatch_custom_event()` 实时推送 `reasoning_token`（DeepSeek 思考过程）和 `reasoning_end`（思考结束信号），service.py 在思考期间缓存 content token，收到 `reasoning_end` 后一次性释放，实现"先思考后输出"。
- **tool_node**：并行执行 `tool_calls` 中注册的工具，通过 `dispatch_custom_event()` 向前端发送进度和结果事件。
- 对话状态通过 `AsyncSqliteSaver` 持久化到 `_graph.db`，以 `conversation_id` 作为 `thread_id`。
- 图编译时通过 config 设置 `recursion_limit=100`，避免多工具调用场景触达默认 25 步上限。

### 哄哄模拟器 Agent 执行流

```
START → emotion_node → rag_node → comfort_agent → [conditional]
                                                    │
                                      有 tool_calls → tool_node → 回到 comfort_agent
                                      无 tool_calls → forgiveness_node → END
```

- **emotion_node**：分析用户输入的情绪（anger/sadness/anxiety/fatigue/calm/joy/fear），输出 `emotion_result`。
- **rag_node**：复用聊天模块的 RAG 检索节点。
- **comfort_agent**：使用情绪分析结果和角色人设生成安抚回复。
- **forgiveness_node**：根据回复质量计算原谅值变化（forgiveness_result），梯度随难度和对话轮次衰减。
- 使用独立的 checkpointer（`_comfort_graph.db`），与聊天 Agent 互不干扰。
- AgentState 通过 `comfort_metadata` 字段传递场景/角色/难度等上下文。

### 多模型支持

`LLMFactory` 统一管理模型实例化，支持 provider：`openai`、`deepseek`、`qwen`、`zhipu`、`ollama`。可用模型列表定义在 `app/common/core/llm_factory.py` 的 `AVAILABLE_MODELS` 中。

**DeepSeek thinking mode**：当 `reasoning_effort` 为 `high` 或 `max` 时，通过 `extra_body={"thinking": {"type": "enabled"}}` 开启 DeepSeek 思考模式，LLM 在响应中返回 `reasoning_content` 字段。通过 monkey-patch（`_convert_delta_to_message_chunk` / `_convert_message_to_dict`）从 stream delta 中捕获 `reasoning_content` 存入 `additional_kwargs`，并在消息序列化时回传。`reasoning_effort="disabled"` 时设置 `extra_body={"thinking": {"type": "disabled"}}` 以关闭思考模式。

### SSE 流式响应

聊天接口 `POST /api/v1/chat/send` 返回 `text/event-stream`。`ChatService.stream_chat` 通过 `graph.astream_events` 订阅事件并格式化为 SSE：

| 事件类型 | 说明 |
|---------|------|
| `token` | LLM 流式输出片段（思考结束后一次性释放） |
| `reasoning_token` | DeepSeek 思考过程实时流（先思考后输出） |
| `reasoning_end` | 思考结束信号，标记推理完成 |
| `tool_start` / `tool_result` | 工具调用开始与结果 |
| `thinking` | 思考/观察步骤 |
| `progress` | 多工具执行进度 |
| `done` / `error` | 完成或错误 |
| `emotion` | 情绪分析结果（哄哄模拟器） |
| `forgiveness` | 原谅值变化（哄哄模拟器） |

SSE 格式化函数位于 `backend/app/common/utils/sse_helper.py`。

### ChatRequest 参数（POST /api/v1/chat/send）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `message` | string | 必填 | 用户消息 |
| `conversation_id` | string | 必填 | 对话 ID |
| `model_provider` | string | `"deepseek"` | 模型提供商 |
| `model_name` | string | `""` | 模型名称（空则使用各 provider 默认） |
| `reasoning_effort` | string | `"high"` | DeepSeek thinking 深度：`high` / `max` / `disabled` |
| `web_search_enabled` | bool | `false` | 是否启用联网搜索 |
| `deep_thinking_enabled` | bool | `true` | 是否展示思考过程（为 false 时 content 直出，不经过 token 缓存） |
| `attachments` | list[string] | `null` | 附件 file_id 列表 |
| `knowledge_doc_ids` | list[string] | `null` | 知识库文档 ID 列表 |
| `comfort_mode` | bool | `false` | 是否为哄哄模拟器模式 |

### 数据库表结构

所有业务数据存储在 **MySQL** 中，通过 `app/common/core/database.py` 统一管理。模块特有的表在各模块 `database.py` 中定义（`main.py` lifespan 中顺序初始化）：
- 共享表（8 张）：`conversations`、`messages`、`users`、`knowledge_docs`、`langgraph_checkpoints`、`langgraph_checkpoint_writes`、`shared_schema_version`
- 系统管理（5 张）：`system_roles`、`system_user_profiles`、`system_user_roles`、`system_audit_logs`、`system_settings`
- 哄哄模拟器（4 张）：`comfort_scenes`、`comfort_characters`、`comfort_memories`、`emotion_statistics`
- AI 测试助手（20 张）：`testing_projects`、`testing_project_members`、`testing_cases`、`testing_generation_tasks`、`testing_generation_results`、`testing_reviews` 等
- 配置中心（6 张）：`config_models`、`config_prompts`、`config_behaviors`、`config_chat`、`config_ui_env`、`config_app_env`

完整表结构文档详见 `docs/技术/数据库/`。

LangGraph 执行状态（checkpoint）仍使用独立的 **SQLite** 文件存储（`_graph.db`、`_comfort_graph.db`、`_testing_graph.db`）。

### AI 测试助手 Agent 执行流

```
START → analyze_node → write_node → review_node → [conditional]
                                                    │
                                      review_passed → pass_through → END
                                      review_failed → revise_node → END
```

- **analyze_node**：需求分析，提取功能点/边界条件/异常场景，输出分析报告。
- **write_node**：基于分析结果编写结构化测试用例（含前置条件/步骤/预期结果）。
- **review_node**：AI 评审，输出 JSON 格式的评分（7 维度 1-10 分）+ 改进建议。优先使用 `with_structured_output`，降级为 JSON 解析。
- **revise_node**：根据评审反馈修订用例（仅在 `review_passed=false` 时执行）。
- **pass_through**：评审通过时将草稿直接作为最终用例。
- State 通过 `TestCaseGenState`（TypedDict）定义，包含 `requirement_text`、`analysis_result`、`test_cases_draft`、`review_result`、`review_passed`、`final_test_cases` 等字段。
- 使用独立 checkpointer（`_testing_graph.db`），通过 `ManagedTestingGraph`（继承 `ManagedGraphBase`）管理生命周期。
- SSE 流通过 `astream_events(v2)` + `langgraph_node` 元数据过滤 token，防止子节点输出泄露。

### AI 测试助手 SSE 事件

`GET /api/v1/testing/generate/{task_id}/stream` 返回 `text/event-stream`：

| 事件类型 | 说明 |
|---------|------|
| `testing_stage` | 阶段切换（analyze/write/review/revise） |
| `testing_token` | 流式 token（带 stage 标签） |
| `testing_review` | 评审结果（结构化 JSON：评分/维度/问题/建议） |
| `testing_progress` | 进度更新（current/total/message） |
| `testing_done` | 生成完成（task_id/generated_count/review_passed） |
| `testing_error` | 错误信息（code/message） |

### AI 测试助手数据库表

在 `app/modules/ai_testing/database.py` 的 `init_testing_tables()` 中创建（`main.py` lifespan 调用），目前共 **20 张表**（经过 15 个迁移版本累积）：

**核心业务表（6 张）**：
| 表名 | 主要字段 |
|------|----------|
| `testing_projects` | id, name, description, status(active/paused/completed/archived), created_at |
| `testing_project_members` | id, project_id FK, name, role(owner/tester/viewer) |
| `testing_project_member_links` | (project_id, member_id) PK，多对多关联 |
| `testing_cases` | id, project_id FK, title, version, priority(P0-P3), case_type, preconditions/steps/expected_results, tags(JSON), status, source, ai_task_id |
| `testing_generation_tasks` | id, project_id FK, input_text, file_path, file_type, file_name, model, status, generated_count |
| `testing_generation_results` | id, task_id FK, stage, content |

**扩展业务表（5 张）**：
| 表名 | 主要字段 |
|------|----------|
| `testing_reviews` | 评审主表：project_id, title, priority, status, progress |
| `testing_review_cases` | 评审-用例关联：review_id, case_id, status |
| `testing_review_reviewers` | 评审人：review_id, member_id, status, progress |
| `testing_config` | 配置表：key, value, category(model/prompt/behavior/secret) |
| `testing_project_versions` | 项目版本：name, description, status, pass_rate |

**辅助表（9 张）**：
| 表名 | 主要字段 |
|------|----------|
| `testing_case_attachments` | 用例附件：file_name, file_path, file_type |
| `testing_case_comments` | 用例评论：content, author |
| `testing_operation_logs` | 操作日志：entity_type, entity_id, action |
| `testing_task_generated_cases` | 生成任务-用例桥接 |
| `testing_generated_case_items` | 生成候选用例项 |
| `testing_ai_tester_sessions` | AI 评测师会话 |
| `testing_ai_tester_messages` | AI 评测师消息 |
| `testing_scheduled_tasks` | 定时任务配置 |
| `testing_scheduled_task_logs` | 定时任务执行日志 |

完整字段定义见 `docs/技术/数据库/AI测试助手模块.md`。

## 前端架构

### 目录结构（模块化）

```
frontend/src/
├── shared/                          # 公共模块
│   ├── api/
│   │   ├── request.ts               # Axios 实例，baseURL 为 /api/v1
│   │   ├── conversation.ts          # 对话 API
│   │   └── models.ts                # 模型列表 API
│   ├── stores/
│   │   ├── conversation.ts          # 对话会话状态
│   │   └── settings.ts              # 模型/设置状态
│   ├── types/
│   │   ├── api.ts                   # 通用 API 类型
│   │   └── conversation.ts          # 对话类型
│   ├── composables/
│   │   ├── useSseStream.ts          # SSE 流式消费（fetch + ReadableStream）
│   │   └── useMarkdownRenderer.ts   # Markdown 渲染
│   ├── components/
│   │   ├── layout/                  # AppHeader, AppSidebar
│   │   ├── common/                  # GlassCard, NeonCard, ModelSelector
│   │   ├── message/                 # MarkdownBody, FilePreview, ImagePreview
│   │   └── sidebar/                 # ConversationList, KnowledgePanel
│   ├── views/
│   │   └── HomeView.vue             # 首页
│   └── router/
│       └── index.ts                 # 路由配置
│
├── modules/
│   ├── chat/                        # AI 聊天室
│   │   ├── api/chat.ts
│   │   ├── stores/chat.ts
│   │   ├── types/chat.ts
│   │   ├── composables/useAtMention.ts
│   │   ├── components/ (ChatInput, ChatMessage, ChatMessageList, ReasoningBlock,
│   │   │                ToolCallStatus, AgentProgressBar, KnowledgePopover, StreamingCursor)
│   │   └── views/ChatView.vue
│   │
│   ├── comfort/                     # 哄哄模拟器
│   │   ├── api/comfort.ts
│   │   ├── stores/comfort.ts
│   │   ├── types/comfort.ts
│   │   ├── components/ (ComfortSetupModal, EmotionBadge, ForgivenessBar, MemoryManager,
│   │   │                EmotionPanel, CharacterAvatar, ComfortMessage, ComfortMessageList)
│   │   └── views/ (ComfortView.vue, EmotionDashboardView.vue)
│   │
│   └── knowledge/                   # 知识库管理
│       ├── api/knowledge.ts
│       ├── stores/knowledge.ts
│       ├── types/knowledge.ts
│       └── views/KnowledgeView.vue
│
│   └── ai_testing/                  # AI 测试助手
│       ├── api/
│       │   ├── project.ts           # 项目 CRUD + 成员 API
│       │   ├── testcase.ts          # 用例 CRUD + Excel API
│       │   └── generation.ts        # 生成任务 + 配置 API
│       ├── components/
│       │   ├── generation/          # SetupGuideModal
│       │   ├── project/             # ProjectForm
│       │   ├── testcase/            # MarkdownField (md-editor-v3)
│       │   └── common/              # StatusTag, PriorityBadge, FilterBar
│       ├── composables/
│       │   └── useGenerationStream.ts  # 专用 SSE composable (EventSource)
│       ├── stores/
│       │   ├── project.ts           # 项目列表 Pinia store
│       │   ├── testcase.ts          # 用例列表 Pinia store
│       │   └── generation.ts        # 流式生成状态 Pinia store
│       ├── types/
│       │   ├── project.ts
│       │   ├── testcase.ts
│       │   └── generation.ts
│       └── views/
│           ├── GenerationView.vue     # AI 用例助手主页
│           ├── ProjectListView.vue    # 项目列表
│           ├── ProjectDetailView.vue  # 项目详情
│           ├── TestCaseListView.vue   # 用例列表（含 Excel 导入导出）
│           ├── TestCaseFormView.vue   # 新建/编辑用例（Markdown 富文本）
│           ├── TestCaseDetailView.vue # 用例详情
│           └── SettingsView.vue       # AI 生成配置页
│
├── main.ts               # 入口（从 shared/router 导入路由）
├── App.vue
├── vite.config.ts         # @/ 路径别名 + unplugin-auto-import（含 @vueuse/core 函数声明）
├── assets/styles/         # 样式
├── auto-imports.d.ts
└── components.d.ts
```

### 关键机制

**SSE 流式处理**：`useSseStream` 封装了 `fetch` + `ReadableStream` 的 SSE 消费逻辑，解析后端推送的事件并调用 `chatStore` 或 `comfortStore` 的方法更新 UI 状态。支持事件类型：`token`（RAF 批处理）、`reasoning_token`（实时追加推理内容）、`reasoning_end`（标记推理完成）、`tool_start/tool_result`、`thinking`、`progress`、`done`/`error`。

**先思考后输出**：后端 `service.py` 在思考期间（`reasoning_token` 阶段）缓存所有 content token，收到 `reasoning_end` 后一次性释放并刷新 SSE 流。前端 `ReasoningBlock` 组件在推理流式时展开显示 `🧠` 块，推理完成后折叠为"已深度思考（X秒）"。通过 `streamState.reasoningComplete` 控制展开/折叠状态。

**路径别名**：`@/` 映射到 `./src/`，在 `vite.config.ts` 和 `tsconfig.json` 中配置。所有模块间的 import 统一使用 `@/` 前缀。

**自动导入**：`unplugin-auto-import` 自动导入 `vue`、`vue-router`、`pinia`；`@vueuse/core` 使用内置 preset 自动导入大部分常用函数。不在内置 preset 中的函数（如 `useDebounceFn`）需在 `vite.config.ts` 的 `AutoImport` 配置中通过 `{ '@vueuse/core': ['函数名'] }` 显式声明。`unplugin-vue-components` 按需自动导入 Naive UI 组件。类型声明文件为 `src/auto-imports.d.ts` 和 `src/components.d.ts`。

> **注意**：新增 `@vueuse/core` 函数引用后，需同步更新 `vite.config.ts` 的 `AutoImport` 配置，否则运行时 Vue setup 阶段会报缺失函数引用错误。`auto-imports.d.ts` 会在 dev server 重启后自动重新生成。

**API 代理**：开发模式下，`vite.config.ts` 将 `/api` 代理到 `http://localhost:8000`，前端代码中直接以 `/api/v1/...` 发起请求。

## 数据持久化

- **业务数据（MySQL）**：所有模块的业务数据存储在 MySQL 中（conversations, messages, users, comfort_*, testing_*, config_*, system_* 等 40+ 张表），通过 `app/common/core/database.py` 的 aiomysql 连接池管理。
- **LangGraph 执行状态（SQLite）**：各模块的 LangGraph graph 使用独立的 SQLite 文件存储 thread checkpoint（`_graph.db`、`_comfort_graph.db`、`_testing_graph.db`）。
- **ChromaDB**：向量数据库，用于知识库文档的 embedding 存储与相似度检索，持久化目录由 `CHROMA_PERSIST_DIR` 指定。
- **文件存储**：上传的知识库文件存入 `UPLOAD_DIR`，应用生成的文件存入 `WORKSPACE_DIR`。

## 添加新工具

如需扩展 Agent 的工具能力：

1. 在 `backend/app/common/agent/tools/` 下新建工具模块，实现 `BaseTool` 子类。
2. 在 `backend/app/common/agent/tools/__init__.py` 的 `TOOL_REGISTRY` 中注册。
3. 在 `DISPLAY_NAMES` 和 `info_map` 中添加前端展示用的名称与图标分类。
4. `agent_node.py` 支持条件绑定：`web_search_enabled=False` 时自动移除 `web_search` 工具。
5. 前端无需额外修改，工具列表通过 `/api/v1/tools` 动态获取。

如需扩展哄哄模拟器的场景/角色：

1. 在 `backend/app/comfort/scene_seed.py` 中添加内置场景或角色数据。
2. 前端 `comfortStore` 会自动通过 API 获取并缓存。

## 注意事项

- 后端目前 **没有测试文件**（`tests/` 目录不存在），新增代码时建议遵循 `.qoder/rules/test-standard.md` 补充测试
- 哄哄模拟器使用独立于聊天模块的 LangGraph graph 和 checkpoint 数据库，两者通过共享的 `AgentState` 类型进行状态传递
- 内置场景/角色数据在应用启动时通过 `seed_builtin_data()` 自动初始化，重复启动不会重复插入
- Graph 对象通过模块级变量（`_agent_graph` / `_comfort_graph`）缓存为单例，修改节点逻辑后需重启后端才能生效
- `duck checker`：后端使用**双存储**模式——MySQL 存储所有业务数据（消息、会话、用例等），独立的 SQLite 文件（`_graph.db` / `_comfort_graph.db` / `_testing_graph.db`）存储各模块 LangGraph 执行状态（thread checkpoint）
- 事件管道：所有 node 通过 `dispatch_custom_event()` 发送自定义事件，service.py 通过 `graph.astream_events(version="v2")` 消费。**不要使用 `StreamWriter`**（已被 `astream_events` 忽略）
- 递归限制：`recursion_limit=100` 设置在 `service.py` 的 config 中，而非 `graph.compile()` — 后者不支持该参数