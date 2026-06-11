<template>
  <span class="priority-badge" :class="[`priority-${priority}`]">
    {{ priority }}
  </span>
</template>

<script setup lang="ts">
import type { CasePriority } from '@/modules/ai_testing/types/testcase'

defineProps<{
  priority: CasePriority
}>()
</script>

<style scoped>
.priority-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  line-height: 1.6;
}

.priority-P0 {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.priority-P1 {
  background: rgba(249, 115, 22, 0.1);
  color: #ea580c;
}

.priority-P2 {
  background: rgba(59, 130, 246, 0.08);
  color: #2563eb;
}

.priority-P3 {
  background: rgba(107, 114, 128, 0.08);
  color: #5C4A38;
}
</style>
