/** 系统管理类型定义 */

export interface UserItem {
  id: string
  username: string
  role: string
  is_active: boolean
  display_name?: string
  email?: string
  phone?: string
  department?: string
  position?: string
  created_at: string
  updated_at?: string
}

export interface UserProfile {
  id: string
  username: string
  role: string
  is_active: boolean
  display_name?: string
  email?: string
  phone?: string
  department?: string
  position?: string
  roles: string[]
  created_at: string
}

export interface UserCreateData {
  username: string
  password: string
  role_ids?: string[]
  display_name?: string
  email?: string
  phone?: string
  department?: string
  position?: string
}

export interface UserUpdateData {
  display_name?: string
  email?: string
  phone?: string
  department?: string
  position?: string
  is_active?: boolean
}

export interface RoleItem {
  id: string
  name: string
  description?: string
  permissions: string[]
  is_builtin: boolean
  user_count: number
  created_at: string
}

export interface RoleCreateData {
  name: string
  description?: string
  permissions: string[]
}

export interface AuditLogItem {
  id: string
  user_id?: string
  username?: string
  action: string
  resource_type?: string
  resource_id?: string
  detail?: string
  ip?: string
  created_at: string
}

export interface OperationLogItem {
  timestamp: string
  module: string
  action: string
  resource_type: string
  resource_id: string
  resource_name: string
  detail: string
  user_id: string
  username: string
  ip: string
  duration_ms: number
}

export interface SystemSetting {
  key: string
  value: string
  description?: string
}

export interface PaginatedResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface SystemStats {
  user_count: number
  role_count: number
  active_sessions: number
  audit_log_count: number
}
