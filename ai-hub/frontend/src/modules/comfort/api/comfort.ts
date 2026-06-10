import request from '@/shared/api/request'
import type { ApiResponse } from '@/shared/types/api'
import type {
  ComfortScene,
  ComfortCharacter,
  ComfortMemory,
  EmotionStat,
  ComfortSessionParams,
} from '@/modules/comfort/types/comfort'

// ─── 场景 ───────────────────────────────────────

/** 获取所有场景 */
export function getScenes(): Promise<ApiResponse<ComfortScene[]>> {
  return request.get('/comfort/scenes')
}

/** 获取单个场景 */
export function getScene(sceneId: string): Promise<ApiResponse<ComfortScene>> {
  return request.get(`/comfort/scenes/${sceneId}`)
}

// ─── 角色 ───────────────────────────────────────

/** 获取角色列表 */
export function getCharacters(sceneId?: string): Promise<ApiResponse<ComfortCharacter[]>> {
  return request.get('/comfort/characters', { params: sceneId ? { scene_id: sceneId } : {} })
}

/** 创建角色 */
export function createCharacter(data: Partial<ComfortCharacter>): Promise<ApiResponse<ComfortCharacter>> {
  return request.post('/comfort/characters', data)
}

/** 更新角色 */
export function updateCharacter(id: string, data: Partial<ComfortCharacter>): Promise<ApiResponse<ComfortCharacter>> {
  return request.patch(`/comfort/characters/${id}`, data)
}

/** 删除角色 */
export function deleteCharacter(id: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/comfort/characters/${id}`)
}

// ─── 记忆 ───────────────────────────────────────

/** 获取会话的记忆列表 */
export function getMemories(convId: string): Promise<ApiResponse<ComfortMemory[]>> {
  return request.get(`/comfort/memories/${convId}`)
}

/** 创建记忆 */
export function createMemory(data: { conversation_id: string; content: string; memory_type?: string; importance?: number }): Promise<ApiResponse<ComfortMemory>> {
  return request.post('/comfort/memories', data)
}

/** 更新记忆 */
export function updateMemory(id: string, content: string): Promise<ApiResponse<boolean>> {
  return request.patch(`/comfort/memories/${id}`, { content })
}

/** 删除记忆 */
export function deleteMemory(id: string): Promise<ApiResponse<boolean>> {
  return request.delete(`/comfort/memories/${id}`)
}

// ─── 情绪统计 ─────────────────────────────────────

/** 获取情绪统计 */
export function getEmotionStats(startDate: string, endDate: string): Promise<ApiResponse<EmotionStat[]>> {
  return request.get('/comfort/stats', { params: { start_date: startDate, end_date: endDate } })
}

// ─── 哄哄会话 ─────────────────────────────────────

/** 创建哄哄模拟器会话 */
export function createComfortSession(params: ComfortSessionParams): Promise<ApiResponse<any>> {
  return request.post('/comfort/session', params)
}

/** 获取哄哄会话信息 */
export function getComfortSessionInfo(convId: string): Promise<ApiResponse<any>> {
  return request.get(`/comfort/session/${convId}`)
}
