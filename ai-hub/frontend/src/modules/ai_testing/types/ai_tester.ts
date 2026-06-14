/** AI 评测师相关类型 */

/** 评测师会话 */
export interface AITesterSession {
  id: string
  name: string
  model: string
  message_count: number
  created_at: string
  updated_at: string
}

/** 创建会话参数 */
export interface AITesterSessionCreate {
  name?: string
  model?: string
}

/** 评测师消息 */
export interface AITesterMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  rating?: 'up' | 'down' | null
  created_at: string
}

/** 发送消息参数 */
export interface AITesterMessageSend {
  session_id: string
  content: string
  model?: string
}
