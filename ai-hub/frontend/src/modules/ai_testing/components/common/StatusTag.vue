<template>
  <span class="status-tag" :class="[`status-${status}`]">
    <span class="status-dot"></span>
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ProjectStatus } from '@/modules/ai_testing/types/project'

const props = defineProps<{
  status: ProjectStatus
}>()

const label = computed(() => {
  const map: Record<ProjectStatus, string> = {
    active: '进行中',
    paused: '已暂停',
    completed: '已完成',
    archived: '已归档',
  }
  return map[props.status] || props.status
})
</script>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.4;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-active {
  background: rgba(16, 185, 129, 0.08);
  color: #059669;
}
.status-active .status-dot {
  background: #10b981;
}

.status-paused {
  background: rgba(245, 158, 11, 0.08);
  color: #d97706;
}
.status-paused .status-dot {
  background: #f59e0b;
}

.status-completed {
  background: rgba(59, 130, 246, 0.08);
  color: #2563eb;
}
.status-completed .status-dot {
  background: #3b82f6;
}

.status-archived {
  background: rgba(107, 114, 128, 0.08);
  color: #5C4A38;
}
.status-archived .status-dot {
  background: #7A6855;
}
</style>
