<template>
  <div class="progress-bar">
    <div class="progress-info">
      <span>{{ progress.message }}</span>
      <span>{{ progress.current }}/{{ progress.total }}</span>
    </div>
    <n-progress
      type="line"
      :percentage="percentage"
      :show-indicator="false"
      :color="'#C67B5C'"
      :rail-color="'rgba(198, 123, 92, 0.1)'"
      :height="6"
      :border-radius="3"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ProgressInfo } from '@/modules/chat/types/chat'

const props = defineProps<{ progress: ProgressInfo }>()

const percentage = computed(() => {
  if (props.progress.total === 0) return 0
  return Math.round((props.progress.current / props.progress.total) * 100)
})
</script>

<style scoped>
.progress-bar {
  padding: 8px 12px;
  border-radius: 8px;
  background: var(--accent-bg);
  border: 1px solid rgba(198, 123, 92, 0.15);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}
</style>
