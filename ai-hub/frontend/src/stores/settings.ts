import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ModelInfo } from '../types/api'
import { getModels } from '../api/models'

const DEFAULT_MODEL: ModelInfo = {
  provider: 'deepseek',
  model: 'deepseek-v4-flash',
  displayName: 'DeepSeek V4 Flash',
}

export const useSettingsStore = defineStore('settings', () => {
  const currentModel = ref<ModelInfo>({ ...DEFAULT_MODEL })
  const availableModels = ref<ModelInfo[]>([])

  async function fetchModels() {
    try {
      const res = await getModels()
      availableModels.value = (res.data || []).map(m => ({
        provider: m.provider,
        model: m.model,
        displayName: m.displayName || m.model,
      }))
      // 如果当前模型不在可用列表中，自动选中第一个
      if (availableModels.value.length > 0) {
        const currentInList = availableModels.value.find(
          m => m.provider === currentModel.value.provider && m.model === currentModel.value.model
        )
        if (!currentInList) {
          currentModel.value = { ...availableModels.value[0] }
        }
      }
    } catch (e) {
      console.error('获取模型列表失败:', e)
    }
  }

  function setModel(model: ModelInfo) {
    currentModel.value = model
  }

  return { currentModel, availableModels, fetchModels, setModel }
})
