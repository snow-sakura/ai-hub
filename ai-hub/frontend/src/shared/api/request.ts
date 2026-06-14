import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 全局 pending 请求追踪，用于组件卸载时取消
const _pendingRequests = new Map<string, AbortController>()

/**
 * 创建可取消的请求配置
 * @param key 请求唯一标识（用于取消时查找）
 */
export function createRequestSignal(key: string): { signal: AbortSignal; cancel: () => void } {
  // 取消同 key 的旧请求（避免竞态）
  const existing = _pendingRequests.get(key)
  if (existing) existing.abort()

  const controller = new AbortController()
  _pendingRequests.set(key, controller)

  return {
    signal: controller.signal,
    cancel: () => {
      controller.abort()
      _pendingRequests.delete(key)
    },
  }
}

// 清理所有 pending 请求（组件生命周期结束时调用）
export function cancelAllRequests() {
  for (const [key, ctrl] of _pendingRequests) {
    ctrl.abort()
    _pendingRequests.delete(key)
  }
}

// ── 响应拦截器 ─────────────────────────────────────────
request.interceptors.response.use(
  (response) => {
    // 请求完成后从追踪 Map 中移除
    const key = response.config.headers?.['X-Request-Key'] as string | undefined
    if (key) _pendingRequests.delete(key)
    return response.data
  },
  async (error) => {
    // 被 AbortController 取消的请求静默处理
    if (axios.isCancel(error)) {
      return Promise.reject(new DOMException('Aborted', 'AbortError'))
    }

    // 自动重试：网络错误或5xx，最多重试1次
    const config = error.config
    if (!config || config._retryCount >= 1) {
      const detail = error.response?.data?.detail
      const message = typeof detail === 'string' ? detail : detail?.message || error.message
      console.error('API Error:', message)
      return Promise.reject(error)
    }
    config._retryCount = (config._retryCount || 0) + 1
    console.warn(`API 请求重试第 ${config._retryCount} 次:`, error.message)
    await new Promise(r => setTimeout(r, 1000 * config._retryCount))
    return request(config)
  }
)

export default request
