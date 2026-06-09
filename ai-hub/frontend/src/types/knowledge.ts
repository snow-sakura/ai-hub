/** 知识库类型定义 */
export interface KnowledgeDoc {
  id: string
  filename: string
  fileType: string
  fileSize: number
  chunkCount: number
  createdAt: string
}
