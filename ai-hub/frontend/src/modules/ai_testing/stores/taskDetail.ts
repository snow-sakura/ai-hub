import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import * as taskDetailApi from '@/modules/ai_testing/api/taskDetail'
import * as generationApi from '@/modules/ai_testing/api/generation'
import type { GenerationTask, GenerationResult } from '@/modules/ai_testing/types/generation'

export const useTaskDetailStore = defineStore('testing-task-detail', () => {
  const task = ref<GenerationTask | null>(null)
  const results = ref<GenerationResult[]>([])
  const generatedCases = ref<Array<Record<string, unknown>>>([])
  const casesTotal = ref(0)
  const casesPage = ref(1)
  const casesPageSize = ref(20)
  const isLoading = ref(false)
  const selectedIds = ref<string[]>([])
  const currentPreviewCase = ref<Record<string, unknown> | null>(null)
  const showPreviewModal = ref(false)

  function isSelected(id: string): boolean {
    return selectedIds.value.includes(id)
  }

  async function fetchTask(taskId: string) {
    try {
      const res = await generationApi.getGenerationTask(taskId)
      task.value = res.data
    } catch (e) {
      console.error('获取任务详情失败:', e)
    }
  }

  async function fetchResults(taskId: string) {
    try {
      const res = await generationApi.getGenerationResults(taskId)
      results.value = res.data || []
    } catch (e) {
      console.error('获取任务结果失败:', e)
    }
  }

  async function fetchGeneratedCases(taskId: string) {
    isLoading.value = true
    try {
      const res = await taskDetailApi.getTaskGeneratedCases(taskId, {
        page: casesPage.value,
        page_size: casesPageSize.value,
      })
      generatedCases.value = res.data.items || []
      casesTotal.value = res.data.total || 0
    } catch (e) {
      console.error('获取生成用例列表失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function batchUpdateCases(taskId: string, caseIds: string[], status: string): Promise<boolean> {
    try {
      await taskDetailApi.batchUpdateGeneratedCases(taskId, { case_ids: caseIds, status })
      await fetchGeneratedCases(taskId)
      return true
    } catch (e) {
      console.error('批量更新用例状态失败:', e)
      return false
    }
  }

  function toggleSelect(id: string) {
    const idx = selectedIds.value.indexOf(id)
    if (idx >= 0) {
      selectedIds.value = selectedIds.value.filter(i => i !== id)
    } else {
      selectedIds.value = [...selectedIds.value, id]
    }
  }

  function toggleSelectAll() {
    if (selectedIds.value.length === generatedCases.value.length) {
      selectedIds.value = []
    } else {
      selectedIds.value = generatedCases.value.map(c => String(c.id))
    }
  }

  function clearSelection() {
    selectedIds.value = []
  }

  function previewCase(caseData: Record<string, unknown>) {
    currentPreviewCase.value = caseData
    showPreviewModal.value = true
  }

  function closePreview() {
    showPreviewModal.value = false
    currentPreviewCase.value = null
  }

  async function changePage(taskId: string, page: number) {
    casesPage.value = page
    await fetchGeneratedCases(taskId)
  }

  async function changePageSize(taskId: string, size: number) {
    casesPageSize.value = size
    casesPage.value = 1
    await fetchGeneratedCases(taskId)
  }

  function reset() {
    task.value = null
    results.value = []
    generatedCases.value = []
    casesTotal.value = 0
    casesPage.value = 1
    casesPageSize.value = 20
    selectedIds.value = []
    currentPreviewCase.value = null
    showPreviewModal.value = false
  }

  return {
    task, results, generatedCases, casesTotal, casesPage, casesPageSize,
    isLoading, selectedIds, currentPreviewCase, showPreviewModal,
    fetchTask, fetchResults, fetchGeneratedCases, batchUpdateCases,
    toggleSelect, toggleSelectAll, isSelected, clearSelection,
    previewCase, closePreview, changePage, changePageSize, reset,
  }
})
