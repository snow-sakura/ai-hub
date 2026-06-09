import request from './request'
import type { ApiResponse } from '../types/api'
import type { Conversation, MessageData } from '../types/conversation'

/** 获取会话列表 */
export function getConversations(): Promise<ApiResponse<Conversation[]>> {
  return request.get('/conversations')
}

/** 创建会话 */
export function createConversation(title = '新会话'): Promise<ApiResponse<Conversation>> {
  return request.post('/conversations', { title })
}

/** 重命名会话 */
export function renameConversation(id: string, title: string): Promise<ApiResponse<Conversation>> {
  return request.patch(`/conversations/${id}`, { title })
}

/** 删除会话 */
export function deleteConversation(id: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/conversations/${id}`)
}

/** 获取会话消息 */
export function getMessages(convId: string): Promise<ApiResponse<MessageData[]>> {
  return request.get(`/conversations/${convId}/messages`)
}
