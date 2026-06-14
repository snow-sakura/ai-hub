/** AI Testing 项目版本类型 */

export type VersionStatus = 'active' | 'released' | 'archived'

export interface ProjectVersion {
  id: string
  name: string
  description: string
  status: VersionStatus
  pass_rate: number
  created_at: string
  updated_at: string
}

export interface VersionCreate {
  name: string
  description?: string
  status?: VersionStatus
  pass_rate?: number
}

export interface VersionUpdate {
  name?: string
  description?: string
  status?: VersionStatus
  pass_rate?: number
}
