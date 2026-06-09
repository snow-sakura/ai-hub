# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目结构概览

```
qoder_one/
├── ai-hub/    # 主要项目：AI 测试平台（全栈 AI 聊天应用）
├── .qoder/              # Qoder 平台配置
│   ├── agents/          # AI Agent 定义（code-reviewer, security-scanner 等）
│   └── rules/           # 项目规范（架构、代码风格、测试、安全等）
└── .claude/             # Claude 配置
```

## AI 测试平台（ai-hub/）

基于 LangGraph 的全栈 AI 聊天应用，支持多模型、RAG 知识库检索和工具调用。

详细文档见 `ai-hub/CLAUDE.md`。

### 常用命令

```bash
# 使用 Docker Compose 同时启动前后端
cd ai-hub && docker-compose up

# 独立启动后端
cd ai-hub/backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 独立启动前端
cd ai-hub/frontend
npm run dev       # 开发服务器，端口 5173
npm run build     # 生产构建
```

### 技术栈

- **后端**：Python FastAPI + LangGraph + LangChain + SQLite + ChromaDB
- **前端**：Vue 3 + TypeScript + Vite + Naive UI + Pinia

### 后端分层架构

```
API（路由/入参校验）→ Service（业务编排）→ Repository（数据访问）→ Domain（领域实体）
```

核心约束：
- API 层不得直接访问数据库
- Service 层是唯一可操作数据库的模块
- `core/` 模块不得引用业务代码
- 禁止反向依赖和循环依赖

### 前端架构

- Vue 3 Composition API + `<script setup>` 语法
- 自动导入（`unplugin-auto-import` + `unplugin-vue-components`），无需手动 import
- SSE 流式响应处理（`useSseStream` composable）
- 开发模式下 Vite 代理 `/api` 到 `http://localhost:8000`

## Qoder 规范（.qoder/rules/）

以下规范文件对代码编写有约束力：

### 代码风格（code-style.md）
- 缩进：2 个空格，禁用 Tab
- 行宽：≤ 100 字符
- 分号：必须省略
- 命名：变量/函数使用 `camelCase`，类/组件使用 `PascalCase`，常量使用 `UPPER_SNAKE_CASE`
- 布尔变量：前缀 `is`/`has`

### 架构约束（architecture.md）
- 严格分层：API → Service → Repository → Domain
- 禁止跨层调用（如 API 直接调 Repository）
- 禁止循环依赖
- 工具函数必须放在 `/utils`

### 测试标准（test-standard.md）
- 遵循测试金字塔：大量单元 + 适量集成 + 少量 E2E
- 测试用例必须使用 AAA 模式（Arrange → Act → Assert）
- 使用等价类划分、边界值分析、判定表等方法设计测试
- 断言必须明确，禁止模糊断言

### 安全规范（security.md）
- API 入参必须经过校验
- 禁止硬编码凭证
- 禁止使用 `eval()`/`Function()` 动态执行代码
