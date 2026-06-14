import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type { AITesterSession, AITesterSessionCreate, AITesterMessage, AITesterMessageSend } from '@/modules/ai_testing/types/ai_tester'

/** 获取会话列表 */
export function listSessions(): Promise<ApiResponse<AITesterSession[]>> {
  return request.get('/testing/ai-tester/sessions')
}

/** 创建会话 */
export function createSession(data: AITesterSessionCreate): Promise<ApiResponse<AITesterSession>> {
  return request.post('/testing/ai-tester/sessions', data)
}

/** 删除会话 */
export function deleteSession(sessionId: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/ai-tester/sessions/${sessionId}`)
}

/** 获取会话消息（分页，offset=0 返回最新 50 条） */
export function getMessages(sessionId: string, offset = 0, limit = 50): Promise<ApiResponse<{ messages: AITesterMessage[]; total: number; offset: number; limit: number }>> {
  return request.get(`/testing/ai-tester/sessions/${sessionId}/messages`, { params: { offset, limit } })
}

/** 发送消息（非流式） */
export function sendMessage(sessionId: string, data: { content: string; model?: string }): Promise<ApiResponse<AITesterMessage>> {
  return request.post(`/testing/ai-tester/sessions/${sessionId}/messages`, data)
}

/** 流式发送消息（SSE），返回 Response 对象供前端自行消费 ReadableStream */
export function streamSendMessage(sessionId: string, content: string, model = ''): Promise<Response> {
  return fetch(`/api/v1/testing/ai-tester/sessions/${sessionId}/messages/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, model }),
  })
}

/** 重命名会话 */
export function updateSession(sessionId: string, data: { name: string }): Promise<ApiResponse<boolean>> {
  return request.put(`/testing/ai-tester/sessions/${sessionId}`, data)
}

/** 批量删除会话 */
export function batchDeleteSessions(ids: string[]): Promise<ApiResponse<boolean>> {
  return request.post('/testing/ai-tester/sessions/batch-delete', { ids })
}

/** 给消息评分 */
export function rateMessage(messageId: string, rating: 'up' | 'down' | null): Promise<ApiResponse<boolean>> {
  return request.put(`/testing/ai-tester/messages/${messageId}/rating`, { rating })
}
