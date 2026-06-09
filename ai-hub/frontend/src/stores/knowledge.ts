import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { KnowledgeDoc } from '../types/knowledge'
import { getKnowledgeDocs, uploadDocument, deleteKnowledgeDoc, rebuildKnowledge } from '../api/knowledge'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const documents = ref<KnowledgeDoc[]>([])
  const isUploading = ref(false)
  const loadError = ref<string | null>(null)

  async function fetchDocuments() {
    loadError.value = null
    try {
      const res = await getKnowledgeDocs()
      documents.value = (res.data || []).map((d: any) => ({
        id: d.id,
        filename: d.filename,
        fileType: d.fileType || d.file_type,
        fileSize: d.fileSize || d.file_size,
        chunkCount: d.chunkCount || d.chunk_count,
        createdAt: d.createdAt || d.created_at,
      }))
    } catch (e) {
      loadError.value = e instanceof Error ? e.message : '获取知识库列表失败'
      console.error('获取知识库列表失败:', e)
    }
  }

  async function upload(file: File) {
    isUploading.value = true
    try {
      await uploadDocument(file)
      await fetchDocuments()
    } finally {
      isUploading.value = false
    }
  }

  async function remove(docId: string) {
    await deleteKnowledgeDoc(docId)
    documents.value = documents.value.filter(d => d.id !== docId)
  }

  async function rebuild() {
    await rebuildKnowledge()
    documents.value = []
  }

  return { documents, isUploading, loadError, fetchDocuments, upload, remove, rebuild }
})
