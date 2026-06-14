<template>
  <div class="page-wrap">
    <n-space vertical :size="16" style="max-width: 900px; margin: 0 auto;">
      <!-- 页头 -->
      <n-page-header title="AI 评测师配置" @back="$router.push('/ai-testing/config')">
        <template #subtitle>
          <n-text depth="3">配置评测维度、评分标准与评审模板</n-text>
        </template>
      </n-page-header>

      <!-- 基础模型配置 -->
      <n-card title="模型配置" size="small">
        <n-form label-placement="top" :model="formData" label-width="120">
          <n-grid :cols="2" :x-gap="16">
            <n-grid-item>
              <n-form-item label="关联模型">
                <n-select
                  v-model:value="formData.provider"
                  :options="providerOptions"
                  placeholder="选择模型提供商"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="模型名">
                <n-input v-model:value="formData.modelName" placeholder="如 deepseek-chat" />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="API Key">
                <n-input v-model:value="formData.apiKey" type="password" show-password-on="click" placeholder="输入 API Key" />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="API Base URL">
                <n-input v-model:value="formData.baseUrl" :placeholder="currentDefaultBaseUrl || 'https://api.openai.com/v1'" />
              </n-form-item>
            </n-grid-item>
          </n-grid>
        </n-form>
      </n-card>

      <!-- 评分阈值与模板 -->
      <n-card title="评分阈值与模板" size="small">
        <n-form label-placement="top" :model="formData">
          <n-grid :cols="2" :x-gap="16">
            <n-grid-item>
              <n-form-item label="最小通过分数">
                <n-input-number
                  v-model:value="formData.minPassScore"
                  :min="0"
                  :max="100"
                  :step="1"
                  style="width: 100%;"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="启用开关">
                <n-switch v-model:value="formData.enabled" />
              </n-form-item>
            </n-grid-item>
          </n-grid>

          <n-form-item label="自动评审提示词模板">
            <n-input
              v-model:value="formData.reviewPromptTemplate"
              type="textarea"
              :rows="6"
              placeholder="请输入自动评审时使用的提示词模板..."
            />
          </n-form-item>

          <n-form-item label="评审报告模板">
            <n-input
              v-model:value="formData.reportTemplate"
              type="textarea"
              :rows="4"
              placeholder="请输入评审报告的生成模板..."
            />
          </n-form-item>
        </n-form>
      </n-card>

      <!-- 评测标准列表 -->
      <n-card title="评测标准列表" size="small">
        <n-table :single-line="false" size="small">
          <thead>
            <tr>
              <th>维度名</th>
              <th>权重</th>
              <th>描述</th>
              <th style="width: 100px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(dim, idx) in dimensions" :key="idx">
              <td>{{ dim.name }}</td>
              <td>
                <n-tag :type="dim.weight >= 70 ? 'success' : dim.weight >= 40 ? 'warning' : 'default'" size="small">
                  {{ dim.weight }}%
                </n-tag>
              </td>
              <td>{{ dim.description }}</td>
              <td>
                <n-button text size="small" type="primary" @click="handleEditDimension(idx)">编辑</n-button>
                <n-button text size="small" type="error" @click="dimensions.splice(idx, 1)">删除</n-button>
              </td>
            </tr>
          </tbody>
        </n-table>
        <div style="margin-top: 12px;">
          <n-button size="small" @click="handleAddDimension">+ 添加维度</n-button>
        </div>
      </n-card>

      <!-- 操作按钮 -->
      <n-space justify="end" :size="12">
        <n-button :loading="testing" @click="handleTestConnection">测试连接</n-button>
        <n-button type="primary" :loading="saving" @click="handleSave">保存配置</n-button>
      </n-space>
      <!-- 维度编辑弹窗 -->
      <n-modal v-model:show="showDimModal" preset="dialog" title="编辑维度" :style="{ width: '480px' }">
        <n-form label-placement="top">
          <n-form-item label="维度名称">
            <n-input v-model:value="editDimData.name" placeholder="输入维度名称" />
          </n-form-item>
          <n-form-item label="权重（0-100）">
            <n-slider v-model:value="editDimData.weight" :min="0" :max="100" :step="5" />
            <span style="margin-left: 12px; font-size: 13px; color: #7A6855;">{{ editDimData.weight }}%</span>
          </n-form-item>
          <n-form-item label="描述">
            <n-input
              v-model:value="editDimData.description"
              type="textarea"
              :rows="3"
              placeholder="描述该维度的评估标准"
            />
          </n-form-item>
        </n-form>
        <template #action>
          <n-button @click="showDimModal = false">取消</n-button>
          <n-button type="primary" @click="handleDimSave">保存</n-button>
        </template>
      </n-modal>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { getConfig, updateConfig, getConfigDefaults } from '@/modules/ai_testing/api/generation'
import type { ConfigItem } from '@/modules/ai_testing/types/generation'
import { findConfigValue } from '@/modules/ai_testing/utils/config'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const saving = ref(false)
const testing = ref(false)

const providerOptions = [
  { label: 'DeepSeek', value: 'deepseek' },
  { label: 'Qwen（通义千问）', value: 'qwen' },
  { label: 'OpenAI', value: 'openai' },
  { label: '智谱 GLM', value: 'zhipu' },
  { label: 'Ollama（本地）', value: 'ollama' },
]

/** 各 provider 的默认 Base URL */
const defaultBaseUrls: Record<string, string> = {
  deepseek: 'https://api.deepseek.com/v1',
  openai: 'https://api.openai.com/v1',
  qwen: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  zhipu: 'https://open.bigmodel.cn/api/paas/v4',
  ollama: 'http://localhost:11434',
}

/** 各 provider 的默认模型名 */
const defaultModelNames: Record<string, string> = {
  deepseek: 'deepseek-v4-flash',
  openai: 'gpt-4o',
  qwen: 'qwen3.7-plus',
  zhipu: 'glm-4-flash',
  ollama: 'qwen2.5:7b',
}

interface Dimension {
  name: string
  weight: number
  description: string
}

const dimensions = reactive<Dimension[]>([
  { name: '功能覆盖', weight: 80, description: '检查用例是否覆盖了所有核心功能点和需求规格' },
  { name: '边界覆盖', weight: 60, description: '评估用例对输入边界、阈值和异常条件的覆盖程度' },
  { name: '场景完整度', weight: 70, description: '判断用例是否涵盖正常场景、异常场景和业务流转' },
  { name: '步骤清晰度', weight: 50, description: '评估测试步骤的描述是否清晰、可执行、步骤完整' },
])

const formData = reactive({
  provider: 'deepseek',
  modelName: 'deepseek-v4-flash',
  apiKey: '',
  baseUrl: '',
  minPassScore: 60,
  enabled: true,
  reviewPromptTemplate: '请根据以下评测维度对测试用例进行评审：\n1. 功能覆盖：检查用例是否覆盖了所有核心功能点\n2. 边界覆盖：评估用例对输入边界的覆盖程度\n3. 场景完整度：判断用例场景是否完整\n4. 步骤清晰度：评估步骤是否清晰可执行\n\n请对每个维度打分（0-100），并给出总分和改善建议。',
  reportTemplate: '# 测试用例评审报告\n\n## 总体评分：{total_score}/100\n\n### 维度评分\n{维度评分表格}\n\n### 改善建议\n{改善建议列表}\n\n---\n*由 AI 评测师自动生成*',
})

/** 当前 provider 的默认 Base URL（用于 placeholder） */
const currentDefaultBaseUrl = computed(() => defaultBaseUrls[formData.provider] || '')

/** 切换 provider 时自动更新模型名和 Base URL */
watch(() => formData.provider, (newProvider) => {
  // 仅当用户手动切换时更新默认值（onMounted 加载时不覆盖已持久化的值）
  formData.modelName = defaultModelNames[newProvider] || formData.modelName
  if (!formData.baseUrl) {
    formData.baseUrl = defaultBaseUrls[newProvider] || ''
  }
})

async function handleTestConnection() {
  testing.value = true
  try {
    const { sendMessage } = await import('@/modules/ai_testing/api/ai_tester')
    const res = await sendMessage('', {
      content: `作为测试评审专家，用一句话回复"连接测试成功"即可。使用模型: ${formData.modelName}`,
    })
    if (res.data?.content) {
      message.success(`连接测试通过 ✓ (${res.data.content.slice(0, 30)}...)`)
    } else {
      message.error('连接测试失败：未返回有效结果')
    }
  } catch (e: any) {
    message.error(`连接测试失败: ${e?.detail?.message || e?.message || '请检查配置'}`)
  } finally {
    testing.value = false
  }
}

onMounted(async () => {
  try {
    // 加载后端默认配置（含默认 Base URL）
    try {
      const defaultsRes = await getConfigDefaults()
      const defaults = defaultsRes.data
      if (defaults?.base_urls) {
        Object.assign(defaultBaseUrls, defaults.base_urls)
      }
    } catch (_e) { /* 可选：默认 URL 加载失败不影响主流程 */ }

    const res = await getConfig('evaluator')
    const items = res.data ?? []

    // 解析基础配置（优先使用已持久化的值）
    formData.provider = findConfigValue(items, 'provider', formData.provider)
    formData.modelName = findConfigValue(items, 'model_name', formData.modelName)
    formData.apiKey = findConfigValue(items, 'api_key', formData.apiKey)
    formData.baseUrl = findConfigValue(items, 'base_url', defaultBaseUrls[formData.provider] || '')
    formData.minPassScore = Number(findConfigValue(items, 'min_pass_score', String(formData.minPassScore)))
    formData.enabled = findConfigValue(items, 'enabled', 'true') === 'true'
    formData.reviewPromptTemplate = findConfigValue(items, 'review_prompt_template', formData.reviewPromptTemplate)
    formData.reportTemplate = findConfigValue(items, 'report_template', formData.reportTemplate)

    // 解析测评维度
    const dimsStr = findConfigValue(items, 'dimensions', '')
    if (dimsStr) {
      const parsed = JSON.parse(dimsStr) as Dimension[]
      if (Array.isArray(parsed) && parsed.length > 0) {
        dimensions.splice(0, dimensions.length, ...parsed)
      }
    }
  } catch (e) {
    console.error('加载评测师配置失败:', e)
  }
})

async function handleSave() {
  saving.value = true
  try {
    // category 统一为 'evaluator' 确保 getConfig('evaluator') 能加载全部字段
    const items: ConfigItem[] = [
      { key: 'provider', value: formData.provider, category: 'evaluator', description: '评测模型提供商' },
      { key: 'model_name', value: formData.modelName, category: 'evaluator', description: '评测模型名称' },
      { key: 'api_key', value: formData.apiKey, category: 'evaluator', description: 'API Key' },
      { key: 'base_url', value: formData.baseUrl, category: 'evaluator', description: 'API Base URL' },
      { key: 'dimensions', value: JSON.stringify(dimensions), category: 'evaluator', description: '评测维度配置' },
      { key: 'min_pass_score', value: String(formData.minPassScore), category: 'evaluator', description: '最小通过分数' },
      { key: 'enabled', value: String(formData.enabled), category: 'evaluator', description: '启用开关' },
      { key: 'review_prompt_template', value: formData.reviewPromptTemplate, category: 'evaluator', description: '自动评审提示词模板' },
      { key: 'report_template', value: formData.reportTemplate, category: 'evaluator', description: '评审报告模板' },
    ]
    await updateConfig(items)
    message.success('评测师配置已保存')
  } catch (e) {
    console.error('保存评测师配置失败:', e)
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

let dimCounter = dimensions.length + 1
function handleAddDimension() {
  dimensions.push({
    name: `新维度 ${dimCounter++}`,
    weight: 50,
    description: '请描述该维度的评估标准',
  })
}

// ── 维度编辑弹窗 ──
const editDimIdx = ref(-1)
const editDimData = reactive({ name: '', weight: 50, description: '' })
const showDimModal = ref(false)

function handleEditDimension(idx: number) {
  editDimIdx.value = idx
  editDimData.name = dimensions[idx].name
  editDimData.weight = dimensions[idx].weight
  editDimData.description = dimensions[idx].description
  showDimModal.value = true
}

function handleDimSave() {
  if (editDimIdx.value >= 0 && editDimIdx.value < dimensions.length) {
    dimensions[editDimIdx.value].name = editDimData.name
    dimensions[editDimIdx.value].weight = editDimData.weight
    dimensions[editDimIdx.value].description = editDimData.description
  }
  showDimModal.value = false
}
</script>

<style scoped>
.page-wrap {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

@media (max-width: 768px) {
  .page-wrap {
    padding: 16px 12px 48px;
  }
}
</style>
