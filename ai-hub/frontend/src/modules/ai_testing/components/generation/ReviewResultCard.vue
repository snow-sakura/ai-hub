<template>
  <n-card v-if="reviewResult" size="small" title="⭐ AI 评审结果" class="review-card">
    <!-- 评审摘要 -->
    <n-text v-if="reviewResult.summary" depth="2" style="font-size: 13px; display: block; margin-bottom: 16px;">
      {{ reviewResult.summary }}
    </n-text>

    <!-- 7 维度评分 -->
    <div class="dimension-grid">
      <div
        v-for="(dim, key) in reviewResult.dimensions"
        :key="key"
        class="dimension-item"
      >
        <div class="dimension-header">
          <span class="dimension-label">{{ dimLabel(key) }}</span>
          <span
            class="dimension-score"
            :style="{ color: scoreColor(dim.score) }"
          >{{ dim.score }}/10</span>
        </div>
        <div class="dimension-bar-bg">
          <div
            class="dimension-bar-fill"
            :style="{ width: (dim.score / 10 * 100) + '%', background: scoreColor(dim.score) }"
          />
        </div>
        <n-text v-if="dim.comment" depth="3" style="font-size: 11px; margin-top: 2px; display: block;">
          {{ dim.comment }}
        </n-text>
      </div>
    </div>

    <!-- 综合评分 -->
    <n-divider style="margin: 12px 0;" />
    <div class="overall-row">
      <span class="overall-label">综合评分</span>
      <span class="overall-score" :style="{ color: scoreColor(reviewResult.overall_score) }">
        {{ reviewResult.overall_score }}/10
      </span>
      <n-tag
        :type="reviewResult.review_passed ? 'success' : 'warning'"
        size="small"
        round
      >
        {{ reviewResult.review_passed ? '✅ 评审通过' : '⚠️ 需修订' }}
      </n-tag>
    </div>

    <!-- 问题列表 -->
    <template v-if="reviewResult.issues?.length">
      <n-divider style="margin: 12px 0;" />
      <div class="section-title">发现的问题</div>
      <n-space vertical :size="6" style="margin-top: 8px;">
        <n-alert
          v-for="(issue, i) in reviewResult.issues"
          :key="i"
          :type="issue.severity === 'critical' ? 'error' : issue.severity === 'major' ? 'warning' : 'info'"
          :bordered="false"
          closable
          style="font-size: 13px;"
        >
          <template #header>
            <span style="font-size: 13px;">{{ issue.description }}</span>
          </template>
          <template v-if="issue.affected_cases?.length">
            <n-text depth="3" style="font-size: 12px;">影响用例: {{ issue.affected_cases.join(', ') }}</n-text>
          </template>
        </n-alert>
      </n-space>
    </template>

    <!-- 改进建议 -->
    <template v-if="reviewResult.improvement_suggestions?.length">
      <n-divider style="margin: 12px 0;" />
      <div class="section-title">改进建议</div>
      <n-space vertical :size="4" style="margin-top: 8px;">
        <n-checkbox
          v-for="(s, i) in reviewResult.improvement_suggestions"
          :key="i"
          v-model:checked="selected[i]"
          style="font-size: 13px; padding: 4px 0; align-items: flex-start;"
        >
          {{ s }}
        </n-checkbox>
      </n-space>

      <!-- 重新生成按钮 -->
      <n-button
        :disabled="selectedCount === 0"
        size="small"
        type="warning"
        style="margin-top: 12px;"
        @click="handleRegen"
      >
        按选中建议重新生成（已选 {{ selectedCount }} 条）
      </n-button>
    </template>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { ReviewEvent } from '@/modules/ai_testing/composables/useGenerationStream'

const props = defineProps<{
  reviewResult: ReviewEvent | null
}>()

const emit = defineEmits<{
  regenerate: [suggestions: string[]]
}>()

const DIM_LABELS: Record<string, string> = {
  coverage: '覆盖率',
  completeness: '完整性',
  accuracy: '准确性',
  priority: '优先级分配',
  edge_cases: '边界覆盖',
  clarity: '清晰度',
  maintainability: '可维护性',
}

function dimLabel(key: string | number): string {
  return DIM_LABELS[String(key)] || String(key)
}

function scoreColor(score: number): string {
  if (score >= 8) return '#22a163'
  if (score >= 6) return '#d4874a'
  return '#d03050'
}

const selected = ref<boolean[]>([])

watch(() => props.reviewResult, (val) => {
  if (val?.improvement_suggestions) {
    selected.value = val.improvement_suggestions.map(() => false)
  } else {
    selected.value = []
  }
}, { immediate: true })

const selectedCount = computed(() => selected.value.filter(Boolean).length)

function handleRegen() {
  const suggestions = (props.reviewResult?.improvement_suggestions || [])
    .filter((_, i) => selected.value[i])
  if (suggestions.length > 0) {
    emit('regenerate', suggestions)
  }
}
</script>

<style scoped>
.review-card {
  border: 1px solid #e8e4e0;
}

.dimension-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.dimension-item {
  display: flex;
  flex-direction: column;
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.dimension-label {
  font-size: 12px;
  color: #5C4A38;
  font-weight: 500;
}

.dimension-score {
  font-size: 12px;
  font-weight: 600;
}

.dimension-bar-bg {
  height: 4px;
  background: #e8e4e0;
  border-radius: 2px;
  overflow: hidden;
}

.dimension-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s;
}

.overall-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.overall-label {
  font-size: 14px;
  font-weight: 600;
  color: #5C4A38;
}

.overall-score {
  font-size: 18px;
  font-weight: 700;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #5C4A38;
}

@media (max-width: 600px) {
  .dimension-grid {
    grid-template-columns: 1fr;
  }
}
</style>
