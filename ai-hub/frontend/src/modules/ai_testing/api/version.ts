import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type {
  ProjectVersion,
  VersionCreate,
  VersionUpdate,
} from '@/modules/ai_testing/types/version'

/** 获取所有版本（独立模块） */
export function getAllVersions(): Promise<ApiResponse<ProjectVersion[]>> {
  return request.get('/testing/versions')
}

/** 创建版本（独立模块） */
export function createVersionStandalone(
  data: VersionCreate
): Promise<ApiResponse<ProjectVersion>> {
  return request.post('/testing/versions', data)
}

/** 获取项目版本列表 */
export function getVersions(projectId: string): Promise<ApiResponse<ProjectVersion[]>> {
  return request.get(`/testing/projects/${projectId}/versions`)
}

/** 创建版本 */
export function createVersion(
  projectId: string,
  data: VersionCreate
): Promise<ApiResponse<ProjectVersion>> {
  return request.post(`/testing/projects/${projectId}/versions`, data)
}

/** 更新版本 */
export function updateVersion(
  versionId: string,
  data: VersionUpdate
): Promise<ApiResponse<ProjectVersion>> {
  return request.put(`/testing/versions/${versionId}`, data)
}

/** 删除版本 */
export function deleteVersion(versionId: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/versions/${versionId}`)
}
