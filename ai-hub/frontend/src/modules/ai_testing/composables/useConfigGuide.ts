import { ref, computed } from 'vue'
import { checkConfig } from '@/modules/ai_testing/api/generation'
import type { ConfigCheckResponse, ConfigCheckItem } from '@/modules/ai_testing/types/generation'

/** 配置引导状态管理 */
export function useConfigGuide() {
  const showGuide = ref(false)
  const configStatus = ref<ConfigCheckResponse | null>(null)
  const loading = ref(false)

  /** 5 项配置检查 */
  const ITEMS = [
    { key: 'model', label: '默认模型', category: 'model' },
    { key: 'analyze_prompt', label: '需求分析提示词', category: 'prompt' },
    { key: 'write_prompt', label: '用例编写提示词', category: 'prompt' },
    { key: 'review_prompt', label: 'AI 评审提示词', category: 'prompt' },
    { key: 'revise_prompt', label: '用例修订提示词', category: 'prompt' },
  ]

  const checkItems = computed<ConfigCheckItem[]>(() => {
    if (!configStatus.value) return ITEMS.map(i => ({ ...i, status: 'missing' as const, message: '待检查' }))
    const map = new Map(configStatus.value.items.map(i => [i.key, i]))
    return ITEMS.map(i => map.get(i.key) || { ...i, status: 'missing' as const, message: '未配置' })
  })

  const allPassed = computed(() => checkItems.value.every(i => i.status === 'ok'))
  const passedCount = computed(() => checkItems.value.filter(i => i.status === 'ok').length)

  async function check() {
    loading.value = true
    try {
      const res = await checkConfig()
      configStatus.value = res.data || null
    } catch {
      configStatus.value = null
    } finally {
      loading.value = false
    }
  }

  function open() {
    showGuide.value = true
    check()
  }

  function close() {
    showGuide.value = false
  }

  return {
    showGuide,
    configStatus,
    checkItems,
    allPassed,
    passedCount,
    loading,
    check,
    open,
    close,
  }
}
