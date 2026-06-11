import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type {
  TestCase,
  TestCaseCreate,
  TestCaseUpdate,
  TestCaseFilter,
  TestCaseListData,
} from '@/modules/ai_testing/types/testcase'

// ─── 用例 CRUD ──────────────────────────────────

/** 获取用例列表 */
export function getTestCases(params?: TestCaseFilter): Promise<ApiResponse<TestCaseListData>> {
  return request.get('/testing/cases', { params })
}

/** 获取用例详情 */
export function getTestCase(id: string): Promise<ApiResponse<TestCase>> {
  return request.get(`/testing/cases/${id}`)
}

/** 创建用例 */
export function createTestCase(data: TestCaseCreate): Promise<ApiResponse<TestCase>> {
  return request.post('/testing/cases', data)
}

/** 更新用例 */
export function updateTestCase(id: string, data: TestCaseUpdate): Promise<ApiResponse<TestCase>> {
  return request.put(`/testing/cases/${id}`, data)
}

/** 删除用例 */
export function deleteTestCase(id: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/cases/${id}`)
}

/** 批量删除用例 */
export function batchDeleteCases(ids: string[]): Promise<ApiResponse<number>> {
  return request.post('/testing/cases/batch-delete', { ids })
}

/** 导出用例为 Excel */
export function exportCases(params?: { project_id?: string | null; ids?: string }): Promise<Blob> {
  return request.get('/testing/cases/export', {
    params,
    responseType: 'blob',
  })
}

/** 获取用例统计 */
export function getCaseStats(projectId?: string | null): Promise<ApiResponse<{
  total: number
  by_priority: Record<string, number>
  by_type: Record<string, number>
  by_status: Record<string, number>
}>> {
  return request.get('/testing/cases/stats', {
    params: projectId ? { project_id: projectId } : {},
  })
}

/** 导入用例 Excel */
export function importCases(file: File, projectId?: string | null): Promise<ApiResponse<{ imported_count: number; ids: string[] }>> {
  const formData = new FormData()
  formData.append('file', file)
  if (projectId) {
    formData.append('project_id', projectId)
  }
  return request.post('/testing/cases/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
