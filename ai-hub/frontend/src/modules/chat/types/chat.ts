/** 上传中的附件（含 File 对象） */
export interface UploadAttachment {
  name: string
  type: 'file' | 'image'
  file: File
}

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
  reasoning?: string                  // DeepSeek 推理过程内容
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
  type: 'token' | 'reasoning_token' | 'reasoning_end' | 'tool_start' | 'tool_result' | 'thinking' | 'progress' | 'done' | 'error' | 'emotion' | 'forgiveness'
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
  reasoning: string                   // DeepSeek 推理内容（实时流式）
  reasoningComplete: boolean          // 推理是否已完成
  currentThinkingSteps: ThinkingStep[]
  currentToolCalls: ToolCallStatus[]
  progress: ProgressInfo | null
  error: string | null
  startTimestamp?: number  // 流开始时间戳，用于计算耗时
}
