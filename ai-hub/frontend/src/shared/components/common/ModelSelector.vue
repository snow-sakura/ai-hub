<template>
  <n-select
    :value="modelValue"
    :options="options"
    :placeholder="loading ? '加载中...' : '选择模型'"
    size="tiny"
    class="model-select"
    :consistent-menu-width="false"
    @update:value="handleChange"
  />
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useSettingsStore } from '@/shared/stores/settings'

const settingsStore = useSettingsStore()
const loading = ref(false)

onMounted(() => {
  if (settingsStore.availableModels.length === 0) {
    loading.value = true
    settingsStore.fetchModels().finally(() => {
      loading.value = false
    })
  }
})

const modelValue = computed(() =>
  `${settingsStore.currentModel.provider}:${settingsStore.currentModel.model}`
)

const options = computed(() => {
  const list = settingsStore.availableModels.map(m => ({
    label: m.displayName,
    value: `${m.provider}:${m.model}`,
  }))
  // 异步加载完成前，至少显示当前选中的模型
  if (list.length === 0 && settingsStore.currentModel.provider) {
    list.push({
      label: settingsStore.currentModel.displayName,
      value: `${settingsStore.currentModel.provider}:${settingsStore.currentModel.model}`,
    })
  }
  return list
})

function handleChange(val: string) {
  const [provider, model] = val.split(':')
  const found = settingsStore.availableModels.find(
    m => m.provider === provider && m.model === model
  )
  if (found) {
    settingsStore.setModel(found)
  }
}
</script>

<style scoped>
.model-select {
  width: 200px;
  min-width: 200px;
  flex-shrink: 0;
}

.model-select :deep(.n-base-selection-input) {
  text-align: center;
  font-size: 12px;
  font-weight: 500;
}

.model-select :deep(.n-select-menu .n-base-select-option) {
  font-size: 12px;
  padding: 6px 12px;
}

.model-select :deep(.n-base-selection) {
  border-radius: 15px;
  background: var(--bg-secondary);
  border: 1px solid rgba(180, 150, 120, 0.2);
  height: 30px;
  min-height: 30px;
}

.model-select :deep(.n-base-selection:hover) {
  border-color: rgba(198, 123, 92, 0.3);
}

.model-select :deep(.n-base-selection-label) {
  font-size: 12px;
  justify-content: center;
}

.model-select :deep(.n-base-selection-label__input) {
  text-align: center;
}

.model-select :deep(.n-base-selection-input) {
  text-align: center;
}

.model-select :deep(.n-base-suffix) {
  display: none;
}
</style>
