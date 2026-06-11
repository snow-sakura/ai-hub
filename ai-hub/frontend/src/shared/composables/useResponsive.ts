import { ref, computed, onMounted, onUnmounted } from 'vue'

/** 断点常量（需与 CSS 保持一致） */
export const BREAKPOINTS = {
  mobile: 480,
  tablet: 768,
  desktop: 1024,
} as const

export type Breakpoint = keyof typeof BREAKPOINTS

/**
 * 响应式断点检测 composable
 * 使用 window.matchMedia，避免 resize 事件频繁触发
 */
export function useResponsive() {
  const width = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)

  let mediaQuery: MediaQueryList | null = null

  function onChange(_e: MediaQueryListEvent | MediaQueryList) {
    width.value = window.innerWidth
  }

  onMounted(() => {
    mediaQuery = window.matchMedia(`(max-width: ${BREAKPOINTS.tablet}px)`)
    mediaQuery.addEventListener('change', onChange as any)
    // 初始化
    onChange(mediaQuery)
  })

  onUnmounted(() => {
    if (mediaQuery) {
      mediaQuery.removeEventListener('change', onChange as any)
    }
  })

  const isMobile = computed(() => width.value <= BREAKPOINTS.tablet)
  const isTablet = computed(
    () => width.value > BREAKPOINTS.mobile && width.value <= BREAKPOINTS.tablet,
  )
  const isDesktop = computed(() => width.value > BREAKPOINTS.tablet)

  return { width, isMobile, isTablet, isDesktop }
}
