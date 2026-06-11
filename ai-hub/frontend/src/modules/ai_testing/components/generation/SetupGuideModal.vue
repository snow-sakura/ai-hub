<template>
  <n-modal
    :show="show"
    preset="card"
    title="📋 AI 生成配置检查"
    style="max-width: 520px;"
    :mask-closable="true"
    @update:show="$emit('update:show', $event)"
  >
    <n-space vertical :size="12">
      <!-- 模型配置 -->
      <n-card size="small" :bordered="false" style="background: var(--n-color-modal);">
        <template #header>
          <n-space align="center" :size="8">
            <span>🤖 模型配置</span>
            <n-tag v-if="modelReady" type="success" size="small">就绪</n-tag>
            <n-tag v-else type="warning" size="small">需配置</n-tag>
          </n-space>
        </template>
        <n-space vertical :size="6">
          <n-text depth="3" style="font-size: 13px;">
            当前模型：
            <n-tag v-if="currentModel" size="small" type="info">{{ currentModel }}</n-tag>
            <n-text v-else type="warning">未选择</n-text>
          </n-text>
          <n-text v-if="!modelReady" depth="3" style="font-size: 12px; color: var(--n-warning-color);">
            请先在配置页面选择 AI 模型并确保 API Key 已设置。
          </n-text>
        </n-space>
      </n-card>

      <!-- 提示词配置 -->
      <n-card size="small" :bordered="false" style="background: var(--n-color-modal);">
        <template #header>
          <n-space align="center" :size="8">
            <span>📝 提示词</span>
            <n-tag v-if="promptReady" type="success" size="small">就绪</n-tag>
            <n-tag v-else type="info" size="small">使用默认</n-tag>
          </n-space>
        </template>
        <n-text depth="3" style="font-size: 13px;">
          {{ promptReady ? '已自定义提示词模板。' : '使用内置默认提示词，可在配置页面自定义。' }}
        </n-text>
      </n-card>

      <!-- 生成行为配置 -->
      <n-card size="small" :bordered="false" style="background: var(--n-color-modal);">
        <template #header>
          <n-space align="center" :size="8">
            <span>🎛️ 生成行为</span>
            <n-tag v-if="behaviorReady" type="success" size="small">就绪</n-tag>
            <n-tag v-else type="info" size="small">使用默认</n-tag>
          </n-space>
        </template>
        <n-text depth="3" style="font-size: 13px;">
          {{ behaviorReady ? '已自定义生成参数。' : '使用默认行为配置，可在配置页面调整。' }}
        </n-text>
      </n-card>

      <!-- 首次使用提示 -->
      <n-alert
        v-if="!modelReady"
        type="warning"
        :bordered="false"
        style="font-size: 13px;"
      >
        模型未配置，AI 生成功能无法使用。请点击下方按钮前往配置页面。
      </n-alert>

      <n-alert v-else type="success" :bordered="false" style="font-size: 13px;">
        配置就绪，可以开始使用 AI 用例生成功能！
      </n-alert>
    </n-space>

    <template #footer>
      <n-space justify="space-between">
        <n-button @click="$emit('update:show', false)">关闭</n-button>
        <n-space>
          <n-button
            v-if="!modelReady"
            type="primary"
            @click="goToSettings"
          >
            前往配置页面 →
          </n-button>
          <n-button
            v-else
            type="primary"
            @click="$emit('update:show', false)"
          >
            开始使用
          </n-button>
        </n-space>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGenerationStore } from '@/modules/ai_testing/stores/generation'
import type { ConfigItem } from '@/modules/ai_testing/types/generation'

defineProps<{ show: boolean }>()
defineEmits<{ 'update:show': [value: boolean] }>()

const router = useRouter()
const store = useGenerationStore()

const currentModel = computed(() => {
  const item = store.configItems.find((c: ConfigItem) => c.key === 'model')
  return item?.value || ''
})

const modelReady = computed(() => !!currentModel.value)
const promptReady = computed(() =>
  store.configItems.some((c: ConfigItem) => c.category === 'prompt' && !!c.value)
)
const behaviorReady = computed(() =>
  store.configItems.some((c: ConfigItem) => c.category === 'behavior' && !!c.value)
)

function goToSettings() {
  router.push('/ai-testing/settings')
}

onMounted(() => {
  store.fetchConfig()
})
</script>
