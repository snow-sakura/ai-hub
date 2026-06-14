/** AI Testing 生成任务相关类型 */

/** 生成阶段 */
export type GenerationStage = 'analyze' | 'write' | 'review' | 'revise' | 'final'

/** 任务状态 */
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed'

/** 输出模式 */
export type OutputMode = 'stream' | 'complete'

/** 生成任务 */
export interface GenerationTask {
  id: string
  project_id: string | null
  project_name?: string
  input_text: string
  requirement_title: string
  file_name: string | null
  file_type: string | null
  model: string
  status: TaskStatus
  generated_count: number
  error_message: string | null
  has_saved_cases?: boolean
  created_at: string
  updated_at: string
}

/** 生成阶段结果 */
export interface GenerationResult {
  id: string
  task_id: string
  stage: GenerationStage
  content: string
  created_at: string
}

/** 生成请求参数 */
export interface GenerateRequest {
  project_id?: string | null
  requirement_title?: string
  input_text?: string
  file_path?: string | null
  file_type?: string | null
  file_name?: string | null
  model?: string
  output_mode?: OutputMode
}

/** 配置检查项 */
export interface ConfigCheckItem {
  key: string
  label: string
  category: string
  status: 'ok' | 'missing'
  message: string
}

/** 配置检查结果 */
export interface ConfigCheckResponse {
  items: ConfigCheckItem[]
  all_passed: boolean
}

/** 文档上传响应 */
export interface DocumentUploadResponse {
  text: string
  file_name: string
  file_type: string
  file_path: string
}

/** 配置项 */
export interface ConfigItem {
  key: string
  value: string
  category: string
  description: string
}

/** 配置默认值（来自后端 /config/defaults） */
export interface ConfigDefaults {
  prompts: Record<string, string>  // { analyze, write, review, revise }
  models: Array<{ provider: string; model: string; display_name: string }>
  base_urls?: Record<string, string>  // provider → 默认 API Base URL
}

/** SSE 生成事件类型 */
export type GenerationSseEvent =
  | 'testing_stage'
  | 'testing_token'
  | 'testing_review'
  | 'testing_progress'
  | 'testing_save_progress'
  | 'testing_done'
  | 'testing_error'
