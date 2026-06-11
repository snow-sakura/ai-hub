import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type { CaseComment, CommentCreate } from '@/modules/ai_testing/types/comment'

/** 获取用例评论列表 */
export function getComments(caseId: string): Promise<ApiResponse<CaseComment[]>> {
  return request.get(`/testing/cases/${caseId}/comments`)
}

/** 创建评论 */
export function createComment(
  caseId: string,
  data: CommentCreate
): Promise<ApiResponse<CaseComment>> {
  return request.post(`/testing/cases/${caseId}/comments`, data)
}

/** 更新评论 */
export function updateComment(
  commentId: string,
  content: string
): Promise<ApiResponse<boolean>> {
  return request.put(`/testing/comments/${commentId}`, { content })
}

/** 删除评论 */
export function deleteComment(commentId: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/comments/${commentId}`)
}
