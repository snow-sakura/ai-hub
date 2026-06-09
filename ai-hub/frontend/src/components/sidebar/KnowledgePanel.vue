<template>
  <div class="knowledge-panel">
    <n-upload
      :show-file-list="false"
      :custom-request="handleUpload"
      accept=".pdf,.docx,.txt"
    >
      <n-button size="small" :loading="knowledgeStore.isUploading" block>
        + 上传文档
      </n-button>
    </n-upload>

    <div class="doc-list">
      <div v-for="doc in knowledgeStore.documents" :key="doc.id" class="doc-item">
        <div class="doc-info">
          <span class="doc-name">📄 {{ doc.filename }}</span>
          <span class="doc-meta">{{ doc.chunkCount }} 片段</span>
        </div>
        <button class="delete-btn" @click="removeDoc(doc.id)" title="删除">✕</button>
      </div>

      <div v-if="knowledgeStore.documents.length === 0" class="empty">
        暂无文档，点击上方上传
      </div>
    </div>

    <n-button
      v-if="knowledgeStore.documents.length > 0"
      size="tiny"
      quaternary
      @click="handleRebuild"
      class="rebuild-btn"
    >
      重建索引
    </n-button>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useKnowledgeStore } from '../../stores/knowledge'
import type { UploadCustomRequestOptions } from 'naive-ui'

const knowledgeStore = useKnowledgeStore()

onMounted(() => {
  knowledgeStore.fetchDocuments()
})

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

function removeDoc(id: string) {
  knowledgeStore.remove(id)
}

function handleRebuild() {
  knowledgeStore.rebuild()
}
</script>

<style scoped>
.knowledge-panel {
  padding: 12px 8px;
}

.doc-list {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  max-height: 200px;
  overflow-y: auto;
}

.doc-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  border-radius: 6px;
  transition: background 0.15s ease;
}

.doc-item:hover {
  background: rgba(180, 150, 120, 0.05);
}

.doc-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
  min-width: 0;
}

.doc-name {
  font-size: 12px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-meta {
  font-size: 10px;
  color: var(--text-muted);
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 11px;
  color: var(--text-muted);
  padding: 2px 4px;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.15s ease;
}

.doc-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: var(--danger);
  background: rgba(239, 68, 68, 0.08);
}

.empty {
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  padding: 12px 8px;
}

.rebuild-btn {
  margin-top: 8px;
  width: 100%;
}
</style>
