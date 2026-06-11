<template>
  <n-space vertical :size="16">
    <!-- 任务信息 -->
    <n-space v-if="taskId" :size="12" align="center">
      <n-text depth="3" style="font-size: 12px;">任务 ID：</n-text>
      <n-text style="font-size: 12px; font-family: monospace;">{{ taskId }}</n-text>
      <n-tag
        :type="isDone ? 'success' : isStreaming ? 'info' : 'default'"
        size="tiny"
        round
      >
        {{ isDone ? '完成' : isStreaming ? '运行中' : '等待' }}
      </n-tag>
    </n-space>

    <!-- StepIndicator 4 步进度 -->
    <StepIndicator :current-stage="currentStage" :is-done="isDone" />

    <!-- 进度条 -->
    <n-progress
      v-if="progress.total > 0"
      type="line"
      :percentage="Math.round(progress.current / progress.total * 100)"
      :indicator-placement="'inside'"
      :status="isDone ? 'success' : errorInfo ? 'error' : undefined"
    >
      {{ progress.message }}
    </n-progress>

    <!-- 2×2 阶段内容网格 -->
    <div class="stage-grid">
      <div v-if="stageContents.analyze || isStageReached('analyze')" class="stage-card">
        <n-card size="small" :segmented="{ content: true }">
          <template #header>
            <div class="card-header" @click="toggleCollapse('analyze')">
              <div class="card-header-left">
                <span class="collapse-icon">{{ collapsed.analyze ? '▶' : '▼' }}</span>
                <span class="card-title">🔍 需求分析</span>
              </div>
              <div class="card-header-right">
                <n-tag v-if="isStageActive('analyze')" type="info" size="tiny" round>生成中...</n-tag>
                <n-tag v-else-if="isStageDone('analyze')" type="success" size="tiny" round>完成</n-tag>
              </div>
            </div>
          </template>
          <n-scrollbar v-if="!collapsed.analyze" style="max-height: 400px;">
            <pre class="stage-content">{{ stageContents.analyze || '' }}<span v-if="isStageActive('analyze')" class="cursor-blink">|</span></pre>
          </n-scrollbar>
        </n-card>
      </div>

      <div v-if="stageContents.write || isStageReached('write')" class="stage-card">
        <n-card size="small" :segmented="{ content: true }">
          <template #header>
            <div class="card-header" @click="toggleCollapse('write')">
              <div class="card-header-left">
                <span class="collapse-icon">{{ collapsed.write ? '▶' : '▼' }}</span>
                <span class="card-title">✍️ 用例编写</span>
              </div>
              <div class="card-header-right">
                <n-tag v-if="isStageActive('write')" type="info" size="tiny" round>生成中...</n-tag>
                <n-tag v-else-if="isStageDone('write')" type="success" size="tiny" round>完成</n-tag>
              </div>
            </div>
          </template>
          <n-scrollbar v-if="!collapsed.write" style="max-height: 400px;">
            <pre class="stage-content">{{ stageContents.write || '' }}<span v-if="isStageActive('write')" class="cursor-blink">|</span></pre>
          </n-scrollbar>
        </n-card>
      </div>

      <!-- AI 评审 → 使用 ReviewResultCard 组件 -->
      <div v-if="reviewResult || isStageReached('review')" class="stage-card">
        <ReviewResultCard
          :review-result="reviewResult"
          @regenerate="(s) => $emit('regenerate', s)"
        />
      </div>

      <div v-if="stageContents.revise || isStageReached('revise')" class="stage-card">
        <n-card size="small" :segmented="{ content: true }">
          <template #header>
            <div class="card-header" @click="toggleCollapse('revise')">
              <div class="card-header-left">
                <span class="collapse-icon">{{ collapsed.revise ? '▶' : '▼' }}</span>
                <span class="card-title">🔧 用例修订</span>
              </div>
              <div class="card-header-right">
                <n-tag v-if="isStageActive('revise')" type="info" size="tiny" round>修订中...</n-tag>
                <n-tag v-else-if="isStageDone('revise')" type="success" size="tiny" round>完成</n-tag>
              </div>
            </div>
          </template>
          <n-scrollbar v-if="!collapsed.revise" style="max-height: 400px;">
            <pre class="stage-content">{{ stageContents.revise || '' }}<span v-if="isStageActive('revise')" class="cursor-blink">|</span></pre>
          </n-scrollbar>
        </n-card>
      </div>
    </div>

    <!-- 错误展示 -->
    <n-alert
      v-if="streamError"
      type="error"
      :title="errorInfo?.code || '错误'"
      :bordered="false"
    >
      {{ streamError }}
    </n-alert>
  </n-space>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import type { GenerationStage } from '@/modules/ai_testing/types/generation'
import type { ReviewEvent, ErrorEvent } from '@/modules/ai_testing/composables/useGenerationStream'
import StepIndicator from '@/modules/ai_testing/components/generation/StepIndicator.vue'
import ReviewResultCard from '@/modules/ai_testing/components/generation/ReviewResultCard.vue'

const props = defineProps<{
  taskId: string
  isStreaming: boolean
  isDone: boolean
  currentStage: GenerationStage | null
  streamingContent: string
  stageContents: Record<string, string>
  reviewResult: ReviewEvent | null
  progress: { current: number; total: number; message: string }
  errorInfo: ErrorEvent | null
  streamError: string | null
}>()

defineEmits<{
  regenerate: [suggestions: string[]]
}>()

const STAGE_ORDER: GenerationStage[] = ['analyze', 'write', 'review', 'revise']
const STAGE_INDEX: Record<string, number> = { analyze: 0, write: 1, review: 2, revise: 3 }

function isStageReached(stage: string): boolean {
  if (!props.currentStage && !props.isDone) return false
  return STAGE_INDEX[props.currentStage || 'revise'] >= STAGE_INDEX[stage]
}

function isStageActive(stage: string): boolean {
  if (!props.isStreaming || !props.currentStage) return false
  return props.currentStage === stage
}

function isStageDone(stage: string): boolean {
  if (!props.stageContents[stage]) return false
  if (props.isStreaming && props.currentStage === stage) return false
  return true
}

const collapsed = reactive<Record<string, boolean>>({
  analyze: false, write: false, review: false, revise: false,
})

function toggleCollapse(stage: string) {
  collapsed[stage] = !collapsed[stage]
}
</script>

<style scoped>
.stage-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.stage-card {
  min-width: 0;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}
.card-header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}
.card-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.collapse-icon {
  font-size: 10px;
  color: #999;
  transition: transform 0.2s;
}
.card-title {
  font-size: 14px;
  font-weight: 600;
}
.stage-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.cursor-blink {
  animation: blink 1s infinite;
  color: var(--n-text-color);
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

@media (max-width: 768px) {
  .stage-grid {
    grid-template-columns: 1fr;
  }
}
</style>
