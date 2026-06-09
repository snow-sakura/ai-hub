<template>
  <div class="kp-wrapper">
    <!-- 头部 -->
    <div class="kp-header">
      <span class="kp-title">📚 知识库</span>
      <span class="kp-count">已选 {{ selectedIds.length }} / {{ knowledgeStore.documents.length }}</span>
    </div>

    <!-- 上传按钮 -->
    <n-upload
      :show-file-list="false"
      :custom-request="handleUpload"
      accept=".pdf,.doc,.docx,.txt"
    >
      <n-button size="small" block dashed :loading="knowledgeStore.isUploading" class="kp-upload-btn">
        <template #icon><span class="kp-plus-icon">+</span></template>
        上传文档（PDF / Word / TXT）
      </n-button>
    </n-upload>

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
          <span class="kp-doc-meta">{{ doc.chunkCount }} 个片段</span>
        </div>
        <button class="kp-delete" @click.stop="removeDoc(doc.id)" title="从知识库删除">✕</button>
      </div>
    </div>

    <div v-else class="kp-empty">
      <span class="kp-empty-icon">📂</span>
      <span>知识库为空，上传文档开始使用</span>
    </div>

    <!-- 底部操作 -->
    <div class="kp-footer">
      <n-button size="small" quaternary @click="handleClearAll">清除选择</n-button>
      <n-button size="small" type="primary" @click="handleConfirm" class="kp-confirm-btn">
        确认引用 ({{ selectedIds.length }})
      </n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useKnowledgeStore } from '../../stores/knowledge'
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
  emit('confirm', selectedIds.value)
}
</script>

<style scoped>
.kp-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
}

.kp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kp-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.kp-count {
  font-size: 11px;
  color: var(--text-muted);
}

.kp-plus-icon {
  font-size: 14px;
  font-weight: 600;
}

.kp-upload-btn {
  font-size: 12px;
}

.kp-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 260px;
  overflow-y: auto;
  flex: 1;
}

.kp-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.kp-item:hover {
  background: rgba(180, 150, 120, 0.06);
}

.kp-item--active {
  background: rgba(198, 123, 92, 0.06);
}

.kp-item--active:hover {
  background: rgba(198, 123, 92, 0.1);
}

.kp-doc-icon {
  font-size: 15px;
  flex-shrink: 0;
}

.kp-doc-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.kp-doc-name {
  font-size: 12px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kp-doc-meta {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 1px;
}

.kp-delete {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 11px;
  color: var(--text-muted);
  padding: 2px 5px;
  border-radius: 4px;
  flex-shrink: 0;
  opacity: 0;
  transition: all 0.15s;
}

.kp-item:hover .kp-delete {
  opacity: 1;
}

.kp-delete:hover {
  color: var(--danger);
  background: rgba(212, 116, 92, 0.1);
}

.kp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.kp-empty-icon {
  font-size: 28px;
}

.kp-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(180, 150, 120, 0.1);
}

.kp-confirm-btn {
  min-width: 100px;
}
</style>
