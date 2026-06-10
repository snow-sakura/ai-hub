import { ref, computed, watch, type Ref } from 'vue'
import { getTools } from '@/shared/api/models'
import type { ToolInfo } from '@/shared/types/api'

/** @ 唤起工具列表 Hook */
export function useAtMention(inputRef: Ref<string>) {
  const showToolList = ref(false)
  const toolList = ref<ToolInfo[]>([])
  const filterText = ref('')

  const filteredTools = computed(() => {
    if (!filterText.value) return toolList.value
    const q = filterText.value.toLowerCase()
    return toolList.value.filter(
      t => t.name.toLowerCase().includes(q) || t.displayName.toLowerCase().includes(q)
    )
  })

  /** 加载工具列表 */
  async function loadTools() {
    if (toolList.value.length > 0) return
    try {
      const res = await getTools()
      toolList.value = res.data || []
    } catch (e) {
      console.error('获取工具列表失败:', e)
    }
  }

  // 监听输入值变化，检测 @ 符号
  watch(inputRef, (value) => {
    const atIndex = value.lastIndexOf('@')

    if (atIndex >= 0 && (atIndex === 0 || value[atIndex - 1] === ' ')) {
      filterText.value = value.slice(atIndex + 1)
      showToolList.value = true
      loadTools()
    } else {
      showToolList.value = false
      filterText.value = ''
    }
  })

  /** 选择工具 */
  function selectTool(tool: ToolInfo) {
    const value = inputRef.value
    const atIndex = value.lastIndexOf('@')

    if (atIndex >= 0) {
      const afterAt = value.slice(atIndex)
      // 找到 @ 后面的空格或结尾
      const spaceIndex = afterAt.indexOf(' ', 1)
      const afterTool = spaceIndex >= 0 ? value.slice(atIndex + spaceIndex) : ''
      inputRef.value = value.slice(0, atIndex) + `@${tool.name} ` + afterTool
    }
    showToolList.value = false
    filterText.value = ''
  }

  return {
    showToolList,
    filteredTools,
    selectTool,
  }
}
