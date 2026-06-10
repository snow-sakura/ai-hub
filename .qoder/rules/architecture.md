---
trigger: always_on
---
# 项目架构约束 (architecture.md)

## 一、分层规则
- **API 层**：仅处理请求/响应，**不得直接访问数据库**
- **Service 层**：**唯一可操作数据库的模块**
- **Domain 层**：纯业务逻辑（**无框架依赖**）

## 二、依赖方向
- **禁止反向依赖**：
  `API → Service → Repository → Domain`（✅ 允许）
  `Domain → Repository`（❌ 禁止）

## 三、模块隔离（前端 + 后端）

### 目录组织
项目代码分为两类目录：
- **shared/**：公共基础设施，被所有模块共享
- **modules/{chat,comfort,knowledge}/**：业务模块，各自独立

### 依赖方向规则
```
modules/chat     → shared/*                     （✅ 允许）
modules/comfort  → shared/*                     （✅ 允许）
modules/knowledge → shared/*                    （✅ 允许）
shared/          → （不依赖任何 modules/*）     （❌ 禁止）
modules/chat     → modules/comfort (limited)     （✅ 仅 stream_service 委托）
modules/comfort  → modules/chat                  （❌ 禁止）
```

### 模块边界约束
- **shared/** 不得导入任何 `modules/*` 中的代码
- **modules/** 之间的交叉引用必须最小化，且只能通过明确定义的接口/服务委托
- **前端**：模块 store 之间允许有限的循环引用（Vue 3 支持 lazy store references），但应避免深层链式依赖

## 四、禁止项
- ❌ 跨层调用（例：API 层直接调用 Repository）
- ❌ 循环依赖（通过 `madge` / `vue-tsc` 检测）
- ❌ 在 Domain 层使用 `console.log`
- ❌ 前端 `src/api/` `src/stores/` `src/types/` 等旧目录已被移除，代码统一放在 `shared/` 或 `modules/*/` 下
