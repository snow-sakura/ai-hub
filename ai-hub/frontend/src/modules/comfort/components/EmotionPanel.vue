<template>
  <div class="emotion-panel" :class="panelClass">
    <!-- 顶部行：角色信息 + 情绪显示 -->
    <div class="panel-header">
      <CharacterAvatar
        :emoji="character?.avatar_emoji || '🎭'"
        :name="character?.name"
        size="sm"
      />
      <div class="header-text">
        <span class="char-name">{{ character?.name || '对方' }}</span>
        <span class="char-identity">{{ character?.identity || '' }}</span>
      </div>
      <div v-if="emotion" class="emotion-display" :class="{ 'animate-pulse': isAnimating }">
        <span class="emotion-emoji">{{ emotion.emoji }}</span>
        <span class="emotion-label">{{ emotionLabel }}</span>
      </div>
    </div>

    <!-- 原谅值进度条 -->
    <div class="forgiveness-section">
      <div class="forgiveness-header">
        <span class="forgiveness-label">原谅值</span>
        <div class="forgiveness-value-group">
          <span class="forgiveness-value" :class="trendClass">
            {{ displayValue }}%
          </span>
          <span v-if="deltaText" class="forgiveness-delta" :class="trendClass">
            {{ deltaText }}
          </span>
        </div>
      </div>
      <div class="forgiveness-track">
        <div
          class="forgiveness-fill"
          :style="{ width: `${displayValue}%`, background: barColor }"
        />
      </div>
      <div v-if="forgivenessData?.reason" class="forgiveness-reason">
        {{ forgivenessData.reason }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { EmotionData, ForgivenessData, ComfortCharacter } from '@/modules/comfort/types/comfort'
import CharacterAvatar from '@/modules/comfort/components/CharacterAvatar.vue'

const props = defineProps<{
  forgiveness: number
  forgivenessData: ForgivenessData | null
  emotion: EmotionData | null
  character: ComfortCharacter | null
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

const isAnimating = ref(false)

const emotionLabel = computed(() => {
  if (!props.emotion) return ''
  return emotionNames[props.emotion.label] || props.emotion.label
})

const displayValue = computed(() => Math.round(props.forgiveness))

const trendClass = computed(() => {
  if (props.forgivenessData?.trend === 'up') return 'trend-up'
  if (props.forgivenessData?.trend === 'down') return 'trend-down'
  return ''
})

const deltaText = computed(() => {
  const delta = props.forgivenessData?.delta
  if (!delta) return ''
  const sign = delta > 0 ? '+' : ''
  return `${sign}${delta.toFixed(1)}`
})

const barColor = computed(() => {
  const v = props.forgiveness
  if (v >= 70) return 'linear-gradient(90deg, #7BA87D, #9BC49D)'
  if (v >= 40) return 'linear-gradient(90deg, #D4A574, #E8C49A)'
  return 'linear-gradient(90deg, #D4745C, #E89A8A)'
})

const panelClass = computed(() => {
  if (!props.forgivenessData) return ''
  if (props.forgivenessData.trend === 'down') return 'panel-shake'
  if (props.forgivenessData.trend === 'up') return 'panel-glow'
  return ''
})

/** 情绪变化时触发动画 */
let _emotionTimer: ReturnType<typeof setTimeout> | null = null
watch(() => props.emotion, () => {
  isAnimating.value = true
  if (_emotionTimer) clearTimeout(_emotionTimer)
  _emotionTimer = setTimeout(() => {
    isAnimating.value = false
    _emotionTimer = null
  }, 600)
})

onUnmounted(() => {
  if (_emotionTimer) clearTimeout(_emotionTimer)
})
</script>

<style scoped>
.emotion-panel {
  padding: 14px 18px;
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 14px;
  margin: 12px 20px 0;
  box-shadow: 0 1px 4px rgba(60, 40, 20, 0.03);
  transition: border-color 0.4s ease, box-shadow 0.4s ease;
  flex-shrink: 0;
}

.panel-glow {
  border-color: rgba(123, 168, 125, 0.3);
  box-shadow: 0 0 0 2px rgba(123, 168, 125, 0.08), inset 0 0 0 1px rgba(123, 168, 125, 0.15);
}

.panel-shake {
  animation: shake 0.4s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0) rotate(0deg); }
  20% { transform: translateX(-2px) rotate(-0.5deg); }
  40% { transform: translateX(2px) rotate(0.5deg); }
  60% { transform: translateX(-1px) rotate(-0.25deg); }
  80% { transform: translateX(1px) rotate(0.25deg); }
}

/* 头部行 */
.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.char-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
}

.char-identity {
  font-size: 11px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 情绪显示 */
.emotion-display {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(198, 123, 92, 0.06);
  border-radius: 999px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.animate-pulse {
  animation: emotionPop 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes emotionPop {
  0% { transform: scale(0.85); opacity: 0.6; }
  40% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

.emotion-emoji {
  font-size: 18px;
  line-height: 1;
}

.emotion-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* 原谅值区域 */
.forgiveness-section {
  margin-top: 10px;
}

.forgiveness-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 5px;
}

.forgiveness-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.forgiveness-value-group {
  margin-left: auto;
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.forgiveness-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  transition: color 0.3s ease, transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.forgiveness-delta {
  font-size: 11px;
  font-weight: 600;
  transition: color 0.3s ease;
}

.trend-up {
  color: #7BA87D;
}

.trend-down {
  color: #D4745C;
}

.forgiveness-track {
  height: 6px;
  background: rgba(180, 150, 120, 0.08);
  border-radius: 3px;
  overflow: hidden;
}

.forgiveness-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1), background 0.5s ease;
}

.forgiveness-reason {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
  line-height: 1.4;
}
</style>
