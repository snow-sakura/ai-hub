/** 系统管理 API */
import request from '@/shared/api/request'
import type {
  UserItem, UserProfile, UserCreateData, UserUpdateData,
  RoleItem, RoleCreateData,
  AuditLogItem, OperationLogItem,
  SystemSetting, PaginatedResult, SystemStats,
} from '@/modules/system/types/system'

// ─── 统计 ────────────────────────────
export function getSystemStats() {
  return request.get<any, { code: number; data: SystemStats }>('/system/stats')
}

// ─── 用户 ────────────────────────────
export function listUsers(page = 1, pageSize = 20) {
  return request.get<any, { code: number; data: PaginatedResult<UserItem> }>('/system/users', { params: { page, page_size: pageSize } })
}

export function getUser(userId: string) {
  return request.get<any, { code: number; data: UserProfile }>(`/system/users/${userId}`)
}

export function createUser(data: UserCreateData) {
  return request.post<any, { code: number; data: UserItem; message: string }>('/system/users', data)
}

export function updateUser(userId: string, data: UserUpdateData) {
  return request.put<any, { code: number; message: string }>(`/system/users/${userId}`, data)
}

export function deleteUser(userId: string) {
  return request.delete<any, { code: number; message: string }>(`/system/users/${userId}`)
}

export function toggleUserActive(userId: string, isActive: boolean) {
  return request.post<any, { code: number; message: string }>(`/system/users/${userId}/toggle-active`, null, { params: { is_active: isActive } })
}

export function getUserRoles(userId: string) {
  return request.get<any, { code: number; data: RoleItem[] }>(`/system/users/${userId}/roles`)
}

export function setUserRoles(userId: string, roleIds: string[]) {
  return request.put<any, { code: number; message: string }>(`/system/users/${userId}/roles`, roleIds)
}

// ─── 角色 ────────────────────────────
export function listRoles() {
  return request.get<any, { code: number; data: RoleItem[] }>('/system/roles')
}

export function createRole(data: RoleCreateData) {
  return request.post<any, { code: number; data: RoleItem; message: string }>('/system/roles', data)
}

export function updateRole(roleId: string, data: Partial<RoleCreateData>) {
  return request.put<any, { code: number; message: string }>(`/system/roles/${roleId}`, data)
}

export function deleteRole(roleId: string) {
  return request.delete<any, { code: number; message: string }>(`/system/roles/${roleId}`)
}

// ─── 审计日志 ────────────────────────
export function listAuditLogs(params: { page?: number; page_size?: number; user_id?: string; action?: string }) {
  return request.get<any, { code: number; data: PaginatedResult<AuditLogItem> }>('/system/audit-logs', { params })
}

// ─── 操作日志 ────────────────────────
export function listOperationLogs(params: { page?: number; page_size?: number; module?: string; action?: string; resource_type?: string; user_id?: string; keyword?: string }) {
  return request.get<any, { code: number; data: PaginatedResult<OperationLogItem> }>('/system/operation-logs', { params })
}

// ─── 系统设置 ────────────────────────
export function listSettings() {
  return request.get<any, { code: number; data: SystemSetting[] }>('/system/settings')
}

export function updateSetting(key: string, value: string) {
  return request.put<any, { code: number; message: string }>(`/system/settings/${key}`, null, { params: { value } })
}
