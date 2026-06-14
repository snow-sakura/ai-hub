import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type { ScheduledTask, ScheduledTaskCreate, ScheduledTaskUpdate, ScheduledTaskLog } from '@/modules/ai_testing/types/scheduledTask'

/** 获取所有定时任务 */
export function listScheduledTasks(): Promise<ApiResponse<ScheduledTask[]>> {
  return request.get('/testing/scheduled-tasks')
}

/** 获取单个定时任务 */
export function getScheduledTask(id: string): Promise<ApiResponse<ScheduledTask>> {
  return request.get(`/testing/scheduled-tasks/${id}`)
}

/** 创建定时任务 */
export function createScheduledTask(data: ScheduledTaskCreate): Promise<ApiResponse<ScheduledTask>> {
  return request.post('/testing/scheduled-tasks', data)
}

/** 更新定时任务 */
export function updateScheduledTask(id: string, data: ScheduledTaskUpdate): Promise<ApiResponse<ScheduledTask>> {
  return request.put(`/testing/scheduled-tasks/${id}`, data)
}

/** 删除定时任务 */
export function deleteScheduledTask(id: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/scheduled-tasks/${id}`)
}

/** 立即执行定时任务 */
export function executeScheduledTask(id: string): Promise<ApiResponse<{ log_id: string; status: string; execution: any }>> {
  return request.post(`/testing/scheduled-tasks/${id}/execute`)
}

/** 获取定时任务的执行日志 */
export function getScheduledTaskLogs(id: string, params?: { limit?: number }): Promise<ApiResponse<ScheduledTaskLog[]>> {
  return request.get(`/testing/scheduled-tasks/${id}/logs`, { params })
}
