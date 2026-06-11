import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { CaseComment, CommentCreate } from '@/modules/ai_testing/types/comment'
import * as commentApi from '@/modules/ai_testing/api/comment'

export const useCommentStore = defineStore('testingComment', () => {
  const comments = ref<CaseComment[]>([])
  const loading = ref(false)

  async function fetchComments(caseId: string) {
    loading.value = true
    try {
      const res = await commentApi.getComments(caseId)
      comments.value = res.data || []
    } finally {
      loading.value = false
    }
  }

  async function create(caseId: string, data: CommentCreate): Promise<boolean> {
    try {
      const res = await commentApi.createComment(caseId, data)
      if (res.data) {
        comments.value.push(res.data)
        return true
      }
    } catch { /* ignore */ }
    return false
  }

  async function update(commentId: string, content: string) {
    try {
      await commentApi.updateComment(commentId, content)
      const idx = comments.value.findIndex(c => c.id === commentId)
      if (idx !== -1) comments.value[idx].content = content
    } catch { /* ignore */ }
  }

  async function remove(commentId: string) {
    try {
      await commentApi.deleteComment(commentId)
      comments.value = comments.value.filter(c => c.id !== commentId)
    } catch { /* ignore */ }
  }

  return { comments, loading, fetchComments, create, update, remove }
})
