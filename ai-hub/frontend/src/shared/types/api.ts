/** 通用 API 响应类型 */
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

/** LLM 模型信息 */
export interface ModelInfo {
  provider: 'deepseek' | 'qwen' | 'zhipu' | 'openai' | 'ollama' | string
  model: string
  displayName: string
}

/** 工具信息 */
export interface ToolInfo {
  name: string
  displayName: string
  description: string
  icon: string
  category: 'search' | 'file' | 'web' | 'system' | 'other'
}

/** SSE 事件类型 */
export type SseEventType =
  | 'token'
  | 'reasoning_token'
  | 'reasoning_end'
  | 'tool_start'
  | 'tool_result'
  | 'thinking'
  | 'progress'
  | 'emotion'
  | 'forgiveness'
  | 'done'
  | 'error'

/** SSE 事件基础结构 */
export interface SseEvent<T = unknown> {
  type: SseEventType
  data?: T
  timestamp?: number
}

/** Token 事件数据 */
export interface TokenData {
  content: string
}

/** 推理 Token 事件数据 */
export interface ReasoningTokenData {
  content: string
}

/** 工具调用开始数据 */
export interface ToolStartData {
  toolCallId: string
  toolName: string
  arguments: Record<string, unknown>
}

/** 工具调用结果数据 */
export interface ToolResultData {
  toolCallId: string
  toolName: string
  result: unknown
  status: 'success' | 'error'
}

/** 思考步骤数据 */
export interface ThinkingData {
  step: string
  detail: string
}

/** 进度数据 */
export interface ProgressData {
  current: number
  total: number
  message: string
}

/** 情绪分析数据（哄哄模式） */
export interface EmotionData {
  emotion: string
  intensity: number
  description: string
}

/** 原谅值数据（哄哄模式） */
export interface ForgivenessData {
  value: number
  change: number
  reason: string
}

/** 完成事件数据 */
export interface DoneData {
  messageId: string
  conversationId: string
}

/** 错误事件数据 */
export interface ErrorData {
  message: string
  code?: number
}
