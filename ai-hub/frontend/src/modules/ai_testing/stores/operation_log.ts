import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { OperationLog } from '@/modules/ai_testing/types/operation_log'
import * as logApi from '@/modules/ai_testing/api/operation_log'

export const useOperationLogStore = defineStore('testingOperationLog', () => {
  const logs = ref<OperationLog[]>([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchCaseLogs(caseId: string, page = 1, pageSize = 50) {
    loading.value = true
    try {
      const res = await logApi.getCaseLogs(caseId, { page, page_size: pageSize })
      if (res.data) {
        logs.value = res.data.items
        total.value = res.data.total
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchProjectLogs(projectId: string, page = 1, pageSize = 50) {
    loading.value = true
    try {
      const res = await logApi.getProjectLogs(projectId, { page, page_size: pageSize })
      if (res.data) {
        logs.value = res.data.items
        total.value = res.data.total
      }
    } finally {
      loading.value = false
    }
  }

  return { logs, total, loading, fetchCaseLogs, fetchProjectLogs }
})
