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

---

> 格式说明：后续版本记录请按 `vX.Y.Z（YYYY-MM-DD）` 格式追加，标注新增/变更/修复内容。
