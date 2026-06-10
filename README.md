# AI Hub — AI-HUB工作台

基于 LangGraph 的全栈 AI 智能平台，支持多模型对话、RAG 知识库检索、工具调用和情绪安抚模拟。

## 功能特性

- **⚡ AI 聊天室** — 多模型自由切换（DeepSeek、Qwen、OpenAI 等），流式 SSE 输出，自动规划复杂任务
- **💖 哄哄模拟器** — 角色扮演情绪安抚场景，情绪分析 + 原谅值系统 + 情绪统计看板
- **🎯 知识库管理** — 上传 PDF/Word/TXT 文档，向量化存储，聊天时自动检索相关片段
- **🔧 内置工具库** — Web 搜索、网页抓取、图片搜索、文件处理、PDF 生成、终端执行等 7 大工具
- **🧠 思考过程** — 类 DeepSeek/Kimi 的思考链展示，折叠式时间轴，推理过程透明可见
- **📋 对话管理** — 自动生成标题、历史记录侧边栏、按时间分组

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Naive UI + Pinia |
| 后端 | Python FastAPI + LangGraph + LangChain |
| 数据库 | SQLite（对话持久化）+ ChromaDB（向量检索）|
| AI 模型 | DeepSeek / Qwen / OpenAI / Zhipu / Ollama |

## 快速开始

### 前置要求

- Node.js >= 18
- Python >= 3.12
- 至少一个 LLM 的 API Key

### 1. 配置后端

```bash
cd ai-hub/backend
cp .env.example .env
# 编辑 .env 填入 API Key
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动后端

```bash
cd ai-hub/backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 启动前端

```bash
cd ai-hub/frontend
npm install
npm run dev
```

打开浏览器访问 `http://localhost:5173`。

### Docker 方式

```bash
cd ai-hub
docker-compose up
```

## 项目结构

```
qoder_one/
├── ai-hub/                # 主项目
│   ├── backend/           # Python FastAPI 后端
│   │   ├── app/
│   │   │   ├── api/v1/    # 路由层（chat, conversation, knowledge, comfort, models）
│   │   │   ├── api/schemas/# Pydantic 请求/响应模型
│   │   │   ├── service/   # 业务逻辑层（chat, conversation, knowledge, comfort）
│   │   │   ├── repository/# 数据访问层（conversation, knowledge, comfort）
│   │   │   ├── agent/     # 聊天 LangGraph Agent（graph, state, nodes, tools）
│   │   │   ├── comfort/   # 哄哄模拟器 LangGraph Agent（独立 graph, nodes, 情绪分析, 原谅值引擎）
│   │   │   ├── core/      # LLM 工厂、数据库、Embedding
│   │   │   └── domain/    # 领域实体与异常
│   │   └── main.py
│   ├── frontend/          # Vue 3 前端（模块化架构）
│   │   └── src/
│   │       ├── shared/    # 公共模块（路由/布局/通用组件/Store/API/Composable）
│   │       ├── modules/   # 业务模块（chat/ comfort/ knowledge/，各含 views/components/stores/api/types）
│   │       └── App.vue
│   └── docker-compose.yml
├── .qoder/                # AI Agent 定义与项目规范
└── CLAUDE.md              # Claude Code 协作指引
```

## 环境变量

参见 `ai-hub/backend/.env.example`，核心配置：

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI 兼容接口密钥 |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 |
| `QWEN_API_KEY` | 通义千问 API 密钥 |
| `ZHIPU_API_KEY` | 智谱 API 密钥 |
