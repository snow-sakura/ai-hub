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
      <!-- 思考过程（流式状态：显示动画指示器） -->
      <ThinkingProcess
        v-if="streamState.currentThinkingSteps.length > 0"
        :steps="streamState.currentThinkingSteps"
        :is-streaming="true"
        :tool-calls="streamState.currentToolCalls"
        :progress="streamState.progress"
      />
      <!-- 独立的工具调用卡片 -->
      <div v-if="streamState.currentToolCalls.length > 0 && streamState.currentThinkingSteps.length === 0" class="tool-calls-area">
        <ToolCallStatus
          v-for="tc in streamState.currentToolCalls"
          :key="tc.toolCallId"
          :tool-call="tc"
        />
      </div>
      <!-- 流式内容 -->
      <div class="assistant-bubble">
        <MarkdownBody :content="streamState.streamingContent" />
        <StreamingCursor />
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="streamState.error" class="error-banner">
      <n-alert type="error" :title="streamState.error" />
    </div>

    <!-- 空状态 -->
    <div v-if="chatStore.messages.length === 0 && !streamState.isStreaming" class="empty-state">
      <div class="empty-icon">🤖</div>
      <h3>AI 超级智能助手</h3>
      <p>发送消息开始对话，支持工具调用、文件上传、联网搜索等功能</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useChatStore } from '@/modules/chat/stores/chat'
import ChatMessage from '@/modules/chat/components/ChatMessage.vue'
import ThinkingProcess from '@/modules/chat/components/ThinkingProcess.vue'
import ToolCallStatus from '@/modules/chat/components/ToolCallStatus.vue'
import StreamingCursor from '@/modules/chat/components/StreamingCursor.vue'
import MarkdownBody from '@/shared/components/message/MarkdownBody.vue'

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

watch(() => chatStore.messages.length, scrollToBottom)
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

.tool-calls-area {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.assistant-bubble {
  border-radius: 12px;
  padding: 0;
  max-width: 100%;
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
