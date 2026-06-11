import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type { CaseAttachment } from '@/modules/ai_testing/types/attachment'

/** 上传用例附件 */
export function uploadAttachment(
  caseId: string,
  file: File
): Promise<ApiResponse<CaseAttachment>> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/testing/cases/${caseId}/attachments`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** 获取用例附件列表 */
export function getAttachments(caseId: string): Promise<ApiResponse<CaseAttachment[]>> {
  return request.get(`/testing/cases/${caseId}/attachments`)
}

/** 删除附件 */
export function deleteAttachment(attachmentId: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/attachments/${attachmentId}`)
}

/** 下载附件（返回 blob） */
export function getAttachmentDownloadUrl(attachmentId: string): string {
  return `/api/v1/testing/attachments/${attachmentId}/download`
}
