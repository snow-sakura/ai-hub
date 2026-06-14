/** 用例评审相关类型 */

export type ReviewStatus = 'pending' | 'in_progress' | 'approved' | 'rejected' | 'cancelled'
export type ReviewPriority = 'P0' | 'P1' | 'P2' | 'P3'
export type ReviewCaseStatus = 'approved' | 'rejected' | 'pending'

/** 评审 */
export interface Review {
  id: string
  project_id: string | null
  project_name: string | null
  title: string
  description: string
  priority: ReviewPriority
  status: ReviewStatus
  progress: number
  due_date: string
  creator: string
  case_count: number
  reviewer_count: number
  created_at: string
  updated_at: string
}

/** 创建评审参数 */
export interface ReviewCreate {
  project_id?: string | null
  title: string
  description?: string
  priority?: ReviewPriority
  due_date?: string | null
  case_ids?: string[]
  reviewer_ids?: string[]
}

/** 更新评审参数 */
export interface ReviewUpdate {
  title?: string
  description?: string
  priority?: ReviewPriority
  status?: ReviewStatus
  progress?: number
  due_date?: string | null
  case_ids?: string[]
  reviewer_ids?: string[]
}

/** 评审关联用例 */
export interface ReviewCase {
  id: string
  review_id: string
  case_id: string
  case_title: string
  case_priority?: string
  case_type?: string
  preconditions?: string
  steps?: string
  expected_results?: string
  comment: string
  status: ReviewCaseStatus
  created_at: string
}

/** 评审列表分页数据 */
export interface ReviewListData {
  items: Review[]
  total: number
  page: number
  page_size: number
}

/** 评审统计 */
export interface ReviewStats {
  pending: number
  in_progress: number
  approved: number
  rejected: number
}
