<template>
  <div :class="['tool-status', `status-${toolCall.status}`, { compact }]">
    <div class="tool-header" @click="toggle">
      <span v-if="toolCall.status === 'running'" class="spinner" />
      <span v-else-if="toolCall.status === 'done'" class="done-icon">✅</span>
      <span v-else-if="toolCall.status === 'error'" class="error-icon">⚠️</span>
      <span class="tool-display">{{ toolCall.display || toolCall.toolName }}</span>
      <span v-if="!compact && hasDetail" :class="['expand-arrow', { open: isExpanded }]">▾</span>
    </div>

    <!-- 简洁模式：只显示结果摘要 -->
    <div v-if="compact && toolCall.summary && toolCall.status === 'done'" class="compact-summary">
      {{ toolCall.summary }}
    </div>

    <!-- 展开详情 -->
    <div v-if="isExpanded && !compact" class="tool-detail">
      <div v-if="toolCall.input" class="tool-section">
        <div class="section-label">入参</div>
        <pre class="section-content">{{ formatJSON(toolCall.input) }}</pre>
      </div>
      <div v-if="toolCall.summary" class="tool-section">
        <div class="section-label">结果摘要</div>
        <div class="section-content">{{ toolCall.summary }}</div>
      </div>
      <div v-if="toolCall.result" class="tool-section">
        <div class="section-label">完整输出</div>
        <pre class="section-content">{{ formatJSON(toolCall.result) }}</pre>
      </div>
      <div v-if="toolCall.status === 'error'" class="tool-section tool-error">
        <div class="section-label">错误</div>
        <div class="section-content">{{ toolCall.summary || '执行失败' }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ToolCallStatus } from '../../types/chat'

const props = withDefaults(defineProps<{
  toolCall: ToolCallStatus
  compact?: boolean
}>(), {
  compact: false,
})

const isExpanded = ref(false)

function toggle() {
  if (!props.compact) {
    isExpanded.value = !isExpanded.value
  }
}

const hasDetail = computed(() =>
  props.toolCall.input || props.toolCall.summary || props.toolCall.result
)

function formatJSON(data: Record<string, any>): string {
  try {
    return JSON.stringify(data, null, 2)
  } catch {
    return String(data)
  }
}
</script>

<style scoped>
.tool-status {
  border-radius: 8px;
  font-size: 13px;
  border: 1px solid rgba(180, 150, 120, 0.1);
  background: var(--bg-secondary);
  overflow: hidden;
}

.tool-status.compact {
  margin-top: 4px;
  border-radius: 6px;
  font-size: 12px;
}

.status-running {
  border-color: rgba(198, 123, 92, 0.25);
  background: var(--accent-bg);
}

.status-error {
  border-color: rgba(212, 80, 60, 0.25);
  background: rgba(212, 80, 60, 0.04);
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  cursor: pointer;
  user-select: none;
}

.compact .tool-header {
  padding: 4px 8px;
  cursor: default;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(198, 123, 92, 0.2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg) }
}

.tool-display {
  color: var(--text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.done-icon {
  font-size: 13px;
  flex-shrink: 0;
}

.error-icon {
  font-size: 13px;
  flex-shrink: 0;
}

.expand-arrow {
  font-size: 11px;
  color: var(--text-muted);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.expand-arrow.open {
  transform: rotate(180deg);
}

/* 简洁模式摘要 */
.compact-summary {
  padding: 0 8px 4px 8px;
  font-size: 11px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 展开详情 */
.tool-detail {
  border-top: 1px solid rgba(180, 150, 120, 0.08);
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.section-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-content {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  background: rgba(0, 0, 0, 0.02);
  padding: 6px 8px;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.tool-error .section-content {
  color: #d4503c;
}
</style>
