---
trigger: always_on
---
# 代码风格规范 (code-style.md)

## 一、基础规范
- **语言**：TypeScript/JavaScript  
- **缩进**：**2 个空格**（禁用 Tab）  
- **行宽**：**≤ 100 字符**  
- **分号**：**必须省略**（ESLint `semi: off`）

## 二、命名规则
- **变量/函数**：`camelCase`（例：`getUserInfo`）  
- **类/组件**：`PascalCase`（例：`UserProfile`）  
- **常量**：`UPPER_SNAKE_CASE`（例：`MAX_RETRY_COUNT`）  
- **布尔变量**：前缀 `is`/`has`（例：`isLoading`）

## 三、注释要求
- **函数必须有 JSDoc**，格式：  
  ```ts
  /**
   * 简短功能描述（≤ 20 字符）
   * 
   * @param param1 - 参数说明
   * @returns 返回值说明
   */