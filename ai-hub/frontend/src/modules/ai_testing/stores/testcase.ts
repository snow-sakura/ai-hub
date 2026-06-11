import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  TestCase,
  TestCaseCreate,
  TestCaseUpdate,
  TestCaseFilter,
  CasePriority,
  CaseStatus,
} from '@/modules/ai_testing/types/testcase'
import * as testcaseApi from '@/modules/ai_testing/api/testcase'

export const useTestCaseStore = defineStore('testing-testcase', () => {
  const cases = ref<TestCase[]>([])
  const currentCase = ref<TestCase | null>(null)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(10)
  const isLoading = ref(false)
  const selectedIds = ref<string[]>([])

  // 筛选条件
  const filters = ref<TestCaseFilter>({
    project_id: null,
    priority: null,
    case_type: null,
    status: null,
    version: null,
    keyword: null,
  })

  // 统计
  const stats = ref<{
    total: number
    by_priority: Record<string, number>
    by_type: Record<string, number>
    by_status: Record<string, number>
  }>({ total: 0, by_priority: {}, by_type: {}, by_status: {} })

  /** 加载用例列表 */
  async function fetchCases() {
    isLoading.value = true
    try {
      const res = await testcaseApi.getTestCases({
        ...filters.value,
        page: page.value,
        page_size: pageSize.value,
      })
      const data = res.data
      cases.value = data.items
      total.value = data.total
    } catch (e) {
      console.error('获取用例列表失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  /** 加载用例详情 */
  async function fetchCase(id: string) {
    isLoading.value = true
    try {
      const res = await testcaseApi.getTestCase(id)
      currentCase.value = res.data
    } catch (e) {
      console.error('获取用例详情失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  /** 创建用例 */
  async function createCase(data: TestCaseCreate): Promise<TestCase | null> {
    try {
      const res = await testcaseApi.createTestCase(data)
      await fetchCases()
      return res.data
    } catch (e) {
      console.error('创建用例失败:', e)
      return null
    }
  }

  /** 更新用例 */
  async function updateCase(id: string, data: TestCaseUpdate): Promise<boolean> {
    try {
      await testcaseApi.updateTestCase(id, data)
      await fetchCases()
      if (currentCase.value?.id === id) {
        await fetchCase(id)
      }
      return true
    } catch (e) {
      console.error('更新用例失败:', e)
      return false
    }
  }

  /** 删除用例 */
  async function deleteCase(id: string): Promise<boolean> {
    try {
      await testcaseApi.deleteTestCase(id)
      await fetchCases()
      return true
    } catch (e) {
      console.error('删除用例失败:', e)
      return false
    }
  }

  /** 批量删除 */
  async function batchDelete(): Promise<number> {
    if (!selectedIds.value.length) return 0
    try {
      const res = await testcaseApi.batchDeleteCases(selectedIds.value)
      selectedIds.value = []
      await fetchCases()
      return res.data
    } catch (e) {
      console.error('批量删除失败:', e)
      return 0
    }
  }

  /** 设置筛选条件 */
  function setFilter(key: keyof TestCaseFilter, value: unknown) {
    filters.value[key] = value as never
    page.value = 1
  }

  /** 加载用例统计 */
  async function fetchStats() {
    try {
      const res = await testcaseApi.getCaseStats(filters.value.project_id)
      stats.value = res.data
    } catch (e) {
      console.error('获取用例统计失败:', e)
    }
  }

  /** 清空选择 */
  function clearSelection() {
    selectedIds.value = []
  }

  return {
    cases,
    currentCase,
    total,
    page,
    pageSize,
    isLoading,
    selectedIds,
    filters,
    stats,
    fetchCases,
    fetchCase,
    createCase,
    updateCase,
    deleteCase,
    batchDelete,
    fetchStats,
    setFilter,
    clearSelection,
  }
})
