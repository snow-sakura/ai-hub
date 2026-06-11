import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  GenerationTask,
  GenerationResult,
  GenerationStage,
  TaskStatus,
  OutputMode,
  ConfigItem,
  ConfigDefaults,
  ConfigCheckResponse,
} from '@/modules/ai_testing/types/generation'
import * as generationApi from '@/modules/ai_testing/api/generation'

export const useGenerationStore = defineStore('testing-generation', () => {
  const currentTask = ref<GenerationTask | null>(null)
  const results = ref<GenerationResult[]>([])
  const configItems = ref<ConfigItem[]>([])
  const configDefaults = ref<ConfigDefaults | null>(null)
  const configStatus = ref<ConfigCheckResponse | null>(null)
  const isLoading = ref(false)
  const isStreaming = ref(false)

  // 任务列表状态
  const tasks = ref<GenerationTask[]>([])
  const tasksTotal = ref(0)
  const tasksPage = ref(1)
  const tasksPageSize = ref(10)
  const tasksLoading = ref(false)
  const tasksFilters = ref<{
    project_id: string | null
    status: string | null
    keyword: string | null
  }>({
    project_id: null,
    status: null,
    keyword: null,
  })

  // 流式状态
  const currentStage = ref<GenerationStage | null>(null)
  const streamingContent = ref('')
  const streamError = ref<string | null>(null)
  const charCount = ref(0)

  /** 创建生成任务 */
  async function createTask(params: {
    project_id?: string | null
    requirement_title?: string
    input_text?: string
    model?: string
    output_mode?: OutputMode
  }): Promise<GenerationTask | null> {
    isLoading.value = true
    try {
      const res = await generationApi.createGenerationTask(params)
      currentTask.value = res.data
      results.value = []
      currentStage.value = null
      streamingContent.value = ''
      streamError.value = null
      charCount.value = 0
      return res.data
    } catch (e) {
      console.error('创建生成任务失败:', e)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /** 获取任务状态 */
  async function fetchTask(taskId: string) {
    try {
      const res = await generationApi.getGenerationTask(taskId)
      currentTask.value = res.data
    } catch (e) {
      console.error('获取任务状态失败:', e)
    }
  }

  /** 获取生成结果 */
  async function fetchResults(taskId: string) {
    try {
      const res = await generationApi.getGenerationResults(taskId)
      results.value = res.data || []
    } catch (e) {
      console.error('获取生成结果失败:', e)
    }
  }

  /** 保存生成的用例到用例库 */
  async function saveCases(
    taskId: string,
    projectId: string | null,
    cases: Array<Record<string, unknown>>
  ): Promise<number> {
    try {
      const res = await generationApi.saveGeneratedCases({
        task_id: taskId,
        project_id: projectId,
        cases,
      })
      return res.data.saved_count
    } catch (e) {
      console.error('保存用例失败:', e)
      return 0
    }
  }

  /** 加载配置 */
  async function fetchConfig(category?: string) {
    try {
      const res = await generationApi.getConfig(category)
      configItems.value = res.data || []
    } catch (e) {
      console.error('获取配置失败:', e)
    }
  }

  /** 更新配置 */
  async function saveConfig(items: ConfigItem[]): Promise<boolean> {
    try {
      await generationApi.updateConfig(items)
      return true
    } catch (e) {
      console.error('保存配置失败:', e)
      return false
    }
  }

  /** 获取配置默认值（默认提示词 + 可用模型列表） */
  async function fetchConfigDefaults() {
    try {
      const res = await generationApi.getConfigDefaults()
      configDefaults.value = res.data
    } catch (e) {
      console.error('获取配置默认值失败:', e)
    }
  }

  /** 检查配置状态（是否就绪） */
  async function fetchConfigStatus() {
    try {
      const res = await generationApi.checkConfig()
      configStatus.value = res.data || null
    } catch (e) {
      console.error('检查配置状态失败:', e)
    }
  }

  /** 更新流式内容 */
  function appendStreamContent(text: string) {
    streamingContent.value += text
    charCount.value = streamingContent.value.length
  }

  /** 设置当前阶段 */
  function setCurrentStage(stage: GenerationStage) {
    currentStage.value = stage
  }

  /** 重置流式状态 */
  function resetStreamState() {
    currentStage.value = null
    streamingContent.value = ''
    streamError.value = null
    charCount.value = 0
    isStreaming.value = false
  }

  /** 加载任务列表 */
  async function fetchTasks() {
    tasksLoading.value = true
    try {
      const res = await generationApi.listGenerationTasks({
        ...tasksFilters.value,
        page: tasksPage.value,
        page_size: tasksPageSize.value,
      })
      tasks.value = res.data.items
      tasksTotal.value = res.data.total
    } catch (e) {
      console.error('获取生成任务列表失败:', e)
    } finally {
      tasksLoading.value = false
    }
  }

  /** 删除生成任务 */
  async function removeTask(taskId: string): Promise<boolean> {
    try {
      await generationApi.deleteGenerationTask(taskId)
      await fetchTasks()
      return true
    } catch (e) {
      console.error('删除生成任务失败:', e)
      return false
    }
  }

  /** 重置全部状态 */
  function reset() {
    currentTask.value = null
    results.value = []
    resetStreamState()
  }

  return {
    currentTask,
    results,
    configItems,
    configDefaults,
    configStatus,
    isLoading,
    isStreaming,
    tasks,
    tasksTotal,
    tasksPage,
    tasksPageSize,
    tasksLoading,
    tasksFilters,
    currentStage,
    streamingContent,
    streamError,
    charCount,
    createTask,
    fetchTask,
    fetchResults,
    saveCases,
    fetchTasks,
    removeTask,
    fetchConfig,
    saveConfig,
    fetchConfigDefaults,
    fetchConfigStatus,
    appendStreamContent,
    setCurrentStage,
    resetStreamState,
    reset,
  }
})
