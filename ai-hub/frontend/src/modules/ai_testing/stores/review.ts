import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Review, ReviewCreate, ReviewUpdate, ReviewStats } from '@/modules/ai_testing/types/review'
import * as reviewApi from '@/modules/ai_testing/api/review'

export const useReviewStore = defineStore('testing-review', () => {
  const reviews = ref<Review[]>([])
  const currentReview = ref<Review | null>(null)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const isLoading = ref(false)
  const stats = ref<ReviewStats>({ pending: 0, in_progress: 0, approved: 0, rejected: 0 })

  async function fetchReviews(params?: {
    project_id?: string | null
    status?: string | null
    keyword?: string | null
    page?: number
    page_size?: number
  }) {
    isLoading.value = true
    try {
      const res = await reviewApi.listReviews(params)
      if (res.data) {
        reviews.value = res.data.items || []
        total.value = res.data.total || 0
        page.value = res.data.page || 1
        pageSize.value = res.data.page_size || 20
      }
    } catch (e) {
      console.error('获取评审列表失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchReview(id: string) {
    try {
      const res = await reviewApi.getReview(id)
      if (res.data) currentReview.value = res.data
    } catch (e) {
      console.error('获取评审详情失败:', e)
    }
  }

  async function fetchStats() {
    try {
      const res = await reviewApi.getReviewStats()
      if (res.data) stats.value = res.data
    } catch (e) {
      console.error('获取评审统计失败:', e)
    }
  }

  async function createReview(data: ReviewCreate) {
    const res = await reviewApi.createReview(data)
    return res.data
  }

  async function updateReview(id: string, data: ReviewUpdate) {
    const res = await reviewApi.updateReview(id, data)
    if (res.data) currentReview.value = res.data
    return res.data
  }

  async function deleteReview(id: string) {
    const res = await reviewApi.deleteReview(id)
    if (res.data) {
      reviews.value = reviews.value.filter(r => r.id !== id)
    }
    return res.data
  }

  return {
    reviews, currentReview, total, page, pageSize, isLoading, stats,
    fetchReviews, fetchReview, fetchStats, createReview, updateReview, deleteReview,
  }
})
