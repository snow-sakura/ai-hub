# 第二阶段：配置中心 + 知识库补完

> 预估工期：5-6天 | 状态：✅ 配置中心部分已完成（知识库文档详情页待补）

## 目标

建立配置中心模块（对应原型 06-配置中心），包括 AI 模型配置、提示词配置、生成行为配置、自动化测试环境配置；补全知识库文档详情页（对应原型 08-知识库）。

---

## 2.1 AI 模型配置管理

### 后端

**数据库表** `backend/app/modules/config_center/database.py`:

```sql
CREATE TABLE config_model_providers (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,       -- openai / deepseek / qwen / zhipu / ollama
  display_name VARCHAR(200),               -- 展示名称
  api_base_url VARCHAR(500),               -- API 地址
  api_key_encrypted VARCHAR(500),          -- 加密后的 API Key
  models JSON,                             -- 可用模型列表 ["gpt-4","gpt-3.5-turbo"]
  is_enabled TINYINT DEFAULT 1,
  sort_order INT DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**API 端点** (`backend/app/modules/config_center/api.py`):

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/config-center/models` | 列出模型配置 |
| POST | `/config-center/models` | 新增模型配置 |
| PUT | `/config-center/models/{id}` | 更新模型配置 |
| DELETE | `/config-center/models/{id}` | 删除 |
| POST | `/config-center/models/{id}/test` | 测试连接 |

### 前端

`frontend/src/modules/config_center/views/AIModelConfigView.vue`:
- 表格展示模型列表（名称/供应商/状态/模型数）
- 新建/编辑对话框（名称、API URL、API Key、可用模型多选）
- 测试连接按钮
- 启用/禁用开关

---

## 2.2 提示词配置管理

### 后端

**数据库表**:

```sql
CREATE TABLE config_prompt_templates (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  category VARCHAR(50) NOT NULL,           -- testing / chat / comfort / review
  content TEXT NOT NULL,                   -- 提示词内容，支持 {{variable}} 模板
  variables JSON,                          -- 变量定义 [{"name":"requirement","desc":"需求文本"}]
  is_default TINYINT DEFAULT 0,
  version INT DEFAULT 1,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**API 端点**:

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/config-center/prompts` | 列表（按 category 筛选） |
| POST | `/config-center/prompts` | 新增 |
| PUT | `/config-center/prompts/{id}` | 更新 |
| DELETE | `/config-center/prompts/{id}` | 删除 |
| POST | `/config-center/prompts/{id}/preview` | 预览渲染结果 |

### 前端

`frontend/src/modules/config_center/views/PromptConfigView.vue`:
- 分类选项卡（AI测试/聊天/哄哄/评审）
- 提示词列表 + 编辑器
- 内置 Monaco Editor 精简版或 textarea
- 变量预览面板

---

## 2.3 生成行为配置

### 后端

**数据库表**:

```sql
CREATE TABLE config_behavior (
  id VARCHAR(36) PRIMARY KEY,
  `key` VARCHAR(100) NOT NULL UNIQUE,      -- temperature / max_tokens / top_k / top_p / chunk_size / recall_count
  `value` JSON NOT NULL,                   -- {"default":0.7,"min":0,"max":2,"step":0.1}
  display_name VARCHAR(200),
  description TEXT,
  category VARCHAR(50) DEFAULT 'general',  -- general / testing / rag
  updated_at TIMESTAMP
);
```

**API 端点**:

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/config-center/behavior` | 配置列表 |
| PUT | `/config-center/behavior/{key}` | 更新配置值 |

### 前端

`frontend/src/modules/config_center/views/GenerationConfigView.vue`:
- 按分类分组的配置卡片
- 滑块/输入框/数字框根据不同字段类型渲染
- 一键恢复默认值

---

## 2.4 环境配置

### 后端

**数据库表**:

```sql
CREATE TABLE config_environments (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  category VARCHAR(50) NOT NULL,           -- app / ui
  config JSON NOT NULL,                    -- {adb_path:"",appium_url:"",playwright_url:"",browser:"chromium"}
  is_default TINYINT DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**API 端点**: 标准 CRUD `/config-center/environments`

### 前端

`frontend/src/modules/config_center/views/EnvironmentConfigView.vue`:
- 按类别（APP/UI）分 tab
- 环境变量键值对编辑
- 默认环境标记

---

## 2.5 知识库文档详情页

补全 `frontend/src/modules/knowledge/views/` 中文档详情页：
- 文档元信息（标题/上传时间/大小/类型）
- 文档内容预览（Markdown 渲染/纯文本/代码高亮）
- 关联测试用例列表
- 版本历史
- 重新上传/删除操作

### 后端补充

**API 端点**（如缺失）：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/knowledge/documents/{id}` | 文档详情含内容 |
| GET | `/knowledge/documents/{id}/versions` | 版本历史 |
| POST | `/knowledge/documents/{id}/reupload` | 重新上传 |

---

## 目录结构产出

```
backend/app/modules/config_center/
├── __init__.py
├── api.py               # CRUD API
├── service.py           # 业务逻辑
├── repository.py        # 数据访问
├── schemas.py           # Pydantic 模型
└── database.py          # 表 DDL

frontend/src/modules/config_center/
├── api/config_center.ts
├── types/config_center.ts
├── views/
│   ├── AIModelConfigView.vue
│   ├── PromptConfigView.vue
│   ├── GenerationConfigView.vue
│   └── EnvironmentConfigView.vue
└── components/layout/
    └── ConfigCenterLayout.vue

frontend/src/modules/knowledge/
└── views/               # 补充文档详情页
```

## 路由

前端路由将在 `/config-center` 下设置嵌套子路由。
