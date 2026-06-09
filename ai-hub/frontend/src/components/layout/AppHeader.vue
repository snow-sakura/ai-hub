<template>
  <header class="app-header">
    <div class="header-left">
      <span class="header-title">{{ activeTitle }}</span>
    </div>
    <div class="header-right">
      <ModelSelector />
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ModelSelector from '../common/ModelSelector.vue'
import { useConversationStore } from '../../stores/conversation'

const convStore = useConversationStore()

const activeTitle = computed(() => {
  if (!convStore.activeConversationId) return 'AI 智能助手'
  const conv = convStore.conversations.find(c => c.id === convStore.activeConversationId)
  return conv?.title || 'AI 智能助手'
})
</script>

<style scoped>
.app-header {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: var(--bg-card);
}

.header-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}
</style>
