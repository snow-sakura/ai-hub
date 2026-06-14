/** 通用轮询 Hook（支持指数退避 + 标签页不可见时暂停） */

import { onUnmounted, ref } from 'vue'

export interface UsePollingOptions {
  /** 轮询间隔（ms），默认 5000 */
  interval?: number
  /** 最小间隔，默认 5000 */
  minInterval?: number
  /** 最大间隔（指数退避上限），默认 30000 */
  maxInterval?: number
  /** 页面不可见时是否暂停，默认 true */
  pauseOnHidden?: boolean
  /** 是否立即开始，默认 true */
  immediate?: boolean
}

export function usePolling(
  fetcher: () => Promise<void>,
  options: UsePollingOptions = {},
) {
  const {
    interval = 5000,
    minInterval = 5000,
    maxInterval = 30000,
    pauseOnHidden = true,
    immediate = true,
  } = options

  let timeoutId: ReturnType<typeof setTimeout> | null = null
  let currentDelay = interval
  const isPaused = ref(false)

  async function fetch() {
    try {
      await fetcher()
      currentDelay = minInterval // 成功时重置间隔
    } catch {
      currentDelay = Math.min(currentDelay * 2, maxInterval) // 失败时指数退避
    }
  }

  function schedule() {
    stop()
    timeoutId = setTimeout(async () => {
      await fetch()
      schedule()
    }, currentDelay)
  }

  function start() {
    currentDelay = minInterval
    fetch().then(() => schedule())
  }

  function stop() {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  function refresh() {
    fetch()
  }

  // 页面可见性变化时暂停/恢复
  function onVisibilityChange() {
    if (document.hidden) {
      stop()
      isPaused.value = true
    } else {
      isPaused.value = false
      if (pauseOnHidden) schedule()
    }
  }

  if (pauseOnHidden) {
    document.addEventListener('visibilitychange', onVisibilityChange)
  }

  if (immediate) start()

  onUnmounted(() => {
    stop()
    if (pauseOnHidden) {
      document.removeEventListener('visibilitychange', onVisibilityChange)
    }
  })

  return { start, stop, refresh, isPaused }
}
