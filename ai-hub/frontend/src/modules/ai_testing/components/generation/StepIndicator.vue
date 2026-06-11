<template>
  <div class="step-indicator">
    <div
      v-for="(step, idx) in steps"
      :key="step.stage"
      class="step-item"
      :class="{ active: idx <= currentIndex, current: idx === currentIndex }"
    >
      <div class="step-circle">
        <span v-if="idx < currentIndex" class="step-check">✓</span>
        <span v-else>{{ idx + 1 }}</span>
      </div>
      <div class="step-content">
        <div class="step-title">{{ step.label }}</div>
        <div class="step-desc">{{ step.desc }}</div>
      </div>
      <div v-if="idx < steps.length - 1" class="step-connector" :class="{ active: idx < currentIndex }" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { GenerationStage } from '@/modules/ai_testing/types/generation'

const props = defineProps<{
  currentStage: GenerationStage | null
  isDone: boolean
}>()

const STEPS = [
  { stage: 'analyze' as const, label: '需求分析', desc: '提取功能点与场景' },
  { stage: 'write' as const, label: '用例编写', desc: '生成结构化用例' },
  { stage: 'review' as const, label: 'AI 评审', desc: '质量评分与反馈' },
  { stage: 'revise' as const, label: '用例修订', desc: '根据反馈优化' },
]

const STAGE_ORDER: GenerationStage[] = ['analyze', 'write', 'review', 'revise']

const steps = STEPS

const currentIndex = computed(() => {
  if (props.isDone) return 4
  if (!props.currentStage) return -1
  return STAGE_ORDER.indexOf(props.currentStage)
})
</script>

<style scoped>
.step-indicator {
  display: flex;
  align-items: flex-start;
  gap: 0;
  width: 100%;
}

.step-item {
  display: flex;
  align-items: center;
  flex: 1;
  position: relative;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  background: #e8e4e0;
  color: #7A6855;
  flex-shrink: 0;
  transition: all 0.3s;
}

.step-item.active .step-circle {
  background: #C67B5C;
  color: #fff;
}

.step-item.current .step-circle {
  box-shadow: 0 0 0 3px rgba(198, 123, 92, 0.3);
}

.step-check {
  font-size: 16px;
}

.step-content {
  margin-left: 10px;
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: #5C4A38;
  white-space: nowrap;
}

.step-item:not(.active) .step-title {
  color: #7A6855;
}

.step-desc {
  font-size: 11px;
  color: #999;
  white-space: nowrap;
}

.step-connector {
  flex: 1;
  height: 2px;
  background: #e8e4e0;
  margin: 0 12px;
  margin-bottom: 16px;
  transition: background 0.3s;
}

.step-connector.active {
  background: #C67B5C;
}

@media (max-width: 768px) {
  .step-desc {
    display: none;
  }
  .step-content {
    margin-left: 6px;
  }
  .step-title {
    font-size: 12px;
  }
  .step-connector {
    margin: 0 6px;
  }
}
</style>
