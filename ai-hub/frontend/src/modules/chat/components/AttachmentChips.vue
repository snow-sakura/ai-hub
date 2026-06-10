<template>
  <!-- 📎 当前附件区 -->
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
      <button class="chip-remove" @click="$emit('removeAttachment', i)">✕</button>
    </div>
  </div>

  <!-- 📚 已选知识库文档区 -->
  <div v-if="knowledgeDocs.length > 0" class="chips-area">
    <span class="chips-label">知识库</span>
    <div
      v-for="doc in knowledgeDocs"
      :key="doc.id"
      class="attach-chip"
      :title="doc.filename"
    >
      <span class="chip-icon">📄</span>
      <span class="chip-name">{{ doc.filename }}</span>
      <span class="chip-meta">{{ doc.chunkCount }} 片段</span>
      <button class="chip-remove" @click="$emit('removeKnowledgeDoc', doc.id)">✕</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UploadAttachment } from '@/modules/chat/types/chat'
import type { KnowledgeDoc } from '@/modules/knowledge/types/knowledge'

defineProps<{
  attachments: UploadAttachment[]
  knowledgeDocs: KnowledgeDoc[]
}>()

defineEmits<{
  removeAttachment: [index: number]
  removeKnowledgeDoc: [id: string]
}>()
</script>

<style scoped>
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
