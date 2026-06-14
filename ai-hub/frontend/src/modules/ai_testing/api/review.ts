import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type { Review, ReviewCreate, ReviewUpdate, ReviewListData, ReviewStats } from '@/modules/ai_testing/types/review'

/** 获取评审列表 */
export function listReviews(params?: {
  project_id?: string | null
  status?: string | null
  keyword?: string | null
  page?: number
  page_size?: number
}): Promise<ApiResponse<ReviewListData>> {
  return request.get('/testing/reviews', { params })
}

/** 获取评审统计 */
export function getReviewStats(): Promise<ApiResponse<ReviewStats>> {
  return request.get('/testing/reviews/stats')
}

/** 创建评审 */
export function createReview(data: ReviewCreate): Promise<ApiResponse<Review>> {
  return request.post('/testing/reviews', data)
}

/** 获取评审详情 */
export function getReview(id: string): Promise<ApiResponse<Review>> {
  return request.get(`/testing/reviews/${id}`)
}

/** 更新评审 */
export function updateReview(id: string, data: ReviewUpdate): Promise<ApiResponse<Review>> {
  return request.put(`/testing/reviews/${id}`, data)
}

/** 删除评审 */
export function deleteReview(id: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/reviews/${id}`)
}

/** 获取评审关联用例 */
export function getReviewCases(reviewId: string): Promise<ApiResponse<import('@/modules/ai_testing/types/review').ReviewCase[]>> {
  return request.get(`/testing/reviews/${reviewId}/cases`)
}

/** 获取评审的评审人列表 */
export function getReviewReviewers(reviewId: string): Promise<ApiResponse<Array<{ id: string; name: string }>>> {
  return request.get(`/testing/reviews/${reviewId}/reviewers`)
}

/** 更新评审中单个用例的状态 */
export function updateReviewCaseStatus(reviewId: string, caseId: string, status: string, comment?: string): Promise<ApiResponse<boolean>> {
  return request.put(`/testing/reviews/${reviewId}/cases/${caseId}`, { status, comment })
}
