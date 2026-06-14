<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">AI 聊天室配置</h1>
      </div>
      <n-space :size="12">
        <n-button @click="handleReset">重置</n-button>
        <n-button type="primary" @click="handleSave" :loading="saving">保存配置</n-button>
      </n-space>
    </header>

    <div class="card-section">
      <div class="card-section-title">聊天室参数配置</div>
      <n-spin :show="loading">
        <n-form label-placement="top">
          <n-form-item label="模型提供商"><n-select v-model:value="form.model_provider" :options="providerOptions" @update:value="onProviderChange" /></n-form-item>
          <n-form-item label="模型名称"><n-select v-model:value="form.model_name" :options="currentModelOptions" /></n-form-item>
          <n-divider />
          <n-row :gutter="20">
            <n-col :span="8"><n-form-item label="最大历史消息数"><n-input-number v-model:value="form.max_history" :min="0" :max="200" /></n-form-item></n-col>
            <n-col :span="8"><n-form-item label="温度 (Temperature)"><div class="slider-wrap"><n-slider v-model:value="form.temperature" :min="0" :max="2" :step="0.1" /><span class="slider-value">{{ form.temperature.toFixed(1) }}</span></div></n-form-item></n-col>
            <n-col :span="8"><n-form-item label="RAG 检索数量"><n-input-number v-model:value="form.rag_top_k" :min="1" :max="20" /></n-form-item></n-col>
          </n-row>
          <n-row :gutter="20">
            <n-col :span="8"><n-form-item label="启用 RAG 知识库"><n-switch v-model:value="form.enable_rag" /></n-form-item></n-col>
            <n-col :span="8"><n-form-item label="启用联网搜索"><n-switch v-model:value="form.enable_web_search" /></n-form-item></n-col>
          </n-row>
          <n-divider />
          <n-form-item label="系统提示词"><n-input v-model:value="form.system_prompt" type="textarea" :rows="6" placeholder="自定义系统提示词（可选）" /></n-form-item>
        </n-form>
      </n-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { getChatConfig, updateChatConfig } from '../api/config'

const message = useMessage()
const loading = ref(false)
const saving = ref(false)

const providerOptions = [
  { label: 'OpenAI', value: 'openai' }, { label: 'DeepSeek', value: 'deepseek' },
  { label: '通义千问', value: 'qwen' }, { label: '智谱 GLM', value: 'zhipu' },
  { label: 'Claude', value: 'claude' }, { label: 'Ollama（本地）', value: 'ollama' },
]

const modelMap: Record<string, string[]> = {
  openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'], deepseek: ['deepseek-chat', 'deepseek-reasoner'],
  qwen: ['qwen-max', 'qwen-plus', 'qwen-turbo'], zhipu: ['glm-4', 'glm-4v', 'glm-3-turbo'],
  claude: ['claude-opus-4-7', 'claude-sonnet-4-6', 'claude-haiku-4-5'], ollama: ['llama3', 'qwen2', 'mistral'],
}

const form = reactive({ model_provider: 'deepseek', model_name: 'deepseek-chat', system_prompt: '', max_history: 50, enable_rag: true, rag_top_k: 3, enable_web_search: false, temperature: 0.7 })
const currentModelOptions = computed(() => (modelMap[form.model_provider] || []).map(m => ({ label: m, value: m })))
function onProviderChange(val: string) { const models = modelMap[val] || []; if (models.length > 0) form.model_name = models[0] }
async function loadData() { loading.value = true; try { const res: any = await getChatConfig(); if (res.data) Object.assign(form, res.data) } catch { /* ignore */ } finally { loading.value = false } }
async function handleSave() { saving.value = true; try { await updateChatConfig({ ...form }); message.success('保存成功') } catch { message.error('保存失败') } finally { saving.value = false } }
function handleReset() { Object.assign(form, { model_provider: 'deepseek', model_name: 'deepseek-chat', system_prompt: '', max_history: 50, enable_rag: true, rag_top_k: 3, enable_web_search: false, temperature: 0.7 }) }
onMounted(loadData)
</script>

<style scoped>
.page-wrap { max-width: 900px; margin: 0 auto; padding: 32px 24px 64px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-title { font-size: 24px; font-weight: 700; color: #3D2E1F; letter-spacing: -0.02em; margin: 0; }
.card-section { background: #FFFDF9; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 12px; padding: 24px; margin-bottom: 20px; }
.card-section-title { font-size: 15px; font-weight: 600; color: #3D2E1F; margin-bottom: 16px; }
.slider-wrap { display: flex; align-items: center; gap: 12px; }
.slider-wrap :deep(.n-slider) { flex: 1; }
.slider-value { font-size: 14px; font-weight: 600; color: #C67B5C; min-width: 32px; text-align: center; }
@media (max-width: 768px) { .page-wrap { padding: 16px 12px 48px; } }
</style>
