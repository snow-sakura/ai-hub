/** AI Testing 用例附件类型 */

export interface CaseAttachment {
  id: string
  case_id: string
  file_name: string
  file_path: string
  file_size: number
  file_type: string
  uploaded_by: string
  created_at: string
}
