---
trigger: always_on
---

---

```markdown
# 安全规范 (security.md)

## 一、输入校验
- **所有 API 入参**：**必须用 Zod 验证**（例：`z.string().email()`）  
- **禁止直接使用 `req.body`**：需通过 `validatedData = schema.parse(req.body)` 转换

## 二、敏感操作
- **密码/密钥**：  
  - 存储必须 **bcrypt 加密**（`cost: 12`）  
  - 传输必须 **HTTPS + JWT**（禁用明文传输）  
- **SQL 查询**：**必须参数化**（禁用字符串拼接）

## 三、权限控制
- **关键接口**：**必须校验 RBAC**（例：`if (!hasPermission('user:delete')) throw Forbidden`）  
- **默认拒绝**：未明确授权的操作视为 **禁止**

## 四、禁止项
- ❌ `eval()`/`Function()` 动态执行代码  
- ❌ 未转义的 HTML 渲染（XSS 风险）  
- ❌ 硬编码凭证（如 `const API_KEY = 'xxx'`）