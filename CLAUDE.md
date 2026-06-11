# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

本仓库是一个 monorepo，当前主要项目为 `ai-hub/`（AI 测试平台）。另有 `.qoder/`（Qoder 平台配置，含 Agent 定义和项目规范）和 `.claude/`（Claude 配置）。

**详细的技术文档、目录结构、执行流、数据库表定义等全部在 `ai-hub/CLAUDE.md` 中，务必先阅读该文件。**

## 项目结构

```
qoder_one/
├── ai-hub/              # 主项目：AI 测试平台
│   ├── backend/         # Python FastAPI + LangGraph 后端
│   ├── frontend/        # Vue 3 + TypeScript + Vite 前端
│   ├── docker-compose.yml
│   ├── backend/Dockerfile
│   └── frontend/Dockerfile
├── .qoder/              # Qoder 平台配置
│   ├── agents/          # AI Agent 定义（code-reviewer, security-scanner 等）
│   └── rules/           # 项目规范（架构、代码风格、测试、安全）
└── .claude/             # Claude 配置
```

## AI 测试平台（ai-hub/）

基于 LangGraph 的全栈 AI 应用，包含三大模块：
- **AI 聊天室** — 多模型对话 + RAG 知识库 + 工具调用
- **哄哄模拟器** — 角色扮演情绪安抚场景 + 原谅值系统 + 情绪统计看板
- **AI 测试助手** — 需求文档 → AI 4 步工作流（分析→编写→评审→修订）→ 测试用例全生命周期管理

### 常用命令

```bash
# 启动全部服务（Docker Compose）
cd ai-hub && docker-compose up

# 独立启动后端（开发模式，--reload 自动重载）
cd ai-hub/backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 独立启动前端（开发模式，端口 5173，代理 /api 到 8000）
cd ai-hub/frontend
npm run dev

# 前端生产构建（先执行 vue-tsc 类型检查）
npm run build

# 初始化环境
cd ai-hub/backend
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
cp .env.example .env   # 编辑 .env 填入至少一个 LLM Provider 的 API Key
cd ../frontend && npm install
```

### 技术栈

- **后端**：Python FastAPI + LangGraph + LangChain + SQLite (aiosqlite) + ChromaDB
- **前端**：Vue 3 + TypeScript + Vite + Naive UI + Pinia + Axios

### 后端分层架构

```
API（路由/入参校验）→ Service（业务编排）→ Repository（数据访问）→ Domain（领域实体）
```

核心约束（完整规范见 `.qoder/rules/architecture.md`）：
- API 层不得直接访问数据库
- Service 层是唯一可操作数据库的模块
- `shared/core/` 模块不得引用业务代码
- 禁止反向依赖和循环依赖

### 环境变量

在 `ai-hub/backend/.env` 中配置。至少需要配置一个 LLM Provider 的 API Key：
- **DeepSeek**（默认推荐，支持 thinking mode 思考过程流式输出）
- OpenAI / Qwen / Zhipu / Ollama（本地模型，无需 API Key）

可选：`PEXELS_API_KEY`、`UNSPLASH_ACCESS_KEY`（图片搜索）。

完整的可用模型列表定义在 `app/shared/core/llm_factory.py` 的 `AVAILABLE_MODELS` 中。

### SSE 事件类型

| 事件 | 说明 |
|------|------|
| `token` / `reasoning_token` / `reasoning_end` | LLM 流式输出 / DeepSeek 思考过程 / 思考结束 |
| `tool_start` / `tool_result` | 工具调用开始与结果 |
| `thinking` / `progress` | 思考步骤 / 多工具执行进度 |
| `done` / `error` | 完成或错误 |
| `emotion` / `forgiveness` | 情绪分析结果 / 原谅值变化（哄哄模拟器） |
| `testing_stage` / `testing_token` / `testing_review` / `testing_progress` / `testing_done` / `testing_error` | AI 测试助手各阶段事件 |

SSE 格式化代码在 `backend/app/shared/utils/sse_helper.py`，前端消费在 `frontend/src/shared/composables/useSseStream.ts`。

### DeepSeek 思考模式

- `reasoning_effort`：`high`（标准）、`max`（深度思考）、`disabled`（关闭）
- `deep_thinking_enabled`：控制前端是否展示思考过程
- `web_search_enabled`：控制是否绑定联网搜索工具
- 后端通过 monkey-patch `_convert_delta_to_message_chunk` / `_convert_message_to_dict` 捕获 `reasoning_content`

### 关键注意事项

- 后端目前 **没有测试文件**（`tests/` 目录不存在），新增代码时建议遵循 `.qoder/rules/test-standard.md`
- 前端 `npm run build` 会先执行 `vue-tsc -b` 类型检查，构建失败时优先排查类型错误
- 首个运行需复制 `backend/.env.example` 为 `.env` 并填入 API Key
- Graph 对象通过模块级变量缓存为单例，修改节点逻辑后需重启后端
- 所有模块的数据文件（SQLite DB、ChromaDB、uploads）存储在 `backend/data/` 目录下
- 前端使用 `unplugin-auto-import` + `unplugin-vue-components`，无需手动 import Vue/Naive UI；但 `@vueuse/core` 不在内置 preset 中的函数（如 `useDebounceFn`）需手动在 `vite.config.ts` 的 AutoImport 配置中声明