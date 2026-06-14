<template>
  <div class="page-wrap">
    <n-space vertical :size="16" style="max-width: 800px; margin: 0 auto;">
      <!-- 页头 -->
      <n-page-header title="AI 评测师配置" @back="$router.push('/ai-testing/ai-tester')">
        <template #subtitle>
          <n-text depth="3">配置评测师角色、模型参数与行为</n-text>
        </template>
      </n-page-header>

      <!-- 评测师角色配置 -->
      <n-card title="评测师角色" size="small">
        <n-form ref="formRef" label-placement="top" :model="formData" :rules="formRules">
          <n-form-item label="评测师角色描述" path="roleDescription">
            <n-input
              v-model:value="formData.roleDescription"
              type="textarea"
              :rows="4"
              placeholder="例：你是一位经验丰富的软件测试工程师，擅长功能测试、边界值分析和场景覆盖评估..."
            />
          </n-form-item>
        </n-form>
      </n-card>

      <!-- 模型配置 -->
      <n-card title="模型配置" size="small">
        <n-form label-placement="top" :model="formData" label-width="120">
          <n-grid :cols="2" :x-gap="16">
            <n-grid-item>
              <n-form-item label="关联模型" path="provider">
                <n-select
                  v-model:value="formData.provider"
                  :options="providerOptions"
                  placeholder="选择模型提供商"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="模型名" path="modelName">
                <n-input v-model:value="formData.modelName" placeholder="如 deepseek-chat" />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="API Key">
                <n-input
                  v-model:value="formData.apiKey"
                  type="password"
                  show-password-on="click"
                  placeholder="输入 API Key"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="API Base URL">
                <n-input v-model:value="formData.baseUrl" placeholder="https://api.openai.com/v1" />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="Temperature">
                <n-input-number
                  v-model:value="formData.temperature"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  :precision="1"
                  style="width: 100%;"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="Max Tokens">
                <n-input-number
                  v-model:value="formData.maxTokens"
                  :min="1"
                  :max="32768"
                  :step="1"
                  style="width: 100%;"
                />
              </n-form-item>
            </n-grid-item>
          </n-grid>

          <n-space vertical :size="12" style="margin-top: 8px;">
            <n-form-item label="启用">
              <n-switch v-model:value="formData.enabled" />
            </n-form-item>
            <n-form-item label="自动评审">
              <n-switch v-model:value="formData.autoReview" />
            </n-form-item>
          </n-space>
        </n-form>
      </n-card>

      <!-- 操作按钮 -->
      <n-space justify="end" :size="12">
        <n-button @click="handleTestConnection">
          测试连接
        </n-button>
        <n-button type="primary" :loading="saving" @click="handleSave">
          保存配置
        </n-button>
      </n-space>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { getConfig, updateConfig } from '@/modules/ai_testing/api/generation'
import type { ConfigItem } from '@/modules/ai_testing/types/generation'

const router = useRouter()
const message = useMessage()
const saving = ref(false)
const formRef = ref<FormInst | null>(null)

const providerOptions = [
  { label: 'DeepSeek', value: 'deepseek' },
  { label: 'Qwen（通义千问）', value: 'qwen' },
  { label: 'SiliconFlow', value: 'siliconflow' },
  { label: 'OpenAI', value: 'openai' },
]

const formRules: FormRules = {
  roleDescription: { required: true, message: '角色描述不能为空', trigger: 'blur' },
  provider: { required: true, message: '请选择模型提供商', trigger: 'change' },
  modelName: { required: true, message: '请输入模型名', trigger: 'blur' },
}

const formData = reactive({
  roleDescription: '你是一位经验丰富的软件测试工程师，擅长功能测试、边界值分析和场景覆盖评估。请根据给定的测试用例，从功能覆盖、边界覆盖、场景完整度、步骤清晰度四个维度进行评审。',
  provider: 'deepseek',
  modelName: 'deepseek-chat',
  apiKey: '',
  baseUrl: '',
  temperature: 0.7,
  maxTokens: 4096,
  enabled: true,
  autoReview: false,
})

/** 测试连接 — 调用后端实际测试 */
async function handleTestConnection() {
  const testMsg = `作为测试工程师，请对以下用例进行快速评审：\n\n标题：登录功能验证\n步骤：1. 输入正确用户名密码 2. 点击登录\n预期：登录成功`
  try {
    const { sendMessage } = await import('@/modules/ai_testing/api/ai_tester')
    const res = await sendMessage('', { content: testMsg })
    if (res.data) {
      message.success('连接测试通过 ✓')
    } else {
      message.error('连接测试失败：未返回结果')
    }
  } catch (e: any) {
    message.error(`连接测试失败：${e?.detail?.message || e?.message || '请检查配置'}`)
  }
}

/** 保存配置 */
async function handleSave() {
  try {
    await formRef.value?.validate()
  } catch {
    message.warning('请完善表单信息')
    return
  }
  saving.value = true
  try {
    const items: ConfigItem[] = [
      { key: 'role_description', value: formData.roleDescription, category: 'ai_tester', description: '' },
      { key: 'provider', value: formData.provider, category: 'ai_tester', description: '' },
      { key: 'model_name', value: formData.modelName, category: 'ai_tester', description: '' },
      { key: 'temperature', value: String(formData.temperature), category: 'ai_tester', description: '' },
      { key: 'max_tokens', value: String(formData.maxTokens), category: 'ai_tester', description: '' },
      { key: 'enabled', value: String(formData.enabled), category: 'ai_tester', description: '' },
      { key: 'auto_review', value: String(formData.autoReview), category: 'ai_tester', description: '' },
    ]
    await updateConfig(items)
    message.success('AI 评测师配置已保存')
  } catch (e) {
    console.error('保存配置失败:', e)
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

/** 初始化：从后端加载配置 */
onMounted(async () => {
  try {
    const res = await getConfig('ai_tester')
    if (res.data) {
      for (const item of res.data) {
        switch (item.key) {
          case 'role_description':
            formData.roleDescription = item.value
            break
          case 'provider':
            formData.provider = item.value
            break
          case 'model_name':
            formData.modelName = item.value
            break
          case 'temperature':
            formData.temperature = Number(item.value)
            break
          case 'max_tokens':
            formData.maxTokens = Number(item.value)
            break
          case 'enabled':
            formData.enabled = item.value === 'true'
            break
          case 'auto_review':
            formData.autoReview = item.value === 'true'
            break
        }
      }
    }
  } catch (e) {
    console.error('加载配置失败:', e)
    // 加载失败则使用默认值
  }
})
</script>

<style scoped>
.page-wrap {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}
@media (max-width: 768px) {
  .page-wrap { padding: 16px 12px 48px; }
}
</style>
