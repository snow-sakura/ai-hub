import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatMessage, ToolCallStatus, ThinkingStep, ProgressInfo, MessageAttachment, StreamState } from '@/modules/chat/types/chat'
import { useConversationStore } from '@/shared/stores/conversation'

/** 创建默认流状态 */
function createStreamState(): StreamState {
  return {
    isStreaming: false,
    streamingContent: '',
    currentThinkingSteps: [],
    currentToolCalls: [],
    progress: null,
    error: null,
  }
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const streamStates = ref<Record<string, StreamState>>({})

  /** 当前对话的流状态 */
  const activeStreamState = computed<StreamState>(() => {
    const convStore = useConversationStore()
    const convId = convStore.activeConversationId
    if (convId && streamStates.value[convId]) {
      return streamStates.value[convId]
    }
    return createStreamState()
  })

  /** 获取指定对话的流状态（不存在则创建） */
  function getOrCreate(convId: string): StreamState {
    if (!streamStates.value[convId]) {
      streamStates.value[convId] = createStreamState()
    }
    return streamStates.value[convId]
  }

  /** 添加用户消息 */
  function addUserMessage(content: string, files?: MessageAttachment[]) {
    messages.value.push({
      id: `user_${Date.now()}`,
      role: 'user',
      content,
      timestamp: Date.now(),
      attachments: files || [],
    })
  }

  /** 开始流式响应（指定对话） */
  function startStreaming(convId: string) {
    const state = getOrCreate(convId)
    state.isStreaming = true
    state.streamingContent = ''
    state.currentThinkingSteps = []
    state.currentToolCalls = []
    state.progress = null
    state.error = null
    state.startTimestamp = Date.now()
  }

  /** 追加流式内容（指定对话） */
  function appendStreamingContent(convId: string, token: string) {
    const state = streamStates.value[convId]
    if (state) state.streamingContent += token
  }

  /** 添加思考步骤（指定对话） */
  function addThinkingStep(convId: string, step: ThinkingStep) {
    const state = streamStates.value[convId]
    if (state) state.currentThinkingSteps.push(step)
  }

  /** 设置工具调用状态（指定对话） */
  function setToolCallStatus(convId: string, toolCallId: string, status: ToolCallStatus) {
    const state = streamStates.value[convId]
    if (!state) return
    const existing = state.currentToolCalls.find(tc => tc.toolCallId === toolCallId)
    if (existing) {
      Object.assign(existing, status)
    } else {
      state.currentToolCalls.push(status)
    }
  }

  /** 设置进度（指定对话） */
  function setProgress(convId: string, p: ProgressInfo) {
    const state = streamStates.value[convId]
    if (state) state.progress = p
  }

  /** 完成流式响应（指定对话） */
  function finalizeStreamingMessage(convId: string, messageId: string) {
    const state = streamStates.value[convId]
    if (!state) return

    if (state.streamingContent || state.currentThinkingSteps.length > 0) {
      messages.value.push({
        id: messageId || `assistant_${Date.now()}`,
        role: 'assistant',
        content: state.streamingContent,
        timestamp: Date.now(),
        thinkingSteps: [...state.currentThinkingSteps],
        toolCalls: [...state.currentToolCalls],
        isStreaming: false,
      })
    }
    state.isStreaming = false
    state.streamingContent = ''
    state.currentThinkingSteps = []
    state.currentToolCalls = []
    state.progress = null
    state.error = null
  }

  /** 设置错误（指定对话） */
  function setStreamError(convId: string, message: string) {
    const state = streamStates.value[convId]
    if (!state) return
    state.error = message
    state.isStreaming = false
  }

  /** 从历史数据加载消息 */
  function loadMessages(data: Array<{ role: string; content: string; metadata: string; created_at: string }>) {
    messages.value = data.map((msg, i) => ({
      id: `hist_${i}_${Date.now()}`,
      role: msg.role as ChatMessage['role'],
      content: msg.content,
      timestamp: new Date(msg.created_at).getTime(),
      metadata: msg.metadata ? JSON.parse(msg.metadata) : {},
    }))
  }

  /** 清空消息 */
  function clearMessages() {
    messages.value = []
  }

  /** 清理指定对话的流状态 */
  function clearStreamState(convId: string) {
    delete streamStates.value[convId]
  }

  return {
    messages,
    streamStates,
    activeStreamState,
    addUserMessage,
    startStreaming,
    appendStreamingContent,
    addThinkingStep,
    setToolCallStatus,
    setProgress,
    finalizeStreamingMessage,
    setStreamError,
    loadMessages,
    clearMessages,
    clearStreamState,
  }
})
