<template>
  <div class="user-bubble">
    <div v-if="attachments && attachments.length > 0" class="user-attachments">
      <div v-for="(att, i) in attachments" :key="i" class="user-attach-chip">
        <span class="user-attach-icon">{{ att.type === 'image' ? '🖼️' : '📄' }}</span>
        <span class="user-attach-name">{{ att.name }}</span>
      </div>
    </div>
    {{ content }}
  </div>
</template>

<script setup lang="ts">
import type { MessageAttachment } from '@/modules/chat/types/chat'

defineProps<{
  content: string
  attachments?: MessageAttachment[]
}>()
</script>

<style scoped>
.user-bubble {
  background: var(--user-bubble-bg);
  border: 1px solid var(--user-bubble-border);
  border-radius: 24px;
  padding: 10px 20px;
  max-width: 75%;
  font-size: 15px;
  line-height: 1.65;
  color: var(--text-primary);
  word-break: break-word;
  white-space: pre-wrap;
}

.user-attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.user-attach-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.15);
  border-radius: 16px;
  font-size: 12px;
}

.user-attach-icon {
  font-size: 12px;
  flex-shrink: 0;
}

.user-attach-name {
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 120px;
}
</style>
