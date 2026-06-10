import { useChatStore } from '@/modules/chat/stores/chat'
import { useComfortStore } from '@/modules/comfort/stores/comfort'

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

/** SSE 流式接收 Hook（支持多对话并行） */
export function useSseStream() {
  const controllers = new Map<string, AbortController>()

  /** 发送聊天消息 */
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
    // 中止该对话的已有流
    const existing = controllers.get(conversationId)
    if (existing) existing.abort()

    const controller = new AbortController()
    controllers.set(conversationId, controller)

    if (comfortMode) {
      useComfortStore().startStreaming()
    } else {
      useChatStore().startStreaming(conversationId)
    }

    // Token RAF 批处理：积攒一帧内的 token 批量提交，避免每 token 触发渲染
    let tokenBuffer = ''
    let rafId: number | null = null

    function flushTokens() {
      if (!tokenBuffer) { rafId = null; return }
      const content = tokenBuffer
      tokenBuffer = ''
      if (comfortMode) {
        useComfortStore().appendStreamingContent(content)
      } else {
        useChatStore().appendStreamingContent(conversationId, content)
      }
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

      if (!response.body) {
        if (comfortMode) {
          useComfortStore().setStreamError('无法获取响应流')
        } else {
          useChatStore().setStreamError(conversationId, '无法获取响应流')
        }
        return
      }

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

          // token 事件走 RAF 批处理缓冲区
          if (parsed.type === 'token') {
            tokenBuffer += parsed.data.content
            if (!rafId) rafId = requestAnimationFrame(flushTokens)
            continue
          }

          // 非 token 事件：先刷空 token 缓冲区再处理
          if (rafId !== null) {
            cancelAnimationFrame(rafId)
            flushTokens()
          }
          handleEvent(conversationId, parsed, comfortMode)
        }
      }

      // 流结束后刷空残留 token
      if (rafId !== null) flushTokens()
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        if (comfortMode) {
          useComfortStore().setStreamError(e.message || '网络错误')
        } else {
          useChatStore().setStreamError(conversationId, e.message || '网络错误')
        }
      }
    } finally {
      controllers.delete(conversationId)
    }
  }

  /** 中止指定对话的流式请求 */
  function abort(conversationId: string) {
    controllers.get(conversationId)?.abort()
    controllers.delete(conversationId)
  }

  return { sendChat, abort }
}
