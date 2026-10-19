# Spec v1.4 — 生成结果修复 + 序列任务调度（免费串行 / 付费并行）

> 状态：已批准，执行中
> 日期：2026-10-18
> 负责人：AI 研发助手
> 关联文档：`docs/requirements.md`（需求）、`docs/user-guide.md`（操作说明）、`docs/architecture.md`（架构）

---

## 1. 背景与问题（Why）

当前 AI 智能测试模块的生成结果"不是失败就是缺失"，经全量代码审计确认根因如下：

| # | 缺陷 | 位置 | 影响 |
|---|------|------|------|
| B1 | `stream_generation_task` 未 import，流式端点必然 NameError 500 | `backend/app/modules/ai_testing/api.py:498` | **前端默认"流式输出"模式 100% 失败**（最核心根因） |
| B2 | `current_user` 未注入，NameError 500 | `api.py:1146`（创建评审）、`api.py:1384/1396/1407/1418`（定时任务 CRUD/执行） | 评审创建、定时任务全部崩溃 |
| B3 | `project_context` 条件赋值后直接使用 | `api.py:418-437` | 修订生成潜在 NameError |
| B4 | LangGraph 异常仅回显通用文案；评审 JSON 解析失败静默降级 | `sse_stream.py:171-177`、`review_node.py:95-97` | 错误不可诊断、评审结果失真 |
| B5 | 生成用例计数靠正则，LLM 格式漂移时计数为 0 | `sse_stream.py:60-71` | 详情页"生成用例数 0"（结果缺失感） |
| B6 | complete 模式任务后台执行，服务重启后永久滞留 running | `api.py:471` | 僵尸任务 |
| B7 | 7 个 AI 配置页面已实现但未注册路由，菜单 4 个入口 404 | `frontend/src/modules/ai_testing/shared/router` 缺失注册 | 配置中心不可达 |
| B8 | 定时任务执行是桩（硬编码 completed/0s，无真实执行） | `service.py:954-963` | 定时任务功能虚假 |
| B9 | `testing_save_progress` 事件前端无监听 | `useGenerationStream.ts` | 保存进度不显示 |

## 2. 目标（What）

1. **修复**上表全部缺陷 B1–B9，恢复"生成→结果"主链路。
2. **新增：序列任务调度**
   - 需求文档按章节/模块拆分为 N 个子任务，构成一个"生成序列"。
   - **免费模型（tier=free）→ 单任务序列**：并发度强制为 1，严格按序列顺序串行执行。
   - **付费模型（tier=paid）→ 并行序列**：并发度 = min(子任务数, `SEQUENCE_MAX_PARALLEL_PAID`，默认 3)，多任务并行执行。
3. **前端显示优化**：序列监控页按序列顺序循环渲染子任务卡片；每个子任务内部按 4 步工作流（分析→编写→评审→修订）循环节流展示；免费模式呈现"串行队列"，付费模式呈现"并行泳道 + 实时槽位"。
4. **零 Key 可验证**：新增 `mock` 演示 Provider（离线确定性流式输出），无 API Key 也可完整走通全流程（用于演示、E2E 验证、GitHub Pages Demo）。
5. **GitHub Pages Demo**：纯 GitHub 实现的静态演示站（页面 + JSON 数据记录均存放于仓库，经 GitHub Actions 发布到 Pages），README 附在线链接。
6. **文档补齐**：需求文档、技术文档、操作说明、README 全流程图文（自动截图）。
7. **Loop Engineering 交付标准**：每个模块完成后必须在真实浏览器中验证并自动截图，报错即修复，通过后才进入下一模块。

## 3. 设计（How）

### 3.1 模型分级（free / paid）

- `ModelConfig`（`app/common/domain/entities.py`）新增字段 `tier: str = "paid"`。
- `AVAILABLE_MODELS` 逐项标注：`ollama/*` 与 `mock/*` 为 **free**，其余云端模型为 **paid**。
- 支持环境变量 `FREE_MODEL_IDS`（逗号分隔）在线覆盖免费名单，`SEQUENCE_MAX_PARALLEL_PAID` 控制付费并行上限。
- `GET /testing/models`（既有接口）返回值追加 `tier` 字段，前端据此展示"免费/付费"徽标并提示并发策略。

### 3.2 mock 演示 Provider

- `llm_factory` 新增 provider `mock`：返回 `FakeListChatModel` 风格的确定性流，按 prompt 类型输出：需求分析报告 / Markdown 用例（`TC-xxx` 格式，可被解析器计数）/ 评审 JSON / 修订稿。
- 用例数量随 prompt 的 section 编号确定性变化（3–6 条），保证计数、评审、落库全链路真实可验。

### 3.3 数据模型（MySQL，迁移 v16）

```sql
CREATE TABLE testing_generation_sequences (
  id VARCHAR(36) PRIMARY KEY,
  project_id VARCHAR(36) NOT NULL,
  title VARCHAR(255) NOT NULL,
  requirement_text TEXT NOT NULL,        -- 原始需求（可截断存摘要）
  model_id VARCHAR(120) NOT NULL,
  model_tier VARCHAR(10) NOT NULL,       -- free | paid（创建时快照）
  strategy VARCHAR(10) NOT NULL,         -- sequential | parallel（由 tier 决定）
  max_parallel INT NOT NULL DEFAULT 1,
  status VARCHAR(20) NOT NULL,           -- pending|running|paused|completed|partial_failed|cancelled
  total INT, success INT, failed INT, running INT,
  error_message TEXT,
  created_by VARCHAR(36), created_at, updated_at
);
ALTER TABLE testing_generation_tasks
  ADD COLUMN sequence_id VARCHAR(36) NULL,
  ADD COLUMN seq_index INT NOT NULL DEFAULT 0,
  ADD COLUMN seq_title VARCHAR(255) NULL;
```

### 3.4 序列调度器（`sequence_scheduler.py`，Service 层）

- 创建序列：按 Markdown 标题（`#`/`##`）或"每 N 行"将需求拆分为子任务；每子任务建一条 `testing_generation_tasks`（携带 sequence_id/seq_index/子需求文）。
- 执行：`asyncio` + 每序列一个 `Semaphore(max_parallel)`；worker 按 `seq_index` 顺序领取任务（保持序列顺序），执行复用既有单任务流水线 `execute_generation_task_background`。
- 并发策略：`free → max_parallel=1`；`paid → min(N, SEQUENCE_MAX_PARALLEL_PAID)`。
- 取消：序列级取消置位（DB 状态位，跨 worker 有效，修复 B6 同类问题）。
- 崩溃恢复：启动钩子扫描 `running` 序列/任务 → 标记 `interrupted`，允许一键重跑失败子任务。
- 进度：子任务状态变化 → 更新序列表计数并广播 SSE。

### 3.5 API（新增 `/testing/sequences`）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/testing/sequences` | 创建序列（自动拆分、按 tier 定并发策略） |
| GET | `/testing/sequences` / `{id}` | 列表 / 详情（含子任务及各自 4 步状态） |
| GET | `/testing/sequences/{id}/stream` | 序列 SSE 总览流 |
| POST | `/testing/sequences/{id}/cancel` | 取消 |
| POST | `/testing/sequences/{id}/retry-failed` | 重跑失败子任务 |
| DELETE | `/testing/sequences/{id}` | 删除（连带子任务） |

SSE 事件：`sequence_progress`（计数快照）、`sequence_subtask`（单子任务状态/阶段/增量 token，携带 seq_index）。

### 3.6 前端

- 路由注册 7 个孤儿配置页 + SettingsView（修复 B7 全部 404）。
- 新增 `SequenceListView` / `SequenceDetailView`：
  - 顶部：序列概览（策略徽标"免费·串行 / 付费·并行 N"、总进度条、槽位指示）。
  - 主体：子任务卡片**严格按 seq_index 排序循环渲染**；卡片内部 4 步步骤条随事件循环推进；付费并行时运行中的多个卡片同时点亮并显示占用槽位号。
- `GenerationView` 增加"单任务 / 序列生成"切换；模型选择器显示免费/付费徽标。

## 4. 验收标准（Loop Engineering）

逐模块在浏览器验证并自动截图（存放 `docs/screenshots/`），控制台无报错：

1. 登录 → 项目列表 → 项目详情 正常。
2. 单任务流式生成（mock）：4 步全链路流式可见、结果落库、用例数 > 0。【验证 B1/B5】
3. 创建评审 → 评审详情正常。【验证 B2】
4. 修订生成正常。【验证 B3】
5. 序列生成（免费 mock）：卡片严格按序逐个执行，并发=1。
6. 序列生成（付费 mock 标注）：≥2 子任务并行执行、槽位可视化。
7. 序列取消 / 失败重跑生效。
8. 7 个配置页可达可保存；Settings 可达。【验证 B7】
9. 定时任务创建/立即执行返回真实执行记录。【验证 B8】
10. 服务重启后 running 任务被标记 interrupted 而非僵尸。【验证 B6】
11. GitHub Pages Demo 在线可访问、数据来自仓库 JSON。
12. 无 `.env`/密钥入库（secret 扫描 0 命中）。

## 5. 里程碑顺序

M1 环境与基线修复 → M2 分级+mock → M3 序列后端 → M4 序列前端 → M5 浏览器循环验证与截图 → M6 Pages Demo → M7 文档与 README → M8 清理与提交。
