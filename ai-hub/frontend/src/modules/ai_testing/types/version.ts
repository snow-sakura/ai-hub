/** AI Testing 项目版本类型 */

export type VersionStatus = 'active' | 'released' | 'archived'

export interface ProjectVersion {
  id: string
  project_id: string
  name: string
  description: string
  status: VersionStatus
  created_at: string
  updated_at: string
}

export interface VersionCreate {
  name: string
  description?: string
  status?: VersionStatus
}

export interface VersionUpdate {
  name?: string
  description?: string
  status?: VersionStatus
}
