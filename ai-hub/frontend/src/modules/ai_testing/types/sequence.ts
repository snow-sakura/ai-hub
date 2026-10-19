/** 生成序列（Sequence）类型 — 免费串行 / 付费并行 */

export type SequenceStatus =
  | 'pending' | 'running' | 'completed' | 'partial_failed' | 'cancelled' | 'interrupted'

export type SubtaskStatus =
  | 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

/** 序列内子任务（严格按 seq_index 排序） */
export interface SequenceSubtask {
  id: string
  seq_index: number
  seq_title: string | null
  model: string
  status: SubtaskStatus
  seq_stage: string | null
  generated_count: number
  error_message: string | null
  created_at: string | null
  updated_at: string | null
  /** 前端运行时状态（SSE 推送）：并行泳道槽位号 */
  slot?: number | null
}

/** 生成序列 */
export interface GenerationSequence {
  id: string
  project_id: string | null
  title: string
  requirement_text: string
  model: string
  model_tier: 'free' | 'paid'
  strategy: 'sequential' | 'parallel'
  max_parallel: number
  status: SequenceStatus
  total: number
  success_count: number
  failed_count: number
  running_count: number
  error_message: string | null
  created_by: string
  created_at: string
  updated_at: string
  subtasks?: SequenceSubtask[]
}

export interface SequenceCreateRequest {
  project_id?: string | null
  title: string
  requirement_text: string
  model: string
  subtask_count?: number | null
}

export interface SequenceListResponse {
  items: GenerationSequence[]
  total: number
  page: number
  page_size: number
}

/** SSE：sequence_subtask 事件负载 */
export interface SequenceSubtaskEvent {
  task_id: string
  seq_index: number
  status: SubtaskStatus
  stage: string | null
  slot?: number
  max_parallel?: number
  generated_count?: number
  seq_title?: string
  message?: string
}

/** SSE：sequence_progress 事件负载 */
export interface SequenceProgressEvent {
  sequence_id: string
  total: number
  success_count: number
  failed_count: number
  running_count: number
  status: SequenceStatus
  strategy?: string
  tier?: string
  max_parallel?: number
}

/** 阶段顺序（与后端 4 步流水线一致，用于卡片步骤条循环渲染） */
export const SEQ_STAGES: Array<{ key: string; label: string }> = [
  { key: 'analyze', label: '分析' },
  { key: 'write', label: '编写' },
  { key: 'review', label: '评审' },
  { key: 'revise', label: '修订' },
]

export const SEQ_STATUS_META: Record<string, { label: string; type: 'default' | 'info' | 'success' | 'warning' | 'error' }> = {
  pending: { label: '排队中', type: 'default' },
  running: { label: '执行中', type: 'info' },
  completed: { label: '成功', type: 'success' },
  failed: { label: '失败', type: 'error' },
  partial_failed: { label: '部分失败', type: 'warning' },
  cancelled: { label: '已取消', type: 'warning' },
  interrupted: { label: '已中断', type: 'warning' },
}
