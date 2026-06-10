import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type { KnowledgeDoc } from '@/modules/knowledge/types/knowledge'

/** 上传文档 */
export function uploadDocument(file: File): Promise<ApiResponse<KnowledgeDoc>> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** 获取知识库列表 */
export function getKnowledgeDocs(): Promise<ApiResponse<KnowledgeDoc[]>> {
  return request.get('/knowledge')
}

/** 删除知识库文档 */
export function deleteKnowledgeDoc(docId: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/knowledge/${docId}`)
}

/** 重建知识库索引 */
export function rebuildKnowledge(): Promise<ApiResponse<any>> {
  return request.post('/knowledge/rebuild')
}
