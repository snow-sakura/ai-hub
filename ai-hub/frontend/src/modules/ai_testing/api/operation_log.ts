import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type { OperationLogListData } from '@/modules/ai_testing/types/operation_log'

/** 获取用例操作日志 */
export function getCaseLogs(
  caseId: string,
  params?: { page?: number; page_size?: number }
): Promise<ApiResponse<OperationLogListData>> {
  return request.get(`/testing/cases/${caseId}/logs`, { params })
}

/** 获取项目操作日志 */
export function getProjectLogs(
  projectId: string,
  params?: { page?: number; page_size?: number }
): Promise<ApiResponse<OperationLogListData>> {
  return request.get(`/testing/projects/${projectId}/logs`, { params })
}
