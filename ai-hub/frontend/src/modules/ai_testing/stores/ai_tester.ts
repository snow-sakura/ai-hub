import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AITesterSession, AITesterSessionCreate, AITesterMessage } from '@/modules/ai_testing/types/ai_tester'
import * as aiTesterApi from '@/modules/ai_testing/api/ai_tester'

export const useAITesterStore = defineStore('testing-ai-tester', () => {
  const sessions = ref<AITesterSession[]>([])
  const currentSessionId = ref<string | null>(null)
  const messages = ref<AITesterMessage[]>([])
  const totalMessages = ref(0)
  const loadedCount = ref(0)
  const isLoading = ref(false)
  const isSending = ref(false)
  const PAGE_SIZE = 50

  async function fetchSessions() {
    try {
      const res = await aiTesterApi.listSessions()
      if (res.data) sessions.value = res.data
    } catch (e) {
      console.error('获取会话列表失败:', e)
    }
  }

  async function createSession(data: AITesterSessionCreate) {
    const res = await aiTesterApi.createSession(data)
    if (res.data) {
      sessions.value.unshift(res.data)
      currentSessionId.value = res.data.id
      messages.value = []
      totalMessages.value = 0
      loadedCount.value = 0
    }
    return res.data
  }

  async function deleteSession(sessionId: string) {
    const res = await aiTesterApi.deleteSession(sessionId)
    if (res.data) {
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      if (currentSessionId.value === sessionId) {
        currentSessionId.value = null
        messages.value = []
        totalMessages.value = 0
        loadedCount.value = 0
      }
    }
    return res.data
  }

  async function updateSession(sessionId: string, data: { name: string }) {
    const res = await aiTesterApi.updateSession(sessionId, data)
    if (res.data) {
      const session = sessions.value.find(s => s.id === sessionId)
      if (session) session.name = data.name
    }
    return res.data
  }

  async function batchDeleteSessions(ids: string[]) {
    const res = await aiTesterApi.batchDeleteSessions(ids)
    if (res.data) {
      sessions.value = sessions.value.filter(s => !ids.includes(s.id))
      if (currentSessionId.value && ids.includes(currentSessionId.value)) {
        currentSessionId.value = null
        messages.value = []
        totalMessages.value = 0
        loadedCount.value = 0
      }
    }
    return res.data
  }

  /** 切换会话 - 先保持旧消息，加载完成再切换（避免空闪） */
  async function selectSession(sessionId: string) {
    currentSessionId.value = sessionId
    isLoading.value = true
    try {
      const res = await aiTesterApi.getMessages(sessionId, 0, PAGE_SIZE)
      if (res.data) {
        messages.value = res.data.messages
        totalMessages.value = res.data.total
        loadedCount.value = res.data.messages.length
      }
    } catch (e) {
      console.error('获取消息列表失败:', e)
      messages.value = []
    } finally {
      isLoading.value = false
    }
  }

  /** 加载更早的消息（前置追加） */
  async function loadMoreMessages() {
    if (!currentSessionId.value || isLoading.value || loadedCount.value >= totalMessages.value) return
    isLoading.value = true
    try {
      const res = await aiTesterApi.getMessages(currentSessionId.value, loadedCount.value, PAGE_SIZE)
      if (res.data) {
        messages.value = [...res.data.messages, ...messages.value]
        loadedCount.value += res.data.messages.length
      }
    } catch (e) {
      console.error('加载更多消息失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  const hasMoreMessages = () => loadedCount.value < totalMessages.value

  async function sendMessage(content: string, model?: string) {
    if (!currentSessionId.value) return
    isSending.value = true
    try {
      const res = await aiTesterApi.sendMessage(currentSessionId.value, { content, model })
      if (res.data) {
        // 发送后重新加载最新消息
        await selectSession(currentSessionId.value!)
        await fetchSessions()
      }
    } catch (e) {
      console.error('发送消息失败:', e)
    } finally {
      isSending.value = false
    }
  }

  return {
    sessions, currentSessionId, messages, totalMessages, loadedCount,
    isLoading, isSending, hasMoreMessages,
    fetchSessions, createSession, deleteSession, updateSession,
    batchDeleteSessions, selectSession, loadMoreMessages, sendMessage,
  }
})
