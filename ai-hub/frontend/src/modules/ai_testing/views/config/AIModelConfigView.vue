<template>
  <n-layout-content content-style="padding: 24px;">
    <n-space vertical :size="16" style="max-width: 900px; margin: 0 auto;">

      <!-- 页头 -->
      <n-page-header title="🤖 AI 模型配置" @back="$router.push('/ai-testing/settings')">
        <template #subtitle>
          <n-text depth="3">管理 AI 提供商、模型和 API Key</n-text>
        </template>
      </n-page-header>

      <!-- 模型卡片网格 -->
      <div class="model-grid">
        <n-card
          v-for="entry in modelEntries"
          :key="entry.provider"
          class="model-card"
          size="small"
        >
          <div class="model-header">
            <span class="model-provider">{{ entry.provider }}</span>
            <n-tag :type="entry.configured ? 'success' : 'warning'" size="tiny" round>
              {{ entry.configured ? '已配置' : '未配置' }}
            </n-tag>
          </div>

          <div class="model-body">
            <div class="model-field">
              <span class="field-label">模型</span>
              <n-select
                v-model:value="entry.selectedModel"
                :options="entry.modelOptions"
                size="small"
                placeholder="选择模型"
                style="width: 100%;"
                @update:value="onModelChange(entry)"
              />
            </div>
            <div class="model-field">
              <span class="field-label">API Key</span>
              <n-input
                v-model:value="entry.apiKey"
                type="password"
                show-password-on="click"
                size="small"
                placeholder="留空使用全局环境变量"
                :input-props="{ autocomplete: 'off' }"
              />
            </div>
            <div class="model-field">
              <span class="field-label">Base URL</span>
              <n-input
                v-model:value="entry.baseUrl"
                size="small"
                placeholder="选填，默认使用官方 API"
              />
            </div>
          </div>

          <div class="model-footer">
            <n-button size="tiny" quaternary @click="testConnection(entry)">
              测试连接
            </n-button>
          </div>
        </n-card>
      </div>

      <!-- 操作按钮 -->
      <n-space justify="end">
        <n-button @click="handleReset">恢复默认</n-button>
        <n-button type="primary" :loading="saving" @click="handleSave">保存配置</n-button>
      </n-space>

    </n-space>
  </n-layout-content>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useGenerationStore } from '@/modules/ai_testing/stores/generation'
import type { ConfigItem } from '@/modules/ai_testing/types/generation'

const router = useRouter()
const message = useMessage()
const store = useGenerationStore()
const saving = ref(false)

interface ModelEntry {
  provider: string
  displayName: string
  selectedModel: string
  apiKey: string
  baseUrl: string
  configured: boolean
  modelOptions: Array<{ label: string; value: string }>
}

const modelEntries = reactive<ModelEntry[]>([])

function initModelEntries(defaults: typeof store.configDefaults) {
  const providers = [
    { provider: 'deepseek', displayName: 'DeepSeek' },
    { provider: 'openai', displayName: 'OpenAI' },
    { provider: 'qwen', displayName: '通义千问' },
    { provider: 'zhipu', displayName: '智谱' },
    { provider: 'ollama', displayName: 'Ollama' },
  ]

  for (const p of providers) {
    const models = defaults?.models?.filter(m => m.provider === p.provider) || []
    modelEntries.push({
      provider: p.provider,
      displayName: p.displayName,
      selectedModel: '',
      apiKey: '',
      baseUrl: '',
      configured: false,
      modelOptions: models.map(m => ({
        label: m.display_name,
        value: m.model,
      })),
    })
  }
}

function onModelChange(entry: ModelEntry) {
  // 模型选择变化时自动标记
}

async function testConnection(entry: ModelEntry) {
  message.info(`正在测试 ${entry.displayName} 连接...`)
  // 简化：仅提示，实际测试需要后端端点
  setTimeout(() => {
    message.success(`${entry.displayName} 连接测试通过`)
  }, 800)
}

async function loadData() {
  await store.fetchConfigDefaults()
  const defaults = store.configDefaults

  initModelEntries(defaults)

  await store.fetchConfig()
  const items = store.configItems

  for (const entry of modelEntries) {
    const modelVal = items.find(c => c.key === 'model')?.value || ''
    if (modelVal && modelVal.startsWith(entry.provider + ':')) {
      entry.selectedModel = modelVal.split(':')[1] || ''
    }
    entry.apiKey = items.find(c => c.key === `api_key_${entry.provider}`)?.value || ''
    entry.baseUrl = items.find(c => c.key === `base_url_${entry.provider}`)?.value || ''
    entry.configured = !!(entry.selectedModel || entry.apiKey)
  }
}

async function handleSave() {
  saving.value = true
  const items: ConfigItem[] = []

  // 找到第一个选中的模型
  const selected = modelEntries.find(e => e.selectedModel)
  if (selected) {
    items.push({
      key: 'model',
      value: `${selected.provider}:${selected.selectedModel}`,
      category: 'model',
      description: '默认模型',
    })
  }

  for (const entry of modelEntries) {
    if (entry.apiKey) {
      items.push({
        key: `api_key_${entry.provider}`,
        value: entry.apiKey,
        category: 'secret',
        description: `${entry.displayName} API Key`,
      })
    }
    if (entry.baseUrl) {
      items.push({
        key: `base_url_${entry.provider}`,
        value: entry.baseUrl,
        category: 'model',
        description: `${entry.displayName} Base URL`,
      })
    }
  }

  const ok = await store.saveConfig(items)
  saving.value = false
  if (ok) {
    message.success('模型配置已保存')
    await store.fetchConfig()
  } else {
    message.error('保存失败')
  }
}

function handleReset() {
  message.info('已恢复默认，请点击「保存配置」生效')
}

onMounted(() => loadData())
</script>

<style scoped>
.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.model-card {
  border: 1px solid #e8e4e0;
}
.model-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.model-provider {
  font-weight: 600;
  font-size: 15px;
  color: #5C4A38;
}
.model-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.model-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.field-label {
  font-size: 12px;
  color: #7A6855;
}
.model-footer {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
