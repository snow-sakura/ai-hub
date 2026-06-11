<template>
  <n-space vertical :size="10">
    <!-- 结果统计 -->
    <n-space :size="12" align="center">
      <n-text>共生成
        <n-tag type="success" size="large" style="margin: 0 4px;">
          {{ displayCount }}
        </n-tag>
        条测试用例
      </n-text>
      <n-tag v-if="reviewPassed" type="success" size="small" round>评审通过</n-tag>
      <n-tag v-if="!reviewPassed && reviewResult" type="warning" size="small" round>建议修订后使用</n-tag>
    </n-space>

    <!-- 操作按钮组 -->
    <n-space :size="8" wrap>
      <n-button
        type="primary"
        :loading="isSaving"
        :disabled="isSaved"
        size="small"
        @click="$emit('save')"
      >
        {{ isSaved ? '✅ 已保存' : '💾 保存到用例库' }}
      </n-button>
      <n-button
        :loading="isExporting"
        size="small"
        @click="$emit('export')"
      >
        📥 下载 Excel
      </n-button>
      <n-button
        v-if="taskId"
        size="small"
        quaternary
        @click="viewDetail"
      >
        📋 查看任务详情
      </n-button>
      <n-button
        size="small"
        quaternary
        @click="$emit('reset')"
      >
        🔄 重新生成
      </n-button>
    </n-space>
  </n-space>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { DoneEvent, ReviewEvent } from '@/modules/ai_testing/composables/useGenerationStream'

const props = defineProps<{
  taskId: string | null
  doneResult: DoneEvent | null
  isSaving: boolean
  isExporting: boolean
  savedCount: number | null
  reviewResult: ReviewEvent | null
}>()

defineEmits<{
  save: []
  export: []
  reset: []
}>()

const router = useRouter()

const isSaved = computed(() =>
  props.savedCount !== null && props.savedCount !== undefined
)

const displayCount = computed(() => {
  if (isSaved.value) return props.savedCount
  return props.doneResult?.generated_count || 0
})

const reviewPassed = computed(() => props.doneResult?.review_passed ?? false)

function viewDetail() {
  if (props.taskId) {
    router.push(`/ai-testing/generate/tasks/${props.taskId}`)
  }
}
</script>
