# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

AI 测试平台（AI Test Platform）——基于 LangGraph 的全栈 AI 聊天应用，支持多模型、RAG 知识库检索和工具调用。

- **后端**：Python FastAPI + LangGraph + LangChain + SQLite + ChromaDB
- **前端**：Vue 3 + TypeScript + Vite + Naive UI + Pinia

## 常用命令

### 启动开发环境

```bash
# 方式一：Docker Compose 同时启动前后端
docker-compose up

# 方式二：独立启动后端
cd backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# 或 python main.py

# 方式三：独立启动前端
cd frontend
npm run dev        # 开发服务器，端口 5173
npm run build      # 生产构建（先执行 vue-tsc 类型检查）
npm run preview    # 预览生产构建
```

### 环境配置

首次运行后端前，复制环境变量文件：

```bash
cp backend/.env.example backend/.env
```

然后在 `.env` 中填入至少一个 LLM Provider 的 API Key（OpenAI / Qwen / Zhipu / Ollama）。

## 后端架构

### 分层结构

```
app/
├── api/v1/          # FastAPI 路由层，按模块组织（chat, conversation, knowledge, models, tools）
├── api/schemas/     # Pydantic 请求/响应模型
├── service/         # 业务逻辑层（ChatService 是核心编排入口）
├── repository/      # 数据访问层（SQLite，aiosqlite 异步驱动）
├── core/            # 基础设施（database, llm_factory, embedding_factory）
├── agent/           # LangGraph Agent 核心
│   ├── graph.py     # 图构建与编译
│   ├── state.py     # AgentState 类型定义
│   ├── nodes/       # 图节点（rag_node, agent_node, tool_node）
│   ├── tools/       # 工具实现与注册表
│   └── prompts.py   # 系统提示词
├── domain/          # 领域实体与异常
└── utils/           # 工具函数（SSE 格式化、文本分割、文件解析）
```

### Agent 执行流

LangGraph 编译后的执行流程为：

```
START → rag_node → agent → [conditional]
                            │
              有 tool_calls → tool_node → 回到 agent
              无 tool_calls → END
```

- **rag_node**：根据最后一条用户消息从 ChromaDB 检索相关知识片段，注入 `rag_context`。
- **agent_node**：调用 LLM 进行推理，LLM 可输出 `tool_calls`。
- **tool_node**：并行执行 `tool_calls` 中注册的工具，通过 `StreamWriter` 向前端发送进度和结果事件。

对话状态通过 `AsyncSqliteSaver` 持久化到 SQLite（`app.db` 的同目录下生成 `_graph.db`），以 `conversation_id` 作为 `thread_id`。

### 多模型支持

`LLMFactory` 统一管理模型实例化，支持 provider：`openai`、`qwen`、`zhipu`、`ollama`。可用模型列表定义在 `app/core/llm_factory.py` 的 `AVAILABLE_MODELS` 中。

### SSE 流式响应

聊天接口 `POST /api/v1/chat/send` 返回 `text/event-stream`。`ChatService.stream_chat` 通过 `graph.astream_events` 订阅事件，将以下类型的事件格式化为 SSE：

- `token`：LLM 流式输出片段
- `tool_start` / `tool_result`：工具调用开始与结果
- `thinking`：思考/观察步骤
- `progress`：多工具执行进度
- `done` / `error`：完成或错误

## 前端架构

### 技术栈与约定

- **Vue 3 Composition API**，使用 `<script setup>` 语法。
- **自动导入**：`unplugin-auto-import` 自动导入 `vue`、`vue-router`、`pinia`、`@vueuse/core`，无需手动 import。
- **组件自动注册**：`unplugin-vue-components` 按需自动导入 Naive UI 组件，无需手动 import。
- 自动导入的类型声明文件为 `src/auto-imports.d.ts` 和 `src/components.d.ts`。

### 目录结构

```
src/
├── api/             # Axios 请求封装，按模块拆分（conversation, knowledge, models）
│   └── request.ts   # Axios 实例，baseURL 为 /api/v1
├── stores/          # Pinia 状态管理，按领域拆分（chat, conversation, knowledge, settings）
├── composables/     # 组合式函数（useSseStream, useMarkdownRenderer, useAtMention）
├── components/      # 组件
│   ├── chat/        # 聊天相关（ChatInput, ChatMessage, ChatMessageList, ThinkingProcess, ToolCallStatus）
│   ├── message/     # 消息内容渲染（MarkdownBody, ImagePreview, FilePreview）
│   ├── sidebar/     # 侧边栏（ConversationList, KnowledgePanel）
│   └── common/      # 通用（ModelSelector, GlassCard, NeonCard）
├── views/           # 页面级组件（HomeView, ChatView）
├── router/          # vue-router 配置
└── types/           # TypeScript 类型定义
```

### 关键机制

**SSE 流式处理**：`useSseStream` 封装了 `fetch` + `ReadableStream` 的 SSE 消费逻辑，解析后端推送的事件并调用 `chatStore` 的方法更新 UI 状态。

**API 代理**：开发模式下，`vite.config.ts` 将 `/api` 代理到 `http://localhost:8000`，前端代码中直接以 `/api/v1/...` 发起请求。

## 数据持久化

- **SQLite**：存储会话（conversations）和消息（messages），以及 LangGraph 的 checkpoint 状态。
- **ChromaDB**：向量数据库，用于知识库文档的 embedding 存储与相似度检索，持久化目录由 `CHROMA_PERSIST_DIR` 指定。
- **文件存储**：上传的知识库文件存入 `UPLOAD_DIR`，应用生成的文件存入 `WORKSPACE_DIR`。

## 添加新工具

如需扩展 Agent 的工具能力：

1. 在 `backend/app/agent/tools/` 下新建工具模块，实现 `BaseTool` 子类。
2. 在 `backend/app/agent/tools/__init__.py` 的 `TOOL_REGISTRY` 中注册。
3. 在 `DISPLAY_NAMES` 和 `info_map` 中添加前端展示用的名称与图标分类。
4. 前端无需额外修改，工具列表通过 `/api/v1/tools` 动态获取。
