<template>
  <div class="page-wrap">
    <div class="tester-layout">
      <!-- 左栏：历史会话 -->
      <n-card class="sidebar-card" title="会话历史" size="small">
        <template #header-extra>
          <n-button text size="tiny" type="primary" @click="handleClearHistory" style="font-size: 12px;">
            清空
          </n-button>
        </template>
        <n-button block type="primary" size="small" @click="handleNewChat" class="new-chat-btn">
          + 新建对话
        </n-button>
        <div class="session-list">
          <div
            v-for="session in store.sessions"
            :key="session.id"
            :class="['session-item', { active: store.currentSessionId === session.id }]"
            @click="store.selectSession(session.id)"
          >
            <div class="session-info">
              <span class="session-name">{{ session.name }}</span>
              <span class="session-time">{{ formatTime(session.created_at) }}</span>
            </div>
            <div class="session-actions" @click.stop>
              <n-button text size="tiny" @click="handleRename(session)">
                <template #icon><span style="font-size: 13px;">✏️</span></template>
              </n-button>
              <n-button text size="tiny" type="error" @click="handleDeleteSession(session)">
                <template #icon><span style="font-size: 13px;">🗑️</span></template>
              </n-button>
            </div>
          </div>
          <div v-if="store.sessions.length === 0" class="session-empty">
            暂无历史会话
          </div>
        </div>
      </n-card>

      <!-- 右栏：聊天区 -->
      <div class="chat-area">
        <!-- 顶栏 -->
        <n-card class="chat-header" size="small" :bordered="false">
          <div class="chat-header-inner">
            <span class="chat-title">{{ currentSession?.name || 'AI 评测师' }}</span>
            <n-select
              v-model:value="selectedModel"
              :options="modelOptions"
              size="small"
              style="width: 180px;"
              placeholder="选择模型"
            />
          </div>
        </n-card>

        <!-- 消息列表 -->
        <div ref="messageContainerRef" class="message-container">
          <!-- 加载更多 -->
          <div v-if="store.hasMoreMessages()" class="load-more-bar">
            <n-button size="tiny" quaternary :loading="store.isLoading" @click="store.loadMoreMessages()">
              加载更多消息
            </n-button>
          </div>
          <div v-if="store.isLoading && store.messages.length === 0" class="message-empty">
            <n-spin size="small" />
            <p>加载中...</p>
          </div>
          <div
            v-for="(msg, idx) in store.messages"
            :key="idx"
            :class="['message-row', msg.role === 'user' ? 'message-row-user' : 'message-row-ai']"
          >
            <div v-if="msg.role === 'assistant'" class="avatar-col">
              <div class="avatar ai-avatar">AI</div>
            </div>
            <div :class="['message-bubble', msg.role === 'user' ? 'bubble-user' : 'bubble-ai']">
              <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
              <div class="message-time">{{ formatTime(msg.created_at) }}</div>
              <!-- AI 消息操作按钮 -->
              <div v-if="msg.role === 'assistant' && msg.id" class="message-actions">
                <n-button text size="tiny" @click="handleCopy(msg.content)" title="复制">
                  <template #icon><span style="font-size: 14px;">📋</span></template>
                </n-button>
                <n-button
                  text size="tiny"
                  :type="msg.rating === 'up' ? 'primary' : 'default'"
                  @click="handleRate(msg, 'up')"
                  title="有用"
                >
                  <template #icon><span style="font-size: 14px;">👍</span></template>
                </n-button>
                <n-button
                  text size="tiny"
                  :type="msg.rating === 'down' ? 'error' : 'default'"
                  @click="handleRate(msg, 'down')"
                  title="无用"
                >
                  <template #icon><span style="font-size: 14px;">👎</span></template>
                </n-button>
              </div>
            </div>
            <div v-if="msg.role === 'user'" class="avatar-col">
              <div class="avatar user-avatar">我</div>
            </div>
          </div>
          <!-- 流式输出消息 -->
          <div v-if="isStreaming" class="message-row message-row-ai">
            <div class="avatar-col">
              <div class="avatar ai-avatar">AI</div>
            </div>
            <div class="message-bubble bubble-ai">
              <div class="message-text" v-html="renderMarkdown(streamContent || '思考中...')"></div>
              <div class="streaming-cursor" v-if="streamContent">▊</div>
            </div>
          </div>
          <div v-if="store.messages.length === 0 && !store.isSending && !isStreaming" class="message-empty">
            <div class="empty-icon">🧪</div>
            <p class="empty-title">开始一个新的测试对话吧</p>
            <div class="example-questions">
              <div class="example-item" @click="fillExample('请帮我评审以下测试用例：\n用例1：登录功能验证\n1. 输入正确用户名密码\n2. 点击登录按钮\n预期：成功跳转到首页')">
                评审测试用例
              </div>
              <div class="example-item" @click="fillExample('针对用户注册功能，帮我设计一套完整的测试用例，包括正常流程和异常场景。')">
                设计测试用例
              </div>
              <div class="example-item" @click="fillExample('API 接口测试中，如何验证接口的幂等性？请给出具体的测试方法。')">
                接口测试咨询
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <n-card class="input-area" size="small" :bordered="false">
          <div class="input-row">
            <n-input
              v-model:value="inputText"
              type="textarea"
              :rows="2"
              placeholder="输入您的问题..."
              :autosize="{ minRows: 2, maxRows: 6 }"
              @keydown.enter.prevent="handleSend"
            />
            <n-button
              circle
              type="primary"
              :disabled="!inputText.trim() || store.isSending"
              :loading="store.isSending"
              @click="handleSend"
            >
              <template #icon><span style="font-size: 16px;">➤</span></template>
            </n-button>
          </div>
        </n-card>
      </div>
    </div>

    <!-- 重命名弹窗 -->
    <n-modal v-model:show="showRenameModal" preset="dialog" title="重命名会话">
      <n-input v-model:value="renameText" placeholder="输入新名称" />
      <template #action>
        <n-button @click="showRenameModal = false">取消</n-button>
        <n-button type="primary" @click="handleRenameConfirm">确认</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { useAITesterStore } from '@/modules/ai_testing/stores/ai_tester'
import { useGenerationStore } from '@/modules/ai_testing/stores/generation'
import { useMarkdownRenderer } from '@/shared/composables/useMarkdownRenderer'
import { rateMessage } from '@/modules/ai_testing/api/ai_tester'
import type { AITesterSession } from '@/modules/ai_testing/types/ai_tester'

const message = useMessage()
const store = useAITesterStore()
const genStore = useGenerationStore()

const inputText = ref('')
const selectedModel = ref('deepseek:deepseek-v4-flash')
const messageContainerRef = ref<HTMLElement | null>(null)
const showRenameModal = ref(false)
const renameText = ref('')
const renamingSessionId = ref<string | null>(null)
const isStreaming = ref(false)
const streamContent = ref('')

/** 模型选项（按 provider 分组，从后端动态加载） */
const modelOptions = computed(() => {
  const defaults = genStore.configDefaults
  if (!defaults?.models || defaults.models.length === 0) {
    // 降级：使用默认选项
    return [{ label: 'DeepSeek V4 Flash', value: 'deepseek:deepseek-v4-flash' }]
  }
  const groups: Record<string, Array<{ label: string; value: string }>> = {}
  for (const m of defaults.models) {
    const key = m.provider
    if (!groups[key]) groups[key] = []
    groups[key].push({ label: m.display_name, value: `${m.provider}:${m.model}` })
  }
  return Object.entries(groups).map(([provider, children]) => ({
    type: 'group',
    label: providerLabels[provider] || provider,
    children,
  }))
})

const providerLabels: Record<string, string> = {
  deepseek: 'DeepSeek',
  openai: 'OpenAI',
  qwen: '通义千问',
  zhipu: '智谱',
  ollama: 'Ollama',
}

const { render: renderMarkdown } = useMarkdownRenderer()

const currentSession = computed(() =>
  store.sessions.find(s => s.id === store.currentSessionId)
)

/** 格式化 ISO 日期字符串为展示格式 */
function formatTime(isoStr: string): string {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  if (isNaN(d.getTime())) return ''
  const month = d.getMonth() + 1
  const day = d.getDate()
  const hours = d.getHours().toString().padStart(2, '0')
  const minutes = d.getMinutes().toString().padStart(2, '0')
  return `${month}/${day} ${hours}:${minutes}`
}

function scrollToBottom() {
  nextTick(() => {
    const el = messageContainerRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

/** 消息列表更新后自动滚动到底部 */
watch(() => store.messages.length, () => {
  scrollToBottom()
})
/** 流式输出时自动滚动 */
watch(streamContent, () => { scrollToBottom() })

/** 新建对话 */
async function handleNewChat() {
  await store.createSession({ name: '新会话', model: selectedModel.value })
  message.success('已创建新对话')
}

/** 发送消息（流式输出） */
async function handleSend() {
  const text = inputText.value.trim()
  if (!text || isStreaming.value || store.isSending) return
  inputText.value = ''

  // 尚未选择会话时自动创建
  if (!store.currentSessionId) {
    await store.createSession({ name: '新会话', model: selectedModel.value })
  }

  const sid = store.currentSessionId!
  // 先显示用户消息
  store.messages.push({ id: '', session_id: sid, role: 'user', content: text, created_at: new Date().toISOString() })

  // 流式输出
  isStreaming.value = true
  streamContent.value = ''
  try {
    const { streamSendMessage } = await import('@/modules/ai_testing/api/ai_tester')
    const response = await streamSendMessage(sid, text, selectedModel.value)
    if (!response.body) throw new Error('No response body')
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      // 按行解析 SSE
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          // 下一行是 data
          continue
        }
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.token) {
              streamContent.value += data.token
            }
          } catch { /* skip unparseable */ }
        }
      }
    }
  } catch (e: any) {
    console.error('流式输出错误:', e)
    streamContent.value += `\n\n[错误: ${e?.message || '连接失败'}]`
  } finally {
    isStreaming.value = false
    // 流结束后重新加载消息列表
    await store.selectSession(store.currentSessionId!)
    await store.fetchSessions()
  }
}

/** 重命名会话 */
function handleRename(session: AITesterSession) {
  renamingSessionId.value = session.id
  renameText.value = session.name
  showRenameModal.value = true
}

/** 确认重命名 */
async function handleRenameConfirm() {
  if (!renamingSessionId.value || !renameText.value.trim()) {
    showRenameModal.value = false
    return
  }
  try {
    await store.updateSession(renamingSessionId.value, { name: renameText.value.trim() })
    message.success('已重命名')
  } catch (e) {
    console.error('重命名失败:', e)
    message.error('重命名失败')
  }
  showRenameModal.value = false
}

/** 删除会话 */
async function handleDeleteSession(session: AITesterSession) {
  await store.deleteSession(session.id)
  message.success('会话已删除')
}

/** 清空所有会话 */
async function handleClearHistory() {
  const ids = store.sessions.map(s => s.id)
  if (ids.length === 0) return
  try {
    await store.batchDeleteSessions(ids)
    message.success(`已清空 ${ids.length} 个会话`)
  } catch (e) {
    console.error('清空会话失败:', e)
    message.error('清空失败')
  }
}

/** 填充示例问题到输入框 */
function fillExample(text: string) {
  inputText.value = text
}

/** 复制消息内容到剪贴板 */
async function handleCopy(content: string) {
  try {
    await navigator.clipboard.writeText(content)
    message.success('已复制')
  } catch {
    message.error('复制失败')
  }
}

/** 给消息评分（切换：相同评分取消，不同评分切换） */
async function handleRate(msg: { id: string; rating?: string | null }, rating: 'up' | 'down') {
  try {
    // 切换逻辑：点击相同评分取消，否则设置为新评分
    const newRating = msg.rating === rating ? null : rating
    await rateMessage(msg.id, newRating)
    msg.rating = newRating
    message.success(newRating ? '已评价' : '已取消评价')
    // 重新加载消息列表获取最新评分状态
    const sid = store.currentSessionId
    if (sid) await store.selectSession(sid)
  } catch (e: any) {
    message.error('评价失败: ' + (e.message || '未知错误'))
  }
}

/** 初始化：加载会话列表和模型列表 */
onMounted(async () => {
  store.fetchSessions()
  await genStore.fetchConfigDefaults()
  const models = genStore.configDefaults?.models
  if (models && models.length > 0) {
    selectedModel.value = `${models[0].provider}:${models[0].model}`
  }
})
</script>

<style scoped>
.page-wrap {
  height: 100%;
  padding: 0;
  overflow: hidden;
}

.tester-layout {
  display: flex;
  height: calc(100vh - 52px);
  gap: 0;
}

/* 左栏 */
.sidebar-card {
  width: 30%;
  min-width: 240px;
  max-width: 320px;
  border-radius: 0;
  border-right: 1px solid rgba(180, 150, 120, 0.12);
  display: flex;
  flex-direction: column;
}

.new-chat-btn {
  margin-bottom: 12px;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.session-item:hover {
  background: rgba(198, 123, 92, 0.06);
}

.session-item.active {
  background: rgba(198, 123, 92, 0.1);
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.session-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #3D2E1F);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-time {
  font-size: 11px;
  color: var(--text-muted, #8B7355);
}

.session-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.session-empty {
  text-align: center;
  color: var(--text-muted, #8B7355);
  font-size: 13px;
  padding: 32px 0;
}

/* 右栏 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-primary, #FBF7F0);
}

.chat-header {
  border-bottom: 1px solid rgba(180, 150, 120, 0.1);
  border-radius: 0;
}

.chat-header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #3D2E1F);
}

/* 消息列表 */
.message-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-row {
  display: flex;
  gap: 10px;
  max-width: 75%;
}

.message-row-user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-row-ai {
  align-self: flex-start;
}

.avatar-col {
  flex-shrink: 0;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.ai-avatar {
  background: var(--accent, #C67B5C);
  color: #fff;
}

.user-avatar {
  background: #D4A574;
  color: #fff;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
}

.bubble-ai {
  background: #F0EBE3;
  border-bottom-left-radius: 4px;
  min-width: 60px;
}

.streaming-cursor {
  display: inline-block;
  animation: blink 1s step-end infinite;
  font-size: 14px;
  color: var(--accent, #C67B5C);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.bubble-user {
  background: var(--user-bubble-bg, #EDE4D6);
  border-bottom-right-radius: 4px;
}

.message-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary, #3D2E1F);
  word-break: break-word;
}
/* Markdown 渲染样式增强 */
.message-text :deep(pre) {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 12px 16px;
  overflow-x: auto;
  margin: 8px 0;
}
.message-text :deep(code) {
  font-size: 13px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.message-text :deep(p) {
  margin: 4px 0;
}
.message-text :deep(ul), .message-text :deep(ol) {
  padding-left: 20px;
  margin: 4px 0;
}
.message-text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 13px;
}
.message-text :deep(th), .message-text :deep(td) {
  border: 1px solid rgba(180, 150, 120, 0.2);
  padding: 6px 10px;
  text-align: left;
}
.message-text :deep(th) {
  background: rgba(198, 123, 92, 0.08);
  font-weight: 600;
}
.message-text :deep(blockquote) {
  border-left: 3px solid var(--accent, #C67B5C);
  margin: 8px 0;
  padding: 4px 12px;
  color: var(--text-secondary, #6B5B4A);
  background: rgba(198, 123, 92, 0.04);
  border-radius: 0 4px 4px 0;
}

/* 消息操作按钮 */
.message-actions {
  display: flex;
  gap: 4px;
  margin-top: 6px;
  opacity: 0;
  transition: opacity 0.2s;
}
.message-bubble:hover .message-actions {
  opacity: 1;
}

.message-time {
  font-size: 11px;
  color: var(--text-muted, #8B7355);
  margin-top: 6px;
  text-align: right;
}

.load-more-bar {
  text-align: center;
  padding: 8px 0;
}

.message-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted, #8B7355);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-title {
  font-size: 15px;
  margin-bottom: 16px;
}

.example-questions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 360px;
}

.example-item {
  padding: 10px 16px;
  border: 1px solid rgba(180, 150, 120, 0.2);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-secondary, #6B5B4A);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.example-item:hover {
  background: rgba(198, 123, 92, 0.06);
  border-color: var(--accent, #C67B5C);
  color: var(--accent, #C67B5C);
}

/* 输入区 */
.input-area {
  border-top: 1px solid rgba(180, 150, 120, 0.1);
  border-radius: 0;
}

.input-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-row .n-input {
  flex: 1;
}

/* 打字指示器 */
.typing-indicator {
  padding: 16px 20px !important;
  min-width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.dot-pulse {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent, #C67B5C);
  animation: dotPulse 1.2s ease-in-out infinite;
}
@keyframes dotPulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}
@media (max-width: 768px) {
  .page-wrap { padding: 0; }
  .tester-layout { flex-direction: column; height: auto; }
  .sidebar-card { width: 100%; max-width: none; border-right: none; border-bottom: 1px solid rgba(180, 150, 120, 0.12); max-height: 200px; }
  .session-list { max-height: 120px; }
  .session-actions { opacity: 1; }
  .chat-area { height: calc(100vh - 52px); }
  .message-container { padding: 12px; }
  .message-row { max-width: 88%; }
  .message-bubble { padding: 10px 12px; }
  .chat-header-inner { gap: 8px; }
  .input-row { gap: 8px; }
  .example-questions { max-width: 100%; }
  .empty-icon { font-size: 36px; }
}
</style>
