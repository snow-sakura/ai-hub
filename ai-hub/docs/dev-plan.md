# 研发计划

> 最后更新：2026-07-04
> 注：仅记录当前阶段的研发进展。未来阶段规划不再在本文件维护。

## 阶段总览

| 阶段 | 内容 | 状态 |
|------|------|------|
| 第一阶段 | 基础设施与清理 | ✅ 已完成 |
| 第二阶段 | 配置中心 + 知识库补完 | ✅ 配置中心已完成，知识库文档详情页待补 |
| 文档更新 | 文档体系完善 | ✅ 已完成 |

---

## 第一阶段：基础设施与清理 ✅ 已完成

> 详细实施记录见：`docs/phase-1-infrastructure.md`

### 完成项

- [x] 1.1 清理无效文件：删除 `OPTIMIZATION_PLAN.md`、`docs/plan_bak/`、`docs/database_bak/`、前端 `__init__.py`（31个）、运行日志
- [x] 1.2 建立文档体系：`architecture.md`、`database-design.md`、`changelog.md`、`dev-plan.md`
- [x] 1.3 操作日志系统：`OperationLogger`（文件系统 JSON Lines + API 查询）
- [x] 1.4 统一布局：`AppLayout.vue`（暖色调侧栏+顶栏+响应式），`App.vue` 路由联动
- [x] 1.5 系统管理后端：JWT 认证、用户CRUD、角色CRUD、审计日志、系统设置
- [x] 1.6 路由修复：拆分 `/testing` 避免路由冲突
- [x] 1.7 共享 auth 模块：JWT 签发/验证、密码哈希、FastAPI 依赖注入
- [x] 1.8 `app/shared/` → `app/common/` 目录重命名，全量 import 路径同步
- [x] 1.9 首页仪表盘：按原型重设计（无侧栏，顶栏+欢迎区+统计卡片+8格功能模块网格）
- [x] 1.10 前端登录/注册页面（双栏品牌展示布局）
- [x] 1.11 系统管理前端：用户管理、角色管理、审计日志、操作日志、系统设置
- [x] 1.12 共享 ModuleLayout.vue 模块侧边栏：消除重复代码，支持 collapsible/flat 两种模式
- [x] 1.13 模块菜单配置集中管理：`module-menus.ts`（6 模块 60+ 菜单项）
- [x] 1.14 SystemLayout 从 n-tabs 改为侧边栏扁平列表
- [x] 1.15 默认管理员账号自动创建（admin/admin123）
- [x] 1.16 前端路由守卫：未登录自动跳转登录页
- [x] 1.17 错误生成模块清理：删除 api_testing、ui_automation、app_automation 模块目录和路由引用
- [x] 1.18 前端布局对齐：配置中心和系统管理所有视图改用内联 scoped CSS，匹配 ai_testing 页面布局样式

### 关键交付物

```
backend/app/common/                        # 公共模块（原 shared）
backend/app/common/auth.py                 # JWT 认证
backend/app/common/logs/operation_logger.py # 操作日志
backend/app/modules/system/                # 系统管理（完整前后端）
frontend/src/shared/views/HomeView.vue     # 首页仪表盘
frontend/src/shared/views/LoginView.vue    # 登录页
frontend/src/shared/views/RegisterView.vue # 注册页
frontend/src/shared/components/layout/ModuleLayout.vue  # 共享模块侧边栏
frontend/src/shared/config/module-menus.ts               # 模块菜单配置
frontend/src/modules/system/               # 系统管理前端（6页面+布局）
docs/architecture.md                      # 架构文档
docs/database-design.md                   # 数据库设计文档
docs/changelog.md                         # 变更日志
docs/dev-plan.md                          # 研发计划（本文档）
docs/phase-1-infrastructure.md            # Phase 1 实施详情
```

---

## 第二阶段：配置中心 + 知识库补完

> 详细规划见：`docs/phase-2-config-center-knowledge.md`

### 配置中心 ✅ 已完成

- [x] AI 模型配置管理（CRUD + 模型供应商选择 + 温度/Token 参数）
- [x] 提示词配置管理（分类管理 + 搜索过滤 + 行内启用开关）
- [x] 生成行为配置（键值对管理 + 智能类型渲染）
- [x] AI 聊天室配置（模型选择 + 对话参数 + RAG/联网搜索）
- [x] UI 环境配置（浏览器类型/视口/超时/截图 CRUD）
- [x] APP 环境配置（平台/包名/Appium/设备/超时 CRUD）
- [x] 配置中心路由注册（`/config/*` 6 个子路由）
- [x] 构建验证：vue-tsc 类型检查通过 + vite build 成功

### 知识库 - 待补

- [ ] 知识库文档详情页
