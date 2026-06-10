import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'

/** 上传聊天附件，返回 file_id */
export function uploadChatAttachment(file: File): Promise<ApiResponse<{
  file_id: string
  filename: string
  file_type: string
  file_size: number
}>> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/chat/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
