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

## 三、模块隔离
- **核心模块**（`/core`）：**不得引用业务代码**  
- **工具函数**：必须放在 `/utils`，**禁止分散在业务目录**

## 四、禁止项
- ❌ 跨层调用（例：API 层直接调用 Repository）  
- ❌ 循环依赖（通过 `madge` 检测）  
- ❌ 在 Domain 层使用 `console.log`