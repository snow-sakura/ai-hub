# AI-HUB 操作说明（v1.4）

> 演示账号：`admin / admin123` · 无需任何 API Key 即可完成全部操作（内置离线演示模型）。

## 0. 启动

```bash
# 后端（默认 8000；本机端口冲突时可用 8010，见 frontend/.env.local 的 VITE_BACKEND_URL）
cd ai-hub/backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
uvicorn main:app --host 0.0.0.0 --port 8010

# 前端（Vite 自动读取 .env.local 的后端地址与端口）
cd ai-hub/frontend && npm install && npm run dev
```

## 1. 登录与看板
浏览器打开提示的地址 → 输入 admin/admin123 → 进入「数据看板」，查看项目、用例与生成趋势。
![看板](./screenshots/01-dashboard.png)

## 2. 创建项目
左侧「项目管理 → + 新建项目」，填写名称/描述并创建。项目用于聚合用例、序列与定时任务。
![项目](./screenshots/02-project-create.png)

## 3. AI 用例生成（单任务）
「AI 智能生成 → AI 用例生成」：
1. （可选）选择所属项目；
2. 选择模型 —— 选项带「·免费 / ·付费」标识，离线环境选 **演示模型（免费 · 串行）**；
3. 粘贴需求（支持 Markdown）→ 开始生成；
4. 观察四步流式进度：需求分析 → 用例编写 → AI 评审（评分卡）→ 用例修订。
![生成中](./screenshots/03-generate-streaming.png)
![完成](./screenshots/04-generate-done.png)

## 4. 结果沉淀（重要）
生成完成后用例处于**候选（待定）**状态，需人工把关：
1. 「AI 生成记录」页可查看任务列表与统计（任务数/完成数/用例数）；
2. 进入任务详情 → 对候选用例逐条点击 **采用**；
3. 点击右上角 **保存到用例库** → 确认 → 用例正式入库并关联项目；
4. 「用例管理」页即可检索、编辑这些用例。
![记录](./screenshots/05-generate-records.png)
![详情保存](./screenshots/06-task-detail-saved.png)
![用例库](./screenshots/07-testcases-library.png)

## 5. 序列生成（v1.4 核心）
「AI 智能生成 → 序列生成」适合长需求批量产出：
1. 填写序列名称，粘贴含多个 `#`/`##` 标题的需求（或点「填入示例需求」）；
2. 选择模型：免费模型自动提示 **串行 ×1**，付费模型提示 **并行 ×3**；
3. 「创建并开始调度」→ 自动进入序列详情：
   - ★ 子任务卡片严格按编号 1..N 排列，每张卡片独立展示 4 步进度循环；
   - 免费模型：同一时刻只有一个卡片推进（串行）；
   - 付费模型：顶部「执行槽位 1/2/3」实时点亮（并行）；
   - 可随时取消整个序列，或对失败子任务一键重跑。
![串行完成](./screenshots/09-seq-serial-done.png)
![并行槽位](./screenshots/10-seq-parallel.png)

## 6. 定时任务（真实执行）
「AI 配置 → 定时任务」：新建任务填写名称、cron（如 `0 8 * * *`）、**关联项目 + 生成模型 + 需求文本**，保存后点「立即执行」或等待 cron 到点。执行日志显示真实耗时与结果摘要，exec_ref 可跳转任务详情。
![定时任务](./screenshots/11-scheduled-task.png)

## 7. 评审 / 评测 / 报告
- 「评审管理」：基于用例库创建评审计划，走查打分（见截图 12）；
- 「AI 评测师」：对生成质量做基准评测；「测试报告」：按项目导出统计报告（截图 13）；
- 「AI 配置」下 5 个配置页（模型 / 提示词 / 生成行为 / AI 模式 / 评测器）全部可用（截图 14）。
![评审](./screenshots/12-reviews.png) ![报告](./screenshots/13-reports.png) ![模型配置](./screenshots/14-config-model.png)

## 8. 在线 Demo
纯 GitHub Pages 数据快照演示（每次推送 `ai-hub/demo/**` 自动重建）：
**https://snow-sakura.github.io/ai-hub/**

## 常见问题
- **生成卡在"执行中"？** 后端重启会自动回收为可重跑；重新生成即可。
- **保存按钮提示"没有可保存的用例"？** 先在任务详情把用例逐条「采用」再保存。
- **想换真实模型？** 在 `backend/.env` 填入任一 Provider Key（DeepSeek/OpenAI/Qwen/智谱），重启后端，模型列表自动出现付费模型。
