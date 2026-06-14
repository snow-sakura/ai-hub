import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Conversation } from '@/shared/types/conversation'
import { getConversations, createConversation, renameConversation, deleteConversation, getMessages } from '@/shared/api/conversation'
import type { PaginatedMessages } from '@/shared/api/conversation'

export const useConversationStore = defineStore('conversation', () => {
  const conversations = ref<Conversation[]>([])
  const activeConversationId = ref<string | null>(null)
  const isLoading = ref(false)

  /** 消息分页状态 */
  const messagePage = ref(1)
  const messageTotal = ref(0)
  const PAGE_SIZE = 50

  /** 是否还有更多历史消息可加载 */
  const hasMoreMessages = ref(false)

  /** 加载会话列表 */
  async function fetchConversations(type?: 'chat' | 'comfort') {
    isLoading.value = true
    try {
      const res = await getConversations(type)
      // 后端返回 snake_case，前端用 camelCase
      conversations.value = (res.data || []).map((c: any) => ({
        id: c.id,
        title: c.title,
        type: c.type,
        createdAt: c.created_at || c.createdAt,
        updatedAt: c.updated_at || c.updatedAt,
      }))
    } catch (e) {
      console.error('获取会话列表失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  /** 创建新会话（映射后端字段） */
  async function create(title = '新会话', type: 'chat' | 'comfort' = 'chat') {
    try {
      const res = await createConversation({ title, type })
      const data = res.data
      const conv: Conversation = {
        id: data.id,
        title: data.title,
        type: data.type || type,
        createdAt: (data as any).created_at || data.createdAt,
        updatedAt: (data as any).updated_at || data.updatedAt,
      }
      conversations.value.unshift(conv)
      activeConversationId.value = conv.id
      const { useChatStore } = await import('@/modules/chat/stores/chat')
      const chatStore = useChatStore()
      chatStore.clearMessages()
      return conv
    } catch (e) {
      console.error('创建会话失败:', e)
    }
  }

  /** 切换会话 */
  async function selectConversation(id: string) {
    activeConversationId.value = id
    // 重置分页状态
    messagePage.value = 1
    const conv = conversations.value.find(c => c.id === id)
    // 哄哄类型会话不加载到 chatStore（防止混合）
    if (conv?.type === 'comfort') return
    const { useChatStore } = await import('@/modules/chat/stores/chat')
    const chatStore = useChatStore()
    // 清理非当前对话的流状态，释放内存
    const keepId = id
    for (const sid of Object.keys(chatStore.streamStates)) {
      if (sid !== keepId) chatStore.clearStreamState(sid)
    }
    chatStore.clearMessages()
    try {
      const res = await getMessages(id, 1, PAGE_SIZE)
      const data = res.data as unknown as PaginatedMessages
      // 后端按 created_at DESC 返回，反转后 oldest first 展示
      chatStore.loadMessages((data.items || []).reverse() as any)
      messageTotal.value = data.total || 0
      hasMoreMessages.value = data.items.length < data.total

      // 如果标题仍是默认的"新会话"，用首条用户消息自动生成
      if (conv && conv.title === '新会话') {
        const msgs = data.items || []
        const firstUserMsg = msgs.find((m: any) => m.role === 'user')
        if (firstUserMsg && firstUserMsg.content) {
          const text = firstUserMsg.content.trim()
          const title = text.length > 10 ? text.slice(0, 10) + '…' : text
          await rename(id, title)
        }
      }
    } catch (e) {
      console.error('获取消息失败:', e)
    }
  }

  /** 加载更早的历史消息（追加到对话顶部） */
  async function loadMoreMessages() {
    if (!activeConversationId.value || !hasMoreMessages.value) return
    const nextPage = messagePage.value + 1
    try {
      const res = await getMessages(activeConversationId.value, nextPage, PAGE_SIZE)
      const data = res.data as unknown as PaginatedMessages
      const { useChatStore } = await import('@/modules/chat/stores/chat')
      const chatStore = useChatStore()
      // 后端 DESC 返回，反转后 prepend（更早的消息在数组前）
      chatStore.prependMessages((data.items || []).reverse() as any)
      messagePage.value = nextPage
      messageTotal.value = data.total || 0
      hasMoreMessages.value = chatStore.messages.length < data.total
    } catch (e) {
      console.error('加载更多消息失败:', e)
    }
  }

  /** 重命名会话 */
  async function rename(id: string, title: string) {
    try {
      await renameConversation(id, { title })
      const conv = conversations.value.find(c => c.id === id)
      if (conv) {
        conv.title = title
        conv.updatedAt = new Date().toISOString()
      }
    } catch (e) {
      console.error('重命名失败:', e)
    }
  }

  /** 删除会话 */
  async function remove(id: string) {
    try {
      await deleteConversation(id)
      conversations.value = conversations.value.filter(c => c.id !== id)
      if (activeConversationId.value === id) {
        activeConversationId.value = conversations.value[0]?.id || null
        if (activeConversationId.value) {
          await selectConversation(activeConversationId.value)
        } else {
          const { useChatStore } = await import('@/modules/chat/stores/chat')
          const chatStore = useChatStore()
          chatStore.clearMessages()
        }
      }
    } catch (e) {
      console.error('删除会话失败:', e)
    }
  }

  return {
    conversations,
    activeConversationId,
    isLoading,
    messagePage,
    messageTotal,
    hasMoreMessages,
    fetchConversations,
    create,
    selectConversation,
    loadMoreMessages,
    rename,
    remove,
  }
}, {
  persist: {
    storage: localStorage,
    paths: ['activeConversationId'], // 只持久化当前选中的会话 ID
  },
})
