import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type {
  TestingProject,
  ProjectMember,
  ProjectCreate,
  ProjectUpdate,
  MemberCreate,
  MemberUpdate,
  ProjectListData,
  DashboardStats,
} from '@/modules/ai_testing/types/project'

// ─── 项目 CRUD ──────────────────────────────────

/** 获取项目列表 */
export function getProjects(params?: {
  status?: string | null
  keyword?: string | null
  page?: number
  page_size?: number
}): Promise<ApiResponse<ProjectListData>> {
  return request.get('/testing/projects', { params })
}

/** 获取项目详情 */
export function getProject(id: string): Promise<ApiResponse<TestingProject>> {
  return request.get(`/testing/projects/${id}`)
}

/** 创建项目 */
export function createProject(data: ProjectCreate): Promise<ApiResponse<TestingProject>> {
  return request.post('/testing/projects', data)
}

/** 更新项目 */
export function updateProject(id: string, data: ProjectUpdate): Promise<ApiResponse<TestingProject>> {
  return request.put(`/testing/projects/${id}`, data)
}

/** 删除项目 */
export function deleteProject(id: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/projects/${id}`)
}

// ─── 项目成员 ──────────────────────────────────────

/** 获取所有成员（独立模块） */
export function getAllMembers(): Promise<ApiResponse<ProjectMember[]>> {
  return request.get('/testing/members')
}

/** 添加成员（独立模块） */
export function addMemberStandalone(data: MemberCreate): Promise<ApiResponse<ProjectMember>> {
  return request.post('/testing/members', data)
}

/** 获取项目成员列表 */
export function getProjectMembers(projectId: string): Promise<ApiResponse<ProjectMember[]>> {
  return request.get(`/testing/projects/${projectId}/members`)
}

/** 添加项目成员 */
export function addMember(projectId: string, data: MemberCreate): Promise<ApiResponse<ProjectMember>> {
  return request.post(`/testing/projects/${projectId}/members`, data)
}

/** 移除项目成员 */
export function removeMember(memberId: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/members/${memberId}`)
}

/** 更新成员角色 */
export function updateMemberRole(memberId: string, data: MemberUpdate): Promise<ApiResponse<boolean>> {
  return request.put(`/testing/members/${memberId}`, data)
}

// ─── 关联版本/成员到项目 ──────────────────────────────

/** 关联已有版本到项目 */
export function linkVersionToProject(versionId: string, projectId: string): Promise<ApiResponse<boolean>> {
  return request.put(`/testing/versions/${versionId}/link-project`, { project_id: projectId })
}

/** 关联已有成员到项目 */
export function linkMemberToProject(memberId: string, projectId: string): Promise<ApiResponse<boolean>> {
  return request.put(`/testing/members/${memberId}/link-project`, { project_id: projectId })
}

/** 从项目中移除成员关联 */
export function unlinkMemberFromProject(memberId: string, projectId: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/members/${memberId}/unlink-project`, { params: { project_id: projectId } })
}

// ─── 仪表盘 ────────────────────────────────────────

export function getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
  return request.get('/testing/dashboard/stats')
}

