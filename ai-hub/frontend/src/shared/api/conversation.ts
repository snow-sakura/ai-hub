import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type {
  Conversation,
  MessageData,
  CreateConversationRequest,
  UpdateConversationRequest,
} from '@/shared/types/conversation'

/** 获取会话列表 */
export function getConversations(type?: 'chat' | 'comfort'): Promise<ApiResponse<Conversation[]>> {
  const params = type ? { type } : undefined
  return request.get('/conversations', { params })
}

/** 创建会话 */
export function createConversation(
  data: CreateConversationRequest = { title: '新会话' }
): Promise<ApiResponse<Conversation>> {
  return request.post('/conversations', data)
}

/** 重命名会话 */
export function renameConversation(
  id: string,
  data: UpdateConversationRequest
): Promise<ApiResponse<Conversation>> {
  return request.patch(`/conversations/${id}`, data)
}

/** 删除会话 */
export function deleteConversation(id: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/conversations/${id}`)
}

/** 分页消息响应 */
export interface PaginatedMessages {
  items: MessageData[]
  total: number
}

/** 获取会话消息（分页） */
export function getMessages(
  convId: string,
  page: number = 1,
  pageSize: number = 50,
): Promise<ApiResponse<PaginatedMessages>> {
  return request.get(`/conversations/${convId}/messages`, {
    params: { page, page_size: pageSize },
  })
}
