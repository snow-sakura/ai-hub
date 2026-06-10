<template>
  <div class="char-avatar" :class="`size-${size}`" :aria-label="name || '角色头像'">
    <span class="avatar-emoji">{{ emoji || '🎭' }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  emoji: string
  name?: string
  size?: 'sm' | 'md' | 'lg'
}>()
</script>

<style scoped>
.char-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 50%;
  background: linear-gradient(
    135deg,
    rgba(198, 123, 92, 0.10),
    rgba(212, 165, 116, 0.10)
  );
  border: 2px solid rgba(180, 150, 120, 0.15);
  user-select: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.char-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(198, 123, 92, 0.12);
}

.size-sm {
  width: 32px;
  height: 32px;
}

.size-sm .avatar-emoji {
  font-size: 18px;
}

.size-md {
  width: 40px;
  height: 40px;
}

.size-md .avatar-emoji {
  font-size: 22px;
}

.size-lg {
  width: 56px;
  height: 56px;
}

.size-lg .avatar-emoji {
  font-size: 32px;
}
</style>
