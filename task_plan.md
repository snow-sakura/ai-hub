# Task Plan: 第一轮代码审查 — 全项目代码审查、问题修复、性能优化、UI 改进

## Goal
对 qoder_one 项目（ai-hub 平台）进行系统性第一轮代码审查，覆盖前后端三大模块（AI聊天室、哄哄模拟器、AI测试助手），发现并修复代码问题、性能瓶颈、安全隐患和 UI 缺陷。

## Current Phase
Phase 1

## Phases

### Phase 1: 后端代码审查 — API / Service / Repository / Domain 层
- [ ] 审查 API 路由层（router、schemas、入参校验）
- [ ] 审查 Service 层（业务编排、错误处理）
- [ ] 审查 Repository 层（数据库查询、CRUD）
- [ ] 审查 Domain 层（实体定义、异常定义）
- [ ] 审查 SSE 流式处理逻辑
- [ ] 审查 LLMFactory 和模型管理
- [ ] 检查配置管理、数据库连接
- **Status:** in_progress

### Phase 2: 前端代码审查 — 组件 / 状态管理 / 类型
- [ ] 审查组件结构（Chat、Comfort、AI Testing）
- [ ] 审查 Pinia stores 和状态管理
- [ ] 审查 TypeScript 类型定义
- [ ] 审查 SSE 消费逻辑
- [ ] 审查路由配置和导航守卫
- **Status:** pending

### Phase 3: 性能优化
- [ ] 后端性能：数据库查询、SSE 流式效率
- [ ] 前端性能：虚拟滚动、chunk 分包、懒加载
- [ ] API 响应优化、减少冗余请求
- **Status:** pending

### Phase 4: UI/UX 改进
- [ ] 检查缺失的空/错误/加载状态
- [ ] 检查响应式布局
- [ ] 检查组件一致性和交互细节
- [ ] 优化主题和视觉细节
- **Status:** pending

### Phase 5: 安全审查与代码质量
- [ ] 检查 API 入参校验完整性
- [ ] 检查 XSS/注入防护
- [ ] 检查凭证管理
- [ ] 代码异味和反模式
- **Status:** pending

### Phase 6: 修复与交付
- [ ] 根据审查结果修复代码问题
- [ ] 提交变更并汇总审查报告
- **Status:** pending

## Key Questions
1. 后端目前没有测试文件，是否需要在审查期间补充关键路径的单元测试？
2. 前端是否使用了正确的虚拟滚动方案处理长列表？
3. SSE 流式处理是否有潜在的连接泄漏或内存泄漏？

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 先审查后修复 | 确保问题列表完整再动手修改，避免修复过程中引入新问题 |
| 增量和分模块更新 | 每个模块的修复作为独立 commit，便于回滚和审查 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- 更新阶段状态：pending → in_progress → complete
- 审查发现同时写入 findings.md
- 所有修复前先记录问题
