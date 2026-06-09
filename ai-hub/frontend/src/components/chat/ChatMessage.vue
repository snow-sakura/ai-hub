<template>
  <div :class="['chat-message', `role-${message.role}`]">
    <!-- AI 消息：无头像、无气泡 → 纯内容 -->
    <div v-if="message.role === 'assistant'" class="ai-content">
      <!-- 思考过程（历史消息：默认折叠） -->
      <ThinkingProcess
        v-if="message.thinkingSteps && message.thinkingSteps.length > 0"
        :steps="message.thinkingSteps"
        :is-streaming="false"
        :tool-calls="message.toolCalls"
      />
      <!-- 工具调用结果 -->
      <div v-if="message.toolCalls && message.toolCalls.length > 0" class="tool-calls-area">
        <ToolCallStatus
          v-for="tc in message.toolCalls"
          :key="tc.toolCallId"
          :tool-call="tc"
        />
      </div>
      <div class="message-content">
        <MarkdownBody :content="message.content" />
      </div>
    </div>

    <!-- 用户消息：胶囊气泡 + 右对齐 -->
    <div v-else class="user-bubble">
      <!-- 附件展示 -->
      <div v-if="message.attachments && message.attachments.length > 0" class="user-attachments">
        <div
          v-for="(att, i) in message.attachments"
          :key="i"
          class="user-attach-chip"
        >
          <span class="user-attach-icon">{{ att.type === 'image' ? '🖼️' : '📄' }}</span>
          <span class="user-attach-name">{{ att.name }}</span>
        </div>
      </div>
      {{ message.content }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage } from '../../types/chat'
import ThinkingProcess from './ThinkingProcess.vue'
import ToolCallStatus from './ToolCallStatus.vue'
import MarkdownBody from '../message/MarkdownBody.vue'

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

.role-assistant {
  /* AI 消息靠左 */
  justify-content: flex-start;
}

.role-user {
  /* 用户消息靠右 */
  justify-content: flex-end;
}

/* AI 消息：纯内容，无气泡背景 */
.ai-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  padding-bottom: 4px;
}

.tool-calls-area {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-content {
  font-size: 15px;
  line-height: 1.75;
  color: var(--text-primary);
}

/* 用户消息：暖色胶囊气泡 */
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

/* 用户消息中的附件展示 */
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

/* 消息间距 */
.chat-message + .chat-message {
  margin-top: 24px;
}
</style>
