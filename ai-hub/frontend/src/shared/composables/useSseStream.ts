import { useChatStore } from '@/modules/chat/stores/chat'
import { useComfortStore } from '@/modules/comfort/stores/comfort'
import { useConversationStore } from '@/shared/stores/conversation'

/** 解析 SSE 事件块 */
function parseSseEvent(block: string): { type: string; data: Record<string, any> } | null {
  const lines = block.split('\n')
  let type = ''
  let dataStr = ''

  for (const line of lines) {
    if (line.startsWith('event: ')) {
      type = line.slice(7).trim()
    } else if (line.startsWith('data: ')) {
      dataStr = line.slice(6)
    }
  }

  if (!type || !dataStr) return null

  try {
    return { type, data: JSON.parse(dataStr) }
  } catch {
    return null
  }
}

/** 处理 SSE 事件（按对话隔离 + 按 comfortMode 分流） */
function handleEvent(convId: string, event: { type: string; data: Record<string, any> }, comfortMode = false) {
  const chatStore = useChatStore()
  const comfortStore = useComfortStore()

  if (comfortMode) {
    // 哄哄模式：路由到 comfortStore
    switch (event.type) {
      case 'token':
        comfortStore.appendStreamingContent(event.data.content)
        break
      case 'done':
        comfortStore.finalizeStreamingMessage(event.data.message_id)
        break
      case 'error':
        comfortStore.setStreamError(event.data.message)
        break
      case 'emotion':
        comfortStore.handleEmotionEvent(event.data as any)
        break
      case 'forgiveness':
        comfortStore.handleForgivenessEvent(event.data as any)
        break
      // tool_start / tool_result / thinking / progress → 哄哄无需关心
    }
    return
  }

  // 普通聊天模式：路由到 chatStore
  switch (event.type) {
    case 'token':
      chatStore.appendStreamingContent(convId, event.data.content)
      break
    case 'reasoning_token':
      chatStore.appendReasoning(convId, event.data.content)
      break
    case 'reasoning_end':
      chatStore.setReasoningComplete(convId)
      break
    case 'tool_start':
      chatStore.setToolCallStatus(convId, event.data.tool_call_id, {
        toolName: event.data.tool_name,
        toolCallId: event.data.tool_call_id,
        display: event.data.display,
        status: 'running',
      })
      chatStore.addThinkingStep(convId, {
        step: 'action',
        content: event.data.display,
        timestamp: Date.now(),
      })
      break
    case 'tool_result':
      chatStore.setToolCallStatus(convId, event.data.tool_call_id, {
        toolName: event.data.tool_name,
        toolCallId: event.data.tool_call_id,
        display: event.data.tool_name,
        status: 'done',
        summary: event.data.summary,
        result: event.data.result,
      })
      break
    case 'thinking':
      chatStore.addThinkingStep(convId, {
        step: event.data.step,
        content: event.data.content,
        timestamp: Date.now(),
      })
      break
    case 'progress':
      chatStore.setProgress(convId, event.data as any)
      break
    case 'emotion':
      useComfortStore().handleEmotionEvent(event.data as any)
      break
    case 'forgiveness':
      useComfortStore().handleForgivenessEvent(event.data as any)
      break
    case 'done':
      chatStore.finalizeStreamingMessage(convId, event.data.message_id)
      break
    case 'error':
      chatStore.setStreamError(convId, event.data.message)
      break
  }
}

/** SSE 流式接收 Hook（支持多对话并行 + 断线重连） */
export function useSseStream() {
  const controllers = new Map<string, AbortController>()
  const MAX_RETRIES = 3
  const RETRY_DELAY_BASE = 1000

  function getRetryDelay(retryCount: number): number {
    return Math.min(RETRY_DELAY_BASE * Math.pow(2, retryCount), 10000)
  }

  /** 根据 comfortMode 获取对应的 Store 引用 */
  function resolveStore(convId: string, comfortMode: boolean) {
    return comfortMode
      ? { store: useComfortStore(), id: convId }
      : { store: useChatStore() as any, id: convId }
  }

  /** 发送聊天消息（支持自动重连，循环重试避免栈增长） */
  async function sendChat(
    message: string,
    conversationId: string,
    modelProvider: string,
    modelName: string,
    fileIds?: string[],
    knowledgeDocIds?: string[],
    comfortMode: boolean = false,
    reasoningEffort: string = 'high',
    webSearchEnabled: boolean = false,
    deepThinkingEnabled: boolean = true,
  ) {
    const existing = controllers.get(conversationId)
    if (existing) existing.abort()

    const convStore = useConversationStore()
    const convExists = convStore.conversations.some(c => c.id === conversationId)
    if (!convExists) {
      console.warn(`[SSE] 对话 ${conversationId} 已不存在`)
      return
    }

    // startStreaming 只在首次调用时执行，不在重试循环内重复
    if (comfortMode) {
      useComfortStore().startStreaming()
    } else {
      useChatStore().startStreaming(conversationId)
    }

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      const controller = new AbortController()
      controllers.set(conversationId, controller)

      let tokenBuffer = ''
      let rafId: number | null = null

      function flushTokens() {
        if (!tokenBuffer) { rafId = null; return }
        const content = tokenBuffer
        tokenBuffer = ''
        const s = resolveStore(conversationId, comfortMode)
        s.store.appendStreamingContent(s.id, content)
        rafId = null
      }

      try {
        const response = await fetch('/api/v1/chat/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message,
            conversation_id: conversationId,
            model_provider: modelProvider,
            model_name: modelName,
            attachments: fileIds || [],
            knowledge_doc_ids: knowledgeDocIds || [],
            comfort_mode: comfortMode,
            reasoning_effort: reasoningEffort,
            web_search_enabled: webSearchEnabled,
            deep_thinking_enabled: deepThinkingEnabled,
          }),
          signal: controller.signal,
        })

        if (!response.body) throw new Error('无法获取响应流')

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const events = buffer.split('\n\n')
          buffer = events.pop() || ''

          for (const eventBlock of events) {
            if (!eventBlock.trim()) continue
            const parsed = parseSseEvent(eventBlock)
            if (!parsed) continue

            if (parsed.type === 'token') {
              tokenBuffer += parsed.data.content
              if (!rafId) rafId = requestAnimationFrame(flushTokens)
              continue
            }

            if (rafId !== null) {
              cancelAnimationFrame(rafId)
              flushTokens()
            }
            handleEvent(conversationId, parsed, comfortMode)
          }
        }

        if (rafId !== null) flushTokens()
        controllers.delete(conversationId)
        return
      } catch (e: any) {
        controllers.delete(conversationId)

        if (e.name === 'AbortError') {
          return
        }

        if (attempt >= MAX_RETRIES) {
          console.error('[SSE] 重试失败')
          const errMsg = '网络连接失败，请稍后重试'
          if (comfortMode) {
            useComfortStore().setStreamError(errMsg)
          } else {
            useChatStore().setStreamError(conversationId, errMsg)
          }
          return
        }

        const delay = getRetryDelay(attempt)
        console.warn(`[SSE] 连接中断，${delay}ms 后第 ${attempt + 1} 次重试...`, e.message)

        const errorMsg = `连接中断，正在重试 (${attempt + 1}/${MAX_RETRIES})...`
        if (comfortMode) {
          useComfortStore().setStreamError(errorMsg)
        } else {
          useChatStore().setStreamError(conversationId, errorMsg)
        }

        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }

  /** 中止指定对话的流式请求 */
  function abort(conversationId: string) {
    controllers.get(conversationId)?.abort()
    controllers.delete(conversationId)
  }

  return { sendChat, abort }
}
