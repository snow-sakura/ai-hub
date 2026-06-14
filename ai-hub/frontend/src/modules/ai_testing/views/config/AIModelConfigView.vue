<template>
  <n-layout-content content-style="padding: 24px;">
    <n-space vertical :size="16" style="max-width: 900px; margin: 0 auto;">

      <!-- 页头 -->
      <n-page-header title="🤖 AI 模型配置" @back="$router.push('/ai-testing/settings')">
        <template #subtitle>
          <n-text depth="3">管理 AI 提供商、模型和 API Key</n-text>
        </template>
      </n-page-header>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrap">
        <n-spin size="large" />
      </div>

      <!-- 错误状态 -->
      <div v-else-if="loadError" class="error-wrap">
        <n-empty description="加载配置失败">
          <template #extra>
            <n-button type="primary" @click="loadData">重新加载</n-button>
          </template>
        </n-empty>
      </div>

      <!-- 模型卡片网格 -->
      <template v-else>
        <div class="model-grid">
          <n-card
            v-for="entry in modelEntries"
            :key="entry.provider"
            class="model-card"
            size="small"
          >
            <div class="model-header">
              <span class="model-provider">{{ entry.displayName }}</span>
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
                  :placeholder="entry.defaultBaseUrl || '选填，默认使用官方 API'"
                />
              </div>
            </div>

            <div class="model-footer">
              <n-button size="tiny" quaternary :loading="entry.testing" @click="testConnection(entry)">
                测试连接
              </n-button>
            </div>
          </n-card>
        </div>

        <!-- 操作按钮 -->
        <n-space justify="end">
          <n-button @click="handleReset" :disabled="saving">恢复默认</n-button>
          <n-button type="primary" :loading="saving" @click="handleSave">保存配置</n-button>
        </n-space>
      </template>

    </n-space>
  </n-layout-content>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useGenerationStore } from '@/modules/ai_testing/stores/generation'
import type { ConfigItem } from '@/modules/ai_testing/types/generation'
import { testConnection as testConnectionApi } from '@/modules/ai_testing/api/generation'

const router = useRouter()
const message = useMessage()
const store = useGenerationStore()

const loading = ref(true)
const loadError = ref(false)
const saving = ref(false)

interface ModelEntry {
  provider: string
  displayName: string
  selectedModel: string
  apiKey: string
  baseUrl: string
  defaultBaseUrl: string
  configured: boolean
  testing: boolean
  modelOptions: Array<{ label: string; value: string }>
}

const PROVIDERS = [
  { provider: 'deepseek', displayName: 'DeepSeek' },
  { provider: 'openai', displayName: 'OpenAI' },
  { provider: 'qwen', displayName: '通义千问' },
  { provider: 'zhipu', displayName: '智谱' },
  { provider: 'ollama', displayName: 'Ollama' },
]

const modelEntries = reactive<ModelEntry[]>([])

/**
 * 创建默认条目（清空并重新填充）
 */
function initModelEntries() {
  modelEntries.splice(0, modelEntries.length)
  const defaults = store.configDefaults
  const baseUrls = defaults?.base_urls ?? {}
  for (const p of PROVIDERS) {
    const models = defaults?.models?.filter((m: any) => m.provider === p.provider) || []
    modelEntries.push({
      provider: p.provider,
      displayName: p.displayName,
      selectedModel: '',
      apiKey: '',
      baseUrl: '',
      defaultBaseUrl: baseUrls[p.provider] || '',
      configured: false,
      testing: false,
      modelOptions: models.map((m: any) => ({
        label: m.display_name,
        value: m.model,
      })),
    })
  }
}

/**
 * 从已保存的配置项恢复每个 provider 的状态
 */
function applyConfigToEntries() {
  const items = store.configItems
  if (!items || items.length === 0) return

  for (const entry of modelEntries) {
    // 按 provider 加载各自保存的模型名：model_deepseek、model_openai …
    entry.selectedModel = items.find(c => c.key === `model_${entry.provider}`)?.value || ''
    entry.apiKey = items.find(c => c.key === `api_key_${entry.provider}`)?.value || ''
    entry.baseUrl = items.find(c => c.key === `base_url_${entry.provider}`)?.value || ''
    // 有 model 或 apiKey 即视为已配置
    entry.configured = !!(entry.selectedModel || entry.apiKey)
  }
}

async function loadData() {
  loading.value = true
  loadError.value = false
  try {
    await store.fetchConfigDefaults()
    initModelEntries()
    await store.fetchConfig()
    applyConfigToEntries()
  } catch (e) {
    console.error('加载模型配置失败:', e)
    loadError.value = true
  } finally {
    loading.value = false
  }
}

function onModelChange(entry: ModelEntry) {
  entry.configured = !!(entry.selectedModel || entry.apiKey)
}

async function testConnection(entry: ModelEntry) {
  entry.testing = true
  message.info(`正在测试 ${entry.displayName} 连接...`)
  try {
    const res = await testConnectionApi({
      provider: entry.provider,
      model_name: entry.selectedModel,
      api_key: entry.apiKey,
      base_url: entry.baseUrl,
    })
    if (res.data?.success) {
      message.success(`${entry.displayName} 连接测试通过 ✓`)
    } else {
      message.error(`${entry.displayName} 连接测试失败: ${res.message || '请检查配置'}`)
    }
  } catch (e: any) {
    message.error(`${entry.displayName} 连接测试失败: ${e?.detail?.message || e?.message || '请检查配置'}`)
  } finally {
    entry.testing = false
  }
}

async function handleSave() {
  saving.value = true
  const items: ConfigItem[] = []

  for (const entry of modelEntries) {
    // 每有模型选择，按 provider 分别保存
    if (entry.selectedModel) {
      items.push({
        key: `model_${entry.provider}`,
        value: entry.selectedModel,
        category: 'model',
        description: `${entry.displayName} 模型`,
      })
    }
    // API Key
    if (entry.apiKey) {
      items.push({
        key: `api_key_${entry.provider}`,
        value: entry.apiKey,
        category: 'secret',
        description: `${entry.displayName} API Key`,
      })
    }
    // Base URL（即使为空也保存，方便恢复默认值）
    items.push({
      key: `base_url_${entry.provider}`,
      value: entry.baseUrl,
      category: 'model',
      description: `${entry.displayName} Base URL`,
    })
  }

  // 向后兼容：保存旧格式 model = "provider:model_name"
  const firstSelected = modelEntries.find(e => e.selectedModel)
  if (firstSelected) {
    items.push({
      key: 'model',
      value: `${firstSelected.provider}:${firstSelected.selectedModel}`,
      category: 'model',
      description: '默认模型（兼容旧格式）',
    })
  }

  try {
    const ok = await store.saveConfig(items)
    if (ok) {
      message.success('模型配置已保存')
      // 保存后不重新加载，当前 entries 已包含用户输入，避免后端数据覆盖
      for (const entry of modelEntries) {
        entry.configured = !!(entry.selectedModel || entry.apiKey)
      }
    } else {
      message.error('保存失败，请重试')
    }
  } catch (e) {
    console.error('保存配置异常:', e)
    message.error('保存异常，请重试')
  } finally {
    saving.value = false
  }
}

async function handleReset() {
  await loadData()
  message.success('已恢复默认配置')
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
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}
.error-wrap {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}

@media (max-width: 768px) {
  .model-grid {
    grid-template-columns: 1fr;
  }
}
</style>
