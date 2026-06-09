/** 通用 API 响应类型 */
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface ModelInfo {
  provider: string
  model: string
  displayName: string
}

export interface ToolInfo {
  name: string
  displayName: string
  description: string
  icon: string
  category: string
}
