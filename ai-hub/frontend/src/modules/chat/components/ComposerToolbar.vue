<template>
  <div class="composer-actions">
    <div class="tool-group">
      <!-- 📎 上传附件入口 -->
      <n-upload
        :show-file-list="false"
        :custom-request="(options) => $emit('fileUpload', options)"
        accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.webp,.svg"
        :multiple="true"
      >
        <n-button size="tiny" secondary class="tool-btn">
          <template #icon>
            <span class="tool-btn-icon">📎</span>
          </template>
          <span class="tool-btn-text">附件</span>
        </n-button>
      </n-upload>

      <!-- 📚 知识库入口 -->
      <n-button size="tiny" secondary class="tool-btn" @click="$emit('knowledgeOpen')">
        <template #icon>
          <span class="tool-btn-icon">📚</span>
        </template>
        <span class="tool-btn-text">知识库</span>
      </n-button>

      <!-- 🧠 深度思考开关 -->
      <button
        class="toggle-btn"
        :class="{ 'toggle-btn--active': deepThinkingEnabled }"
        @click="$emit('update:deepThinkingEnabled', !deepThinkingEnabled)"
      >
        <span class="toggle-icon">🧠</span>
        <span class="toggle-label">深度思考</span>
      </button>

      <!-- 🌐 联网搜索开关 -->
      <button
        class="toggle-btn"
        :class="{ 'toggle-btn--active': webSearchEnabled }"
        @click="$emit('update:webSearchEnabled', !webSearchEnabled)"
      >
        <span class="toggle-icon">🌐</span>
        <span class="toggle-label">联网搜索</span>
      </button>
    </div>

    <div class="spacer" />

    <div class="right-group">
      <ModelSelector />
      <n-button
        circle
        size="small"
        class="send-btn"
        :disabled="!canSend"
        :type="canSend ? 'primary' : 'default'"
        @click="$emit('send')"
      >
        <template #icon>
          <span v-if="!isStreaming" class="send-icon">↑</span>
          <span v-else class="stop-icon">■</span>
        </template>
      </n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import ModelSelector from '@/shared/components/common/ModelSelector.vue'

defineProps<{
  deepThinkingEnabled: boolean
  webSearchEnabled: boolean
  canSend: boolean
  isStreaming: boolean
}>()

defineEmits<{
  send: []
  fileUpload: [options: any]
  knowledgeOpen: []
  'update:deepThinkingEnabled': [value: boolean]
  'update:webSearchEnabled': [value: boolean]
}>()
</script>

<style scoped>
.composer-actions {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.spacer {
  flex: 1;
}

.tool-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tool-btn {
  flex-shrink: 0;
  height: 30px;
  padding: 0 12px;
  border-radius: 15px;
  gap: 4px;
  border: 1px solid rgba(180, 150, 120, 0.2) !important;
}

.tool-btn-icon {
  font-size: 14px;
  line-height: 1;
}

.tool-btn-text {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 14px;
  border: 1px solid rgba(180, 150, 120, 0.15);
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  color: var(--text-secondary);
  flex-shrink: 0;
  height: 28px;
}

.toggle-btn:hover {
  border-color: rgba(180, 150, 120, 0.3);
  background: rgba(180, 150, 120, 0.04);
}

.toggle-btn--active {
  border-color: rgba(198, 123, 92, 0.35);
  background: rgba(198, 123, 92, 0.06);
  color: var(--accent);
}

.toggle-icon { font-size: 13px; }

.toggle-label {
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.right-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.send-btn {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border: 1px solid rgba(180, 150, 120, 0.25) !important;
}

.send-btn:not(.n-button--primary) {
  border-color: rgba(180, 150, 120, 0.35) !important;
}

.send-icon {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.stop-icon {
  font-size: 11px;
  font-weight: 700;
  color: var(--danger);
}
</style>
