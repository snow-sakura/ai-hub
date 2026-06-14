<template>
  <div class="page-wrap">
    <n-space vertical :size="16" style="max-width: 900px; margin: 0 auto;">
      <!-- 页头 -->
      <n-page-header title="AI 智能模式配置" @back="$router.push('/ai-testing/config')">
        <template #subtitle>
          <n-text depth="3">配置智能模式、浏览器引擎与页面解析参数</n-text>
        </template>
      </n-page-header>

      <!-- 模式卡片 -->
      <div class="mode-grid">
        <n-card
          :class="['mode-card', { 'mode-active': aiMode === 'text' }]"
          size="small"
          @click="aiMode = 'text'"
        >
          <div class="mode-header">
            <span class="mode-icon">📝</span>
            <span class="mode-title">文本模式</span>
            <n-tag :type="aiMode === 'text' ? 'success' : 'default'" size="tiny" round>
              {{ aiMode === 'text' ? '已启用' : '未启用' }}
            </n-tag>
          </div>
          <p class="mode-desc">DOM 解析，快速高效，适合标准页面结构</p>
        </n-card>

        <n-card
          :class="['mode-card', { 'mode-active': aiMode === 'visual' }]"
          size="small"
          @click="aiMode = 'visual'"
        >
          <div class="mode-header">
            <span class="mode-icon">👁️</span>
            <span class="mode-title">视觉模式</span>
            <n-tag :type="aiMode === 'visual' ? 'success' : 'default'" size="tiny" round>
              {{ aiMode === 'visual' ? '已启用' : '未启用' }}
            </n-tag>
          </div>
          <p class="mode-desc">截图识别，适合复杂页面和动态渲染内容</p>
        </n-card>

        <n-card
          :class="['mode-card', { 'mode-active': aiMode === 'hybrid' }]"
          size="small"
          @click="aiMode = 'hybrid'"
        >
          <div class="mode-header">
            <span class="mode-icon">🔄</span>
            <span class="mode-title">混合模式</span>
            <n-tag :type="aiMode === 'hybrid' ? 'success' : 'default'" size="tiny" round>
              {{ aiMode === 'hybrid' ? '已启用' : '未启用' }}
            </n-tag>
          </div>
          <p class="mode-desc">DOM + 视觉双重解析，准确度最高</p>
        </n-card>
      </div>

      <!-- 浏览器引擎配置 -->
      <n-card title="浏览器引擎配置" size="small">
        <n-form label-placement="top" :model="browserConfig" label-width="140">
          <n-grid :cols="2" :x-gap="16">
            <n-grid-item>
              <n-form-item label="浏览器引擎">
                <n-select
                  v-model:value="browserConfig.engine"
                  :options="engineOptions"
                  placeholder="选择浏览器引擎"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="目标浏览器">
                <n-select
                  v-model:value="browserConfig.browser"
                  :options="browserOptions"
                  placeholder="选择浏览器"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="无头模式">
                <n-switch v-model:value="browserConfig.headless" />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="页面加载超时 (ms)">
                <n-input-number
                  v-model:value="browserConfig.timeout"
                  :min="1000"
                  :max="120000"
                  :step="1000"
                  style="width: 100%;"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="截图质量">
                <n-select
                  v-model:value="browserConfig.screenshotQuality"
                  :options="qualityOptions"
                  placeholder="选择截图质量"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="视口宽度">
                <n-input-number
                  v-model:value="browserConfig.viewportWidth"
                  :min="800"
                  :max="3840"
                  :step="100"
                  style="width: 100%;"
                />
              </n-form-item>
            </n-grid-item>
          </n-grid>
        </n-form>
      </n-card>

      <!-- 操作按钮 -->
      <n-space justify="end" :size="12">
        <n-button :loading="testing" @click="handleTestConfig">测试配置</n-button>
        <n-button type="primary" :loading="saving" @click="handleSave">保存配置</n-button>
      </n-space>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { getConfig, updateConfig } from '@/modules/ai_testing/api/generation'
import type { ConfigItem } from '@/modules/ai_testing/types/generation'
import { findConfigValue } from '@/modules/ai_testing/utils/config'

const router = useRouter()
const message = useMessage()
const saving = ref(false)
const testing = ref(false)
const aiMode = ref<'text' | 'visual' | 'hybrid'>('text')

const engineOptions = [
  { label: 'Playwright', value: 'playwright' },
  { label: 'Selenium', value: 'selenium' },
]

const browserOptions = [
  { label: 'Chrome', value: 'chrome' },
  { label: 'Firefox', value: 'firefox' },
  { label: 'Edge', value: 'edge' },
]

const qualityOptions = [
  { label: '低 (30%)', value: '30' },
  { label: '中 (60%)', value: '60' },
  { label: '高 (80%)', value: '80' },
  { label: '原图 (100%)', value: '100' },
]

const browserConfig = reactive({
  engine: 'playwright',
  browser: 'chrome',
  headless: true,
  timeout: 30000,
  screenshotQuality: '80',
  viewportWidth: 1920,
})

onMounted(async () => {
  try {
    const res = await getConfig('ai_mode')
    const items = res.data ?? []
    if (items.length === 0) return

    // 解析 AI 模式
    const mode = findConfigValue(items, 'ai_mode', aiMode.value)
    if (['text', 'visual', 'hybrid'].includes(mode)) {
      aiMode.value = mode as 'text' | 'visual' | 'hybrid'
    }

    // 解析浏览器配置
    browserConfig.engine = findConfigValue(items, 'browser_engine', browserConfig.engine)
    browserConfig.browser = findConfigValue(items, 'browser', browserConfig.browser)
    browserConfig.headless = findConfigValue(items, 'headless', String(browserConfig.headless)) === 'true'
    browserConfig.timeout = Number(findConfigValue(items, 'page_load_timeout', String(browserConfig.timeout)))
    browserConfig.screenshotQuality = findConfigValue(items, 'screenshot_quality', browserConfig.screenshotQuality)
    browserConfig.viewportWidth = Number(findConfigValue(items, 'viewport_width', String(browserConfig.viewportWidth)))
  } catch (e) {
    console.error('加载智能模式配置失败:', e)
  }
})

async function handleTestConfig() {
  testing.value = true
  try {
    const { sendMessage } = await import('@/modules/ai_testing/api/ai_tester')
    const res = await sendMessage('', {
      content: `使用当前配置回复"配置测试通过"即可。引擎: ${browserConfig.engine}, 浏览器: ${browserConfig.browser}`,
    })
    if (res.data) {
      message.success('配置测试通过 ✓')
    } else {
      message.error('配置测试失败')
    }
  } catch (e: any) {
    message.error(`配置测试失败: ${e?.detail?.message || e?.message || '请检查配置'}`)
  } finally {
    testing.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const items: ConfigItem[] = [
      { key: 'ai_mode', value: aiMode.value, category: 'ai_mode', description: 'AI 智能模式' },
      { key: 'browser_engine', value: browserConfig.engine, category: 'ai_mode', description: '浏览器引擎' },
      { key: 'browser', value: browserConfig.browser, category: 'ai_mode', description: '目标浏览器' },
      { key: 'headless', value: String(browserConfig.headless), category: 'ai_mode', description: '无头模式' },
      { key: 'page_load_timeout', value: String(browserConfig.timeout), category: 'ai_mode', description: '页面加载超时' },
      { key: 'screenshot_quality', value: browserConfig.screenshotQuality, category: 'ai_mode', description: '截图质量' },
      { key: 'viewport_width', value: String(browserConfig.viewportWidth), category: 'ai_mode', description: '视口宽度' },
    ]
    await updateConfig(items)
    message.success('AI 智能模式配置已保存')
  } catch (e) {
    console.error('保存智能模式配置失败:', e)
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page-wrap {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

.mode-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.mode-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(180, 150, 120, 0.12);
}

.mode-card:hover {
  border-color: var(--accent-light, #D49472);
  box-shadow: 0 2px 8px rgba(198, 123, 92, 0.1);
}

.mode-active {
  border-color: var(--accent, #C67B5C) !important;
  background: rgba(198, 123, 92, 0.04) !important;
}

.mode-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.mode-icon {
  font-size: 20px;
}

.mode-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #3D2E1F);
  flex: 1;
}

.mode-desc {
  font-size: 12px;
  color: var(--text-muted, #8B7355);
  margin: 0;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .page-wrap {
    padding: 16px 12px 48px;
  }
  .mode-grid {
    grid-template-columns: 1fr;
  }
}
</style>
