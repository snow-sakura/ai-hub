<template>
  <n-layout-content content-style="padding: 24px;">
    <n-space vertical :size="16" style="max-width: 900px; margin: 0 auto;">

      <!-- 页头 -->
      <n-page-header title="📝 提示词模板" @back="$router.push('/ai-testing/settings')">
        <template #subtitle>
          <n-text depth="3">自定义各生成阶段的提示词模板，展开可编辑</n-text>
        </template>
        <template #extra>
          <n-button size="small" quaternary @click="showLoadDefaults = true">
            加载默认
          </n-button>
        </template>
      </n-page-header>

      <!-- 提示词卡片网格 -->
      <div class="prompt-grid">
        <n-card
          v-for="tmpl in promptTemplates"
          :key="tmpl.key"
          class="prompt-card"
          size="small"
        >
          <div class="prompt-header">
            <span class="prompt-title">{{ tmpl.label }}</span>
            <n-space :size="6">
              <n-tag :type="tmpl.type === 'writer' ? 'success' : 'warning'" size="tiny">
                {{ tmpl.type === 'writer' ? '编写' : '评审' }}
              </n-tag>
              <n-tag v-if="tmpl.isCustomized" size="tiny" type="warning">
                已自定义
              </n-tag>
              <n-tag v-else size="tiny" type="info">
                默认
              </n-tag>
            </n-space>
          </div>

          <n-input
            v-model:value="tmpl.content"
            type="textarea"
            :rows="6"
            :placeholder="tmpl.placeholder"
            class="prompt-input"
            @update:value="onInput(tmpl)"
          />
          <div class="prompt-footer">
            <n-text depth="3" style="font-size: 12px;">{{ tmpl.content.length }} 字</n-text>
            <n-button text size="tiny" @click="previewTmpl = tmpl">
              👁️ 预览
            </n-button>
            <n-button text size="tiny" @click="restoreDefault(tmpl)" style="margin-left: auto;">
              🔄 恢复默认
            </n-button>
          </div>
        </n-card>
      </div>

      <!-- 操作按钮 -->
      <n-space justify="end">
        <n-button @click="handleResetAll">全部恢复默认</n-button>
        <n-button type="primary" :loading="saving" @click="handleSave">保存配置</n-button>
      </n-space>

      <!-- 预览弹窗 -->
      <n-modal :show="!!previewTmpl" preset="card" title="提示词预览" style="max-width: 700px;" @update:show="previewTmpl = null">
        <pre style="white-space: pre-wrap; font-size: 13px; line-height: 1.6;">{{ previewTmpl?.content }}</pre>
      </n-modal>

      <!-- 加载默认确认 -->
      <n-modal v-model:show="showLoadDefaults" preset="card" title="加载默认提示词" style="max-width: 500px;">
        <n-p>确定将所有提示词模板恢复为系统默认值？自定义内容将丢失。</n-p>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showLoadDefaults = false">取消</n-button>
            <n-button type="primary" @click="doLoadDefaults">确认加载</n-button>
          </n-space>
        </template>
      </n-modal>

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
const showLoadDefaults = ref(false)
const previewTmpl = ref<PromptTemplate | null>(null)

interface PromptTemplate {
  key: string
  label: string
  content: string
  defaultValue: string
  type: 'writer' | 'reviewer'
  isCustomized: boolean
  placeholder: string
}

const promptTemplates = reactive<PromptTemplate[]>([
  { key: 'analyze_prompt', label: '需求分析', content: '', defaultValue: '', type: 'writer', isCustomized: false, placeholder: '加载默认模板中...' },
  { key: 'write_prompt', label: '用例编写', content: '', defaultValue: '', type: 'writer', isCustomized: false, placeholder: '加载默认模板中...' },
  { key: 'review_prompt', label: 'AI 评审', content: '', defaultValue: '', type: 'reviewer', isCustomized: false, placeholder: '加载默认模板中...' },
  { key: 'revise_prompt', label: '用例修订', content: '', defaultValue: '', type: 'reviewer', isCustomized: false, placeholder: '加载默认模板中...' },
])

function onInput(tmpl: PromptTemplate) {
  tmpl.isCustomized = tmpl.content !== tmpl.defaultValue
}

function restoreDefault(tmpl: PromptTemplate) {
  tmpl.content = tmpl.defaultValue
  tmpl.isCustomized = false
  message.info(`已恢复 ${tmpl.label} 为默认值`)
}

function handleResetAll() {
  for (const tmpl of promptTemplates) {
    tmpl.content = tmpl.defaultValue
    tmpl.isCustomized = false
  }
  message.info('已全部恢复默认')
}

function doLoadDefaults() {
  showLoadDefaults.value = false
  for (const tmpl of promptTemplates) {
    tmpl.content = tmpl.defaultValue
    tmpl.isCustomized = false
  }
  message.success('已加载默认提示词')
}

async function loadData() {
  await store.fetchConfigDefaults()
  const defaults = store.configDefaults
  if (defaults) {
    for (const tmpl of promptTemplates) {
      const key = tmpl.key.replace('_prompt', '')
      tmpl.defaultValue = defaults.prompts[key] || ''
      tmpl.placeholder = tmpl.defaultValue ? '' : '（暂无默认模板）'
    }
  }

  await store.fetchConfig()
  const items = store.configItems
  for (const tmpl of promptTemplates) {
    const saved = items.find(c => c.key === tmpl.key)?.value || ''
    tmpl.content = saved || tmpl.defaultValue
    tmpl.isCustomized = tmpl.content !== tmpl.defaultValue
  }
}

async function handleSave() {
  saving.value = true
  const items: ConfigItem[] = []
  for (const tmpl of promptTemplates) {
    items.push({
      key: tmpl.key,
      value: tmpl.content !== tmpl.defaultValue ? tmpl.content : '',
      category: 'prompt',
      description: tmpl.label,
    })
  }
  const ok = await store.saveConfig(items)
  saving.value = false
  if (ok) {
    message.success('提示词配置已保存')
    await store.fetchConfig()
  } else {
    message.error('保存失败')
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.prompt-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}
.prompt-card {
  border: 1px solid #e8e4e0;
}
.prompt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.prompt-title {
  font-weight: 600;
  font-size: 15px;
  color: #5C4A38;
}
.prompt-input {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
}
.prompt-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}
</style>
