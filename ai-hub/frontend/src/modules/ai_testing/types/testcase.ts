/** AI Testing 测试用例相关类型 */

/** 用例优先级 */
export type CasePriority = 'P0' | 'P1' | 'P2' | 'P3'

/** 用例状态 */
export type CaseStatus = 'draft' | 'active' | 'deprecated'

/** 用例来源 */
export type CaseSource = 'manual' | 'ai' | 'import'

/** 测试用例 */
export interface TestCase {
  id: string
  project_id: string | null
  project_name: string | null
  title: string
  version: string
  priority: CasePriority
  case_type: string
  preconditions: string
  steps: string
  expected_results: string
  tags: string[]
  status: CaseStatus
  source: CaseSource
  ai_task_id: string | null
  author: string
  created_at: string
  updated_at: string
}

/** 创建用例参数 */
export interface TestCaseCreate {
  project_id?: string | null
  title: string
  version?: string
  priority?: CasePriority
  case_type?: string
  preconditions?: string
  steps?: string
  expected_results?: string
  tags?: string[]
  status?: CaseStatus
  author?: string
}

/** 更新用例参数 */
export interface TestCaseUpdate {
  project_id?: string | null
  title?: string
  version?: string
  priority?: CasePriority
  case_type?: string
  preconditions?: string
  steps?: string
  expected_results?: string
  tags?: string[]
  status?: CaseStatus
}

/** 用例筛选参数 */
export interface TestCaseFilter {
  project_id?: string | null
  priority?: CasePriority | null
  case_type?: string | null
  status?: CaseStatus | null
  version?: string | null
  keyword?: string | null
  page?: number
  page_size?: number
}

/** 用例列表分页响应 */
export interface TestCaseListData {
  items: TestCase[]
  total: number
  page: number
  page_size: number
}
