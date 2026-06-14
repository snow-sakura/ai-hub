# 待办事项

> 按时间倒序记录

## 2026-06-15

### [清理] 文档体系重构 — 仅保留现阶段文档

- [x] 文档审核：遍历所有 14 个文档文件，按"仅保留现阶段功能模块"原则审核
- [x] 删除：`docs/phase-3-api-testing.md`、`phase-4-ui-automation.md`、`phase-5-app-automation.md`（模块已删除）
- [x] 删除：`docs/phase-3-ai-testing-optimization.md`、`phase-4-testing-delivery.md`（未来阶段，非现阶段）
- [x] 重命名：`phase-2-config-dashboard.md` → `phase-2-config-center-knowledge.md`
- [x] 重写：`docs/architecture.md` — 目录结构从 9 模块缩减为 6 模块
- [x] 重写：`docs/database-design.md` — 移除 api_testing 表定义，新增 config_center 6 表字段
- [x] 重写：`docs/dev-plan.md` — 精简为仅 Phase 1-2 当前阶段
- [x] 更新：`docs/project-rules.md` — 3.3 节 "9 大功能模块" → "6 大功能模块"
- [x] 更新：`docs/database-changelog.md` — api_testing 表标记为已删除
- [x] 更新：`docs/phase-4-testing-delivery.md` — 移除已删除模块引用
- [x] 同步：`backend/app/common/logs/operation_logger.py` — 文档示例更新
- [x] 同步：`backend/app/modules/ai_testing/database.py` — 迁移注释更新
- [x] 文档同步：所有交叉引用路径更新为新的文件名

### [布局] 视图样式对齐 ai_testing 布局

- [x] 配置中心：UiEnvConfigView、AppEnvConfigView 内联 scoped CSS 对齐
- [x] 系统管理：UserList、RoleList、AuditLog、OperationLog、Settings、Dashboard 内联 scoped CSS 对齐
- [x] 删除：`src/shared/styles/page-layout.css`（无任何视图引用）
- [x] 构建验证：vue-tsc + vite build 通过

## 2026-06-14

### [新增] 配置中心前端模块（6 个视图）

- [x] 创建 API 层：`config_center/api/config.ts`（6 组实体完整 CRUD 类型定义 + 请求函数）
- [x] AI 模型配置：供应商卡片网格 + 连接配置 + 温度滑动条 + 高级设置
- [x] 提示词配置：搜索过滤 + 数据表格 + 新建/编辑弹窗 + 行内启用开关
- [x] 生成行为配置：键值对卡片列表 + 自动保存 + 智能类型渲染（文本/开关/数字）
- [x] AI 聊天室配置：模型选择 + 对话参数 + RAG/联网搜索开关 + 系统提示词
- [x] UI 环境配置：环境卡片网格（浏览器类型/视口/超时/截图开关）+ CRUD 弹窗
- [x] APP 环境配置：环境卡片网格（平台/包名/Appium/设备/超时）+ CRUD 弹窗
- [x] 路由注册：`/config/*` 6 个子路由挂载到 ConfigLayout
- [x] ConfigLayout：复用 ModuleLayout 组件（flat 模式侧栏）
- [x] 构建验证：vue-tsc 类型检查通过 + vite build 成功

### [修正] Phase 1 重构 — 错误优先级修正

- [x] 清理：删除错误生成的 ui_automation、app_automation、api_testing 模块目录和前端引用
- [x] 清理：删除 OPTIMIZATION_PLAN.md 等无效文件
- [x] 清理：更新 main.py 移除已删除模块的 import 和 init 调用
- [x] 清理：更新 router.py 移除已删除模块的路由注册
- [x] 清理：更新前端路由、菜单配置、App.vue、HomeView 移除已删除模块引用
- [x] 文档：更新 docs/database-changelog.md 记录清理操作并注明已废弃

### 第一阶段：基础设施与清理 ✅

- [x] 清理：删除 OPTIMIZATION_PLAN.md、docs/plan_bak/、docs/database_bak/、前端 __init__.py
- [x] 清理：删除运行日志文件(backend.log, frontend.log)
- [x] 文档体系：创建 docs/architecture.md、docs/database-design.md、docs/changelog.md、docs/dev-plan.md
- [x] 操作日志：创建 OperationLogger（文件系统 JSON Lines + API 查询）
- [x] 系统管理：JWT 认证、用户 CRUD、角色权限、审计日志、系统设置
- [x] 路由修复：拆分 /testing → /testing + /api-testing，修复 auth_router 独立
- [x] 创建 shared/auth.py（JWT 签发/验证、密码哈希、依赖注入）
- [x] 统一布局：创建 AppLayout.vue（暖色调侧栏+顶栏+响应式），更新 App.vue
- [x] `app/shared/` → `app/common/` 重命名，同步更新所有模块 import
- [x] 首页仪表盘：按原型重设计（无侧栏，顶栏+欢迎区+统计卡片+8格功能模块网格）
- [x] 前端登录/注册页面
- [x] 系统管理前端：用户管理、角色管理、审计日志、操作日志、系统设置

### 第二阶段：配置中心 + 知识库补完 ✅ 配置中心已完成

- [x] AI 模型配置管理（CRUD + 模型供应商选择 + 温度/Token 参数）
- [x] 提示词配置管理（分类管理 + 搜索过滤 + 行内启用开关）
- [x] 生成行为配置（键值对管理 + 智能类型渲染）
- [x] AI 聊天室配置（模型选择 + 对话参数 + RAG/联网搜索）
- [x] UI 环境配置（浏览器类型/视口/超时/截图 CRUD）
- [x] APP 环境配置（平台/包名/Appium/设备/超时 CRUD）
- [ ] 知识库补完：文档详情页
