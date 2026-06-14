/** 认证 API */
import request from './request'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  password: string
  display_name?: string
  email?: string
}

export interface TokenResult {
  access_token: string
  token_type: string
  expires_in: number
}

/** 登录 */
export async function login(data: LoginData): Promise<TokenResult> {
  const res: any = await request.post('/auth/login', data)
  return res.data
}

/** 注册 */
export async function register(data: RegisterData): Promise<{ access_token: string } & Record<string, any>> {
  const res: any = await request.post('/auth/register', data)
  return res.data
}

/** 获取当前用户信息 */
export async function getCurrentUser(): Promise<Record<string, any>> {
  const res: any = await request.get('/auth/me')
  return res.data
}
