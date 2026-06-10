/** 会话类型定义 */
export interface Conversation {
  id: string
  title: string
  type?: string          // 'chat' | 'comfort'，后端按此过滤
  createdAt: string
  updatedAt: string
}

export interface MessageData {
  id: string
  conversationId: string
  role: string
  content: string
  metadata: string
  createdAt: string
}
