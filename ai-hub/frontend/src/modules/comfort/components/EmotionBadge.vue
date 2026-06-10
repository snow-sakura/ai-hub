<template>
  <div v-if="emotion" class="emotion-badge" :class="{ 'animate-in': animate }">
    <span class="emoji">{{ emotion.emoji }}</span>
    <div class="info">
      <span class="label">{{ emotionNames[emotion.label] || emotion.label }}</span>
      <div class="intensity-bar">
        <div class="intensity-fill" :style="{ width: `${emotion.intensity * 100}%` }" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { EmotionData } from '@/modules/comfort/types/comfort'

const props = defineProps<{
  emotion: EmotionData | null
}>()

const emotionNames: Record<string, string> = {
  anger: '愤怒',
  sadness: '悲伤',
  anxiety: '焦虑',
  fatigue: '疲惫',
  calm: '平静',
  joy: '喜悦',
  fear: '恐惧',
}

const animate = ref(false)
watch(() => props.emotion, () => {
  animate.value = true
  setTimeout(() => { animate.value = false }, 600)
})
</script>

<style scoped>
.emotion-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 20px;
  transition: all 0.3s ease;
}

.animate-in {
  animation: pop 0.4s ease;
}

@keyframes pop {
  0% { transform: scale(0.9); opacity: 0.5; }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}

.emoji {
  font-size: 24px;
  line-height: 1;
}

.info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
}

.intensity-bar {
  width: 48px;
  height: 4px;
  background: rgba(180, 150, 120, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.intensity-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 2px;
  transition: width 0.5s ease;
}
</style>
