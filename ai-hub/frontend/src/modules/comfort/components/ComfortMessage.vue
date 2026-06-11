<template>
  <div :class="['comfort-message', `role-${message.role}`]">
    <!-- AI 角色消息：头像 + 气泡 -->
    <div v-if="message.role === 'assistant'" class="char-message">
      <CharacterAvatar
        :emoji="character?.avatar_emoji || '🎭'"
        :name="character?.name"
        size="sm"
      />
      <div class="char-bubble">
        <span class="char-name-label">{{ character?.name || '对方' }}</span>
        <MarkdownBody :content="message.content" />
      </div>
    </div>

    <!-- 用户消息 -->
    <UserBubble v-else :content="message.content" />
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage } from '@/modules/chat/types/chat'
import type { ComfortCharacter } from '@/modules/comfort/types/comfort'
import CharacterAvatar from '@/modules/comfort/components/CharacterAvatar.vue'
import MarkdownBody from '@/shared/components/message/MarkdownBody.vue'
import UserBubble from '@/shared/components/message/UserBubble.vue'

defineProps<{
  message: ChatMessage
  character: ComfortCharacter | null
}>()
</script>

<style scoped>
.comfort-message {
  display: flex;
  max-width: 768px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px;
}

@media (max-width: 768px) {
  .comfort-message {
    padding: 0 16px;
  }
}

.role-assistant {
  justify-content: flex-start;
}

.role-user {
  justify-content: flex-end;
}

/* 角色消息：头像 + 气泡 */
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
  letter-spacing: 0.02em;
}

/* 消息间距 */
.comfort-message + .comfort-message {
  margin-top: 20px;
}
</style>
