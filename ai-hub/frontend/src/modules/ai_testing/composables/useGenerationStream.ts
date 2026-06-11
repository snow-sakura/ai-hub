/**
 * useGenerationStream - AI 用例生成 SSE 流式 composable
 *
 * 独立于通用 useSseStream.ts，因为事件类型和状态结构不同。
 * 使用原生 EventSource API，与 FastAPI SSE 端点配合。
 */

import type { GenerationStage } from '@/modules/ai_testing/types/generation'
import { useGenerationStore } from '@/modules/ai_testing/stores/generation'

/** SSE 事件数据 */
export interface StageEvent {
  stage: GenerationStage
  current: number
}

export interface TokenEvent {
  stage: GenerationStage
  content: string
}

export interface ReviewEvent {
  overall_score: number
  review_passed: boolean
  dimensions: Record<string, { score: number; comment: string }>
  issues: Array<{ severity: string; description: string; affected_cases: string[] }>
  improvement_suggestions: string[]
  summary: string
}

export interface ProgressEvent {
  current: number
  total: number
  message: string
}

export interface DoneEvent {
  task_id: string
  generated_count: number
  review_passed: boolean
  overall_score: number
}

export interface ErrorEvent {
  code: string
  message: string
}

/** 阶段配置 */
export const STAGE_LABELS: Record<GenerationStage, string> = {
  analyze: '需求分析',
  write: '用例编写',
  review: 'AI 评审',
  revise: '用例修订',
  final: '生成完成',
}

export const STAGE_ICONS: Record<GenerationStage, string> = {
  analyze: '🔍',
  write: '✍️',
  review: '⭐',
  revise: '🔧',
  final: '✅',
}

const SSE_BASE = '/api/v1/testing/generate'

export function useGenerationStream() {
  const store = useGenerationStore()

  // 本地响应式状态
  const isConnecting = ref(false)
  const isDone = ref(false)
  const localStreaming = ref(false)
  const doneResult = ref<DoneEvent | null>(null)
  const errorInfo = ref<ErrorEvent | null>(null)
  const reviewResult = ref<ReviewEvent | null>(null)
  const progress = ref({ current: 0, total: 4, message: '' })
  const stageContents = reactive<Record<string, string>>({})

  let eventSource: EventSource | null = null

  /** 开始 SSE 流 */
  function start(taskId: string, customSuggestions?: string[]) {
    // 防止重复连接
    if (eventSource) stop()

    isConnecting.value = true
    isDone.value = false
    localStreaming.value = true
    doneResult.value = null
    errorInfo.value = null
    reviewResult.value = null
    progress.value = { current: 0, total: 4, message: '连接中...' }
    // 清空 stageContents（reactive 对象，逐个删除 key）
    for (const k of Object.keys(stageContents)) delete stageContents[k]

    store.isStreaming = true
    localStreaming.value = true
    store.resetStreamState()

    // 构造 URL，附加自定义改进建议
    let url = `${SSE_BASE}/${taskId}/stream`
    if (customSuggestions && customSuggestions.length > 0) {
      const encoded = encodeURIComponent(JSON.stringify(customSuggestions))
      url += `?custom_suggestions=${encoded}`
    }
    eventSource = new EventSource(url)

    // ── 阶段切换 ──────────────────────────────────────────────
    eventSource.addEventListener('testing_stage', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as StageEvent
      store.setCurrentStage(data.stage)
      progress.value = { ...progress.value, current: data.current }
    })

    // ── 流式 token ────────────────────────────────────────────
    eventSource.addEventListener('testing_token', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as TokenEvent
      store.appendStreamContent(data.content)

      // 按阶段累积内容
      const key = data.stage
      stageContents[key] = (stageContents[key] || '') + data.content
    })

    // ── 评审结果 ──────────────────────────────────────────────
    eventSource.addEventListener('testing_review', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as ReviewEvent
      reviewResult.value = data
    })

    // ── 进度更新 ──────────────────────────────────────────────
    eventSource.addEventListener('testing_progress', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as ProgressEvent
      progress.value = data
    })

    // ── 完成 ──────────────────────────────────────────────────
    eventSource.addEventListener('testing_done', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as DoneEvent
      isDone.value = true
      doneResult.value = data
      progress.value = { current: 4, total: 4, message: '生成完成' }
      store.setCurrentStage('final')
      store.isStreaming = false
      localStreaming.value = false
      cleanup()
    })

    // ── 错误 ──────────────────────────────────────────────────
    eventSource.addEventListener('testing_error', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as ErrorEvent
      errorInfo.value = data
      store.streamError = data.message
      store.isStreaming = false
      localStreaming.value = false
      cleanup()
    })

    // ── 连接错误 ──────────────────────────────────────────────
    eventSource.onerror = () => {
      if (!isDone.value && !errorInfo.value) {
        errorInfo.value = { code: 'CONNECTION_ERROR', message: 'SSE 连接中断' }
        store.streamError = '连接中断，请检查网络'
      }
      store.isStreaming = false
      localStreaming.value = false
      cleanup()
    }

    eventSource.onopen = () => {
      isConnecting.value = false
    }
  }

  /** 停止 SSE 流 */
  function stop() {
    cleanup()
    store.isStreaming = false
    localStreaming.value = false
  }

  function cleanup() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    isConnecting.value = false
  }

  onUnmounted(() => cleanup())

  /** 从已有的任务结果填充状态（用于查看历史记录） */
  function loadFromExisting(task: { id: string; generated_count?: number }, results: Array<{ stage: string; content: string }>) {
    isDone.value = true
    store.isStreaming = false
    localStreaming.value = false
    store.setCurrentStage('final')
    store.resetStreamState()

    const stageOrder = ['analyze', 'write', 'review', 'revise']
    const contents: Record<string, string> = {}
    let fullContent = ''
    let finalContent = ''
    let reviewRes: ReviewEvent | null = null
    let reviewPassed = false
    let overallScore = 0

    for (const stage of stageOrder) {
      const r = results.find(r => r.stage === stage)
      if (!r) continue
      const content = r.content || ''
      contents[stage] = content

      if (stage === 'review') {
        try {
          const parsed = JSON.parse(content) as ReviewEvent
          reviewRes = parsed
          reviewPassed = parsed.review_passed ?? false
          overallScore = parsed.overall_score ?? 0
        } catch { /* empty */ }
      } else if (stage === 'revise') {
        finalContent = content
      }

      if (stage !== 'review') {
        store.appendStreamContent(content)
        fullContent += content
      }
    }

    // 补充 final 结果
    const finalResult = results.find(r => r.stage === 'final')
    if (finalResult?.content) {
      contents.revise = finalResult.content
      store.appendStreamContent(finalResult.content)
    }

    Object.assign(stageContents, contents)
    reviewResult.value = reviewRes
    doneResult.value = {
      task_id: task.id,
      generated_count: task.generated_count || 0,
      review_passed: reviewPassed,
      overall_score: overallScore,
    }
    progress.value = { current: 4, total: 4, message: '生成完成' }
  }

  return {
    // 状态（返回原始 ref，组件 template 自动解包，script 用 .value）
    isConnecting,
    isStreaming: localStreaming,
    isDone,
    currentStage: computed(() => store.currentStage),
    streamingContent: computed(() => store.streamingContent),
    stageContents,
    reviewResult,
    progress,
    doneResult,
    errorInfo,
    streamError: computed(() => store.streamError),

    // 操作
    start,
    stop,
    loadFromExisting,
  }
}
