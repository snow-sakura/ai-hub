import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type {
  GenerationTask,
  GenerationResult,
  GenerateRequest,
  ConfigItem,
  ConfigCheckResponse,
  ConfigDefaults,
  DocumentUploadResponse,
} from '@/modules/ai_testing/types/generation'

// ─── AI 生成 ──────────────────────────────────────

/** 创建 AI 生成任务 */
export function createGenerationTask(data: GenerateRequest): Promise<ApiResponse<GenerationTask>> {
  return request.post('/testing/generate', data)
}

/** 获取生成任务状态 */
export function getGenerationTask(taskId: string): Promise<ApiResponse<GenerationTask>> {
  return request.get(`/testing/generate/${taskId}`)
}

/** 获取生成任务的所有阶段结果 */
export function getGenerationResults(taskId: string): Promise<ApiResponse<GenerationResult[]>> {
  return request.get(`/testing/generate/${taskId}/results`)
}

/** 将 AI 生成的用例保存到用例库 */
export function saveGeneratedCases(data: {
  task_id: string
  project_id?: string | null
  cases: Array<Record<string, unknown>>
}): Promise<ApiResponse<{ saved_count: number; ids: string[] }>> {
  return request.post('/testing/generate/save-cases', data)
}

/** 获取生成任务列表 */
export function listGenerationTasks(params: {
  project_id?: string | null
  status?: string | null
  keyword?: string | null
  page?: number
  page_size?: number
}): Promise<ApiResponse<{ items: GenerationTask[]; total: number; page: number; page_size: number }>> {
  return request.get('/testing/generate/tasks', { params })
}

/** 删除生成任务 */
export function deleteGenerationTask(taskId: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/testing/generate/tasks/${taskId}`)
}

/** 更新生成任务状态 */
export function updateTaskStatus(taskId: string, status: string): Promise<ApiResponse<boolean>> {
  return request.put(`/testing/generate/tasks/${taskId}/status`, { status })
}

/** 上传文档并解析内容 */
export function uploadDocument(
  file: File
): Promise<ApiResponse<DocumentUploadResponse>> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/testing/generate/upload-doc', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// ─── 配置 ────────────────────────────────────────

/** 获取配置列表 */
export function getConfig(category?: string | null): Promise<ApiResponse<ConfigItem[]>> {
  return request.get('/testing/config', { params: category ? { category } : {} })
}

/** 批量更新配置 */
export function updateConfig(items: ConfigItem[]): Promise<ApiResponse<boolean>> {
  return request.put('/testing/config', { items })
}

/** 检查配置状态 */
export function checkConfig(): Promise<ApiResponse<ConfigCheckResponse>> {
  return request.get('/testing/config/check')
}

/** 获取配置默认值（默认提示词 + 可用模型列表） */
export function getConfigDefaults(): Promise<ApiResponse<ConfigDefaults>> {
  return request.get('/testing/config/defaults')
}
