/** AI Testing 项目相关类型 */

/** 项目状态 */
export type ProjectStatus = 'active' | 'paused' | 'completed' | 'archived'

/** 成员角色 */
export type MemberRole = 'owner' | 'tester' | 'viewer'

/** 项目 */
export interface TestingProject {
  id: string
  name: string
  description: string
  status: ProjectStatus
  case_count: number
  member_count: number
  created_at: string
  updated_at: string
}

/** 项目成员 */
export interface ProjectMember {
  id: string
  project_id: string
  name: string
  role: MemberRole
  created_at: string
}

/** 创建项目参数 */
export interface ProjectCreate {
  name: string
  description?: string
  status?: ProjectStatus
}

/** 更新项目参数 */
export interface ProjectUpdate {
  name?: string
  description?: string
  status?: ProjectStatus
}

/** 创建成员参数 */
export interface MemberCreate {
  name: string
  role?: MemberRole
}

/** 更新成员角色参数 */
export interface MemberUpdate {
  role: MemberRole
}

/** 项目列表分页响应 */
export interface ProjectListData {
  items: TestingProject[]
  total: number
  page: number
  page_size: number
}
