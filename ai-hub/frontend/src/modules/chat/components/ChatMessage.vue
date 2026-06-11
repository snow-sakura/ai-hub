<template>
  <div :class="['chat-message', `role-${message.role}`]">
    <!-- AI 消息 -->
    <div v-if="message.role === 'assistant'" class="ai-content">
      <!-- DeepSeek 推理过程 -->
      <ReasoningBlock
        v-if="message.reasoning"
        :content="message.reasoning"
        :is-streaming="false"
      />
      <!-- 工具调用简单摘要 -->
      <div v-if="message.toolCalls && message.toolCalls.length > 0" class="tool-chips">
        <div
          v-for="tc in message.toolCalls"
          :key="tc.toolCallId"
          class="tool-chip"
        >
          <span :class="['tool-chip-icon', `status-${tc.status}`]">{{ tc.status === 'done' ? '✓' : tc.status === 'error' ? '!' : '⟳' }}</span>
          <span class="tool-chip-name">{{ tc.toolName }}</span>
          <span v-if="tc.summary" class="tool-chip-summary">{{ tc.summary.slice(0, 40) }}</span>
        </div>
      </div>
      <div class="message-content">
        <MarkdownBody :content="message.content" />
      </div>
    </div>

    <!-- 用户消息 -->
    <UserBubble v-else :content="message.content" :attachments="message.attachments" />
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage } from '@/modules/chat/types/chat'
import ReasoningBlock from '@/modules/chat/components/ReasoningBlock.vue'
import MarkdownBody from '@/shared/components/message/MarkdownBody.vue'
import UserBubble from '@/shared/components/message/UserBubble.vue'

defineProps<{
  message: ChatMessage
}>()
</script>

<style scoped>
.chat-message {
  display: flex;
  max-width: 768px;
  width: 100%;
  margin: 0 auto;
  padding: 0 48px;
}

@media (max-width: 768px) {
  .chat-message {
    padding: 0 16px;
  }
}

.role-assistant {
  justify-content: flex-start;
}

.role-user {
  justify-content: flex-end;
}

.ai-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  padding-bottom: 4px;
}

.message-content {
  font-size: 15px;
  line-height: 1.75;
  color: var(--text-primary);
}

/* 工具调用简单芯片 */
.tool-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tool-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: var(--bg-secondary);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 12px;
  font-size: 11px;
  color: var(--text-muted);
}

.tool-chip-icon {
  font-size: 12px;
  flex-shrink: 0;
  font-weight: 600;
}
.status-done { color: #52c41a; }
.status-error { color: #ff4d4f; }
.status-running { color: var(--accent); }

.tool-chip-name {
  font-weight: 500;
  color: var(--text-secondary);
}

.tool-chip-summary {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 120px;
}

.chat-message + .chat-message {
  margin-top: 24px;
}
</style>
