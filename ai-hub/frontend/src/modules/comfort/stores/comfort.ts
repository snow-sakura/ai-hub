import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  ComfortScene,
  ComfortCharacter,
  ComfortMemory,
  EmotionData,
  ForgivenessData,
  ComfortMetadata,
} from '@/modules/comfort/types/comfort'
import type { ChatMessage } from '@/modules/chat/types/chat'
import * as comfortApi from '@/modules/comfort/api/comfort'

export const useComfortStore = defineStore('comfort', () => {
  // ─── 场景和角色 ─────────────────────────────────
  const scenes = ref<ComfortScene[]>([])
  const characters = ref<ComfortCharacter[]>([])
  const selectedScene = ref<ComfortScene | null>(null)
  const selectedCharacter = ref<ComfortCharacter | null>(null)
  const difficulty = ref(3)

  // ─── 会话状态 ─────────────────────────────────
  const conversationId = ref<string | null>(null)
  const metadata = ref<ComfortMetadata | null>(null)
  const memories = ref<ComfortMemory[]>([])

  // ─── 消息队列（独立于 chatStore）───────────────
  const messages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const streamingContent = ref('')
  const streamError = ref<string | null>(null)

  // ─── 实时情绪/原谅值 ───────────────────────────
  const currentEmotion = ref<EmotionData | null>(null)
  const currentForgiveness = ref<ForgivenessData | null>(null)
  const emotionHistory = ref<EmotionData[]>([])

  /** 当前原谅值 */
  const forgivenessValue = computed(() => {
    if (currentForgiveness.value) return currentForgiveness.value.current
    if (metadata.value) return metadata.value.forgiveness
    return 50
  })

  /** 加载场景列表 */
  async function fetchScenes() {
    try {
      const res = await comfortApi.getScenes()
      scenes.value = res.data || []
    } catch (e) {
      console.error('获取场景列表失败:', e)
    }
  }

  /** 按场景加载角色 */
  async function fetchCharacters(sceneId?: string) {
    try {
      const res = await comfortApi.getCharacters(sceneId)
      characters.value = res.data || []
    } catch (e) {
      console.error('获取角色列表失败:', e)
    }
  }

  /** 选择场景 */
  function selectScene(scene: ComfortScene) {
    selectedScene.value = scene
    difficulty.value = scene.difficulty_default
    selectedCharacter.value = null
    fetchCharacters(scene.id)
  }

  /** 选择角色 */
  function selectCharacter(character: ComfortCharacter) {
    selectedCharacter.value = character
  }

  /** 创建哄哄会话 */
  async function startSession(): Promise<string | null> {
    if (!selectedScene.value || !selectedCharacter.value) return null
    try {
      const res = await comfortApi.createComfortSession({
        scene_id: selectedScene.value.id,
        character_id: selectedCharacter.value.id,
        difficulty: difficulty.value,
        title: `${selectedScene.value.icon} ${selectedScene.value.name} - ${selectedCharacter.value.name}`,
      })
      const data = res.data
      conversationId.value = data.conversation.id
      metadata.value = data.metadata
      return data.conversation.id
    } catch (e) {
      console.error('创建哄哄会话失败:', e)
      return null
    }
  }

  /** 加载会话信息 */
  async function loadSessionInfo(convId: string) {
    try {
      const res = await comfortApi.getComfortSessionInfo(convId)
      const data = res.data
      if (data.metadata && data.metadata.scene_id) {
        metadata.value = data.metadata
        conversationId.value = convId
        if (data.scene) {
          selectedScene.value = data.scene
        }
        if (data.character) {
          selectedCharacter.value = data.character
        }
      }
    } catch (e) {
      console.error('加载哄哄会话信息失败:', e)
    }
  }

  /** 加载记忆 */
  async function fetchMemories(convId: string) {
    try {
      const res = await comfortApi.getMemories(convId)
      memories.value = res.data || []
    } catch (e) {
      console.error('获取记忆列表失败:', e)
    }
  }

  /** 处理情绪事件 */
  function handleEmotionEvent(data: EmotionData) {
    currentEmotion.value = data
    emotionHistory.value.push(data)
    // 保留最近 50 条，避免无限增长
    if (emotionHistory.value.length > 50) {
      emotionHistory.value = emotionHistory.value.slice(-50)
    }
  }

  /** 处理原谅值事件 */
  function handleForgivenessEvent(data: ForgivenessData) {
    currentForgiveness.value = data
    if (metadata.value) {
      metadata.value.forgiveness = data.current
      metadata.value.turn_count += 1
    }
  }

  /** 重置状态 */
  function reset() {
    selectedScene.value = null
    selectedCharacter.value = null
    conversationId.value = null
    metadata.value = null
    memories.value = []
    currentEmotion.value = null
    currentForgiveness.value = null
    emotionHistory.value = []
    difficulty.value = 3
    messages.value = []
    isStreaming.value = false
    streamingContent.value = ''
    streamError.value = null
  }

  // ─── 消息管理 ─────────────────────────────────
  /** 添加用户消息 */
  function addUserMessage(content: string) {
    messages.value.push({
      id: `comfort_user_${Date.now()}`,
      role: 'user',
      content,
      timestamp: Date.now(),
    })
  }

  /** 开始流式响应 */
  function startStreaming() {
    isStreaming.value = true
    streamingContent.value = ''
    streamError.value = null
  }

  /** 追加流式内容 */
  function appendStreamingContent(token: string) {
    streamingContent.value += token
  }

  /** 完成流式消息，推入消息列表 */
  function finalizeStreamingMessage(messageId?: string) {
    if (streamingContent.value) {
      messages.value.push({
        id: messageId || `comfort_assistant_${Date.now()}`,
        role: 'assistant',
        content: streamingContent.value,
        timestamp: Date.now(),
        isStreaming: false,
      })
    }
    isStreaming.value = false
    streamingContent.value = ''
    streamError.value = null
  }

  /** 设置流错误 */
  function setStreamError(message: string) {
    streamError.value = message
    isStreaming.value = false
  }

  /** 从历史数据加载消息 */
  function loadMessages(data: Array<{ role: string; content: string; created_at: string }>) {
    messages.value = data.map((msg, i) => ({
      id: `comfort_hist_${i}_${Date.now()}`,
      role: msg.role as ChatMessage['role'],
      content: msg.content,
      timestamp: new Date(msg.created_at).getTime(),
    }))
  }

  /** 清空消息 */
  function clearMessages() {
    messages.value = []
  }

  return {
    scenes,
    characters,
    selectedScene,
    selectedCharacter,
    difficulty,
    conversationId,
    metadata,
    memories,
    currentEmotion,
    currentForgiveness,
    emotionHistory,
    forgivenessValue,
    // 消息队列
    messages,
    isStreaming,
    streamingContent,
    streamError,
    fetchScenes,
    fetchCharacters,
    selectScene,
    selectCharacter,
    startSession,
    loadSessionInfo,
    fetchMemories,
    handleEmotionEvent,
    handleForgivenessEvent,
    reset,
    // 消息管理
    addUserMessage,
    startStreaming,
    appendStreamingContent,
    finalizeStreamingMessage,
    setStreamError,
    loadMessages,
    clearMessages,
  }
})
