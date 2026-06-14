# AI-Hub 全面加固计划：JWT 认证 + 迁移修复 + MySQL Checkpoint + 优化

## Context

经过全面调研，当前项目状态：
- **SQLite→MySQL**：业务数据已全部使用 MySQL。但 **LangGraph checkpoint 仍用 SQLite**（`_graph.db`, `_comfort_graph.db`, `_testing_graph.db`）
- **认证**：零鉴权，所有 API 端点完全开放
- **迁移机制**：`_run_migrations()` 是空壳 — 仅插入版本号但无实际 ALTER TABLE
- **URL 校验**：`socket.gethostbyname()` 同步阻塞
- **MySQL 优化**：连接池 maxsize=10，无 query_timeout，无 pool_recycle

本计划涵盖 6 大任务组，共 28 个实施步骤。

---

## Task 1: JWT 认证基础设施

### Task 1.1: 添加依赖
**修改** `backend/requirements.txt`
- 添加 `PyJWT>=2.9.0`、`passlib[bcrypt]>=1.7.4`、`slowapi>=0.1.9`

### Task 1.2: JWT 配置
**修改** `backend/app/config.py`
- 添加: `jwt_secret: str`, `jwt_algorithm: str = "HS256"`, `jwt_expire_minutes: int = 1440`

### Task 1.3: users 表
**修改** `backend/app/shared/core/database.py`
- 在 `CREATE_TABLES_SQL` 添加 `users` 表 + `idx_users_username` 索引

### Task 1.4: Auth Service
**新建** `backend/app/shared/service/auth_service.py`
- `hash_password()` / `verify_password()` / `create_access_token()` / `decode_access_token()` / `register_user()` / `authenticate_user()`

### Task 1.5: Auth Depends Guard
**新建** `backend/app/shared/core/auth_deps.py`
- `get_current_user()` — 验证 Bearer token → 返回 user dict 或 401

### Task 1.6: Auth API
**新建** `backend/app/api/v1/auth.py`
- `POST /api/v1/auth/register` (公开), `POST /api/v1/auth/login` (公开), `GET /api/v1/auth/me` (需认证)

### Task 1.7: 注册路由 + Admin Seeder + 启动警告
**修改** `backend/app/api/v1/router.py` — 添加 auth_router
**新建** `backend/app/shared/core/auth_seed.py` — `seed_admin_user()`
**修改** `backend/main.py` — lifespan 调用 seeder + 凭证安全检查

---

## Task 2: 对所有 API 端点施加认证

### Task 2.1-2.6: 逐个模块添加 `Depends(get_current_user)`
- `knowledge/api.py` — 添加 Depends(get_db_dep) + Depends(get_current_user)
- `chat/api.py` — 添加 Depends(get_current_user)；SSE `/chat/send` 使用 `?token=` query 参数
- `conversation.py` — 改为 Depends(get_db_dep) + Depends(get_current_user)
- `models.py`, `tools.py` — 添加 Depends(get_current_user)
- `comfort/api.py` — 追加 Depends(get_current_user)
- `ai_testing/api.py` — `stream_generation` SSE 使用 `?token=` query 参数

---

## Task 3: LangGraph Checkpoint → MySQL 迁移

### Task 3.1: 创建 MySQLSaver
**新建** `backend/app/shared/core/mysql_saver.py`
- 实现 LangGraph `BaseCheckpointSaver` 接口
- 序列化 checkpoint state 为 JSON（处理 Message 对象的序列化）
- 在 MySQL 中创建 `langgraph_checkpoints` 和 `langgraph_checkpoint_writes` 两张表
- 实现 `aget_tuple()`, `aput()`, `alist()`, `aput_writes()`, `adelete_thread()`

### Task 3.2: 更新 managed_graph.py
**修改** `backend/app/shared/core/managed_graph.py`
- `_setup_checkpointer()` 根据配置决定使用 `AsyncSqliteSaver` 或 `MySQLSaver`
- 添加 `use_mysql_checkpoint: bool = True` 参数

### Task 3.3: 更新三个 graph.py
**修改** `backend/app/modules/chat/graph.py`
- 调用 `super().__init__(db_suffix='_graph', use_mysql_checkpoint=True)`

**修改** `backend/app/modules/comfort/graph.py`
- 调用 `super().__init__(db_suffix='_comfort_graph', use_mysql_checkpoint=True)`

**修改** `backend/app/modules/ai_testing/graph.py`
- 调用 `super().__init__(db_suffix='_testing_graph', use_mysql_checkpoint=True)`

### Task 3.4: 添加配置项
**修改** `backend/app/config.py`
- 添加: `langgraph_checkpoint_backend: str = "mysql"` (可选: `sqlite` / `mysql`)

### Task 3.5: 更新数据库 DDL
**修改** `backend/app/shared/core/database.py`
- 在 `CREATE_TABLES_SQL` 添加 `langgraph_checkpoints` 和 `langgraph_checkpoint_writes` 表

---

## Task 4: 数据库迁移修复

### Task 4.1: 修复 ai_testing _run_migrations()
**修改** `backend/app/modules/ai_testing/database.py`
- v5: 执行实际 ALTER TABLE 添加 `requirement_title`, `output_mode`, `enable_auto_review`, `review_timeout`
- v6: 创建 `testing_task_generated_cases` 和 `testing_generated_case_items`（带 IF NOT EXISTS）
- 使用 INFORMATION_SCHEMA 检查列存在性

### Task 4.2: 添加 comfort 迁移机制
**修改** `backend/app/modules/comfort/database.py`
- 创建 `comfort_schema_version` + `_run_comfort_migrations()`

### Task 4.3: 添加 shared 层迁移机制
**修改** `backend/app/shared/core/database.py`
- 创建 `shared_schema_version` + `_run_shared_migrations()`

---

## Task 5: URL 校验器异步化

### Task 5.1: 添加异步函数
**修改** `backend/app/shared/utils/url_validator.py`
- 添加 `async is_safe_url_async()` — `run_in_executor` 异步 DNS 解析

### Task 5.2: 标注同步调用者
**修改** `backend/app/shared/agent/tools/downloader.py`, `web_scraper.py`
- 添加注释：`is_safe_url()` 在 LangGraph executor 线程池中执行，不阻塞事件循环

---

## Task 6: MySQL 优化 + 凭证轮换

### Task 6.1: 连接池调优
**修改** `backend/app/config.py` — 添加 `mysql_pool_size`, `mysql_pool_recycle`
**修改** `backend/app/shared/core/database.py` — `_create_pool()` 使用 pool_recycle, connect_timeout, minsize=2

### Task 6.2: .env.example 更新
**修改** `backend/.env.example` — JWT 配置、凭证轮换指南、MYSQL_USER 建议

### Task 6.3: 启动凭证安全警告
**修改** `backend/main.py` — lifespan 检查 jwt_secret/mysql_user 默认值

---

## 验证步骤

```bash
# 后端编译
cd backend
for f in main.py app/config.py app/shared/core/database_bak.py app/shared/core/auth_deps.py \
  app/shared/service/auth_service.py app/api/v1/auth.py app/modules/ai_testing/database_bak.py \
  app/modules/comfort/database_bak.py app/shared/utils/url_validator.py \
  app/shared/core/mysql_saver.py app/shared/core/managed_graph.py \
  app/modules/chat/graph.py app/modules/comfort/graph.py app/modules/ai_testing/graph.py;
do python -m py_compile $f && echo "OK $f" || echo "FAIL $f"; done

# 前端
cd frontend && npx vue-tsc --noEmit && npx vite build

# 功能验证
# 1. POST /api/v1/auth/login → token
# 2. GET /api/v1/testing/projects (无 token) → 401
# 3. GET /api/v1/testing/projects (带 token) → 200
# 4. SSE /testing/generate/{id}/stream?token= → 流式
# 5. LangGraph 对话 → checkpoint 存入 MySQL langgraph_checkpoints 表
```
