<template>
  <div class="message-list" ref="listRef">
    <transition-group name="slide-up">
      <ChatMessage
        v-for="msg in chatStore.messages"
        :key="msg.id"
        :message="msg"
      />
    </transition-group>

    <!-- 流式消息 -->
    <div v-if="streamState.isStreaming" class="streaming-message">
      <!-- DeepSeek 推理过程（推理结束前实时流式，结束后可折叠） -->
      <ReasoningBlock
        :content="streamState.reasoning"
        :is-streaming="!streamState.reasoningComplete"
      />
      <!-- 流式内容 -->
      <div class="streaming-content">{{ streamState.streamingContent }}</div>
      <StreamingCursor v-if="streamState.streamingContent" />
    </div>

    <!-- 错误提示 -->
    <div v-if="streamState.error" class="error-banner">
      <n-alert type="error" :title="streamState.error" />
    </div>

    <!-- 空状态 -->
    <div v-if="chatStore.messages.length === 0 && !streamState.isStreaming" class="empty-state">
      <div class="empty-icon">🤖</div>
      <h3>AI聊天室</h3>
      <p>发送消息开始对话，支持工具调用、文件上传、联网搜索等功能</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useChatStore } from '@/modules/chat/stores/chat'
import ChatMessage from '@/modules/chat/components/ChatMessage.vue'
import ReasoningBlock from '@/modules/chat/components/ReasoningBlock.vue'
import StreamingCursor from '@/modules/chat/components/StreamingCursor.vue'

const chatStore = useChatStore()
const listRef = ref<HTMLElement>()

/** 当前活跃对话的流式状态 */
const streamState = computed(() => chatStore.activeStreamState)

/** 自动滚动到底部 */
function scrollToBottom() {
  nextTick(() => {
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  })
}

// 监听消息数量变化，自动滚动
watch(() => chatStore.messages.length, scrollToBottom)

// 监听流式内容变化，自动滚动
watch(() => streamState.value.streamingContent, scrollToBottom)
watch(() => streamState.value.currentThinkingSteps.length, scrollToBottom)
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 48px 24px 24px;
  display: flex;
  flex-direction: column;
}

.streaming-message {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 48px;
  max-width: 768px;
  width: 100%;
  margin: 0 auto;
}

.streaming-content {
  font-size: 15px;
  line-height: 1.75;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.error-banner {
  max-width: 768px;
  margin: 0 auto;
  width: 100%;
  padding: 8px 48px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  gap: 12px;
}

.empty-icon {
  font-size: 56px;
  opacity: 0.7;
}

.empty-state h3 {
  font-size: 22px;
  font-weight: 500;
  color: var(--text-primary);
}

.empty-state p {
  font-size: 14px;
  max-width: 360px;
  text-align: center;
  line-height: 1.8;
}
</style>
