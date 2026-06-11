import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { CaseAttachment } from '@/modules/ai_testing/types/attachment'
import * as attachmentApi from '@/modules/ai_testing/api/attachment'

export const useAttachmentStore = defineStore('testingAttachment', () => {
  const attachments = ref<CaseAttachment[]>([])
  const loading = ref(false)

  async function fetchAttachments(caseId: string) {
    loading.value = true
    try {
      const res = await attachmentApi.getAttachments(caseId)
      attachments.value = res.data || []
    } finally {
      loading.value = false
    }
  }

  async function upload(caseId: string, file: File): Promise<boolean> {
    try {
      const res = await attachmentApi.uploadAttachment(caseId, file)
      if (res.data) {
        attachments.value.push(res.data)
        return true
      }
    } catch { /* ignore */ }
    return false
  }

  async function remove(attachmentId: string) {
    try {
      await attachmentApi.deleteAttachment(attachmentId)
      attachments.value = attachments.value.filter(a => a.id !== attachmentId)
    } catch { /* ignore */ }
  }

  return { attachments, loading, fetchAttachments, upload, remove }
})
