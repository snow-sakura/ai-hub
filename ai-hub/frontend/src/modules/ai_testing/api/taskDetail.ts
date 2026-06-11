import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'

/** 获取生成任务的详细用例 */
export function getTaskGeneratedCases(
  taskId: string,
  params?: { page?: number; page_size?: number; status?: string }
): Promise<ApiResponse<{ items: Array<Record<string, unknown>>; total: number }>> {
  return request.get(`/testing/generate/tasks/${taskId}/generated-cases`, { params })
}

/** 批量更新生成用例状态 */
export function batchUpdateGeneratedCases(
  taskId: string,
  data: { case_ids: string[]; status: string }
): Promise<ApiResponse<{ updated: number }>> {
  return request.post(`/testing/generate/tasks/${taskId}/batch-update-cases`, data)
}

/** 取消生成任务 */
export function cancelGenerationTask(taskId: string): Promise<ApiResponse<boolean>> {
  return request.post(`/testing/generate/${taskId}/cancel`)
}

/** 将已采用的生成用例保存到用例库 */
export function saveTaskCasesToLibrary(
  taskId: string,
  projectId?: string | null
): Promise<ApiResponse<{ saved_count: number }>> {
  return request.post(`/testing/generate/tasks/${taskId}/save-cases`, { project_id: projectId })
}

/** 获取生成统计 */
export function getGenerationStats(params?: {
  start_date?: string
  end_date?: string
}): Promise<ApiResponse<{
  total_tasks: number
  completed_tasks: number
  total_cases: number
  avg_score: number
}>> {
  return request.get('/testing/generate/stats', { params })
}
