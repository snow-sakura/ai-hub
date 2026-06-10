# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

AI 测试平台（AI Test Platform）——基于 LangGraph 的全栈 AI 应用，包含两大模块：

- **AI 聊天室**：多模型对话 + RAG 知识库 + 工具调用
- **哄哄模拟器**：角色扮演情绪安抚场景 + 原谅值系统 + 情绪统计看板

## 技术栈

- **后端**：Python FastAPI + LangGraph + LangChain + SQLite + ChromaDB
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
│   ├── api/v1/          # FastAPI 路由层
│   │   ├── chat.py           # 聊天 SSE 端点
│   │   ├── conversation.py   # 会话 CRUD
│   │   ├── knowledge.py      # 知识库管理
│   │   ├── models.py         # 模型列表
│   │   ├── tools.py          # 工具列表
│   │   ├── comfort.py        # 哄哄模拟器 CRUD + 统计
│   │   └── router.py         # 路由聚合，注册所有模块
│   ├── api/schemas/     # Pydantic 请求/响应模型
│   │   ├── chat.py
│   │   ├── conversation.py
│   │   ├── knowledge.py
│   │   ├── common.py         # ApiResponse 泛型包装
│   │   └── comfort.py        # 哄哄模拟器场景/角色/记忆/统计 Schema
│   ├── service/         # 业务逻辑层
│   │   ├── chat_service.py         # 聊天核心编排
│   │   ├── conversation_service.py
│   │   ├── knowledge_service.py
│   │   └── comfort_service.py      # 哄哄业务：场景/角色/记忆/统计/会话
│   ├── repository/      # 数据访问层（SQLite，aiosqlite 异步驱动）
│   │   ├── conversation_repo.py
│   │   ├── knowledge_repo.py
│   │   └── comfort_repo.py         # 哄哄表：scenes/characters/memories/emotion_stats
│   ├── core/            # 基础设施
│   │   ├── database.py           # SQLite 连接管理 + 表创建
│   │   ├── llm_factory.py        # LLM 工厂（多 provider）
│   │   └── embedding_factory.py  # Embedding 工厂
│   ├── agent/           # AI 聊天室 LangGraph Agent
│   │   ├── graph.py         # 图构建与编译
│   │   ├── state.py         # AgentState（含 comfort 扩展字段）
│   │   ├── prompts.py       # 系统提示词
│   │   ├── nodes/           # 图节点
│   │   │   ├── agent_node.py   # LLM 推理节点
│   │   │   ├── rag_node.py     # ChromaDB 检索
│   │   │   └── tool_node.py    # 工具执行节点
│   │   └── tools/           # 工具实现
│   │       ├── web_search.py
│   │       ├── web_scraper.py
│   │       ├── image_search.py
│   │       ├── pdf_generator.py
│   │       ├── file_ops.py
│   │       ├── downloader.py
│   │       └── terminal.py
│   ├── comfort/         # 哄哄模拟器 LangGraph Agent
│   │   ├── graph.py            # 图构建（独立 checkpointer）
│   │   ├── scene_seed.py       # 内置场景/角色种子数据
│   │   ├── emotion_analyzer.py # 情绪分析逻辑
│   │   ├── forgiveness_engine.py # 原谅值计算引擎
│   │   ├── comfort_prompts.py  # 系统提示词
│   │   └── nodes/
│   │       ├── emotion_node.py     # 情绪分析节点
│   │       ├── comfort_agent_node.py # 安抚回复生成节点
│   │       └── forgiveness_node.py # 原谅值计算节点
│   ├── domain/          # 领域实体与异常
│   │   ├── entities.py
│   │   ├── comfort_entities.py # ComfortScene/Character/Memory/EmotionResult/ForgivenessResult
│   │   └── exceptions.py
│   └── utils/
│       └── sse_helper.py      # SSE 事件格式化（含 emotion/forgiveness 事件）
├── main.py              # FastAPI 应用入口
├── config.py            # Pydantic Settings 配置
└── requirements.txt     # 依赖清单
```

### 聊天 Agent 执行流

```
START → rag_node → agent → [conditional]
                            │
              有 tool_calls → tool_node → 回到 agent
              无 tool_calls → END
```

- **rag_node**：根据最后一条用户消息从 ChromaDB 检索相关知识片段，注入 `rag_context`。
- **agent_node**：调用 LLM 进行推理，LLM 可输出 `tool_calls`。
- **tool_node**：并行执行 `tool_calls` 中注册的工具，通过 `StreamWriter` 向前端发送进度和结果事件。
- 对话状态通过 `AsyncSqliteSaver` 持久化到 `_graph.db`，以 `conversation_id` 作为 `thread_id`。

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

`LLMFactory` 统一管理模型实例化，支持 provider：`openai`、`deepseek`、`qwen`、`zhipu`、`ollama`。可用模型列表定义在 `app/core/llm_factory.py` 的 `AVAILABLE_MODELS` 中。

### SSE 流式响应

聊天接口 `POST /api/v1/chat/send` 返回 `text/event-stream`。`ChatService.stream_chat` 通过 `graph.astream_events` 订阅事件并格式化为 SSE：

| 事件类型 | 说明 |
|---------|------|
| `token` | LLM 流式输出片段 |
| `tool_start` / `tool_result` | 工具调用开始与结果 |
| `thinking` | 思考/观察步骤 |
| `progress` | 多工具执行进度 |
| `done` / `error` | 完成或错误 |
| `emotion` | 情绪分析结果（哄哄模拟器） |
| `forgiveness` | 原谅值变化（哄哄模拟器） |

SSE 格式化函数位于 `backend/app/utils/sse_helper.py`。

### 数据库表结构

表在 `app/core/database.py` 的 `init_db()` 中创建。模块特有的表在各模块 repo 中创建：
- 聊天相关：`conversations`、`messages` + `_graph.db`（LangGraph checkpoint）
- 知识库相关：`documents`、`chunks` + ChromaDB（向量检索）
- 哄哄模拟器：`comfort_scenes`、`comfort_characters`、`comfort_memories`、`emotion_stats`
- 内置场景/角色数据在 `app/comfort/scene_seed.py` 中通过 `seed_builtin_data()` 初始化

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
│   │   ├── components/ (ChatInput, ChatMessage, ChatMessageList, ThinkingProcess,
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
├── main.ts               # 入口（从 shared/router 导入路由）
├── App.vue
├── vite.config.ts         # 配置了 @/ 路径别名
├── assets/styles/         # 样式
├── auto-imports.d.ts
└── components.d.ts
```

### 关键机制

**SSE 流式处理**：`useSseStream` 封装了 `fetch` + `ReadableStream` 的 SSE 消费逻辑，解析后端推送的事件并调用 `chatStore` 或 `comfortStore` 的方法更新 UI 状态。

**路径别名**：`@/` 映射到 `./src/`，在 `vite.config.ts` 和 `tsconfig.json` 中配置。所有模块间的 import 统一使用 `@/` 前缀。

**自动导入**：`unplugin-auto-import` 自动导入 `vue`、`vue-router`、`pinia`、`@vueuse/core`；`unplugin-vue-components` 按需自动导入 Naive UI 组件。类型声明文件为 `src/auto-imports.d.ts` 和 `src/components.d.ts`。

**API 代理**：开发模式下，`vite.config.ts` 将 `/api` 代理到 `http://localhost:8000`，前端代码中直接以 `/api/v1/...` 发起请求。

## 数据持久化

- **聊天 SQLite**：存储会话（conversations）和消息（messages），以及 LangGraph 的 checkpoint（`_graph.db`）。
- **哄哄 SQLite**：`comfort_scenes`、`comfort_characters`、`comfort_memories`、`emotion_stats` 表 + 独立的 checkpoint（`_comfort_graph.db`）。
- **ChromaDB**：向量数据库，用于知识库文档的 embedding 存储与相似度检索，持久化目录由 `CHROMA_PERSIST_DIR` 指定。
- **文件存储**：上传的知识库文件存入 `UPLOAD_DIR`，应用生成的文件存入 `WORKSPACE_DIR`。

## 添加新工具

如需扩展 Agent 的工具能力：

1. 在 `backend/app/agent/tools/` 下新建工具模块，实现 `BaseTool` 子类。
2. 在 `backend/app/agent/tools/__init__.py` 的 `TOOL_REGISTRY` 中注册。
3. 在 `DISPLAY_NAMES` 和 `info_map` 中添加前端展示用的名称与图标分类。
4. 前端无需额外修改，工具列表通过 `/api/v1/tools` 动态获取。

如需扩展哄哄模拟器的场景/角色：

1. 在 `backend/app/comfort/scene_seed.py` 中添加内置场景或角色数据。
2. 前端 `comfortStore` 会自动通过 API 获取并缓存。

## 注意事项

- 后端目前 **没有测试文件**（`tests/` 目录不存在），新增代码时建议遵循 `.qoder/rules/test-standard.md` 补充测试
- 哄哄模拟器使用独立于聊天模块的 LangGraph graph 和 checkpoint 数据库，两者通过共享的 `AgentState` 类型进行状态传递
- 内置场景/角色数据在应用启动时通过 `seed_builtin_data()` 自动初始化，重复启动不会重复插入