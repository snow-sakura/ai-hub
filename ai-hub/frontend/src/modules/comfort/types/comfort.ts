/** 哄哄模拟器类型定义 */

/** 场景 */
export interface ComfortScene {
  id: string
  name: string
  description: string
  icon: string
  initial_prompt: string
  difficulty_default: number
  tags: string[]
  sort_order: number
  is_builtin: boolean
}

/** 角色 */
export interface ComfortCharacter {
  id: string
  name: string
  age: number | null
  identity: string
  personality_tags: string[]
  speaking_style: string
  avatar_emoji: string
  backstory: string
  scene_id: string | null
  is_builtin: boolean
}

/** 记忆 */
export interface ComfortMemory {
  id: string
  conversation_id: string
  content: string
  memory_type: 'fact' | 'preference' | 'event'
  importance: number
  created_at: string
}

/** 情绪分析结果 */
export interface EmotionData {
  label: string
  intensity: number
  emoji: string
  message_index?: number
}

/** 原谅值数据 */
export interface ForgivenessData {
  current: number
  delta: number
  reason: string
  trend: 'up' | 'down' | 'stable'
}

/** 情绪统计 */
export interface EmotionStat {
  id: string
  user_date: string
  emotion_label: string
  avg_intensity: number
  count: number
  comfort_score: number | null
}

/** 哄哄会话元数据 */
export interface ComfortMetadata {
  scene_id: string
  scene_name: string
  character_id: string
  character_name: string
  difficulty: number
  forgiveness: number
  emotion_log: Array<{ label: string; intensity: number; turn: number }>
  turn_count: number
}

/** 哄哄会话创建参数 */
export interface ComfortSessionParams {
  scene_id: string
  character_id: string
  difficulty: number
  title?: string
}
