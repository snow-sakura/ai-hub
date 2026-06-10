import request from '@/shared/api/request'
import type { ApiResponse, ModelInfo, ToolInfo } from '@/shared/types/api'

/** 获取模型列表 */
export function getModels(): Promise<ApiResponse<ModelInfo[]>> {
  return request.get('/models')
}

/** 获取工具列表 */
export function getTools(): Promise<ApiResponse<ToolInfo[]>> {
  return request.get('/tools')
}

/** 搜索图片 */
export function searchImages(query: string, count = 3): Promise<ApiResponse<any[]>> {
  return request.get('/tools/image-search', { params: { query, count } })
}
