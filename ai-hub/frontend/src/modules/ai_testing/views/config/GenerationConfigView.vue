<template>
  <n-layout-content content-style="padding: 24px;">
    <n-space vertical :size="16" style="max-width: 700px; margin: 0 auto;">

      <!-- 页头 -->
      <n-page-header title="🎛️ 生成行为" @back="$router.push('/ai-testing/settings')">
        <template #subtitle>
          <n-text depth="3">配置 AI 用例生成的输出模式、数量和超时参数</n-text>
        </template>
      </n-page-header>

      <!-- 基本设置 -->
      <n-card title="基本设置" size="small">
        <n-form label-placement="left" label-width="140">
          <n-form-item label="最大用例数">
            <n-input-number
              v-model:value="maxCases"
              :min="5"
              :max="200"
              style="width: 140px;"
            />
            <n-text depth="3" style="margin-left: 12px; font-size: 12px;">
              单次生成的上限
            </n-text>
          </n-form-item>
          <n-form-item label="评审通过阈值">
            <n-input-number
              v-model:value="reviewThreshold"
              :min="1"
              :max="10"
              style="width: 140px;"
            />
            <n-text depth="3" style="margin-left: 12px; font-size: 12px;">
              综合评分 ≥ 此值时评审通过（1-10）
            </n-text>
          </n-form-item>
          <n-form-item label="输出语言">
            <n-select
              v-model:value="language"
              :options="[
                { label: '中文', value: 'zh' },
                { label: 'English', value: 'en' },
              ]"
              style="width: 140px;"
            />
          </n-form-item>
        </n-form>
      </n-card>

      <!-- 输出模式 -->
      <n-card title="输出模式" size="small">
        <n-radio-group v-model:value="outputMode" name="output-mode">
          <n-space vertical :size="12">
            <n-card size="small" :bordered="true" :class="{ 'mode-card-active': outputMode === 'stream' }">
              <n-radio value="stream" style="width: 100%;">
                <div style="padding-left: 8px;">
                  <div style="font-weight: 500;">流式输出 (Stream)</div>
                  <n-text depth="3" style="font-size: 12px;">实时推送 token，边生成边展示，支持阶段切换和进度提示</n-text>
                </div>
              </n-radio>
            </n-card>
            <n-card size="small" :bordered="true" :class="{ 'mode-card-active': outputMode === 'complete' }">
              <n-radio value="complete" style="width: 100%;">
                <div style="padding-left: 8px;">
                  <div style="font-weight: 500;">完整输出 (Complete)</div>
                  <n-text depth="3" style="font-size: 12px;">生成完毕后一次性展示结果，适合简单需求</n-text>
                </div>
              </n-radio>
            </n-card>
          </n-space>
        </n-radio-group>
      </n-card>

      <!-- 自动化 -->
      <n-card title="自动化" size="small">
        <n-form label-placement="left" label-width="160">
          <n-form-item label="启用自动评审">
            <n-switch v-model:value="enableAutoReview" />
            <n-text depth="3" style="margin-left: 12px; font-size: 12px;">
              生成后自动进行 AI 评审
            </n-text>
          </n-form-item>
          <n-form-item label="评审超时（秒）">
            <n-input-number
              v-model:value="reviewTimeout"
              :min="30"
              :max="600"
              :step="30"
              style="width: 140px;"
            />
          </n-form-item>
        </n-form>
      </n-card>

      <!-- 操作按钮 -->
      <n-space justify="end">
        <n-button @click="handleReset">恢复默认</n-button>
        <n-button type="primary" :loading="saving" @click="handleSave">保存配置</n-button>
      </n-space>

    </n-space>
  </n-layout-content>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useGenerationStore } from '@/modules/ai_testing/stores/generation'
import type { ConfigItem } from '@/modules/ai_testing/types/generation'

const router = useRouter()
const message = useMessage()
const store = useGenerationStore()
const saving = ref(false)

const maxCases = ref(30)
const reviewThreshold = ref(7)
const language = ref('zh')
const outputMode = ref<'stream' | 'complete'>('stream')
const enableAutoReview = ref(true)
const reviewTimeout = ref(120)

async function loadData() {
  await store.fetchConfig()
  const items = store.configItems

  const findNum = (key: string, defaultVal: number) => {
    const v = items.find(c => c.key === key)?.value
    return v ? parseInt(v) || defaultVal : defaultVal
  }

  maxCases.value = findNum('max_cases', 30)
  reviewThreshold.value = findNum('review_threshold', 7)
  language.value = items.find(c => c.key === 'language')?.value || 'zh'
  outputMode.value = (items.find(c => c.key === 'output_mode')?.value as 'stream' | 'complete') || 'stream'
  enableAutoReview.value = items.find(c => c.key === 'enable_auto_review')?.value !== '0'
  reviewTimeout.value = findNum('review_timeout', 120)
}

async function handleSave() {
  saving.value = true
  const items: ConfigItem[] = [
    { key: 'max_cases', value: String(maxCases.value), category: 'behavior', description: '最大用例数' },
    { key: 'review_threshold', value: String(reviewThreshold.value), category: 'behavior', description: '评审通过阈值' },
    { key: 'language', value: language.value, category: 'behavior', description: '输出语言' },
    { key: 'output_mode', value: outputMode.value, category: 'behavior', description: '输出模式' },
    { key: 'enable_auto_review', value: enableAutoReview.value ? '1' : '0', category: 'behavior', description: '启用自动评审' },
    { key: 'review_timeout', value: String(reviewTimeout.value), category: 'behavior', description: '评审超时' },
  ]
  const ok = await store.saveConfig(items)
  saving.value = false
  if (ok) {
    message.success('生成行为配置已保存')
    await store.fetchConfig()
  } else {
    message.error('保存失败')
  }
}

function handleReset() {
  maxCases.value = 30
  reviewThreshold.value = 7
  language.value = 'zh'
  outputMode.value = 'stream'
  enableAutoReview.value = true
  reviewTimeout.value = 120
  message.info('已恢复默认值，请点击「保存配置」生效')
}

onMounted(() => loadData())
</script>

<style scoped>
.mode-card-active {
  border-color: #C67B5C;
  background: rgba(198, 123, 92, 0.04);
}
</style>
