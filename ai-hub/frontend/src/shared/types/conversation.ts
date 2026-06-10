/** 会话类型定义 */
export interface Conversation {
  id: string
  title: string
  type: 'chat' | 'comfort'  // 会话类型：普通聊天 / 哄哄模拟器
  createdAt: string
  updatedAt: string
}

/** 消息数据（从后端获取的原始格式） */
export interface MessageData {
  id: string
  conversationId: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata: string  // JSON 字符串，需要解析
  createdAt: string
}

/** 解析后的消息元数据 */
export interface MessageMetadata {
  model?: string
  provider?: string
  toolCalls?: Array<{
    toolCallId: string
    toolName: string
    arguments: Record<string, unknown>
  }>
  reasoning?: string
  [key: string]: unknown
}

/** 创建会话请求参数 */
export interface CreateConversationRequest {
  title?: string
  type?: 'chat' | 'comfort'
}

/** 更新会话请求参数 */
export interface UpdateConversationRequest {
  title: string
}

/** 发送消息请求参数 */
export interface SendMessageRequest {
  message: string
  conversationId?: string
  modelProvider?: string
  modelName?: string
  fileIds?: string[]
  knowledgeDocIds?: string[]
  comfortMode?: boolean
  reasoningEffort?: 'low' | 'medium' | 'high' | 'max'
  webSearchEnabled?: boolean
  deepThinkingEnabled?: boolean
}

/** 知识库文档信息 */
export interface KnowledgeDocument {
  id: string
  filename: string
  fileSize: number
  uploadedAt: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  chunkCount?: number
}

/** 上传知识库文档响应 */
export interface UploadKnowledgeResponse {
  documentId: string
  filename: string
  status: string
}
