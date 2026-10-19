/** 定时任务模块类型 */
export type TaskModule = 'api' | 'ui' | 'app'

/** 定时任务执行日志 */
export interface ScheduledTaskLog {
  id: string
  task_id: string
  status: 'running' | 'success' | 'failed'
  duration: string
  started_at: string
  completed_at: string | null
  /** 执行引用（如生成的用例集/报告 ID） */
  exec_ref?: string | null
  /** 执行摘要（如「生成 N 条用例」） */
  summary?: string | null
}

/** 定时任务记录 */
export interface ScheduledTask {
  id: string
  name: string
  module: TaskModule
  cron_expr: string
  enabled: boolean
  /** 关联项目（AI 用例生成型任务） */
  project_id?: string | null
  /** 生成模型（provider:model 格式） */
  model?: string | null
  /** 定时生成的需求文本 */
  input_text?: string | null
  last_run_at: string | null
  next_run_at: string | null
  recent_runs?: ScheduledTaskLog[]
  created_at: string
  updated_at: string
}

/** 创建定时任务请求 */
export interface ScheduledTaskCreate {
  name: string
  module: TaskModule
  cron_expr: string
  project_id?: string | null
  model?: string | null
  input_text?: string | null
}

/** 更新定时任务请求 */
export interface ScheduledTaskUpdate {
  name?: string
  module?: TaskModule
  cron_expr?: string
  enabled?: boolean
  project_id?: string | null
  model?: string | null
  input_text?: string | null
}
