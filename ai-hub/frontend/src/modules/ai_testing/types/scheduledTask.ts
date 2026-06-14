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
}

/** 定时任务记录 */
export interface ScheduledTask {
  id: string
  name: string
  module: TaskModule
  cron_expr: string
  enabled: boolean
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
}

/** 更新定时任务请求 */
export interface ScheduledTaskUpdate {
  name?: string
  module?: TaskModule
  cron_expr?: string
  enabled?: boolean
}
