# Findings & Decisions

## Requirements
- 全面审查 qoder_one 项目（ai-hub/）的代码质量
- 覆盖后端（Python FastAPI + LangGraph）和前端（Vue 3 + TypeScript）
- 覆盖三个业务模块：AI聊天室、哄哄模拟器、AI测试助手
- 发现问题后直接修复
- 优化前后端性能、UI/UX

## Research Findings

### Backend Issues Found
1. **CRITICAL: 重复的 db 获取/关闭样板代码** — comfort/api.py 和 ai_testing/api.py 的每个 handler 都重复 `db = await get_db()` + `try/finally: await db.close()`，约 20+ 处重复
2. **HIGH: chat/api.py send_chat 缺少外层异常处理** — StreamingResponse 生成器没有 try/except 包装
3. **HIGH: ChatRequest.message 缺少 max_length 验证** — 消息无长度限制，可能被滥用
4. **HIGH: agent_node.py 无条件发送 reasoning_end** — 即使 reasoning_effort="disabled" 也发送 reasoning_end 事件
5. **HIGH: ai_testing/sse_stream.py 流式中途关闭 db 后重新获取** — 第 93 行关闭后又在第 187 行重新获取新连接
6. **MEDIUM: ai_testing 用例计数靠字符串匹配** — 通过 `final_content.count("**用例 ID**")` 估算，不可靠
7. **MEDIUM: API 返回类型不精确** — 很多返回 `ApiResponse[dict[str, Any]]` 而非具体类型
8. **LOW: Repository 层 update 方法字符串拼接 SQL** — 每个方法重复 set_clause 拼接逻辑

### Frontend Issues Found
9. **HIGH: ChatMessageList 流式滚动无节流** — 每个 token 都触发 scrollToIndex，频繁重排
10. **MEDIUM: 两个 watch 同时触发滚动** — streamingContent + currentThinkingSteps 各自独立 watch
11. **MEDIUM: useSseStream resolveStore 热路径调用 store** — 每个事件都调用 useChatStore/useComfortStore
12. **MEDIUM: Message 组件使用 emoji 而非图标** — ✅ ⚠️ 🔄 跨平台显示不一致
13. **LOW: 空状态使用 emoji 🤖** — 建议使用图标组件
14. **LOW: 404 路由无明确提示** — 直接重定向到首页

### Performance Issues
15. **MEDIUM: 虚拟滚动 estimateSize 偏低** — estimateSize: 80，实际消息可能更高
16. **LOW: 每个 API 请求新建 DB 连接** — 无连接池

### Security Issues
17. **MEDIUM: 错误响应包含 traceback** — service.py 中的 error event 包含 `traceback.format_exc()[-500:]`
18. **LOW: ChatRequest 无长度限制** — 空消息或超长消息

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| 沿用现有架构风格 | 项目已有明确的分层架构，审查遵循该约束 |
| 不引入新的第三方库 | 第一轮审查以优化现有代码为主 |
| SSE 流式处理保持现有模式 | fetch + ReadableStream 已成熟 |
| 使用 FastAPI Depends 优化 DB 连接 | 减少舒适模块和测试模块的样板代码 |
| DB 连接不改为连接池 | SQLite 不支持并发写连接池 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| 无 | 第一轮审查，尚未遇到实施问题 |

## Resources
- 后端入口: ai-hub/backend/main.py
- 路由汇总: ai-hub/backend/app/api/v1/router.py
- 配置: ai-hub/backend/app/config.py
- LLM工厂: ai-hub/backend/app/shared/core/llm_factory.py
- 数据库: ai-hub/backend/app/shared/core/database.py
- 前端入口: ai-hub/frontend/src/main.ts
- 路由: ai-hub/frontend/src/shared/router/index.ts
- SSE消费: ai-hub/frontend/src/shared/composables/useSseStream.ts
