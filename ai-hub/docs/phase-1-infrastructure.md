# 第一阶段：基础设施与清理

> 预估工期：5-7天 | 状态：已完成

## 目标

清理无效文件，建立文档体系、操作日志系统、统一布局，完成系统管理模块和前后端基础设施。

---

## 1.1 清理无效文件

### 已删除
| 文件/目录 | 原因 |
|-----------|------|
| `OPTIMIZATION_PLAN.md` | 过时规划文件 |
| `docs/plan_bak/` | 规划文件备份，不再需要 |
| `docs/database_bak/` | 数据库设计备份，已有新文档 |
| 前端各模块 `__init__.py` | Vue/TS 项目不需要 Python 包标识 |
| 后端 `app/shared/` 目录 | 已重命名为 `app/common/` |

---

## 1.2 文档体系

### 已创建
| 文档 | 内容 |
|------|------|
| `docs/architecture.md` | 架构图、数据流、模块依赖、技术选型 |
| `docs/database-design.md` | 所有表定义（含字段、索引、外键） |
| `docs/changelog.md` | 版本变更记录 |
| `docs/dev-plan.md` | 7 阶段研发计划完整分解 |
| `docs/phase-1-infrastructure.md` | 本文件，Phase 1 实施详情 |
| `docs/phase-*.md` | 各阶段独立实施文档（Phase 2~7） |

---

## 1.3 操作日志系统

### OperationLogger

**文件路径**: `backend/app/common/logs/operation_logger.py`

文件系统 + API 查询双模式：
- 写入：`logs/operations/YYYY-MM-DD/{module}.log`（JSON Lines 格式）
- 查询：`GET /api/v1/system/operation-logs`
- 保留 90 天，自动轮转

**API**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/system/operation-logs` | 查询操作日志（分页、筛选） |

---

## 1.4 后端 `shared/` → `common/` 重命名

### 变更范围
| 旧路径 | 新路径 |
|--------|--------|
| `app/shared/core/` | `app/common/core/` |
| `app/shared/agent/` | `app/common/agent/` |
| `app/shared/service/` | `app/common/service/` |
| `app/shared/repository/` | `app/common/repository/` |
| `app/shared/domain/` | `app/common/domain/` |
| `app/shared/utils/` | `app/common/utils/` |
| `app/shared/logs/` | `app/common/logs/` |

所有模块中 `import` 路径已同步更新。通过 `grep -r "app\.shared"` 验证无残留引用。

---

## 1.5 系统管理模块

### 后端

| 功能 | API 端点 | 说明 |
|------|---------|------|
| 用户管理 | CRUD `/api/v1/system/users` | 用户信息、启用/禁用 |
| 角色管理 | CRUD `/api/v1/system/roles` | 角色 CRUD，内置角色不可删 |
| 认证登录 | `POST /api/v1/auth/login` | JWT 签发 |
| 注册 | `POST /api/v1/auth/register` | 新用户注册 |
| 当前用户 | `GET /api/v1/auth/me` | 获取登录用户信息 |
| 审计日志 | `GET /api/v1/system/audit-logs` | 审计记录查询 |
| 设置 | GET/PUT `/api/v1/system/settings` | 系统设置 |

### 默认管理员账号
首次启动时自动创建：

| 字段 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | `admin123` |
| 角色 | admin（系统管理员，全部权限） |

创建逻辑见 `backend/app/modules/system/database.py` 的 `_seed_default_admin()` 函数。
默认凭据可通过 `.env` 文件覆盖。首次登录后请在系统管理 → 用户管理中修改密码。

### 数据库变更
| 表名 | 用途 |
|------|------|
| `system_roles` | 角色定义（admin/project_admin/tester/viewer） |
| `system_user_profiles` | 用户扩展信息（显示名、邮箱、头像、状态） |
| `system_user_roles` | 用户-角色关联 |
| `system_audit_logs` | 审计日志 |
| `system_settings` | 系统设置键值存储 |

### 前端
| 页面 | 路由 | 说明 |
|------|------|------|
| 系统概览 | `/system` | 系统统计看板 |
| 用户管理 | `/system/users` | 用户列表 + 新建/编辑/启用/禁用 |
| 角色管理 | `/system/roles` | 角色列表 + 新建/编辑权限 |
| 审计日志 | `/system/audit-logs` | 审计记录查询 |
| 操作日志 | `/system/operation-logs` | 操作日志查询 |
| 系统设置 | `/system/settings` | 系统设置修改 |

---

## 1.6 首页仪表盘

**文件路径**: `frontend/src/shared/views/HomeView.vue`

按原型 `00-首页仪表盘` 重新设计：
- 独立布局（无 AppLayout 侧边栏）
- 顶栏：Logo + 语言切换 + 用户头像下拉（未登录显示登录/注册按钮）
- 欢迎区：渐变标题
- 统计卡片：项目数、用例数、今日执行、通过率
- 功能网格：8 个模块卡片（3 列布局）
- 底部信息

---

## 1.7 统一布局

### AppLayout.vue
**文件路径**: `frontend/src/shared/components/layout/AppLayout.vue`

- 固定左栏（220px）+ 顶栏 + 内容区
- 品牌标识 "AI-HUB / 智能测试平台"
- 8 个模块入口导航（带 SVG 图标）
- 路由激活高亮（3px 左边框 + 暖色调）
- 响应式：≤768px 缩为图标模式

### 条件排除
App.vue 中，以下路由不包裹 AppLayout：

| 类型 | 路径 | 原因 |
|------|------|------|
| 精确排除 | `/`, `/login`, `/register` | 首页/登录/注册独立布局 |
| 前缀排除 | `/chat`, `/comfort`, `/emotion-dashboard` | 聊天/哄哄模拟器自带独立布局 |
| 前缀排除 | `/ai-testing`, `/api-testing` | 模块自带 ModuleLayout 侧边栏 |
| 前缀排除 | `/ui-automation`, `/app-automation` | 模块自带 ModuleLayout 侧边栏 |
| 前缀排除 | `/system` | 模块自带 ModuleLayout 侧边栏 |

---

## 1.8 路由修复

| 问题 | 修复 |
|------|------|
| `ai_testing` 和 `api_testing` 共享 `/testing` 前缀 | 拆分为 `/testing` 和 `/api-testing` |
| `auth_router` 和 `system_router` 指向同一对象 | 创建独立 router 对象 |

---

## 1.9 登录注册页面（本次补充）

### 修改内容
参考竞品 testhub 双栏设计，将 LoginView.vue 和 RegisterView.vue 从简单居中卡片改为双栏布局：
- **左栏**：品牌展示区（暖色调渐变背景 #C67B5C → #D4A574）
  - 特性卡片（2×2 网格）：AI 智能生成、多类型测试、自动化执行、数据看板
  - AI 能力徽章标签
  - 语言切换器 + 装饰动画
- **右栏**：表单区（白色背景，固定宽度 480px）

### 涉及文件
- `frontend/src/shared/views/LoginView.vue` — 完整重写
- `frontend/src/shared/views/RegisterView.vue` — 完整重写

---

## 1.10 模块侧边栏统一（本次补充）

### 共享 ModuleLayout.vue
**文件路径**: `frontend/src/shared/components/layout/ModuleLayout.vue`

从 TestingLayout.vue 提取公共结构创建共享组件：
- 240px 侧边栏 + 品牌区 + 菜单 + 返回首页
- 顶部面包屑导航 + 语言切换
- 移动端汉堡菜单 + 遮罩层
- 支持 `collapsible`（可折叠分组）和 `flat`（扁平列表）两种模式

### 共享菜单配置
**文件路径**: `frontend/src/shared/config/module-menus.ts`

所有模块侧边栏菜单定义集中管理：

| 模块 | 模式 | 菜单内容 |
|------|------|---------|
| ai-testing | collapsible | 5 组 16 项（数据看板/项目管理/用例管理/AI生成/配置） |
| api-testing | collapsible | 4 组 9 项（概览/接口管理/测试执行/配置） |
| ui-automation | collapsible | 4 组 12 项（概览/测试管理/报表/配置） |
| app-automation | flat | 12 项（概览/看板/项目管理/元素管理/包名管理/设备管理/测试用例/套件/录制/执行记录/定时任务/通知） |
| system | flat | 6 项（概览/用户管理/角色管理/审计日志/操作日志/设置） |

### 布局文件变更
| 文件 | 操作 |
|------|------|
| `TestingLayout.vue` | 简化为 `<ModuleLayout module="ai-testing" />` |
| `ApiTestingLayout.vue` | 简化为 `<ModuleLayout module="api-testing" />` |
| `UiAutomationLayout.vue` | 简化为 `<ModuleLayout module="ui-automation" />` |
| `AppAutomationLayout.vue` | 新建：`<ModuleLayout module="app-automation" />` |
| `SystemLayout.vue` | 从 n-tabs 改为侧边栏扁平列表 |

### 路由变更
`/app-automation` 从扁平路由改为嵌套布局路由，与其它模块一致。

---

## 1.11 默认管理员账号自动创建（本次补充）

**文件路径**: `backend/app/modules/system/database.py`

`_seed_default_admin()` 函数在首次启动时自动创建默认管理员：

| 字段 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | `admin123` |
| 角色 | admin（系统管理员，全部权限） |

创建逻辑：
1. 检查 `users` 表中是否已存在 `username='admin'` 的用户
2. 不存在时，创建用户并写入 `users`、`system_user_profiles`、`system_user_roles` 三张表
3. 密码使用 `hash_password()`（bcrypt）加密存储
4. 凭据可通过 `.env` 文件覆盖

---

## 1.12 前端路由守卫（本次补充）

**文件路径**: `frontend/src/shared/router/index.ts`

添加 `router.beforeEach` 导航守卫实现认证保护：

| 规则 | 说明 |
|------|------|
| 白名单 | `/login`、`/register` 无需认证即可访问 |
| 未登录 | 访问其他路由自动跳转 `/login?redirect=<原路径>` |
| 登录成功 | LoginView 根据 `redirect` 参数跳回目标页面 |
| 存储方式 | `localStorage.getItem('access_token')` |
