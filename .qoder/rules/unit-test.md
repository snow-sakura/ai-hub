---
trigger: always_on
---

---

```markdown
# 单元测试规范 (unit-test.md)

## 一、覆盖要求
- **新功能**：**覆盖率 ≥ 80%**  
- **核心模块**：**覆盖率 ≥ 90%**  
- **测试文件命名**：`{模块名}.test.ts`（例：`auth.service.test.ts`）

## 二、结构规范
- **测试用例分组**：  
  ```ts
  describe('AuthService', () => {
    describe('login', () => {
      it('应返回 JWT 令牌', async () => { ... });
    });
  });