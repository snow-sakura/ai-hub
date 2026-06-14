<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">AI 模型配置</h1>
      </div>
      <n-space :size="12">
        <n-button @click="testConnection">测试连接</n-button>
        <n-button type="primary" @click="handleSave" :loading="saving">保存配置</n-button>
      </n-space>
    </header>

    <!-- AI 提供商选择 -->
    <div class="card-section">
      <div class="card-section-title">选择 AI 提供商</div>
      <div class="provider-grid">
        <div
          v-for="p in providers"
          :key="p.id"
          class="provider-card"
          :class="{ active: selectedProvider === p.id }"
          @click="selectedProvider = p.id"
        >
          <span class="provider-icon">{{ p.icon }}</span>
          <span class="provider-name">{{ p.name }}</span>
        </div>
      </div>
    </div>

    <!-- 模型连接配置 -->
    <div class="card-section">
      <div class="card-section-title">模型连接配置</div>
      <n-form label-placement="top">
        <n-form-item label="API 密钥">
          <n-input v-model:value="form.api_key" type="password" show-password-on="click" placeholder="输入 API Key" />
        </n-form-item>
        <n-row :gutter="20">
          <n-col :span="12">
            <n-form-item label="模型选择">
              <n-select v-model:value="form.model_name" :options="modelOptions" placeholder="选择模型" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="API 地址">
              <n-input v-model:value="form.api_base_url" placeholder="API 基础地址" />
            </n-form-item>
          </n-col>
        </n-row>
        <n-row :gutter="20">
          <n-col :span="12">
            <n-form-item label="温度 (Temperature)">
              <div class="slider-wrap"><n-slider v-model:value="form.temperature" :min="0" :max="2" :step="0.1" /><span class="slider-value">{{ form.temperature.toFixed(1) }}</span></div>
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="最大 Token 数">
              <n-input-number v-model:value="form.max_tokens" :min="1" :max="128000" />
            </n-form-item>
          </n-col>
        </n-row>
      </n-form>
    </div>

    <!-- 高级设置 -->
    <div class="card-section">
      <div class="card-section-title">高级设置</div>
      <n-form label-placement="top">
        <n-row :gutter="20">
          <n-col :span="12"><n-form-item label="启用状态"><n-switch v-model:value="form.enabled" /></n-form-item></n-col>
          <n-col :span="12"><n-form-item label="排序优先级"><n-input-number v-model:value="form.sort_order" :min="0" :max="999" /></n-form-item></n-col>
        </n-row>
      </n-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { listModels, createModel, updateModel, type ModelConfigItem } from '../api/config'

const message = useMessage()
const saving = ref(false)

const providers = [
  { id: 'openai', name: 'GPT-4o', icon: '🤖' }, { id: 'claude', name: 'Claude', icon: '🟣' },
  { id: 'deepseek', name: 'DeepSeek', icon: '🔵' }, { id: 'qwen', name: '通义千问', icon: '🟢' },
  { id: 'zhipu', name: '智谱 GLM', icon: '🔷' }, { id: 'ollama', name: 'Ollama（本地）', icon: '🖥️' },
]

const selectedProvider = ref('openai')
const currentModelId = ref<string | null>(null)

const form = reactive({ provider: 'openai', model_name: '', api_key: '', api_base_url: '', temperature: 0.7, max_tokens: 4096, enabled: true, sort_order: 0 })

const modelOptions = computed(() => {
  const map: Record<string, string[]> = {
    openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    claude: ['claude-opus-4-7', 'claude-sonnet-4-6', 'claude-haiku-4-5'],
    deepseek: ['deepseek-chat', 'deepseek-reasoner'],
    qwen: ['qwen-max', 'qwen-plus', 'qwen-turbo'],
    zhipu: ['glm-4', 'glm-4v', 'glm-3-turbo'],
    ollama: ['llama3', 'qwen2', 'mistral'],
  }
  return (map[selectedProvider.value] || []).map(m => ({ label: m, value: m }))
})

async function loadData() {
  try {
    const res: any = await listModels()
    if (res.data && res.data.length > 0) {
      const first = res.data[0] as ModelConfigItem
      currentModelId.value = first.id
      Object.assign(form, { provider: first.provider, model_name: first.model_name, api_key: first.api_key, api_base_url: first.api_base_url, temperature: first.temperature, max_tokens: first.max_tokens, enabled: first.enabled, sort_order: first.sort_order })
      selectedProvider.value = first.provider
    }
  } catch { /* ignore */ }
}

async function handleSave() {
  saving.value = true
  try {
    form.provider = selectedProvider.value
    if (currentModelId.value) { await updateModel(currentModelId.value, { ...form }); message.success('配置更新成功') }
    else { const res: any = await createModel({ ...form }); currentModelId.value = res.data.id; message.success('配置创建成功') }
  } catch { message.error('保存失败') }
  finally { saving.value = false }
}

function testConnection() { message.info('连接测试功能待实现') }

onMounted(loadData)
</script>

<style scoped>
.page-wrap {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #3D2E1F;
  letter-spacing: -0.02em;
  margin: 0;
}
.card-section {
  background: #FFFDF9;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}
.card-section-title {
  font-size: 15px;
  font-weight: 600;
  color: #3D2E1F;
  margin-bottom: 16px;
}
.provider-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.provider-card {
  padding: 16px 12px;
  text-align: center;
  border-radius: 8px;
  border: 1px solid rgba(180, 150, 120, 0.12);
  cursor: pointer;
  transition: all 0.2s;
  background: #FFFDF9;
}
.provider-card:hover { border-color: #D49472; }
.provider-card.active { border-color: #C67B5C; background: rgba(198, 123, 92, 0.06); font-weight: 600; color: #C67B5C; }
.provider-icon { font-size: 28px; display: block; margin-bottom: 6px; }
.provider-name { font-size: 14px; color: #5C4A38; }
.provider-card.active .provider-name { color: #C67B5C; }
.slider-wrap { display: flex; align-items: center; gap: 12px; }
.slider-wrap :deep(.n-slider) { flex: 1; }
.slider-value { font-size: 14px; font-weight: 600; color: #C67B5C; min-width: 32px; text-align: center; }
@media (max-width: 768px) { .page-wrap { padding: 16px 12px 48px; } .provider-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
