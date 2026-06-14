# ai-testing gap analysis: prototype vs current implementation

> 分析 aihub-pic/ 原型页面与当前 ai_testing 模块的差距，为优化提供依据。
> 2026-06-14

## overview

Current ai_testing module has:
- backend: 14 files, ~60 endpoints, 22 tables (fully implemented)
- frontend: 8 views, 6+ components, 3 stores, 3 api modules
- langgraph pipeline: analyze → write → review → revise

Prototype pages to compare:
- 01-ai智能测试: 4 pages (ai模式配置, ai用例生成, ai评测师, ai测试报告)
- 05-测试管理: 5 pages (模块概览, 项目管理, 版本管理, 成员管理, 用例评审)

---

## 1. ai用例生成 (ai case generation)

### prototype layout (ai用例生成.html)
- two-column grid (1fr / 1.6fr)
- left panel: project selector + requirement textarea + model select + generate button + generation history list
- right panel: action bar + 7-column table (id, module, title, preconditions, steps, expected, priority)
- table: striped rows, hover highlight, priority color coding, module tag badges

### current implementation (GenerationView.vue)
- `frontend/src/modules/ai_testing/views/GenerationView.vue`
- similar layout but single column, setup guide modal
- has sse streaming (useGenerationStream.ts)
- missing: two-column layout with project/requirement on left, results on right
- missing: generation history list
- missing: priority color coding, module tag badges

### gap: medium
- [ ] restructure to two-column layout matching prototype
- [ ] add generation history list (left panel)
- [ ] add module tag badges to table rows
- [ ] add priority color coding
- [ ] keep sse streaming integration

---

## 2. ai评测师 (ai evaluator)

### prototype layout (ai评测师.html)
- two-column grid (1fr / 1.3fr)
- left panel: case selection (checkbox list with select-all) + evaluation config (criteria pills + model select + start button)
- right panel: score summary (4 stat cards) + issue list (severity badges + suggestions)

### current implementation (AITesterView.vue)
- `frontend/src/modules/ai_testing/views/AITesterView.vue`
- chat-style interface (session list + message stream)
- ai tester session management (create, delete, send messages)
- prototype is about batch evaluation, not chat interaction

### gap: large
- [ ] redesign as batch evaluation tool (not chat)
- [ ] add case selection with checkbox list
- [ ] add evaluation criteria pill tags
- [ ] add score summary grid (4 stat cards)
- [ ] add issue list with severity badges
- [ ] keep the existing ai_tester_sessions/messages backend for future use

---

## 3. ai测试报告 (ai test report)

### prototype layout (ai测试报告.html)
- filter card: project dropdown + date range + query/reset buttons
- report list: stacked items with name/time/task/status + view/download actions
- report detail card: 4-column stats + donut chart + module bars + 3-tab case table

### current implementation (TestReportView.vue)
- `frontend/src/modules/ai_testing/views/TestReportView.vue`
- needs verification of current layout

### gap: unknown (needs current file read)

---

## 4. ai智能模式配置 (ai smart mode config)

### prototype layout (ai智能模式配置.html)
- single column, max-width 880px
- 3 tabs: 基础配置 / 模型配置 / 高级配置
- toggles, provider cards, api key input, sliders, prompt template textarea

### current implementation (AIModeConfigView.vue + AIModelConfigView.vue + GenerationConfigView.vue)
- split across multiple pages in ai_testing/views/config/
- prototype consolidates into one page with tabs

### gap: medium
- [ ] consolidate into single page with tab navigation per prototype
- [ ] add provider card selection (3-column grid)
- [ ] add range sliders for temperature and context window
- [ ] add notification settings section

---

## 5. 测试管理模块 (test management overview)

### prototype layout (测试管理模块.html)
- module header: icon + title + description
- stats overview: 4 stat cards (projects, versions, members, pending reviews)
- feature grid: 5 clickable cards leading to sub-pages

### current implementation
- DashboardView.vue covers this partially
- no dedicated overview page matching prototype

### gap: medium
- [ ] restructure dashboard to match module overview layout
- [ ] add feature grid with 5 sub-page cards
- [ ] add stats overview cards

---

## 6. 项目管理 (project management)

### prototype layout (项目管理.html)
- filter bar: search + status dropdown + count
- 6-column table: name, owner, start/end dates, status, actions
- create modal with form fields
- status tags: active/done/archived

### current implementation (ProjectListView.vue)
- `frontend/src/modules/ai_testing/views/ProjectListView.vue`
- similar functionality but layout may differ

### gap: small
- [ ] verify table columns match prototype
- [ ] add status tag variants

---

## 7. 版本管理 (version management)

### prototype layout (版本管理.html)
- sub-nav bar (5 pills: 模块概览, 项目管理, 版本管理, 成员管理, 用例评审)
- version cards (stacked, not table): version tag + number + status + project + date + changelog
- create modal

### current implementation (ProjectVersionsView.vue)
- `frontend/src/modules/ai_testing/views/ProjectVersionsView.vue`
- needs verification of layout

### gap: medium
- [ ] add sub-nav pill bar across 05-pages
- [ ] redesign as card-based (not table) per prototype
- [ ] add changelog display

---

## 8. 成员管理 (member management)

### prototype layout (成员管理.html)
- sub-nav bar (same 5 pills)
- member cards: avatar circle + name/email + role tag + online status + actions
- invite modal

### current implementation (ProjectMembersView.vue)
- `frontend/src/modules/ai_testing/views/ProjectMembersView.vue`
- needs verification of layout

### gap: medium
- [ ] add sub-nav pill bar
- [ ] redesign as card-based (not table)
- [ ] add online/offline status
- [ ] add avatar with first-character fallback

---

## 9. 用例评审 (case review)

### prototype layout (用例评审.html)
- sub-nav bar (same 5 pills)
- filter bar + 6-column table: review name, project, reviewer, status, date, actions
- reviewer avatars (colored circles with "+N" overflow)
- create modal

### current implementation (ReviewListView.vue + ReviewDetailView.vue)
- `frontend/src/modules/ai_testing/views/ReviewListView.vue`
- `frontend/src/modules/ai_testing/views/ReviewDetailView.vue`
- backend has full reviews CRUD + review_cases + review_reviewers
- needs verification of layout

### gap: small-medium
- [ ] add sub-nav pill bar
- [ ] add reviewer avatar circles with "+N"

---

## summary

| priority | page | gap | effort |
|----------|------|-----|--------|
| high | ai评测师 | large (chat→batch redesign) | 2-3d |
| high | ai用例生成 | medium (layout restructure) | 1-2d |
| medium | 测试管理模块 | medium (new overview page) | 1d |
| medium | 版本管理 | medium (card-based redesign) | 1d |
| medium | 成员管理 | medium (card-based redesign) | 1d |
| medium | ai智能模式配置 | medium (consolidate pages) | 1-2d |
| low | 项目管理 | small (table alignment) | 0.5d |
| low | 用例评审 | small (reviewer avatars) | 0.5d |
| low | ai测试报告 | unknown | 0.5d |
| total | — | — | ~8-12d |

> note: 05-测试管理 pages share a common sub-nav pill bar, so implementing it once benefits all 5 pages.
