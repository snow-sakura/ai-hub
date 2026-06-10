<template>
  <div class="forgiveness-bar">
    <div class="bar-header">
      <span class="bar-label">原谅值</span>
      <span class="bar-value" :class="trendClass">
        {{ displayValue }}
        <span class="trend-icon">{{ trendIcon }}</span>
      </span>
    </div>
    <div class="bar-track">
      <div
        class="bar-fill"
        :style="{ width: `${displayValue}%`, background: barColor }"
      />
    </div>
    <div v-if="deltaText" class="bar-delta" :class="trendClass">
      {{ deltaText }}
    </div>
    <div v-if="reason" class="bar-reason">{{ reason }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  value: number
  delta?: number
  reason?: string
  trend?: 'up' | 'down' | 'stable'
}>()

const displayValue = computed(() => Math.round(props.value))

const trendClass = computed(() => {
  if (props.trend === 'up') return 'trend-up'
  if (props.trend === 'down') return 'trend-down'
  return ''
})

const trendIcon = computed(() => {
  if (props.trend === 'up') return '↑'
  if (props.trend === 'down') return '↓'
  return '—'
})

const deltaText = computed(() => {
  if (!props.delta) return ''
  const sign = props.delta > 0 ? '+' : ''
  return `${sign}${props.delta.toFixed(1)}`
})

const barColor = computed(() => {
  const v = props.value
  if (v >= 70) return 'linear-gradient(90deg, #7BA87D, #9BC49D)'
  if (v >= 40) return 'linear-gradient(90deg, #D4A574, #E8C49A)'
  return 'linear-gradient(90deg, #D4745C, #E89A8A)'
})
</script>

<style scoped>
.forgiveness-bar {
  padding: 12px 16px;
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid rgba(180, 150, 120, 0.12);
}

.bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.bar-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.bar-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.trend-icon {
  font-size: 12px;
}

.trend-up { color: #7BA87D; }
.trend-down { color: #D4745C; }

.bar-track {
  height: 8px;
  background: rgba(180, 150, 120, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1), background 0.5s ease;
}

.bar-delta {
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
}

.bar-reason {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
  line-height: 1.4;
}
</style>
