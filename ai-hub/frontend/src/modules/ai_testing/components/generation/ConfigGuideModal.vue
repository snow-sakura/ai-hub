<template>
  <n-modal
    :show="show"
    preset="card"
    title="AI 生成配置检查"
    style="max-width: 560px;"
    :mask-closable="true"
    @update:show="$emit('update:show', $event)"
  >
    <div class="guide-overlay">
      <!-- 整体进度 -->
      <n-progress
        v-if="passedCount > 0"
        type="line"
        :percentage="Math.round(passedCount / ITEMS.length * 100)"
        :indicator-placement="'inside'"
        class="guide-progress"
      />

      <n-alert v-if="allPassed" type="success" :bordered="false" style="font-size: 13px;">
        所有配置就绪，可以开始使用 AI 用例生成功能！
      </n-alert>

      <!-- 5 项配置状态列表 -->
      <n-space vertical :size="8" class="guide-items">
        <n-card
          v-for="item in checkItems"
          :key="item.key"
          size="small"
          :bordered="false"
          class="guide-item"
        >
          <div class="guide-item-row">
            <n-tag
              :type="item.status === 'ok' ? 'success' : 'warning'"
              size="small"
              round
            >
              <template v-if="item.status === 'ok' && item.message === '使用默认模板'">
                ✅ 默认模板
              </template>
              <template v-else-if="item.status === 'ok'">
                ✅ 已配置
              </template>
              <template v-else>
                ❌ 未配置
              </template>
            </n-tag>
            <span class="guide-item-label">{{ item.label }}</span>
            <n-tag size="small" :bordered="false" class="guide-item-cat">
              {{ CATEGORY_LABELS[item.category] || item.category }}
            </n-tag>
          </div>
        </n-card>
      </n-space>

      <!-- 操作 -->
      <div class="guide-actions">
        <n-checkbox v-model:checked="dontShowAgain">
          不再提示
        </n-checkbox>
      </div>
    </div>

    <template #footer>
      <n-space justify="space-between">
        <n-button @click="$emit('update:show', false)">关闭</n-button>
        <n-button
          v-if="!allPassed"
          type="primary"
          @click="goToSettings"
        >
          前往配置页面
        </n-button>
        <n-button
          v-else
          type="primary"
          @click="$emit('update:show', false)"
        >
          开始使用
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { checkConfig } from '@/modules/ai_testing/api/generation'
import type { ConfigCheckItem } from '@/modules/ai_testing/types/generation'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()

const router = useRouter()

const CATEGORY_LABELS: Record<string, string> = {
  model: '模型',
  prompt: '提示词',
  behavior: '行为',
}

const ITEMS = [
  { key: 'model', label: '默认模型', category: 'model' },
  { key: 'analyze_prompt', label: '需求分析提示词', category: 'prompt' },
  { key: 'write_prompt', label: '用例编写提示词', category: 'prompt' },
  { key: 'review_prompt', label: 'AI 评审提示词', category: 'prompt' },
  { key: 'revise_prompt', label: '用例修订提示词', category: 'prompt' },
  { key: 'language', label: '输出语言', category: 'behavior' },
]

const rawItems = ref<ConfigCheckItem[]>([])
const dontShowAgain = ref(false)

const checkItems = computed(() => {
  if (rawItems.value.length > 0) return rawItems.value
  return ITEMS.map(i => ({ ...i, status: 'missing' as const, message: '待检查' }))
})

const allPassed = computed(() => checkItems.value.every(i => i.status === 'ok'))
const passedCount = computed(() => checkItems.value.filter(i => i.status === 'ok').length)

function goToSettings() {
  emit('update:show', false)
  router.push('/ai-testing/settings')
}

onMounted(async () => {
  try {
    const res = await checkConfig()
    if (res.data?.items) {
      rawItems.value = res.data.items
    }
  } catch {
    rawItems.value = []
  }
})
</script>

<style scoped>
.guide-overlay {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.guide-progress {
  margin-bottom: 4px;
}
.guide-items {
  margin-top: 4px;
}
.guide-item {
  background: var(--n-color-modal);
}
.guide-item-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.guide-item-label {
  font-size: 14px;
  font-weight: 500;
  color: #5C4A38;
}
.guide-item-cat {
  margin-left: auto;
  opacity: 0.6;
}
.guide-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
}
</style>
