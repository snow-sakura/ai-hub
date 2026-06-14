/** 系统管理 API */
import request from './request'

/** 获取系统统计概览 */
export async function getSystemStats(): Promise<{
  user_count: number
  role_count: number
  active_sessions: number
  audit_log_count: number
}> {
  const res: any = await request.get('/system/stats')
  return res.data
}
