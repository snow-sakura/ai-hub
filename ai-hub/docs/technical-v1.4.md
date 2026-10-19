# v1.4 技术文档 — 序列调度与生成链路修复实现

> 面向开发者。需求见 [requirements-v1.4.md](./requirements-v1.4.md)，规格见 [spec-v1.4-generation-sequence.md](./spec-v1.4-generation-sequence.md)。

## 1. 缺陷根因与修复清单

| ID | 根因（代码级） | 修复 |
|----|--------------|------|
| B1 | `api.py` 引用 `stream_generation_task` 未导入 → 路由注册即 NameError | 补导入 |
| B2 | reviews:create 与 4 个定时端点调用未定义的 `current_user` | 统一 `get_optional_user` 依赖 |
| B3 | `project_context` 分支未初始化 → UnboundLocalError | 初始化空串 |
| B4 | 四节点用 `ainvoke`，`astream_events` 捕不到 `on_chat_model_stream` → 前端无 token | 新增 `nodes/node_utils.py:astream_collect`，四节点改 `astream` 逐 token 转发 |
| B5 | 完成用例数按段落估算恒为 0 | `_count_generated_cases` 改用 `parse_markdown_to_cases` 真实计数 |
| B6 | 进程重启后任务停留 running | `database.recover_interrupted_tasks()` + lifespan 启动时回收 |
| B7 | LangGraph 异常吞掉原因 | SSE `testing_error` 透出真实 message |
| B8 | 定时任务执行=写假日志；且后台协程复用请求级连接（请求结束连接归还池，`_conn=None` → AttributeError）、更新未 commit（close 回滚）| `execute_scheduled_task` 创建真实生成任务；`_execute` 自取 `get_db()` 连接并显式 `commit()`，finally 归还 |
| B9 | 前端未监听 `testing_save_progress` | `useGenerationStream` 补监听 |
| B10 | review 解析失败静默 | fallback 写入 summary 并保留原文 |
| B11 | `POST /generate/tasks/{id}/save-cases` 复用 `SaveCasesRequest`（必填 task_id）而前端 body 仅 `{project_id}` → 422 | 新增 `SaveTaskCasesRequest{project_id?}` |

## 2. 模型分级（tier）

```
ModelConfig.tier: "free" | "paid"
llm_factory.get_model_tier(provider, model):
  1) settings.free_model_ids 命中 → free
  2) AVAILABLE_MODELS 显式标注 → 采信
  3) provider == ollama → free（兜底）
  4) 其余 → paid
```
`/testing/config/defaults` 的模型项附带 `id`（`provider:model`）、`tier`、`sequence_hint`；前端选择器渲染「·免费/·付费」。

## 3. 内置 mock provider（离线全流程）

`app/common/core/mock_chat_model.py:MockChatModel(BaseChatModel)`
- 确定性：按 prompt 关键词识别 analyze/write/review/revise 四阶段，输出符合平台 Markdown 契约的固定结构；
- 种子取自输入文本 hash，同输入同输出（可复现演示/测试）；
- review 首轮固定 `passed=false`（6/10），驱动 revise 第四步真实发生；
- 模型 id：`mock:mock-demo`（free）、`mock:mock-pro`（paid）。
任何无 Key 环境可完整验收；真实 Key 配于 `backend/.env` 即切换真实模型。

## 4. 序列调度器（sequence_scheduler.py）

```
split_requirement(text, n?)      #/#→ heading 感知拆分（不足章节自动均分段落）
decide_strategy(model)           # tier→ (sequential|parallel, max_parallel)
SequenceScheduler
  ├─ Semaphore(max_parallel) 槽位控制；串行=max_parallel 1
  ├─ 子任务 = 常规生成任务（sequence_id/seq_index/seq_title 挂接），
  │  执行体复用 execute_generation_task_background（自管连接）
  ├─ _SequenceHub: 订阅制 SSE 广播（sequence_progress / sequence_subtask / sequence_done）
  ├─ 失败不阻塞其它槽位；retry_failed 重置失败子任务并重新入队
  └─ scheduled_task_cron_loop: croniter 每 30s 扫描到期任务 → execute_scheduled_task
```

**连接纪律**：一切后台协程（调度、生成、定时）必须 `get_db()` 自取连接 + `commit()` + finally `close()`；请求级 `Depends(get_db_dep)` 连接在响应返回时已归还池。

## 5. 数据模型（migration v16）

- 新表 `testing_generation_sequences`：id/title/project_id/model/strategy(sequential|parallel)/max_parallel/status/total_count/created_by…
- `testing_generation_tasks` + `sequence_id, seq_index, seq_title, seq_stage`
- `testing_scheduled_tasks` + `project_id, model, input_text, exec_ref, summary`；logs 表补 `exec_ref/summary`
- 幂等迁移：`information_schema` 探测列后 `ALTER`，重启安全。

## 6. API 增量（/api/v1/testing）

| 方法与路径 | 说明 |
|-----------|------|
| POST /sequences | 创建序列（拆分+策略+启动） |
| GET /sequences | 列表（含进度计数） |
| GET /sequences/{id} | 详情（含子任务与各自阶段） |
| GET /sequences/{id}/stream | 序列级 SSE（slot/seq_index/stage） |
| POST /sequences/{id}/cancel | 取消（级联取消 pending 子任务） |
| POST /sequences/{id}/retry | 重跑失败子任务 |
| DELETE /sequences/{id} | 删除序列及子任务 |
| POST /generate/tasks/{id}/save-cases | 采用用例入库（SaveTaskCasesRequest） |
| POST /scheduled-tasks/{id}/execute | 立即执行 → 真实生成任务 + 日志 |

## 7. 前端结构增量

- `views/sequenced/SequenceListView.vue`：创建表单（策略实时预览）+ 列表进度条；
- `views/sequenced/SequenceDetailView.vue`：按 `seq_index` 严格排序卡片流；每卡 n-steps 四步循环推进；并行模式显示槽位泳道；SSE 优先 + 轮询兜底；取消/重跑；
- `types/sequence.ts`、`api/generation.ts` 序列 API、`useGenerationStream` save_progress；
- 路由补登 7 个配置页 + sequences 两页 + settings；`vite.config.ts` 支持 `.env.local` 的 `VITE_BACKEND_URL`/`VITE_DEV_PORT`（多项目共存端口隔离）。

## 8. 部署与验证

- `requirements.txt` **+croniter**；`.env` 新增可选：`FREE_MODEL_IDS`、`SEQUENCE_MAX_PARALLEL_PAID`；
- 验证矩阵与截图见 [user-guide.md](./user-guide.md) §验证；演示数据快照见 `ai-hub/demo/data/run.json`（Pages 自动部署）。
