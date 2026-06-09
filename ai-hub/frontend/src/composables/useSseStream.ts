import { useChatStore } from '../stores/chat'

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

/** 处理 SSE 事件（按对话隔离） */
function handleEvent(convId: string, event: { type: string; data: Record<string, any> }) {
  const chatStore = useChatStore()

  switch (event.type) {
    case 'token':
      chatStore.appendStreamingContent(convId, event.data.content)
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
  ) {
    // 中止该对话的已有流
    const existing = controllers.get(conversationId)
    if (existing) existing.abort()

    const controller = new AbortController()
    controllers.set(conversationId, controller)

    const chatStore = useChatStore()
    chatStore.startStreaming(conversationId)

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
        }),
        signal: controller.signal,
      })

      if (!response.body) {
        chatStore.setStreamError(conversationId, '无法获取响应流')
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
          if (parsed) handleEvent(conversationId, parsed)
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        chatStore.setStreamError(conversationId, e.message || '网络错误')
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
