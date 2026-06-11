<template>
  <n-layout-content content-style="padding: 24px;">
    <n-space vertical :size="16" style="max-width: 960px; margin: 0 auto;">

      <!-- 页头 -->
      <n-page-header :title="isHistoryView ? '查看生成记录' : 'AI 用例助手'" @back="$router.back()">
        <template #extra>
          <n-space>
            <n-button quaternary size="small" @click="showSetupGuide = true" title="配置检查">
              ⚙️
            </n-button>
            <n-button quaternary size="small" @click="$router.push('/ai-testing/settings')" title="设置">
              📋
            </n-button>
          </n-space>
        </template>
        <template #subtitle>
          <n-text depth="3">
            {{ isHistoryView ? '查看历史 AI 生成任务的完整记录' : '输入需求文档 → AI 自动分析 → 评审 → 修订 → 高质量测试用例' }}
          </n-text>
        </template>
      </n-page-header>

      <!-- 历史记录提示 -->
      <n-alert v-if="isHistoryView" type="info" :bordered="false" closable>
        <template #header>查看历史生成记录 — 任务 ID: {{ currentTaskId }}</template>
        当前为只读模式。
      </n-alert>

      <!-- ═══════════ Zone 1: 需求输入 ═══════════ -->
      <n-card size="small" title="📄 需求输入" :collapsible="true" :default-collapsed="isStreaming || isDone">
        <n-space vertical :size="12">
          <n-space align="center" :size="12">
            <n-text style="min-width: 80px; font-size: 13px;">所属项目</n-text>
            <n-select
              v-model:value="selectedProjectId"
              :options="projectOptions"
              placeholder="选择项目（可选）"
              clearable
              style="width: 280px;"
              size="small"
              :disabled="isStreaming || isHistoryView"
            />
          </n-space>

          <RequirementInput ref="requirementInputRef" :disabled="isStreaming || isHistoryView" />

          <!-- 操作行 -->
          <n-space align="center" :size="12">
            <n-text style="font-size: 13px;">输出模式</n-text>
            <n-radio-group v-model:value="outputMode" size="small" :disabled="isStreaming">
              <n-radio-button value="stream">流式输出</n-radio-button>
              <n-radio-button value="complete">完整输出</n-radio-button>
            </n-radio-group>

            <n-button
              type="primary"
              :loading="isLoading"
              :disabled="!canGenerate || isStreaming"
              @click="handleGenerate"
            >
              开始生成
            </n-button>

            <n-button
              v-if="isStreaming"
              type="error"
              ghost
              size="small"
              @click="handleStop"
            >
              停止
            </n-button>
          </n-space>
        </n-space>
      </n-card>

      <!-- ═══════════ Zone 2: 生成进度 ═══════════ -->
      <n-card
        v-if="isStreaming || isDone || streamError"
        size="small"
        title="🚀 生成进度"
      >
        <GenerationProgress
          :task-id="currentTaskId"
          :is-streaming="isStreaming"
          :is-done="isDone"
          :current-stage="currentStage"
          :streaming-content="streamingContent"
          :stage-contents="{ ...stageContents }"
          :review-result="reviewResult"
          :progress="progress"
          :error-info="errorInfo"
          :stream-error="streamError"
          @regenerate="handleRegenerate"
        />
      </n-card>

      <!-- ═══════════ Zone 3: 生成结果 ═══════════ -->
      <n-card
        v-if="isDone"
        size="small"
        title="📊 生成结果"
      >
        <GenerationResult
          :task-id="currentTaskId"
          :is-done="isDone"
          :done-result="doneResult"
          :is-saving="isSaving"
          :is-exporting="isExporting"
          :saved-count="savedCount"
          :review-result="reviewResult"
          :stage-contents="{ ...stageContents }"
          @save="handleSaveCases"
          @export="handleExportExcel"
          @reset="handleReset"
          @regenerate="handleRegenerate"
        />
      </n-card>

    </n-space>

    <ConfigGuideModal v-model:show="showSetupGuide" />
  </n-layout-content>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useGenerationStore } from '@/modules/ai_testing/stores/generation'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import { useGenerationStream } from '@/modules/ai_testing/composables/useGenerationStream'
import RequirementInput from '@/modules/ai_testing/components/generation/RequirementInput.vue'
import GenerationProgress from '@/modules/ai_testing/components/generation/GenerationProgress.vue'
import GenerationResult from '@/modules/ai_testing/components/generation/GenerationResult.vue'
import ConfigGuideModal from '@/modules/ai_testing/components/generation/ConfigGuideModal.vue'
import type { ConfigItem, OutputMode } from '@/modules/ai_testing/types/generation'

const router = useRouter()
const route = useRoute()
const message = useMessage()
const store = useGenerationStore()
const projectStore = useProjectStore()

const {
  isStreaming,
  isDone,
  currentStage,
  streamingContent,
  stageContents,
  reviewResult,
  progress,
  doneResult,
  errorInfo,
  streamError,
  start,
  stop,
  loadFromExisting,
} = useGenerationStream()

const isHistoryView = ref(false)
const requirementInputRef = ref<InstanceType<typeof RequirementInput> | null>(null)
const isLoading = ref(false)
const isSaving = ref(false)
const isExporting = ref(false)
const showSetupGuide = ref(false)
const currentTaskId = ref('')
const selectedProjectId = ref<string | null>(null)
const outputMode = ref<OutputMode>('stream')
const savedCount = ref<number | null>(null)

const projectOptions = computed(() =>
  projectStore.projects.map(p => ({ label: p.name, value: p.id }))
)

const canGenerate = computed(() => {
  const text = requirementInputRef.value?.text || ''
  return text.trim().length >= 10
})

async function handleGenerate() {
  if (!canGenerate.value || isStreaming.value) return
  isLoading.value = true

  const input = requirementInputRef.value
  if (!input) return

  const configItem = store.configItems.find((c: ConfigItem) => c.key === 'model')
  const task = await store.createTask({
    project_id: selectedProjectId.value,
    requirement_title: input.title,
    input_text: input.text,
    model: configItem?.value || '',
    output_mode: outputMode.value,
  })

  if (!task) {
    message.error('创建任务失败，请检查配置')
    isLoading.value = false
    return
  }

  currentTaskId.value = task.id
  isLoading.value = false

  if (outputMode.value === 'complete') {
    await pollCompleteResult(task.id)
  } else {
    start(task.id)
  }
}

async function pollCompleteResult(taskId: string) {
  const api = await import('@/modules/ai_testing/api/generation')
  const maxAttempts = 120
  let attempts = 0

  while (attempts < maxAttempts) {
    attempts++
    await new Promise(r => setTimeout(r, 1000))
    try {
      const res = await api.getGenerationTask(taskId)
      const task = res.data
      if (!task) continue
      if (task.status === 'completed') {
        const resultsRes = await api.getGenerationResults(taskId)
        const results = resultsRes.data || []
        const stageOrder = ['analyze', 'write', 'review', 'revise']
        let finalContent = ''
        let reviewRes = null
        let stageIdx = 0
        for (const stage of stageOrder) {
          const sr = results.find((r: { stage: string }) => r.stage === stage)
          if (!sr) continue
          stageIdx++
          if (stage === 'review') {
            try { reviewRes = JSON.parse(sr.content); reviewResult.value = reviewRes } catch {}
          } else if (stage === 'final') {
            finalContent = sr.content
          } else {
            store.appendStreamContent(sr.content)
            stageContents[stage] = sr.content
            progress.value = { current: stageIdx, total: 4, message: `阶段 ${stage} 完成` }
          }
        }
        if (finalContent) {
          store.appendStreamContent(finalContent)
          stageContents.revise = finalContent
        }
        isDone.value = true
        doneResult.value = {
          task_id: taskId, generated_count: task.generated_count || 0,
          review_passed: reviewRes?.review_passed || false, overall_score: reviewRes?.overall_score || 0,
        }
        progress.value = { current: 4, total: 4, message: '生成完成' }
        store.setCurrentStage('final')
        store.isStreaming = false
        return
      }
      if (task.status === 'failed') {
        errorInfo.value = { code: 'TASK_FAILED', message: task.error_message || '生成失败' }
        store.streamError = task.error_message || '任务执行失败'
        store.isStreaming = false
        return
      }
      progress.value = { current: Math.min(attempts, 4), total: 4, message: '生成中...' }
    } catch (e) {
      console.error('轮询失败:', e)
    }
  }
  errorInfo.value = { code: 'TIMEOUT', message: '等待生成结果超时' }
  store.streamError = '等待生成结果超时'
  store.isStreaming = false
}

function handleStop() {
  stop()
  message.info('已停止生成')
}

function parseTestCaseFields(content: string): Array<Record<string, unknown>> {
  const cases: Array<Record<string, unknown>> = []
  const blocks = content.split(/\n-{3,}\n/)
  for (const block of blocks) {
    if (!block.trim()) continue
    const titleMatch = block.match(/\*\*标题\*\*\s*:\s*(.+)/)
    if (!titleMatch) continue
    const title = titleMatch[1].trim()
    const priorityRaw = block.match(/\*\*优先级\*\*\s*:\s*(.+)/)
    const priority = priorityRaw ? priorityRaw[1].trim().toUpperCase() : 'P2'
    const pVal = ['P0', 'P1', 'P2', 'P3'].includes(priority) ? priority : 'P2'
    const typeMatch = block.match(/\*\*用例类型\*\*\s*:\s*(.+)/)
    let caseType = typeMatch ? typeMatch[1].trim() : 'functional'
    const validTypes = ['functional', 'performance', 'security', 'compatibility', 'ui', 'api']
    if (!validTypes.includes(caseType)) caseType = 'functional'
    const preMatch = block.match(/\*\*前置条件\*\*\s*:\s*(.*?)(?=\n\*\*|$)/)
    const stepsMatch = block.match(/\*\*测试步骤\*\*\s*:\s*([\s\S]*?)(?=\n\*\*|$)/)
    const erMatch = block.match(/\*\*预期结果\*\*\s*:\s*([\s\S]*?)(?=\n\*\*|$)/)
    const tagsMatch = block.match(/\*\*标签\*\*\s*:\s*(.+)/)
    cases.push({
      title, priority: pVal, case_type: caseType,
      preconditions: preMatch?.[1].trim() || '',
      steps: stepsMatch?.[1].trim() || '',
      expected_results: erMatch?.[1].trim() || '',
      tags: tagsMatch ? tagsMatch[1].split(',').map(t => t.trim()).filter(Boolean) : ['ai-generated'],
    })
  }
  return cases
}

async function handleSaveCases() {
  if (!doneResult.value) return
  isSaving.value = true
  const finalContent = stageContents.revise || stageContents.write || streamingContent.value
  let parsedCases = parseTestCaseFields(finalContent)
  if (parsedCases.length === 0) {
    parsedCases.push({
      title: `AI 生成 - ${(requirementInputRef.value?.title || '').slice(0, 30) || '测试用例'}`,
      preconditions: '', steps: finalContent, expected_results: '',
      priority: 'P1', case_type: 'functional', tags: ['ai-generated'],
    })
  }
  const count = await store.saveCases(doneResult.value.task_id, selectedProjectId.value, parsedCases)
  isSaving.value = false
  if (count > 0) {
    savedCount.value = count
    message.success(`已保存 ${count} 条用例到用例库`)
    try {
      const { updateTaskStatus } = await import('@/modules/ai_testing/api/generation')
      await updateTaskStatus(doneResult.value.task_id, 'completed')
    } catch {}
  } else {
    message.warning('保存失败')
  }
}

async function handleExportExcel() {
  if (!doneResult.value?.task_id) { message.warning('无结果可导出'); return }
  isExporting.value = true
  try {
    const url = `/api/v1/testing/generate/${doneResult.value.task_id}/export`
    const response = await fetch(url)
    if (!response.ok) throw new Error(`导出失败: ${response.status}`)
    const blob = await response.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `ai_generated_cases_${Date.now()}.xlsx`
    a.click()
    URL.revokeObjectURL(a.href)
    message.success('已下载 Excel')
  } catch (e) {
    message.error('导出失败')
  }
  isExporting.value = false
}

async function handleRegenerate(suggestions: string[]) {
  if (suggestions.length === 0) return
  const input = requirementInputRef.value
  if (!input) return
  message.info(`正在按 ${suggestions.length} 条建议重新生成...`)
  const configItem = store.configItems.find((c: ConfigItem) => c.key === 'model')
  const task = await store.createTask({
    project_id: selectedProjectId.value, requirement_title: input.title,
    input_text: input.text, model: configItem?.value || '', output_mode: outputMode.value,
  })
  if (!task) { message.error('创建任务失败'); return }
  currentTaskId.value = task.id
  start(task.id, suggestions)
}

function handleReset() {
  currentTaskId.value = ''
  savedCount.value = null
  store.reset()
}

async function loadExistingTask(taskId: string) {
  isLoading.value = true
  try {
    const { getGenerationTask, getGenerationResults } = await import('@/modules/ai_testing/api/generation')
    const [taskRes, resultsRes] = await Promise.all([getGenerationTask(taskId), getGenerationResults(taskId)])
    const task = taskRes.data
    const results = resultsRes.data || []
    if (!task) { message.error('任务不存在'); return }
    currentTaskId.value = task.id
    selectedProjectId.value = task.project_id
    if (requirementInputRef.value) {
      requirementInputRef.value.title = task.requirement_title || ''
      requirementInputRef.value.text = task.input_text || ''
    }
    loadFromExisting(task, results)
    isHistoryView.value = true
  } catch (e) {
    message.error('加载历史记录失败')
  } finally { isLoading.value = false }
}

onMounted(() => {
  projectStore.fetchProjects()
  store.fetchConfig()
  const taskId = route.query.task_id as string | undefined
  if (taskId) loadExistingTask(taskId)
})
</script>
