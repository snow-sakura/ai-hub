<template>
  <div class="comfort-message-list" ref="listRef">
    <!-- 空状态：角色专属问候 -->
    <div v-if="isEmpty" class="comfort-empty">
      <div class="empty-card">
        <CharacterAvatar
          :emoji="comfortStore.selectedCharacter?.avatar_emoji || '🎭'"
          :name="comfortStore.selectedCharacter?.name"
          size="lg"
        />
        <h3 class="empty-name">{{ comfortStore.selectedCharacter?.name || '对方' }}</h3>
        <span class="empty-identity">
          {{ comfortStore.selectedCharacter?.identity || '' }}
        </span>
        <p class="empty-backstory">
          {{ comfortStore.selectedCharacter?.backstory || '' }}
        </p>
        <div class="empty-hint">
          <span class="hint-icon">💬</span>
          <span>说点什么来安慰 TA 吧</span>
        </div>
      </div>
    </div>

    <!-- 历史消息 -->
    <transition-group name="slide-up">
      <ComfortMessage
        v-for="msg in comfortStore.messages"
        :key="msg.id"
        :message="msg"
        :character="comfortStore.selectedCharacter"
      />
    </transition-group>

    <!-- 流式消息（仅渲染内容，无 thinking/tool） -->
    <div v-if="comfortStore.isStreaming" class="streaming-area">
      <!-- 有内容：角色头像 + 气泡 -->
      <div v-if="comfortStore.streamingContent" class="char-message streaming-msg">
        <CharacterAvatar
          :emoji="comfortStore.selectedCharacter?.avatar_emoji || '🎭'"
          :name="comfortStore.selectedCharacter?.name"
          size="sm"
        />
        <div class="char-bubble">
          <span class="char-name-label">
            {{ comfortStore.selectedCharacter?.name || '对方' }}
          </span>
          <div class="streaming-text">{{ comfortStore.streamingContent }}</div>
          <span class="streaming-cursor" />
        </div>
      </div>

      <!-- 无内容：正在输入指示器 -->
      <div v-else class="typing-indicator">
        <CharacterAvatar
          :emoji="comfortStore.selectedCharacter?.avatar_emoji || '🎭'"
          :name="comfortStore.selectedCharacter?.name"
          size="sm"
        />
        <div class="typing-bubble">
          <span class="typing-dot" />
          <span class="typing-dot" />
          <span class="typing-dot" />
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="comfortStore.streamError" class="error-banner">
      <n-alert type="error" :title="comfortStore.streamError" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useComfortStore } from '@/modules/comfort/stores/comfort'
import ComfortMessage from '@/modules/comfort/components/ComfortMessage.vue'
import CharacterAvatar from '@/modules/comfort/components/CharacterAvatar.vue'
const comfortStore = useComfortStore()
const listRef = ref<HTMLElement>()

const isEmpty = computed(() =>
  comfortStore.messages.length === 0 && !comfortStore.isStreaming
)

/** 自动滚动到底部 */
function scrollToBottom() {
  nextTick(() => {
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  })
}

watch(() => comfortStore.messages.length, scrollToBottom)
watch(() => comfortStore.streamingContent, scrollToBottom)
</script>

<style scoped>
.comfort-message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0 16px;
  display: flex;
  flex-direction: column;
}

/* 空状态：角色专属问候 */
.comfort-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
}

.empty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
  max-width: 320px;
}

.empty-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.empty-identity {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.empty-backstory {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-muted);
  margin: 4px 0 0;
}

.empty-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--accent);
  font-weight: 500;
  margin-top: 8px;
  opacity: 0.8;
}

.hint-icon {
  font-size: 16px;
}

/* 流式消息区域 */
.streaming-area {
  max-width: 768px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px;
}

.streaming-msg {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 0;
}

.streaming-msg .char-message {
  padding: 0;
}

/* 复用 ComfortMessage 的 char-message / char-bubble 样式 */
.char-message {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  max-width: 85%;
}

.char-bubble {
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 20px;
  border-top-left-radius: 6px;
  padding: 12px 16px;
  box-shadow: 0 1px 4px rgba(60, 40, 20, 0.04);
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-primary);
  min-width: 0;
}

.char-name-label {
  display: block;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.streaming-cursor {
  display: inline-block;
  width: 2px;
  height: 16px;
  background: var(--accent);
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: blink 0.8s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 正在输入指示器 */
.typing-indicator {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  max-width: 768px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px;
}

.typing-bubble {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 20px;
  border-top-left-radius: 6px;
  padding: 14px 18px;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: typingBounce 1.2s ease-in-out infinite;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingBounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

/* 错误提示 */
.error-banner {
  max-width: 768px;
  margin: 12px auto;
  width: 100%;
  padding: 0 24px;
}

/* 过渡动画 */
.slide-up-enter-active {
  transition: all 0.3s ease-out;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
</style>
