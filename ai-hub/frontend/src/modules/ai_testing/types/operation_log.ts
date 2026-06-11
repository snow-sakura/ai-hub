/** AI Testing 操作日志类型 */

export interface OperationLog {
  id: string
  entity_type: 'project' | 'case' | 'member' | 'version'
  entity_id: string
  action: string
  operator: string
  detail: string
  created_at: string
}

/** 操作日志列表 */
export interface OperationLogListData {
  items: OperationLog[]
  total: number
  page: number
  page_size: number
}
