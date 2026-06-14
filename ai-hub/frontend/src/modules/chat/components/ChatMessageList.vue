<template>
  <div ref="listRef" class="message-list" @scroll="onScroll">
    <!-- 加载更多历史消息 -->
    <div v-if="convStore.hasMoreMessages && !isLoadingMore" class="load-more" @click="loadMore">
      <span class="load-more-text">↑ 加载更多历史消息</span>
    </div>
    <div v-if="isLoadingMore" class="load-more load-more--loading">
      <span class="load-more-spinner">⋯</span>
    </div>

    <!-- 虚拟列表（消息数 > 0 时渲染） -->
    <div
      v-if="chatStore.messages.length > 0"
      :style="{
        height: `${virtualizer.getTotalSize()}px`,
        position: 'relative',
        width: '100%',
      }"
    >
      <div
        v-for="vRow in virtualizer.getVirtualItems()"
        :key="String(vRow.key)"
        :data-index="vRow.index"
        :ref="(el: any) => { if (el) virtualizer.measureElement(el) }"
        :style="{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          transform: `translateY(${vRow.start}px)`,
        }"
      >
        <ChatMessage :message="chatStore.messages[vRow.index]" />
      </div>
    </div>

    <!-- 流式消息 -->
    <div v-if="streamState.isStreaming" class="streaming-message">
      <ReasoningBlock
        :content="streamState.reasoning"
        :is-streaming="!streamState.reasoningComplete"
      />
      <div class="streaming-content">{{ streamState.streamingContent }}</div>
      <StreamingCursor v-if="streamState.streamingContent" />
    </div>

    <!-- 错误提示 -->
    <div v-if="streamState.error" class="error-banner">
      <n-alert type="error" :title="streamState.error" />
    </div>

    <!-- 空状态 -->
    <div v-if="chatStore.messages.length === 0 && !streamState.isStreaming" class="empty-state">
      <div class="empty-icon-card">
        <div class="empty-icon">🤖</div>
      </div>
      <h3>AI聊天室</h3>
      <p>发送消息开始对话，支持工具调用、文件上传、联网搜索等功能</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useVirtualizer } from '@tanstack/vue-virtual'
import { useChatStore } from '@/modules/chat/stores/chat'
import { useConversationStore } from '@/shared/stores/conversation'
import ChatMessage from '@/modules/chat/components/ChatMessage.vue'
import ReasoningBlock from '@/modules/chat/components/ReasoningBlock.vue'
import StreamingCursor from '@/modules/chat/components/StreamingCursor.vue'

const chatStore = useChatStore()
const convStore = useConversationStore()
const listRef = ref<HTMLElement>()
const isLoadingMore = ref(false)
const prevVirtualHeight = ref(0)

/** 当前活跃对话的流式状态 */
const streamState = computed(() => chatStore.activeStreamState)

// RAF 节流：流式内容更新时限制滚动频率，避免频繁重排
let scrollRafId: number | null = null

function throttledScrollToBottom() {
  if (scrollRafId !== null) return
  scrollRafId = requestAnimationFrame(() => {
    scrollRafId = null
    virtualizer.value.scrollToIndex(chatStore.messages.length, { align: 'end', behavior: 'auto' })
  })
}

/** 虚拟滚动实例 */
// 使用 getter 访问 chatStore.messages.length，Vue 响应式自动追踪变化
const virtualizer = useVirtualizer({
  get count() { return chatStore.messages.length },
  getScrollElement: () => listRef.value || null,
  estimateSize: () => 80,
  getItemKey: (index: number) => chatStore.messages[index]?.id || index,
  overscan: 5,
  measureElement: (el: Element | null) => el?.getBoundingClientRect().height || 80,
  followOnAppend: true,
})

/** 加载更多历史消息 */
async function loadMore() {
  if (isLoadingMore.value || !convStore.hasMoreMessages || !listRef.value) return
  isLoadingMore.value = true
  prevVirtualHeight.value = virtualizer.value.getTotalSize()
  await convStore.loadMoreMessages()
  await nextTick()
  // 保持滚动位置：新内容在顶部，用户看到的区域不变
  if (listRef.value) {
    listRef.value.scrollTop += virtualizer.value.getTotalSize() - prevVirtualHeight.value
  }
  isLoadingMore.value = false
}

/** 滚动到顶部时自动加载更多 */
async function onScroll() {
  if (isLoadingMore.value || !convStore.hasMoreMessages || !listRef.value) return
  if (listRef.value.scrollTop <= 60) {
    await loadMore()
  }
}

/** 自动滚动到底部 */
function scrollToBottom() {
  const count = chatStore.messages.length
  if (count > 0) {
    virtualizer.value.scrollToIndex(count - 1, { align: 'end', behavior: 'auto' })
  }
}

// 监听消息数量变化，自动滚动（排除加载更多场景）
watch(() => chatStore.messages.length, () => {
  if (!isLoadingMore.value) {
    nextTick(scrollToBottom)
  }
})

// 监听流式内容变化，自动滚动（RAF 节流）
watch(() => streamState.value.streamingContent, () => {
  throttledScrollToBottom()
})
watch(() => streamState.value.currentThinkingSteps.length, () => {
  throttledScrollToBottom()
})

// 组件卸载时清理 RAF
onUnmounted(() => {
  if (scrollRafId !== null) cancelAnimationFrame(scrollRafId)
})
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 32px 24px 24px;
}

@media (max-width: 768px) {
  .message-list {
    padding: 24px 12px 16px;
  }
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

@media (max-width: 768px) {
  .streaming-message {
    padding: 0 16px;
  }
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

@media (max-width: 768px) {
  .error-banner {
    padding: 8px 16px;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 200px);
  color: var(--text-muted);
  gap: 12px;
  background: var(--bg-card);
  border-radius: 16px;
  border: var(--border);
  box-shadow: var(--shadow-sm);
  padding: 40px 24px;
  margin: 24px;
}

.empty-icon {
  font-size: 56px;
  opacity: 0.7;
}

.empty-icon-card {
  width: 88px;
  height: 88px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--accent-bg), var(--warm-bg));
  border: 1px solid rgba(198, 123, 92, 0.2);
  box-shadow: var(--shadow-sm);
  margin-bottom: 8px;
}

.empty-state h3 {
  font-size: 22px;
  font-weight: 500;
  color: var(--accent);
}

.empty-state p {
  font-size: 14px;
  max-width: 360px;
  text-align: center;
  line-height: 1.8;
}

/* 加载更多 */
.load-more {
  display: flex;
  justify-content: center;
  padding: 12px 0;
  cursor: pointer;
  user-select: none;
}

.load-more-text {
  font-size: 12px;
  color: var(--text-muted);
  transition: color 0.2s;
}

.load-more:hover .load-more-text {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.load-more--loading {
  cursor: default;
}

.load-more-spinner {
  font-size: 18px;
  color: var(--text-muted);
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}
</style>
