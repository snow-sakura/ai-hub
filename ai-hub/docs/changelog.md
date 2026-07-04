# 版本更新日志

## [v2.1] - 2026-07-04

### 文档体系完善

- 更新根目录 `README.md` — 整合 ai-hub 和 testhub 两个项目的介绍，建立统一项目概览
- 更新 `docs/architecture.md` — 同步 shared→common 目录变更，更新模块状态和目录结构
- 更新 `docs/database-design.md` — 完善数据库表结构文档，同步配置中心表定义
- 更新 `docs/dev-plan.md` — 更新阶段状态，标记配置中心已完成
- 更新 `docs/project-rules.md` — 完善编码规范和安全规则
- 更新 `ai-hub/claude.md` — 同步目录结构变更，更新模块状态和新增文件

### 前端变更

- 新增 `AuthView.vue` — 统一认证视图组件
- 新增 `user.ts` store — 用户状态管理
- 更新路由配置 `router/index.ts` — 优化路由结构和导航守卫
- 更新国际化配置 — 完善中英文翻译
- 更新 `vite.config.ts` — 优化构建配置
- 更新 `tsconfig.json` — 完善 TypeScript 配置

### 数据库变更

- 配置中心模块表结构完整定义（config_models, config_prompts, config_behaviors, config_chat, config_ui_env, config_app_env）

## [v2.0] - 2026-06-14

### 重构开始
- 基于原型设计重构项目结构，按 9 大功能模块重新组织代码
- 结合竞品 testhub 项目优化后端实现
- 清理无效文件和代码
- 建立文档体系

### 变更
- 删除 `OPTIMIZATION_PLAN.md` 等无效规划文件
- 删除前端 `__init__.py` 文件（Vue/TS 项目不需要）
- 合并 05-测试管理 功能到 01-AI智能测试 模块
- 新增操作日志文件系统存储 (OperationLogger)
- 新增系统管理模块：用户管理、角色权限、认证登录(JWT)、审计日志
- 创建共享 auth 模块 (JWT 签发/验证/密码哈希)
- 后端 `app/shared/` 目录重命名为 `app/common/`，同步更新所有模块 import 路径
- 首页 HomeView 按照原型「首页仪表盘」重新设计：移除侧栏、独立顶栏+欢迎区+统计卡片+8格功能模块卡片+底部
- 研发计划文档全面落地：更新 dev-plan.md 为完整7阶段任务分解，新建 phase-2~7 独立实施文档（含数据库DDL、API设计、前端页面清单、目录结构）
- 前端登录/注册页面 (LoginView, RegisterView)
- 系统管理完整前端（6个子页面+Tab布局）：用户管理、角色管理、审计日志、操作日志、系统设置
- 修复路由冲突：ai_testing 和 api_testing 原共享 `/testing` 前缀，现拆分为 `/testing` 和 `/api-testing`
- 修复 router.py 中 auth_router 和 system_router 指向同一对象的问题

### 数据库变更
- 新增表：`system_roles`、`system_user_profiles`、`system_user_roles`、`system_audit_logs`、`system_settings`
- 新增表：默认角色数据 (admin, project_admin, tester, viewer)
- 无破坏性变更

### 前端布局变更
- 新建 `AppLayout.vue` — 统一暖色调侧栏+顶栏布局，匹配原型设计
- App.vue 根据路由自动切换「全局布局」和「独立布局」（聊天室/哄哄模拟器保留各自布局）
- 侧栏导航包含所有 9 个功能模块入口

### 路由变更
| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `/testing`(接口测试) | `/api-testing` | 避免与AI测试冲突 |
| `/auth`(与system共享) | 独立auth_router | 不再共享同一router对象 |

### 2026-06-14 补充变更（Phase 1 收尾）

| 变更 | 文件 | 说明 |
|------|------|------|
| 共享模块侧边栏 | `ModuleLayout.vue` | 消除 TestingLayout/ApiTestingLayout/UiAutomationLayout 三份重复代码 |
| 模块菜单配置 | `module-menus.ts` | 6 模块 60+ 菜单项集中管理，支持 collapsible/flat 模式 |
| APP自动化布局 | `AppAutomationLayout.vue` | 新建，使用共享 ModuleLayout |
| SystemLayout重构 | `SystemLayout.vue` | n-tabs → 侧边栏扁平列表 |
| APP路由结构 | `router/index.ts` | 扁平路由 → 嵌套布局路由，与其他模块一致 |
| 登录页增强 | `LoginView.vue` | 简单居中 → 双栏品牌展示布局 |
| 注册页增强 | `RegisterView.vue` | 简单居中 → 双栏品牌展示布局 |
| 默认管理员 | `database.py` | `_seed_default_admin()` 首次启动自动创建 |
| 路由守卫 | `router/index.ts` | `router.beforeEach` 认证保护，未登录跳转 `/login` |
| Phase 1 文档 | `docs/phase-1-infrastructure.md` | 新建，记录全部实施详情 |
