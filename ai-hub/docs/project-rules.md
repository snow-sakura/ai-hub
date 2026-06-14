# AI-HUB 项目研发规则

> 最后更新：2026-06-14
> 适用范围：仅限 `ai-hub/` 项目
> 用途：所有阶段研发、代码审查、任务执行必须参照本规则

---

## 一、技术栈与选型规则

| 领域 | 强制选择 | 禁止项 |
|------|---------|--------|
| 后端框架 | FastAPI（异步原生） | ❌ Django、Flask |
| 前端框架 | Vue 3 + TypeScript + Vite（Composition API） | ❌ React、Angular |
| UI 组件库 | Naive UI（暖色调主题覆盖 #C67B5C） | ❌ Element Plus、Ant Design |
| 状态管理 | Pinia（模块化 store） | ❌ Vuex |
| AI 工作流 | LangGraph + LangChain | ❌ 手工编排 |
| 数据库 | MySQL 8.0+（aiomysql 驱动，InnoDB, utf8mb4） | ❌ SQLite（除开发回退）、MongoDB |
| 认证方式 | JWT（PyJWT） + bcrypt（passlib） | ❌ Session、OAuth（除非特别需求） |
| 定时任务 | apscheduler（最小依赖） | ❌ Celery、Redis Queue |
| 消息队列 | 不引入 | ❌ RabbitMQ、Kafka |
| 向量检索 | ChromaDB | ❌ Milvus、Pinecone |
| 操作日志 | 文件系统 JSON Lines + API 查询 | ❌ 数据库存储 |

## 二、后端分层架构规则

### 2.1 四层结构

```
API（路由/入参校验） → Service（业务编排） → Repository（数据访问） → Domain（领域实体）
```

### 2.2 层间约束

| 约束 | 说明 |
|------|------|
| API 层 | 仅处理请求/响应序列化，**不得直接访问数据库** |
| Service 层 | **唯一可操作数据库的层**，负责业务编排 |
| Repository 层 | SQL 查询封装，返回 dict，**不含业务逻辑** |
| Domain 层 | 纯数据类型/实体定义，**无框架依赖**，无 `console.log` |

### 2.3 依赖方向（强制）

```
API → Service → Repository → Domain    ✅ 允许
Domain → Repository                      ❌ 禁止（反向依赖）
API → Repository (skip Service)          ❌ 禁止（跨层调用）
```

### 2.4 模块文件命名规范

每个模块必须包含 5 个文件：

```
apps/{module}/
├── api.py           # FastAPI 路由（from app.dependencies import get_db_dep）
├── schemas.py       # Pydantic 请求/响应模型
├── service.py       # 业务逻辑（依赖 repository）
├── repository.py    # 数据访问（SQL）
├── database.py      # 表 DDL 定义（CREATE TABLE ...）
└── domain.py        # 领域实体（可选，复杂场景）
```

## 三、模块隔离规则

### 3.1 模块目录结构

```
frontend/src/modules/{module}/      # 前端模块
backend/app/modules/{module}/       # 后端模块
```

### 3.2 依赖方向

```
modules/{X} → shared/*             ✅ 模块可依赖公共基础设施
shared/* → modules/{X}             ❌ 公共层不得依赖任何业务模块
modules/{X} → modules/{Y}          ❌ 禁止模块间交叉引用
```

### 3.3 6 大功能模块

| 模块 | 状态 | 说明 |
|------|------|------|
| `system` | ✅ 完整 | 认证 + 用户/角色/审计/设置管理 |
| `chat` | ✅ 完整 | AI 聊天室（多模型 + RAG） |
| `comfort` | ✅ 完整 | 哄哄模拟器 |
| `knowledge` | ⚠️ 基本完整 | 知识库（需补文档详情页） |
| `ai_testing` | ⚠️ 已实现 | AI 测试 + 测试管理（需 UI 对齐原型） |
| `config_center` | ✅ 完整 | 配置中心（6 页配置管理） |

> 注：`api_testing`、`ui_automation`、`app_automation` 模块已在 Phase 1 修正中清理删除。

## 四、API 设计规则

### 4.1 统一响应格式

```python
# 成功
{"code": 200, "data": {...}, "message": "操作成功"}

# 列表
{"code": 200, "data": {"items": [...], "total": N, "page": 1, "page_size": 20}}

# 错误
raise HTTPException(status_code=400, detail="错误描述")
```

### 4.2 路由汇总

所有模块路由在 `backend/app/api/v1/router.py` 中集中注册：

```python
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(system_router, prefix="/system", tags=["系统管理"])
```

### 4.3 路由路径规则

- 认证相关：`/auth/*`
- 系统管理：`/system/*`
- 功能模块：`/{module-name}/*`（全小写连字符，如 `/api-testing`）
- 分页参数：`?page=1&page_size=20`
- 筛选参数：查询字符串（如 `?user_id=xxx&action=create`）

### 4.4 SSE 流式事件

LangGraph 流式输出统一使用 SSE 协议，事件类型定义在 `backend/app/common/utils/sse_helper.py`：

| 事件 | 说明 |
|------|------|
| `token` | LLM 流式文本 |
| `reasoning_token` | DeepSeek 思考过程 |
| `reasoning_end` | 思考结束 |
| `tool_start` / `tool_result` | 工具调用 |
| `thinking` / `progress` | 进度 |
| `done` / `error` | 完成/错误 |
| `{module_name}_stage` / `{module_name}_token` / `{module_name}_done` | 模块自定义事件 |

## 五、数据库设计规则

### 5.1 通用规范

- **主键**：UUID v4 字符串（`VARCHAR(36)`）
- **引擎**：`ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`
- **表名**：全小写下划线，如 `system_roles`、`testing_projects`
- **时间字段**：`TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
- **软删除**：不实现软删除，物理删除即可（KISS）

### 5.2 表定义位置

- 共享表：`backend/app/common/core/database.py`
- 模块表：`backend/app/modules/{module}/database.py`

### 5.3 增量迁移原则

```python
# 每个模块的 database.py 使用 CREATE TABLE IF NOT EXISTS
async def init_{module}_tables(db) -> None:
    await db.execute("SET sql_notes = 0")
    try:
        await db.executescript(TABLES_SQL)
    finally:
        await db.execute("SET sql_notes = 1")
```

- 禁止 `DROP TABLE` 或其他破坏性 DDL（除非明确要求）
- 新增字段使用 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`
- 模块级版本控制（如有变更，通过模块 `database.py` 管理）

### 5.4 索引规则

- 外键字段必须建索引（`INDEX idx_{table}_{column}`）
- 高频查询字段建索引（状态、类型、时间）
- 避免在 JSON/text 字段上建索引

## 六、前端设计规则

### 6.1 UI 风格

- **主色调**：`#C67B5C`（暖色系棕橙色）
- **布局**：侧边栏 220-240px + 顶栏 48px + 内容区
- **侧边栏模式**：
  - `collapsible`（可折叠分组）：菜单项多的模块（ai-testing、api-testing、ui-automation）
  - `flat`（扁平列表）：菜单项少的模块（system、config-center、app-automation）
- 所有模块侧边栏使用共享 `ModuleLayout.vue`

### 6.2 路由规则

- **路由守卫**：`router.beforeEach` 检查 `localStorage.getItem('access_token')`
- **白名单**：`/login`、`/register` 无需认证
- **登录跳转**：未登录用户重定向到 `/login?redirect=<原路径>`
- **模块路由**：嵌套布局路由，子页面作为 children

### 6.3 登录/注册页

双栏布局：
- **左栏**：品牌展示（暖色渐变背景 + 特性卡片 2×2 网格 + AI 能力标签）
- **右栏**：表单区（白色背景，固定 480px/500px 宽度）

### 6.4 通用组件

- `AppLayout.vue`：统一全局布局（8 个模块导航 + 响应式）
- `ModuleLayout.vue`：模块内部侧边栏布局
- 条件排除布局的路由：`/`、`/login`、`/register`、`/chat`、`/comfort`、`/emotion-dashboard`

## 七、安全规则

### 7.1 认证安全

- 密码存储使用 bcrypt（`passlib.context.CryptContext(schemes=["bcrypt"])`）
- JWT 密钥必须从 `.env` 读取，禁止硬编码
- JWT 过期时间默认 24 小时
- 未认证接口通过 `Depends(get_current_user)` 保护
- 前端路由守卫：所有页面（除登录/注册）需要 token

### 7.2 角色与权限

```
admin（管理员）       → ["*"]                               — 全部权限
project_admin（项目管理） → ["project:*"]                    — 项目内全部权限
tester（测试工程师）    → ["project:view", "case:*", "execution:*", "report:*"]
viewer（只读用户）     → ["project:view", "report:view"]
```

- 内置角色（`is_builtin=1`）**不可删除**
- 删除角色时必须检查 `is_builtin` 标志位

### 7.3 默认管理员

- 账号：`admin` / `admin123`
- 创建时机：首次启动自动创建（幂等）
- 警告：生产环境首次登录后立即修改密码
- 覆盖方式：通过 `.env` 环境变量配置

### 7.4 CORS

- 开发环境：`http://localhost:5173`
- 生产环境：必须指定具体域名，禁止使用 `*`

## 八、代码迁移规则（testhub → ai-hub）

| testhub（Django） | ai-hub（FastAPI） | 说明 |
|-------------------|-------------------|------|
| `models.py` | `database.py` + `schemas.py` | DDL + Pydantic 分离 |
| `views.py` | `api.py` + `service.py` | 路由 + 业务分离 |
| `serializers.py` | `schemas.py` | 请求/响应模型 |
| `tasks.py` | LangGraph `async` flow / apscheduler | AI 工作流或定时任务 |
| `admin.py` | ❌ 不迁移 | Django 专属功能 |
| `dashboard.py` | ❌ 不迁移 | Django 专属功能 |

- 不复制 Django 独有功能（admin、dashboard、migration framework）
- 表结构可参考，但需适配 MySQL + InnoDB + utf8mb4

## 九、编码规范

### 9.1 Python

- **注释**：中文注释，解释 WHY 而非 WHAT
- **导入顺序**：标准库 → 第三方 → 项目内部，空行分隔
- **异步**：优先 `async/await`，`def` 仅在纯同步函数使用
- **类型提示**：函数参数和返回值必须标注类型
- **错误处理**：业务异常使用 `raise ValueError()`，API 层捕获转为 `HTTPException`

### 9.2 TypeScript/Vue

- **命名**：组件 `PascalCase`，变量/函数 `camelCase`，常量 `UPPER_SNAKE_CASE`
- **布尔变量**：前缀 `is`/`has`
- **自动导入**：`unplugin-auto-import` + `unplugin-vue-components`，无需手动 import Vue/Naive UI
- **新增 `@vueuse/core` 函数**：必须在 `vite.config.ts` 的 `AutoImport` 配置中显式声明
- **构建**：先 `vue-tsc -b` 类型检查，再 `vite build`

## 十、默认凭据与配置

### 10.1 默认管理员

| 字段 | 默认值 | 覆盖方式 |
|------|--------|---------|
| 用户名 | `admin` | `.env` 中配置 |
| 密码 | `admin123` | `.env` 中配置 |

### 10.2 后端默认端口

| 服务 | 默认端口 |
|------|---------|
| FastAPI 后端 | 8000 |
| Vite 前端 | 5173 |

### 10.3 数据库连接池

```env
MYSQL_POOL_SIZE=10
MYSQL_POOL_RECYCLE=3600
```

## 十一、实施原则（KISS）

1. **最少代码**：用最少的代码解决问题，不做过度推测
2. **不提前抽象**：三个相似行优于一个过早的抽象
3. **不添加未来可能需要的功能**：只在需要时实现
4. **不添加注释说明 WHAT**：好命名比注释更清晰；只在 WHY 非明显时写注释
5. **增量为先**：每个阶段只实现该阶段的目标，不超前实现
6. **文档同步**：代码变更必须同步更新相关文档（dev-plan.md、changelog.md、phase-*.md）

---

## 附录：Phase 1 审计发现的待修复问题

以下为 Phase 1 实施完成后审查发现的问题：

| 问题 | 严重度 | 状态 | 修复方案 |
|------|--------|------|---------|
| JWT_SECRET_KEY 硬编码 | 中 | ✅ 已修复 | 迁移到 `config.py` 的 `jwt_secret_key` 字段，从 `.env` 读取 |
| 内置角色可被删除 | 中 | ✅ 已修复 | `delete_role()` 增加 `is_builtin` 检查，内置角色不允许删除 |
| settings API 代码异味 | 低 | ✅ 已修复 | `SystemRepository(await svc.repo.db)` 改为直接调用 `svc.repo` |
| OperationLogger 未集成到其他模块 | 低 | ⏳ 后续阶段 | 新增模块时按需集成操作日志记录 |
