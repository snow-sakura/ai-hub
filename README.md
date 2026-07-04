# Qoder One — AI 测试平台集合

本仓库是一个 monorepo，包含两个核心测试平台项目：

- **AI-HUB** — 基于 LangGraph 的全栈 AI 智能平台
- **TestHub** — 基于 Django + Vue 的智能测试管理平台

---

## 📁 项目结构

```
qoder_one/
├── ai-hub/                # AI 智能测试平台（LangGraph + FastAPI + Vue 3）
│   ├── backend/           # Python FastAPI 后端
│   ├── frontend/          # Vue 3 + TypeScript 前端
│   ├── docs/              # 技术文档
│   └── docker-compose.yml # Docker 部署配置
├── testhub/               # 智能测试管理平台（Django + Vue 3）
│   ├── apps/              # Django 应用模块
│   ├── backend/           # Django 项目配置
│   ├── frontend/          # Vue 3 前端
│   ├── ai_doc/            # AI 生成的需求文档
│   └── docs/              # 技术文档
├── picture/               # 设计原型图片资源
├── .qoder/                # Qoder 平台配置
│   ├── agents/            # AI Agent 定义
│   └── rules/             # 项目规范
├── claude.md              # Claude Code 协作指引
└── README.md              # 本文件
```

---

## 🤖 AI-HUB — AI 智能平台

基于 LangGraph 的全栈 AI 智能平台，支持多模型对话、RAG 知识库检索、工具调用和情绪安抚模拟。

### 功能特性

- **⚡ AI 聊天室** — 多模型自由切换（DeepSeek、Qwen、OpenAI 等），流式 SSE 输出，自动规划复杂任务
- **💖 哄哄模拟器** — 角色扮演情绪安抚场景，情绪分析 + 原谅值系统 + 情绪统计看板
- **🎯 知识库管理** — 上传 PDF/Word/TXT 文档，向量化存储，聊天时自动检索相关片段
- **🔧 内置工具库** — Web 搜索、网页抓取、图片搜索、文件处理、PDF 生成、终端执行等 7 大工具
- **🧠 思考过程** — 类 DeepSeek/Kimi 的思考链展示，折叠式时间轴，推理过程透明可见
- **📋 AI 智能测试** — 需求文档 → AI 4 步工作流（分析→编写→评审→修订）→ 测试用例管理
- **⚙️ 配置中心** — AI 模型配置、提示词管理、生成行为配置、环境配置
- **👤 系统管理** — 用户管理、角色权限、审计日志、操作日志、系统设置

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Naive UI + Pinia |
| 后端 | Python FastAPI + LangGraph + LangChain |
| 数据库 | MySQL 8.0+（业务数据）+ ChromaDB（向量检索）+ SQLite（LangGraph checkpoint）|
| AI 模型 | DeepSeek / Qwen / OpenAI / Zhipu / Ollama |

### 快速开始

```bash
# 启动后端
cd ai-hub/backend
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端
cd ai-hub/frontend
npm install
npm run dev
```

更多详情请查看 [ai-hub 文档](./ai-hub/docs/)

---

## 🧪 TestHub — 智能测试管理平台

基于 AI 驱动的全栈测试管理平台，集成 AI 需求分析、测试用例管理、API 测试、UI/APP 自动化测试等模块。

### 核心特性

- **🤖 AI 智能化能力** — AI 需求分析、智能测试用例生成、多模型支持、AI 智能浏览器自动化
- **🔐 安全机制** — JWT 双 Token 认证、自动刷新、Token 黑名单、请求队列
- **🌐 API 测试** — HTTP/WebSocket 请求、环境变量、测试套件、定时任务、Allure 报告
- **🖥️ UI 自动化测试** — Selenium/Playwright 双引擎、页面对象模式、AI 智能模式
- **📱 APP 自动化测试** — Airtest 框架、设备管理、组件化编排、Celery 异步执行
- **📊 测试执行与报告** — 测试计划、执行记录、多维度统计、Allure 报告
- **🏭 数据工厂** — 50+ 实用工具（字符处理、编码转换、加密解密、JSON 工具等）

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Element Plus + Pinia |
| 后端 | Python Django 4.2 + Django REST Framework |
| 数据库 | MySQL 8.0+ |
| 自动化 | Selenium、Playwright、Airtest、Allure |

### 快速开始

```bash
cd testhub
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 初始化数据库
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# 启动服务
python manage.py runserver
```

更多详情请查看 [testhub/README.md](./testhub/README.md) 和 [testhub/docs/](./testhub/docs/)

---

## 📚 文档目录

| 文档路径 | 说明 |
|---------|------|
| [ai-hub/docs/architecture.md](./ai-hub/docs/architecture.md) | AI-HUB 系统架构 |
| [ai-hub/docs/database-design.md](./ai-hub/docs/database-design.md) | AI-HUB 数据库设计 |
| [ai-hub/docs/changelog.md](./ai-hub/docs/changelog.md) | AI-HUB 版本更新日志 |
| [ai-hub/docs/dev-plan.md](./ai-hub/docs/dev-plan.md) | AI-HUB 研发计划 |
| [ai-hub/docs/project-rules.md](./ai-hub/docs/project-rules.md) | AI-HUB 研发规则 |
| [testhub/docs/](./testhub/docs/) | TestHub 技术文档 |
| [.qoder/rules/](./.qoder/rules/) | Qoder 平台规范（架构、代码风格、安全等）|

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 许可证

本项目采用 MIT 许可证。

---

Made with ❤️ by 大刚（公众号：测试开发实战）