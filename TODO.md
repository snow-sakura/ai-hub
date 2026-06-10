# 版本发布记录

## v1.0.0（2026-06-09）

🎉 初始版本发布。

### 核心功能

- **AI 聊天室**：多模型对话（DeepSeek / Qwen / OpenAI / Zhipu / Ollama），SSE 流式输出，自动生成对话标题
- **知识库管理**：上传 PDF/Word/TXT 文档，向量化检索，聊天时自动引用
- **工具调用**：Web 搜索、网页抓取、图片搜索、文件读写、PDF 生成、终端执行
- **思考过程展示**：类 DeepSeek/Kimi 的推理链可视化，可折叠时间轴
- **对话管理**：历史记录侧边栏，按时间分组，新建/删除对话
- **首页**：功能卡片入口，带悬浮动画和标签展示
- **文件解析**：支持 PDF（PyMuPDF）、Word（.docx/.doc）、TXT 格式

### 技术架构

- 后端：FastAPI + LangGraph + LangChain + SQLite + ChromaDB
- 前端：Vue 3 + TypeScript + Vite + Naive UI + Pinia
- 流式通信：Server-Sent Events（SSE）

### 项目结构

- 严格分层架构：API → Service → Repository → Domain
- LangGraph Agent 编排：rag_node → agent_node → tool_node
- 自动导入：unplugin-auto-import + unplugin-vue-components

## v1.2.0（2026-06-10）

### 品牌与文案更新

- **品牌统一**：首页标题、侧边栏、知识库返回按钮统一改为「AI-HUB工作台」
- **聊天页标题**：空状态标题改为「AI聊天室」
- **首页副标题**：同步更新为「智能对话 · 知识管理 · 创意无限」

### UI/UX 优化

- **图标升级**：首页卡片图标全面更换为炫酷风格（⚡🎯💖🛠️🛡️✦）
- **Logo 图标**：从 🧪 更换为 ✦，更加简约现代

---

## v1.1.0（2026-06-10）

### 新增功能

- **🤗 哄哄模拟器**：角色扮演情绪安抚场景，支持情绪分析（7 类情绪）、原谅值动态计算、情绪统计看板
- **📊 情绪仪表盘**：情绪分布分析、原谅值趋势图表、哄人能力雷达图，支持时间范围筛选
- **📝 记忆管理**：哄哄模拟器内联记忆查看与编辑面板

### 架构重构

- **前端模块化重构**：将原扁平目录重构为 `shared/` + `modules/` 架构
  - `shared/`：公共路由、布局、通用组件、Store、API 封装、Composable
  - `modules/chat/`：AI 聊天室独立模块（组件/Store/API/类型）
  - `modules/comfort/`：哄哄模拟器独立模块（组件/Store/API/类型）
  - `modules/knowledge/`：知识库管理独立模块（Store/API/类型）
- **后端独立 Agent 流**：哄哄模拟器使用独立的 LangGraph graph 和 checkpoint 数据库
- **API 路由聚合**：统一通过 `router.py` 注册所有模块路由

### 问题修复

- **消息隔离**：修复 AI 聊天室与哄哄模拟器共享消息状态的 Bug，各自拥有独立 Store
- **SSE 事件分发**：`useSseStream` 根据 `comfortMode` 路由到对应的 Store
- **知识库错误关联**：AI 聊天不再主动声明关联知识库，仅在选择文档后显示
- **文案统一**：所有「AI 工作台」「AI 智能助手」统一改为「AI 超级智能助手」
- **路径别名修复**：`vite.config.ts` 补充 `@/` 路径别名配置，修复构建报错

### UI/UX 优化

- **图表图标加大加深**：情绪分布标签 12px→15px，统计卡片数值 22px→28px
- **模型选择器加宽**：下拉框宽度 130px→200px，完整显示模型名称
- **知识库弹窗重新设计**：去除标题重复，优化卡片样式、空状态、底部操作栏
- **构建配置修复**：补充 `resolve.alias` 支持 `@/` 导入路径

---

> 格式说明：后续版本记录请按 `vX.Y.Z（YYYY-MM-DD）` 格式追加，标注新增/变更/修复内容。
