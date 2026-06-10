/** 附件信息 */
export interface MessageAttachment {
  name: string
  type: 'file' | 'image'
}

/** 消息类型定义 */
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'tool' | 'system'
  content: string
  timestamp: number
  thinkingSteps?: ThinkingStep[]
  toolCalls?: ToolCallStatus[]
  isStreaming?: boolean
  metadata?: Record<string, any>
  attachments?: MessageAttachment[]
}

export interface ThinkingStep {
  step: 'thought' | 'action' | 'observation'
  content: string
  timestamp: number
}

export interface ToolCallStatus {
  toolName: string
  toolCallId: string
  display: string
  status: 'running' | 'done' | 'error'
  summary?: string
  result?: Record<string, any>
  input?: Record<string, any>  // 工具入参
}

export interface ChatEvent {
  type: 'token' | 'tool_start' | 'tool_result' | 'thinking' | 'progress' | 'done' | 'error' | 'emotion' | 'forgiveness'
  data: Record<string, any>
}

export interface ProgressInfo {
  current: number
  total: number
  message: string
}

/** 单次对话的流式状态 */
export interface StreamState {
  isStreaming: boolean
  streamingContent: string
  currentThinkingSteps: ThinkingStep[]
  currentToolCalls: ToolCallStatus[]
  progress: ProgressInfo | null
  error: string | null
  startTimestamp?: number  // 流开始时间戳，用于计算耗时
}
