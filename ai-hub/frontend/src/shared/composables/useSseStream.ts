import { useChatStore } from '@/modules/chat/stores/chat'
import { useComfortStore } from '@/modules/comfort/stores/comfort'
import { useConversationStore } from '@/shared/stores/conversation'

/** 解析 SSE 事件块（兼容多行 data） */
function parseSseEvent(block: string): { type: string; data: Record<string, any> } | null {
  const lines = block.split('\n')
  let type = ''
  let dataStr = ''

  for (const line of lines) {
    if (line.startsWith('event: ')) {
      type = line.slice(7).trim()
    } else if (line.startsWith('data: ')) {
      // 多行 data = 拼接换行（SSE 规范）
      dataStr = dataStr ? dataStr + '\n' + line.slice(6) : line.slice(6)
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
    case 'done':
      chatStore.finalizeStreamingMessage(convId, event.data.message_id)
      break
    case 'error':
      chatStore.setStreamError(convId, event.data.message)
      break
  }
}

/** SSE 流式接收 Hook（支持多对话并行 + 断线重连） */

// 模块级单例：跨所有 useSseStream 调用共享，确保 abort() 可取消任何对话的流
const _controllers = new Map<string, AbortController>()

export function useSseStream() {
  const MAX_RETRIES = 3
  const RETRY_DELAY_BASE = 1000

  function getRetryDelay(retryCount: number): number {
    return Math.min(RETRY_DELAY_BASE * Math.pow(2, retryCount), 10000)
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
    // 预先获取 store 引用（Pinia store 是单例，只需获取一次）
    const chatStore = useChatStore()
    const comfortStore = useComfortStore()

    const existing = _controllers.get(conversationId)
    if (existing) existing.abort()

    // 哄哄对话由 comfortStore 管理，不在 convStore 中，跳过检查
    if (!comfortMode) {
      const convStore = useConversationStore()
      const convExists = convStore.conversations.some(c => c.id === conversationId)
      if (!convExists) {
        console.warn(`[SSE] 对话 ${conversationId} 已不存在`)
        return
      }
    }

    // startStreaming 只在首次调用时执行，不在重试循环内重复
    if (comfortMode) {
      comfortStore.startStreaming()
    } else {
      chatStore.startStreaming(conversationId)
    }

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      const controller = new AbortController()
      _controllers.set(conversationId, controller)

      let tokenBuffer = ''
      let rafId: number | null = null

      function flushTokens() {
        if (!tokenBuffer) { rafId = null; return }
        const content = tokenBuffer
        tokenBuffer = ''
        if (comfortMode) {
          comfortStore.appendStreamingContent(content)
        } else {
          chatStore.appendStreamingContent(conversationId, content)
        }
        rafId = null
      }

      // 重试时恢复 isStreaming，确保流式光标正常显示
      if (attempt > 0) {
        if (comfortMode) {
          comfortStore.startStreaming()
        } else {
          chatStore.startStreaming(conversationId)
        }
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
        _controllers.delete(conversationId)
        return
      } catch (e: any) {
        _controllers.delete(conversationId)

        // 取消 RAF 防止写入已清理的状态
        if (rafId !== null) {
          cancelAnimationFrame(rafId)
          rafId = null
          tokenBuffer = ''
        }

        if (e.name === 'AbortError') {
          return
        }

        if (attempt >= MAX_RETRIES) {
          console.error('[SSE] 重试失败')
          const errMsg = '网络连接失败，请稍后重试'
          if (comfortMode) {
            comfortStore.setStreamError(errMsg)
          } else {
            chatStore.setStreamError(conversationId, errMsg)
          }
          return
        }

        const delay = getRetryDelay(attempt)
        console.warn(`[SSE] 连接中断，${delay}ms 后第 ${attempt + 1} 次重试...`, e.message)

        const errorMsg = `连接中断，正在重试 (${attempt + 1}/${MAX_RETRIES})...`
        if (comfortMode) {
          comfortStore.setStreamError(errorMsg)
        } else {
          chatStore.setStreamError(conversationId, errorMsg)
        }

        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }

  /** 中止指定对话的流式请求 */
  function abort(conversationId: string) {
    _controllers.get(conversationId)?.abort()
    _controllers.delete(conversationId)
  }

  /** 清理所有进行中的流式请求（组件卸载时调用，防止内存泄漏） */
  function cleanupAll() {
    for (const [id, controller] of _controllers) {
      controller.abort()
    }
    _controllers.clear()
  }

  return { sendChat, abort, cleanupAll }
}
