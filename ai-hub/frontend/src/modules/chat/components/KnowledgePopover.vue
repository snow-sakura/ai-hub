<template>
  <div class="kp-wrapper">
    <!-- 文档列表 -->
    <div v-if="knowledgeStore.documents.length > 0" class="kp-list">
      <div
        v-for="doc in knowledgeStore.documents"
        :key="doc.id"
        :class="['kp-item', { 'kp-item--active': selectedIds.includes(doc.id) }]"
        @click="toggleDoc(doc.id)"
      >
        <n-checkbox :checked="selectedIds.includes(doc.id)" @click.stop="toggleDoc(doc.id)" />
        <span class="kp-doc-icon">📄</span>
        <div class="kp-doc-info">
          <span class="kp-doc-name">{{ doc.filename }}</span>
          <span class="kp-doc-meta">{{ doc.chunkCount }} 个片段 · {{ formatSize(doc.fileSize) }}</span>
        </div>
        <button class="kp-delete" @click.stop="removeDoc(doc.id)" title="从知识库删除">✕</button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="kp-empty">
      <div class="kp-empty-icon"><span>📂</span></div>
      <span class="kp-empty-text">知识库为空</span>
      <span class="kp-empty-hint">上传文档后即可在对话中引用</span>
    </div>

    <!-- 上传按钮 -->
    <n-upload
      :show-file-list="false"
      :custom-request="handleUpload"
      accept=".pdf,.doc,.docx,.txt"
    >
      <n-button size="small" block dashed :loading="knowledgeStore.isUploading" class="kp-upload-btn">
        上传文档（PDF / Word / TXT）
      </n-button>
    </n-upload>

    <!-- 已选计数 -->
    <div class="kp-count-bar">
      <span class="kp-count-text">已选 {{ selectedIds.length }} 个文档</span>
    </div>

    <!-- 底部操作 -->
    <div class="kp-footer">
      <n-button size="tiny" quaternary @click="handleClearAll" class="kp-clear-btn">
        清除选择
      </n-button>
      <n-button size="tiny" type="primary" @click="handleConfirm" :disabled="selectedIds.length === 0" class="kp-confirm-btn">
        确认引用 ({{ selectedIds.length }})
      </n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useKnowledgeStore } from '@/modules/knowledge/stores/knowledge'
import type { UploadCustomRequestOptions } from 'naive-ui'

const emit = defineEmits<{
  confirm: [docIds: string[]]
  close: []
}>()

const knowledgeStore = useKnowledgeStore()
const selectedIds = ref<string[]>([])

onMounted(() => {
  knowledgeStore.fetchDocuments()
})

function toggleDoc(id: string) {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(id)
  }
}

async function handleUpload(options: UploadCustomRequestOptions) {
  const file = options.file?.file
  if (file) {
    try {
      await knowledgeStore.upload(file)
      options.onFinish()
    } catch {
      options.onError()
    }
  }
}

async function removeDoc(id: string) {
  await knowledgeStore.remove(id)
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
}

function handleClearAll() {
  selectedIds.value = []
}

function handleConfirm() {
  emit('confirm', [...selectedIds.value])
}

function formatSize(bytes: number): string {
  if (!bytes && bytes !== 0) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>

<style scoped>
.kp-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 200px;
}

/* 文档列表 */
.kp-list {
  display: flex;
  flex-direction: column;
  gap: 3px;
  max-height: 280px;
  overflow-y: auto;
  flex: 1;
}

.kp-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
}

.kp-item:hover {
  background: rgba(180, 150, 120, 0.06);
  border-color: rgba(180, 150, 120, 0.12);
}

.kp-item--active {
  background: rgba(198, 123, 92, 0.07);
  border-color: rgba(198, 123, 92, 0.18);
}

.kp-item--active:hover {
  background: rgba(198, 123, 92, 0.1);
}

.kp-doc-icon {
  font-size: 18px;
  flex-shrink: 0;
  line-height: 1;
}

.kp-doc-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.kp-doc-name {
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.kp-doc-meta {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.kp-delete {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-muted);
  padding: 3px 6px;
  border-radius: 6px;
  flex-shrink: 0;
  opacity: 0;
  transition: all 0.15s;
  line-height: 1;
}

.kp-item:hover .kp-delete {
  opacity: 1;
}

.kp-delete:hover {
  color: var(--danger);
  background: rgba(212, 116, 92, 0.1);
}

/* 空状态 */
.kp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 40px 16px;
  flex: 1;
}

.kp-empty-icon {
  font-size: 36px;
  margin-bottom: 4px;
  opacity: 0.6;
}

.kp-empty-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.kp-empty-hint {
  font-size: 12px;
  color: var(--text-muted);
}

/* 上传按钮 */
.kp-upload-btn {
  font-size: 12px;
  border-radius: 8px;
}

/* 已选计数 */
.kp-count-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px 0;
}

.kp-count-text {
  font-size: 11px;
  color: var(--text-muted);
}

/* 底部操作 */
.kp-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(180, 150, 120, 0.1);
}

.kp-clear-btn {
  font-size: 12px;
}

.kp-confirm-btn {
  min-width: 110px;
  font-size: 12px;
}
</style>
