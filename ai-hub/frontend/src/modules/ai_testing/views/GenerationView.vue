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

          <n-space align="center" :size="12">
            <n-text style="min-width: 80px; font-size: 13px;">AI 模型</n-text>
            <n-select
              v-model:value="selectedModel"
              :options="modelOptions"
              placeholder="选择模型"
              style="width: 280px;"
              size="small"
              :disabled="isStreaming"
              filterable
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
          :stage-contents="stageContents"
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
    <SavePreviewModal
      v-model:show="showSavePreview"
      :cases="previewCases"
      :saving="isSaving"
      @save="handleConfirmSave"
    />
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
import SavePreviewModal from '@/modules/ai_testing/components/generation/SavePreviewModal.vue'
import type { OutputMode } from '@/modules/ai_testing/types/generation'
import * as generationApi from '@/modules/ai_testing/api/generation'
import request from '@/shared/api/request'

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
const selectedModel = ref('')
const outputMode = ref<OutputMode>('stream')
const savedCount = ref<number | null>(null)
const showSavePreview = ref(false)
const previewCases = ref<Array<Record<string, unknown>>>([])

const projectOptions = computed(() =>
  projectStore.projects.map(p => ({ label: p.name, value: p.id }))
)

/** 模型选项（按 provider 分组） */
const modelOptions = computed(() => {
  const defaults = store.configDefaults
  if (!defaults?.models || defaults.models.length === 0) return []
  const groups: Record<string, Array<{ label: string; value: string }>> = {}
  for (const m of defaults.models) {
    const key = m.provider
    if (!groups[key]) groups[key] = []
    groups[key].push({ label: m.display_name, value: `${m.provider}:${m.model}` })
  }
  // 转为 n-select 分组格式
  return Object.entries(groups).map(([provider, children]) => ({
    type: 'group',
    label: providerLabels[provider] || provider,
    children,
  }))
})

const providerLabels: Record<string, string> = {
  deepseek: 'DeepSeek',
  openai: 'OpenAI',
  qwen: '通义千问',
  zhipu: '智谱',
  ollama: 'Ollama',
}

const canGenerate = computed(() => {
  const text = requirementInputRef.value?.text || ''
  return text.trim().length >= 10
})

async function handleGenerate() {
  if (!canGenerate.value || isStreaming.value) return
  isLoading.value = true

  const input = requirementInputRef.value
  if (!input) return

  const task = await store.createTask({
    project_id: selectedProjectId.value,
    requirement_title: input.title,
    input_text: input.text,
    model: selectedModel.value,
    output_mode: outputMode.value,
  })

  if (!task || !task.id) {
    message.error('创建任务失败，请检查配置')
    isLoading.value = false
    return
  }

  currentTaskId.value = task.id
  isLoading.value = false

  if (outputMode.value === 'complete') {
    // complete 模式：先触发后端后台执行，再轮询等待结果
    try {
      await generationApi.executeGenerationTask(task.id)
    } catch (e) {
      message.error('启动生成任务失败')
      isLoading.value = false
      return
    }
    await pollCompleteResult(task.id)
  } else {
    start(task.id)
  }
}

async function pollCompleteResult(taskId: string) {
  const maxAttempts = 120
  const maxInterval = 30000
  let attempts = 0

  while (attempts < maxAttempts) {
    attempts++
    // 指数退避：1/2/4/8/.../30s max
    const delay = Math.min(1000 * Math.pow(2, attempts - 1), maxInterval)
    await new Promise(r => setTimeout(r, delay))
    try {
      const res = await generationApi.getGenerationTask(taskId)
      const task = res.data
      if (!task) continue
      if (task.status === 'completed') {
        const resultsRes = await generationApi.getGenerationResults(taskId)
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
            try { reviewRes = JSON.parse(sr.content); reviewResult.value = reviewRes } catch (e) { console.warn('解析评审结果失败:', e) }
          } else {
            store.appendStreamContent(sr.content)
            stageContents[stage] = sr.content
            progress.value = { current: stageIdx, total: 4, message: `阶段 ${stage} 完成` }
          }
        }
        // 单独搜索 final 阶段结果（不在 stageOrder 中）
        const finalResult = results.find((r: { stage: string }) => r.stage === 'final')
        if (finalResult?.content) {
          finalContent = finalResult.content
          store.appendStreamContent(finalContent)
          stageContents.revise = finalContent
        } else if (stageContents.revise) {
          finalContent = stageContents.revise
        } else if (stageContents.write) {
          finalContent = stageContents.write
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

async function handleStop() {
  // 先调用后端取消 API 停止 LangGraph 执行
  if (currentTaskId.value) {
    try {
      await generationApi.cancelGenerationTask(currentTaskId.value)
    } catch (e) {
      console.warn('取消任务 API 调用失败:', e)
    }
  }
  stop()
  message.info('已停止生成')
}

function parseTestCaseFields(content: string): Array<Record<string, unknown>> {
  // 多种 Markdown 块分隔符，按优先级尝试
  const separators = [
    /\n-{3,}\n/, /\n_{3,}\n/, /\n\*{3,}\n/,
    /\n###\s+(?:用例|测试用例|Case)\s*\d*/i,
    /\n##\s+(?:用例|测试用例)\s*\d*/i,
    /\n---\n/,
  ]
  let blocks = [content]
  for (const sep of separators) {
    const split = content.split(sep)
    if (split.length > 1) { blocks = split; break }
  }

  // 多种字段名匹配模式（优先严格匹配，降级到宽松匹配）
  const strictFieldPatterns: Array<[string, RegExp]> = [
    ['title', /\*\*标题\*\*\s*[：:]\s*(.+)/],
    ['priority', /\*\*优先级\*\*\s*[：:]\s*(.+)/],
    ['type', /\*\*用例类型\*\*\s*[：:]\s*(.+)/],
    ['preconditions', /\*\*前置条件\*\*\s*[：:]\s*([\s\S]*?)(?=\n\*\*|$)/],
    ['steps', /\*\*测试步骤\*\*\s*[：:]\s*([\s\S]*?)(?=\n\*\*|$)/],
    ['expected', /\*\*预期结果\*\*\s*[：:]\s*([\s\S]*?)(?=\n\*\*|$)/],
    ['tags', /\*\*标签\*\*\s*[：:]\s*(.+)/],
  ]
  const looseFieldPatterns: Array<[string, RegExp]> = [
    ['title', /#+\s*标题\s*[：:]\s*(.+)/],
    ['title', /标题\s*[：:]\s*(.+)/],
    ['priority', /优先级\s*[：:]\s*(.+)/],
    ['type', /(?:用例)?类型\s*[：:]\s*(.+)/],
    ['preconditions', /前置条件\s*[：:]\s*([\s\S]*?)(?=\n(?:优先级|类型|测试步骤|预期结果|标签|$))/],
    ['steps', /(?:测试)?步骤\s*[：:]\s*([\s\S]*?)(?=\n(?:前置条件|优先级|预期结果|标签|$))/],
    ['expected', /预期结果\s*[：:]\s*([\s\S]*?)(?=\n(?:前置条件|步骤|优先级|标签|$))/],
    ['tags', /标签\s*[：:]\s*(.+)/],
  ]

  function extractField(block: string, field: string, patterns: Array<[string, RegExp]>): string {
    for (const [name, re] of patterns) {
      if (name !== field) continue
      const m = block.match(re)
      if (m) return m[1].trim()
    }
    return ''
  }

  function extractFirst(block: string, patterns: Array<[string, RegExp]>): string {
    for (const [, re] of patterns) {
      const m = block.match(re)
      if (m) return m[1].trim()
    }
    return ''
  }

  const cases: Array<Record<string, unknown>> = []
  for (const block of blocks) {
    if (!block.trim()) continue

    // 先用严格模式提取标题
    let title = extractField(block, 'title', strictFieldPatterns)
    if (!title) title = extractField(block, 'title', looseFieldPatterns)
    // 降级：使用块内第一个加粗文本或首行作为标题
    if (!title) {
      const boldMatch = block.match(/\*\*(.+?)\*\*/)
      if (boldMatch) title = boldMatch[1].trim()
    }
    if (!title) {
      title = block.trim().split('\n')[0].replace(/^[#*\s]+/, '').trim()
    }
    if (!title) continue

    // 提取各字段：先严格后宽松
    const priorityRaw = extractField(block, 'priority', strictFieldPatterns)
      || extractField(block, 'priority', looseFieldPatterns)
    const priority = priorityRaw.toUpperCase()
    const pVal = ['P0', 'P1', 'P2', 'P3'].includes(priority) ? priority : 'P2'

    const typeRaw = extractField(block, 'type', strictFieldPatterns)
      || extractField(block, 'type', looseFieldPatterns)
    const validTypes = ['functional', 'performance', 'security', 'compatibility', 'ui', 'api']
    const caseType = validTypes.includes(typeRaw) ? typeRaw : 'functional'

    const preconditions = extractField(block, 'preconditions', strictFieldPatterns)
      || extractField(block, 'preconditions', looseFieldPatterns)
    const steps = extractField(block, 'steps', strictFieldPatterns)
      || extractField(block, 'steps', looseFieldPatterns)
    const expected = extractField(block, 'expected', strictFieldPatterns)
      || extractField(block, 'expected', looseFieldPatterns)
    const tagsRaw = extractField(block, 'tags', strictFieldPatterns)
      || extractField(block, 'tags', looseFieldPatterns)
    const tags = tagsRaw ? tagsRaw.split(/[,，、]/).map(t => t.trim()).filter(Boolean) : ['ai-generated']

    cases.push({
      title, priority: pVal, case_type: caseType,
      preconditions, steps, expected_results: expected, tags,
    })
  }
  return cases
}

async function handleSaveCases() {
  if (!doneResult.value) return
  const finalContent = stageContents.revise || stageContents.write || streamingContent.value
  let parsedCases = parseTestCaseFields(finalContent)
  if (parsedCases.length === 0) {
    message.warning('未能解析出结构化用例，将保存全部原始内容到一条用例中')
    parsedCases.push({
      title: `AI 生成 - ${(requirementInputRef.value?.title || '').slice(0, 30) || '测试用例'}`,
      preconditions: '', steps: finalContent, expected_results: '',
      priority: 'P1', case_type: 'functional', tags: ['ai-generated'],
    })
  }
  // 显示预览对话框让用户确认
  previewCases.value = parsedCases
  showSavePreview.value = true
}

async function handleConfirmSave(cases: Array<Record<string, unknown>>) {
  if (!doneResult.value || cases.length === 0) return
  isSaving.value = true
  showSavePreview.value = false
  const count = await store.saveCases(doneResult.value.task_id, selectedProjectId.value, cases)
  if (count > 0) {
    savedCount.value = count
    message.success(`已保存 ${count} 条用例到用例库`)
  } else {
    message.warning('保存失败，请检查字段是否完整')
  }
  isSaving.value = false
}

async function handleExportExcel() {
  if (!doneResult.value?.task_id) { message.warning('无结果可导出'); return }
  isExporting.value = true
  try {
    // 使用 Axios（自动注入 Bearer token），以 blob 形式下载
    const resp = await request.get(`/testing/generate/${doneResult.value.task_id}/export`, {
      responseType: 'blob',
    })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(resp.data)
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
  if (suggestions.length === 0 || !currentTaskId.value) return
  message.info(`正在按 ${suggestions.length} 条建议修订生成...`)
  try {
    const res = await generationApi.reviseGenerationTask(currentTaskId.value, suggestions)
    if (res.code && res.code !== 200) {
      message.error(res.message || '修订生成失败')
      return
    }
    // 重新加载结果刷新 UI
    const [resultsRes] = await Promise.all([
      generationApi.getGenerationResults(currentTaskId.value),
    ])
    const results = resultsRes.data || []
    const taskRes = await generationApi.getGenerationTask(currentTaskId.value)
    loadFromExisting(taskRes.data || { id: currentTaskId.value }, results)
    message.success('修订完成')
  } catch (e) {
    message.error('修订生成请求失败')
  }
}

function handleReset() {
  currentTaskId.value = ''
  savedCount.value = null
  store.reset()
}

async function loadExistingTask(taskId: string) {
  isLoading.value = true
  try {
    const [taskRes, resultsRes] = await Promise.all([generationApi.getGenerationTask(taskId), generationApi.getGenerationResults(taskId)])
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

onMounted(async () => {
  projectStore.fetchProjects()
  // 加载配置默认值（含模型列表），设置默认模型
  await store.fetchConfigDefaults()
  const models = store.configDefaults?.models
  if (models && models.length > 0) {
    selectedModel.value = `${models[0].provider}:${models[0].model}`
  }
  // 仍需加载已保存的配置（如 API Key 等）
  store.fetchConfig()
  const taskId = route.query.task_id as string | undefined
  const shouldRetry = route.query.retry === '1'
  if (taskId) {
    loadExistingTask(taskId)
    // retry=1 表示从任务详情页跳转回来，自动触发重新生成
    if (shouldRetry && requirementInputRef.value) {
      handleRetry()
    }
  }
})

/** 查看详情页面跳回的重新生成 */
async function handleRetry() {
  if (!currentTaskId.value) return
  message.info('正在重新生成...')
  const input = requirementInputRef.value
  if (!input) return
  const task = await store.createTask({
    project_id: selectedProjectId.value,
    requirement_title: input.title,
    input_text: input.text,
    model: selectedModel.value,
    output_mode: outputMode.value,
  })
  if (!task || !task.id) { message.error('创建任务失败'); return }
  currentTaskId.value = task.id
  start(task.id)
}
</script>

<style scoped>
@media (max-width: 768px) {
  :deep(.n-layout-content) {
    padding: 12px !important;
  }
  :deep(.n-space) {
    max-width: 100% !important;
  }
  :deep(.n-page-header) {
    flex-direction: column;
    gap: 8px;
  }
  :deep(.n-select) {
    width: 100% !important;
  }
  :deep(.n-space-align-center) {
    flex-wrap: wrap;
  }
  :deep(.n-radio-group) {
    flex-wrap: wrap;
  }
}
</style>
