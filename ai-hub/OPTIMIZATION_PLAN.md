# 全量代码优化计划

基于四轮代码审查（2026-06-10），汇总所有待修复问题，按阶段逐步实施。

## 已修复（等待提交）

以下为第二轮/第三轮审查修复内容，当前在 working tree 中未提交：

| # | 文件 | 修复内容 |
|---|------|---------|
| 1 | `chat/service.py` | `db = None` 初始化防止 NameError；清理 `【修复】` 标记 |
| 2 | `useSseStream.ts` | 移 `activeRequests` 死代码；成功路径加 `controllers.delete()`；移冗余 `some()` 检查 |
| 3 | `chat.ts` / `conversation.ts` | 清理 `【修复】` 注释标记 |
| 4 | `knowledge/api.py` | 内联 import 移到文件顶部 |
| 5 | `managed_graph.py`（新） | 提取 `ManagedGraphBase` 抽象基类，模板方法模式 |
| 6 | `chat/graph.py` / `comfort/graph.py` | 继承 `ManagedGraphBase`，移除重复 `__init__`/`close`/checkpointer |
| 7 | `agent_utils.py`（新） | 提取 `merge_tool_call_chunks` 消除 28 行重复 |
| 8 | `agent_node.py` / `comfort_agent_node.py` | 使用共享 `merge_tool_call_chunks` |
| 9 | `managed_graph.py` | 修复 `str.replace` 路径脆弱（改 `os.path.splitext`） |
| 10 | `vite.config.ts` | AutoImport 新增 `{ '@vueuse/core': ['useDebounceFn'] }`，修复页面因缺失自动导入崩溃 |
| 11 | `ai_testing/repository.py` | 修复 MySQL 保留字 `key` 缺少反引号导致的 1064 语法错误 |
| 12 | `ai_testing/database.py` | 移除 `TINYINT(1)` 弃用语法；DDL 包裹 `SET SQL_NOTES=0/1` 抑制告警 |
| 13 | `shared/core/database.py` | DDL 包裹 `SET SQL_NOTES=0/1` 抑制告警 |
| 14 | `comfort/database.py` | DDL 包裹 `SET SQL_NOTES=0/1` 抑制告警 |

---

## Phase 1：快速修复与安全加固（预计 1 天）

低风险、独立的小改动，可并行实施。

### 1.1 前端死代码与空渲染

| # | 文件 | 改动 | 风险 |
|---|------|------|------|
| 1 | `ForgivenessBar.vue` | 删除未使用的组件（无任何 view 引用） | 低 |
| 2 | `StreamingCursor.vue` | `v-if="streamingContent"` 控制空内容时不渲染 `<span>` | 低 |
| 3 | `NeonCard.vue` | 移除不生效的光晕 CSS 变量，或添加 mousemove JS 事件 | 低 |

### 1.2 错误处理与边界

| # | 文件 | 改动 | 风险 |
|---|------|------|------|
| 4 | `App.vue` / 各页面根容器 | 用 `<ErrorBoundary>` 包裹每个页面 | 低 |
| 5 | `router/index.ts` | 添加 `path: '/:pathMatch(.*)*'` 404 页面 | 低 |
| 6 | `ComfortView.vue` | `fetchScenes`/`fetchModels` 添加 `catch` 错误 UI 反馈 | 低 |
| 7 | `EmotionDashboardView.vue` | `fetchStats` 错误透传到 UI | 低 |

### 1.3 数据库加固

| # | 文件 | 改动 | 风险 |
|---|------|------|------|
| 8 | `database.py` | `get_db()` 添加 `PRAGMA busy_timeout=5000` | 低 |

### 1.4 token_buffer 上限

| # | 文件 | 改动 | 风险 |
|---|------|------|------|
| 9 | `service.py` | `token_buffer` 设 65536 字符软上限，超限 token 直接透传 | 低 |

---

## Phase 2：组件重构（预计 2 天）

中等工作量，涉及组件拆分和提取。

### 2.1 共享用户气泡

| # | 文件 | 改动 | 风险 |
|---|------|------|------|
| 1 | 新建 `UserBubble.vue` | 从 `ChatMessage.vue` 和 `ComfortMessage.vue` 提取用户气泡样式+结构 | 中 |
| 2 | `ChatMessage.vue` | 用 `UserBubble` 替换内联气泡 | 低 |
| 3 | `ComfortMessage.vue` | 用 `UserBubble` 替换内联气泡 | 低 |

### 2.2 ChatInput 拆分

| # | 文件 | 改动 | 风险 |
|---|------|------|------|
| 4 | 新建 `ComposerToolbar.vue` | 从 ChatInput 提取：深度思考开关、联网搜索、模型选择、知识库按钮 | 中 |
| 5 | 新建 `AttachmentChips.vue` | 从 ChatInput 提取：已选附件展示列表 | 中 |
| 6 | `ChatInput.vue` | 引用新子组件，保留输入框+发送按钮核心逻辑 | 中 |

### 2.3 KnowledgeView 拆分

| # | 文件 | 改动 | 风险 |
|---|------|------|------|
| 7 | 新建 `KnowledgeStatsCards.vue` | 统计卡片（文档数/分块数/存储空间） | 低 |
| 8 | 新建 `KnowledgeTable.vue` | 文档表格+搜索过滤 | 中 |
| 9 | 新建 `KnowledgeDragUpload.vue` | 拖拽上传区域 | 低 |
| 10 | `KnowledgeView.vue` | 引用子组件，精简为编排视图 | 低 |

### 2.4 EmotionDashboard 拆分

| # | 文件 | 改动 | 风险 |
|---|------|------|------|
| 11 | 新建 `EmotionDistributionChart.vue` | 情绪分布统计面板 | 低 |
| 12 | 新建 `ForgivenessTrendChart.vue` | 原谅值趋势面板 | 低 |
| 13 | 新建 `AbilityRadar.vue` | 能力分析雷达图 | 低 |
| 14 | `EmotionDashboardView.vue` | 引用子组件 | 低 |

### 2.5 状态管理优化

| # | 文件 | 改动 | 风险 |
|---|------|------|------|
| 15 | `chat.ts` | `selectConversation` 时 `clearStreamState` 非活跃对话 | 低 |
| 16 | `comfort.ts` | `emotionHistory` 裁剪为最近 50 条 | 低 |
| 17 | `useSseStream.ts` | `handleEvent` 中非 comfort 模式收到 emotion 事件直接 `return` 避免初始化 comfort store | 低 |

---

## Phase 3：性能优化（预计 3 天）

核心性能改进，需要仔细设计和测试。

### 3.1 SSE 事件批处理

| # | 文件 | 改动 | 影响 |
|---|------|------|------|
| 1 | `service.py` | `reasoning_end` 后 token 按 10-20 个一组拼接发送 | SSE 事件数减少 95%+ |

### 3.2 消息分页

| # | 文件 | 改动 | 影响 |
|---|------|------|------|
| 2 | `conversation_repo.py` | `list_messages` 加 `limit`/`offset` 参数 | 后端控制 |
| 3 | `conversation_api.py` | 查询接口支持分页参数 | |
| 4 | `conversation.ts`（前端） | 分页加载历史消息，保留最近 50 条在内存 | 控制内存+DOM |

### 3.3 流式跳过全量 Markdown

| # | 文件 | 改动 | 影响 |
|---|------|------|------|
| 5 | `MarkdownBody.vue` | 流式阶段（`isStreaming=true`）显示纯文本 `streamingContent`，finalize 后一次性渲染 Markdown | 大幅减少 token 流期间 CPU 使用 |

### 3.4 节点异步化

| # | 文件 | 改动 | 影响 |
|---|------|------|------|
| 6 | `agent_node.py` | `async def agent_node` + `llm_with_tools.astream()` | 释放事件循环 |
| 7 | `tool_node.py` | 复用线程池 + asyncio 原生 HTTP | 减少线程开销 |
| 8 | `comfort_agent_node.py` | 同上异步化 | |

### 3.5 comfort 查询优化

| # | 文件 | 改动 | 影响 |
|---|------|------|------|
| 9 | `ComfortRepo` | metadata/scene/character/memories 合并为 JOIN 查询 | 4次→1次 DB 查询 |

---

## Phase 4：大工程（预计 5 天）

需要架构决策的重度改动。

### 4.1 虚拟滚动

| # | 文件 | 改动 | 影响 |
|---|------|------|------|
| 1 | `package.json` | 添加 `vue-virtual-scroller` 或 `@tanstack/vue-virtual` | 千条消息场景避免 DOM 崩溃 |
| 2 | `ChatMessageList.vue` | 替换 `v-for` + `transition-group` 为虚拟滚动 | |
| 3 | `ComfortMessageList.vue` | 同上 | |

### 4.2 移动端适配

| # | 文件 | 改动 | 影响 |
|---|------|------|------|
| 4 | `AppSidebar.vue` | 改为可折叠 drawer（<768px 自动折叠，汉堡按钮展开） | 全站响应式 |
| 5 | 全局样式 | 添加 `--bp-tablet: 768px`、`--bp-mobile: 480px` 断点系统 | |
| 6 | `ChatMessage.vue` | 消息横向 padding 改为响应式 | |
| 7 | `ChatInput.vue` | 工具栏按钮窄屏换行处理 | |

### 4.3 构建优化

| # | 文件 | 改动 | 影响 |
|---|------|------|------|
| 8 | `vite.config.ts` | `chunkSizeWarningLimit` 降至 500KB | 及早发现大 chunk |

---

## 里程碑

| 阶段 | 预计工时 | 交付物 |
|------|---------|--------|
| 基础提交（当前未提交改动） | — | 14 项修复 |
| Phase 1 | 1 天 | 死代码清理、错误处理、数据库加固 |
| Phase 2 | 2 天 | 组件提取和拆分、状态裁剪 |
| Phase 3 | 3 天 | SSE 批处理、分页、Markdown 流式优化、节点异步化 |
| Phase 4 | 5 天 | 虚拟滚动、移动端适配、构建优化 |

总计约 11 天工程工作量。
