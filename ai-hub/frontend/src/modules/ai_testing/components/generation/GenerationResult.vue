<template>
  <n-space vertical :size="16">
    <n-card v-if="isDone && doneResult" size="small" title="✅ 生成完成">
      <ResultOperations
        :task-id="taskId"
        :done-result="doneResult"
        :is-saving="isSaving"
        :is-exporting="isExporting"
        :saved-count="savedCount ?? null"
        :review-result="reviewResult"
        @save="$emit('save')"
        @export="$emit('export')"
        @reset="$emit('reset')"
      />
    </n-card>

    <!-- 评审结果卡片（结果页也展示） -->
    <ReviewResultCard
      v-if="reviewResult"
      :review-result="reviewResult"
      @regenerate="(s) => $emit('regenerate', s)"
    />

    <!-- 最终内容预览 -->
    <n-card v-if="finalContent" size="small" title="最终输出">
      <n-scrollbar style="max-height: 500px;">
        <pre class="final-content">{{ finalContent }}</pre>
      </n-scrollbar>
    </n-card>
  </n-space>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DoneEvent, ReviewEvent } from '@/modules/ai_testing/composables/useGenerationStream'
import ReviewResultCard from '@/modules/ai_testing/components/generation/ReviewResultCard.vue'
import ResultOperations from '@/modules/ai_testing/components/generation/ResultOperations.vue'

const props = defineProps<{
  taskId: string | null
  isDone: boolean
  doneResult: DoneEvent | null
  isSaving: boolean
  isExporting: boolean
  savedCount?: number | null
  reviewResult: ReviewEvent | null
  stageContents?: Record<string, string>
}>()

defineEmits<{
  save: []
  export: []
  reset: []
  regenerate: [suggestions: string[]]
}>()

const finalContent = computed(() => {
  if (!props.stageContents) return ''
  return props.stageContents.revise || props.stageContents.write || ''
})
</script>

<style scoped>
.final-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  font-family: 'SF Mono', 'Fira Code', monospace;
}
</style>
