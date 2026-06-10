<template>
  <div class="chat-input-area">
    <div class="composer">
      <!-- 第一行：输入框独占 -->
      <n-input
        v-model:value="inputText"
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 6 }"
        placeholder="输入消息... Enter 发送，Shift+Enter 换行"
        class="composer-input"
        @keydown="handleKeydown"
      />

      <!-- 第二行：控件栏 → 左侧两个独立入口 + 右侧模型/发送 -->
      <div class="composer-actions">
        <div class="tool-group">
          <!-- 📎 上传附件入口 -->
          <n-upload
            :show-file-list="false"
            :custom-request="handleFileUpload"
            accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.webp,.svg"
            :multiple="true"
          >
            <n-button size="tiny" secondary class="tool-btn">
              <template #icon>
                <span class="tool-btn-icon">📎</span>
              </template>
              <span class="tool-btn-text">附件</span>
            </n-button>
          </n-upload>

          <!-- 📚 知识库入口 → 打开 Modal 进行选择管理 -->
          <n-button size="tiny" secondary class="tool-btn" @click="showKnowledgeModal = true">
            <template #icon>
              <span class="tool-btn-icon">📚</span>
            </template>
            <span class="tool-btn-text">知识库</span>
          </n-button>

          <!-- 🧠 深度思考开关 -->
          <button
            class="toggle-btn"
            :class="{ 'toggle-btn--active': deepThinkingEnabled }"
            @click="deepThinkingEnabled = !deepThinkingEnabled"
          >
            <span class="toggle-icon">🧠</span>
            <span class="toggle-label">深度思考</span>
          </button>

          <!-- 🌐 联网搜索开关 -->
          <button
            class="toggle-btn"
            :class="{ 'toggle-btn--active': webSearchEnabled }"
            @click="webSearchEnabled = !webSearchEnabled"
          >
            <span class="toggle-icon">🌐</span>
            <span class="toggle-label">联网搜索</span>
          </button>
        </div>

        <!-- 占位弹簧 -->
        <div class="spacer" />

        <!-- 右侧控件组 -->
        <div class="right-group">
          <!-- 模型选择器 -->
          <ModelSelector />

          <!-- 发送按钮 -->
          <n-button
            circle
            size="small"
            class="send-btn"
            :disabled="!canSend"
            :type="canSend ? 'primary' : 'default'"
            @click="send"
          >
            <template #icon>
              <span v-if="!streamState.isStreaming" class="send-icon">↑</span>
              <span v-else class="stop-icon">■</span>
            </template>
          </n-button>
        </div>
      </div>
    </div>

    <!-- 📎 当前附件区（随消息发送的临时附件） -->
    <div v-if="attachments.length > 0" class="chips-area">
      <span class="chips-label">附件</span>
      <div
        v-for="(att, i) in attachments"
        :key="i"
        class="attach-chip"
        :title="att.name"
      >
        <span class="chip-icon">{{ att.type === 'image' ? '🖼️' : '📄' }}</span>
        <span class="chip-name">{{ att.name }}</span>
        <button class="chip-remove" @click="removeAttachment(i)">✕</button>
      </div>
    </div>

    <!-- 📚 已选知识库文档区（仅展示用户在弹窗中选择的文档） -->
    <div v-if="selectedKnowledgeDocs.length > 0" class="chips-area">
      <span class="chips-label">知识库</span>
      <div
        v-for="doc in selectedKnowledgeDocs"
        :key="doc.id"
        class="attach-chip"
        :title="doc.filename"
      >
        <span class="chip-icon">📄</span>
        <span class="chip-name">{{ doc.filename }}</span>
        <span class="chip-meta">{{ doc.chunkCount }} 片段</span>
        <button class="chip-remove" @click="removeSelectedDoc(doc.id)">✕</button>
      </div>
    </div>

    <!-- 📚 知识库选择 Modal -->
    <n-modal
      v-model:show="showKnowledgeModal"
      preset="card"
      :style="{ maxWidth: '440px' }"
      title="📚 知识库"
      :bordered="false"
      :segmented="{ content: true, footer: 'soft' }"
      size="small"
    >
      <KnowledgePopover @confirm="onKnowledgeConfirm" />
    </n-modal>

    <!-- @ 工具列表弹出层 -->
    <div v-if="showToolList" class="tool-popup">
      <div
        v-for="tool in filteredTools"
        :key="tool.name"
        class="tool-item"
        @click="selectTool(tool)"
      >
        <span class="tool-icon">{{ toolIcon(tool.icon) }}</span>
        <div>
          <div class="tool-name">{{ tool.displayName }}</div>
          <div class="tool-desc">{{ tool.description?.slice(0, 50) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useChatStore } from '@/modules/chat/stores/chat'
import { useConversationStore } from '@/shared/stores/conversation'
import { useSettingsStore } from '@/shared/stores/settings'
import { useKnowledgeStore } from '@/modules/knowledge/stores/knowledge'
import { useSseStream } from '@/shared/composables/useSseStream'
import { useAtMention } from '@/modules/chat/composables/useAtMention'
import ModelSelector from '@/shared/components/common/ModelSelector.vue'
import KnowledgePopover from '@/modules/chat/components/KnowledgePopover.vue'
import { uploadChatAttachment } from '@/modules/chat/api/chat'
import type { UploadCustomRequestOptions } from 'naive-ui'
import type { KnowledgeDoc } from '@/modules/knowledge/types/knowledge'

const IMAGE_EXTS = ['jpg','jpeg','png','gif','webp','svg']

const chatStore = useChatStore()
const convStore = useConversationStore()
const settingsStore = useSettingsStore()
const knowledgeStore = useKnowledgeStore()
const { sendChat, abort } = useSseStream()

/** 当前对话的流状态 */
const streamState = computed(() => chatStore.activeStreamState)

const inputText = ref('')
const { showToolList, filteredTools, selectTool } = useAtMention(inputText)

/** 临时附件（本次消息带上的文件） */
interface Attachment {
  name: string
  type: 'file' | 'image'
  file: File
}
const attachments = ref<Attachment[]>([])

/** 深度思考/联网搜索开关 */
const deepThinkingEnabled = ref(true)
const webSearchEnabled = ref(false)

/** 知识库选择相关 */
const showKnowledgeModal = ref(false)
const selectedKnowledgeDocIds = ref<string[]>([])

/** 用户在知识库弹窗中勾选的文档（从 store 中过滤） */
const selectedKnowledgeDocs = computed<KnowledgeDoc[]>(() =>
  knowledgeStore.documents.filter(d => selectedKnowledgeDocIds.value.includes(d.id))
)

/** 切换/新建对话时清空附件和知识库选择 */
watch(() => convStore.activeConversationId, () => {
  attachments.value = []
  selectedKnowledgeDocIds.value = []
})

/** 是否可以发送 */
const canSend = computed(() =>
  (inputText.value.trim() || attachments.value.length > 0) && !streamState.value.isStreaming
)

/** 📎 上传文件/图片附件（仅本次消息） */
async function handleFileUpload(options: UploadCustomRequestOptions) {
  const file = options.file?.file
  if (!file) return
  const ext = file.name.split('.').pop()?.toLowerCase() || ''
  attachments.value.push({
    name: file.name,
    type: IMAGE_EXTS.includes(ext) ? 'image' : 'file',
    file,
  })
  options.onFinish()
}

/** 移除附件 */
function removeAttachment(i: number) {
  attachments.value.splice(i, 1)
}

/** 📚 知识库弹窗确认回调 - 保存选中的文档 ID */
function onKnowledgeConfirm(ids: string[]) {
  selectedKnowledgeDocIds.value = ids
  showKnowledgeModal.value = false
}

/** 从已选列表中移除某个知识库文档 */
function removeSelectedDoc(id: string) {
  const idx = selectedKnowledgeDocIds.value.indexOf(id)
  if (idx >= 0) selectedKnowledgeDocIds.value.splice(idx, 1)
}

/** 工具图标映射 */
function toolIcon(icon: string): string {
  const map: Record<string, string> = {
    search: '🔍',
    'file-text': '📄',
    globe: '🌐',
    terminal: '💻',
    image: '🖼️',
  }
  return map[icon] || '🔧'
}

/** 发送消息 */
async function send() {
  if (!canSend.value || streamState.value.isStreaming) return

  const text = inputText.value.trim()

  if (!convStore.activeConversationId) {
    const conv = await convStore.create()
    if (!conv) return
    // 用首条消息前 10 字作为对话标题
    const title = text.length > 10 ? text.slice(0, 10) + '…' : text
    await convStore.rename(conv.id, title)
  }

  const fileAttachments = attachments.value.map(a => ({ name: a.name, type: a.type }))

  chatStore.addUserMessage(text, fileAttachments)
  inputText.value = ''

  // 上传附件到后端获取 file_id
  const fileIds: string[] = []
  if (attachments.value.length > 0) {
    for (const att of attachments.value) {
      try {
        const res = await uploadChatAttachment(att.file)
        fileIds.push(res.data.file_id)
      } catch (e) {
        console.error('附件上传失败:', att.name, e)
      }
    }
  }
  attachments.value = []

  const kbDocIds = [...selectedKnowledgeDocIds.value]
  selectedKnowledgeDocIds.value = []

  await sendChat(
    text,
    convStore.activeConversationId!,
    settingsStore.currentModel.provider,
    settingsStore.currentModel.model,
    fileIds,
    kbDocIds,
    false,
    deepThinkingEnabled.value ? 'high' : 'disabled',
    webSearchEnabled.value,
    deepThinkingEnabled.value,
  )
}

/** 键盘事件 */
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}
</script>

<style scoped>
.chat-input-area {
  padding: 0 24px 20px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.composer {
  max-width: 768px;
  width: 100%;
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.15);
  border-radius: 20px;
  padding: 12px 16px;
  box-shadow: 0 2px 12px rgba(60, 40, 20, 0.06);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.composer:focus-within {
  border-color: rgba(198, 123, 92, 0.35);
  box-shadow: 0 2px 16px rgba(198, 123, 92, 0.08);
}

/* 输入框 */
.composer-input {
  width: 100%;
}

.composer-input :deep(.n-input) {
  border: none !important;
  background: transparent !important;
}

/* 外层容器 padding 清掉，避免多层叠加 */
.composer-input :deep(.n-input__textarea) {
  padding: 0 !important;
}

.composer-input :deep(.n-input__textarea-wrapper) {
  padding: 0 !important;
}

/* textarea 和 placeholder 使用相同的 padding 实现文字/光标上下居中 */
.composer-input :deep(.n-input__placeholder) {
  padding: 8px 0 !important;
  font-size: 15px;
  line-height: 1.6;
  text-align: left;
}

.composer-input :deep(.n-input__placeholder) span {
  padding: 8px 0 !important;
  line-height: 1.6;
}

.composer-input :deep(.n-input__textarea-el) {
  font-size: 15px;
  line-height: 1.6;
  resize: none;
  padding: 8px 0 !important;
  text-align: left !important;
  vertical-align: top;
}

/* 控件栏 */
.composer-actions {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.spacer {
  flex: 1;
}

/* 左侧工具按钮组：📎附件 📚知识库 */
.tool-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tool-btn {
  flex-shrink: 0;
  height: 30px;
  padding: 0 12px;
  border-radius: 15px;
  gap: 4px;
  border: 1px solid rgba(180, 150, 120, 0.2) !important;
}

.tool-btn-icon {
  font-size: 14px;
  line-height: 1;
}

.tool-btn-text {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Toggle 开关按钮 */
.toggle-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 14px;
  border: 1px solid rgba(180, 150, 120, 0.15);
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  color: var(--text-secondary);
  flex-shrink: 0;
  height: 28px;
}

.toggle-btn:hover {
  border-color: rgba(180, 150, 120, 0.3);
  background: rgba(180, 150, 120, 0.04);
}

.toggle-btn--active {
  border-color: rgba(198, 123, 92, 0.35);
  background: rgba(198, 123, 92, 0.06);
  color: var(--accent);
}

.toggle-icon { font-size: 13px; }

.toggle-label {
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

/* 右侧控件组 */
.right-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.send-btn {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border: 1px solid rgba(180, 150, 120, 0.25) !important;
}

.send-btn:not(.n-button--primary) {
  border-color: rgba(180, 150, 120, 0.35) !important;
}

.send-icon {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.stop-icon {
  font-size: 11px;
  font-weight: 700;
  color: var(--danger);
}

.tool-popup {
  position: absolute;
  bottom: calc(100% + 4px);
  left: 50%;
  transform: translateX(-50%);
  max-width: 400px;
  width: calc(100% - 48px);
  max-height: 280px;
  overflow-y: auto;
  padding: 8px;
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 14px;
  box-shadow: var(--shadow-md);
  z-index: 100;
}

.tool-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.tool-item:hover {
  background: var(--accent-bg);
}

.tool-icon { font-size: 18px; }

.tool-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.tool-desc {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* 附件/知识库 chips 区域 */
.chips-area {
  max-width: 768px;
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.chips-label {
  font-size: 11px;
  color: var(--text-muted);
  flex-shrink: 0;
  margin-right: 2px;
}

.attach-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  background: var(--bg-secondary);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 20px;
  font-size: 12px;
  cursor: default;
  max-width: 240px;
}

.chip-icon {
  font-size: 13px;
  flex-shrink: 0;
}

.chip-name {
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chip-meta {
  color: var(--text-muted);
  font-size: 10px;
  flex-shrink: 0;
}

.chip-remove {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 10px;
  color: var(--text-muted);
  padding: 1px 3px;
  border-radius: 3px;
  flex-shrink: 0;
  line-height: 1;
  transition: all 0.15s;
}

.chip-remove:hover {
  color: var(--danger);
  background: rgba(212, 116, 92, 0.1);
}
</style>
