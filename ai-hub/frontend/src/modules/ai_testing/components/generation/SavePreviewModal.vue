<template>
  <n-modal
    :show="show"
    preset="card"
    title="保存到用例库 — 预览"
    style="max-width: 900px; width: 90%;"
    :mask-closable="false"
    @update:show="onClose"
  >
    <div v-if="localCases.length === 0" class="empty-state">
      <n-empty description="没有可保存的用例">
        <template #extra>
          <n-button size="small" @click="onClose">关闭</n-button>
        </template>
      </n-empty>
    </div>

    <template v-else>
      <n-alert type="info" :bordered="false" style="font-size: 13px; margin-bottom: 12px;">
        以下是从 AI 生成结果中解析出的用例，请确认字段后点击"保存"。未勾选的用例不会被保存。
      </n-alert>

      <!-- 批量操作 -->
      <n-space style="margin-bottom: 8px;" :size="8">
        <n-button size="tiny" quaternary @click="selectAll">全选</n-button>
        <n-button size="tiny" quaternary @click="deselectAll">取消全选</n-button>
        <span style="font-size: 12px; color: #7A6855;">已选 {{ selectedCount }} / {{ localCases.length }} 条</span>
      </n-space>

      <!-- 用例列表 -->
      <n-scrollbar style="max-height: 480px;">
        <n-space vertical :size="8">
          <n-card
            v-for="(c, idx) in localCases"
            :key="idx"
            size="small"
            :segmented="{ content: true }"
            class="preview-case-card"
          >
            <template #header>
              <n-space :size="8" align="center">
                <n-checkbox v-model:checked="c._selected" />
                <span class="case-index">#{{ idx + 1 }}</span>
                <n-input
                  v-model:value="c.title"
                  size="small"
                  placeholder="用例标题"
                  :maxlength="500"
                  style="flex: 1; min-width: 200px;"
                />
                <n-select
                  v-model:value="c.priority"
                  :options="priorityOptions"
                  size="small"
                  style="width: 100px;"
                />
                <n-select
                  v-model:value="c.case_type"
                  :options="typeOptions"
                  size="small"
                  style="width: 120px;"
                />
              </n-space>
            </template>

            <n-space vertical :size="6">
              <n-space :size="8" align="center">
                <span class="field-label">前置条件</span>
                <n-input
                  v-model:value="c.preconditions"
                  type="textarea"
                  size="small"
                  :rows="2"
                  :maxlength="5000"
                  placeholder="前置条件（可选）"
                  style="flex: 1;"
                />
              </n-space>
              <n-space :size="8" align="center">
                <span class="field-label">测试步骤</span>
                <n-input
                  v-model:value="c.steps"
                  type="textarea"
                  size="small"
                  :rows="3"
                  :maxlength="5000"
                  placeholder="测试步骤（可选）"
                  style="flex: 1;"
                />
              </n-space>
              <n-space :size="8" align="center">
                <span class="field-label">预期结果</span>
                <n-input
                  v-model:value="c.expected_results"
                  type="textarea"
                  size="small"
                  :rows="2"
                  :maxlength="5000"
                  placeholder="预期结果（可选）"
                  style="flex: 1;"
                />
              </n-space>
              <n-space :size="8" align="center">
                <span class="field-label">标签</span>
                <n-dynamic-tags v-model:value="c.tags" size="small" style="flex: 1;" />
              </n-space>
            </n-space>
          </n-card>
        </n-space>
      </n-scrollbar>
    </template>

    <template #footer>
      <n-space justify="space-between">
        <n-text depth="3" style="font-size: 12px;">
          已选 {{ selectedCount }} 条，将保存到用例库
        </n-text>
        <n-space :size="8">
          <n-button @click="onClose">取消</n-button>
          <n-button
            type="primary"
            :loading="saving"
            :disabled="selectedCount === 0"
            @click="handleSave"
          >
            保存（{{ selectedCount }}）条
          </n-button>
        </n-space>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface PreviewCase {
  title: string
  priority: string
  case_type: string
  preconditions: string
  steps: string
  expected_results: string
  tags: string[]
  _selected: boolean
}

const props = defineProps<{
  show: boolean
  cases: Array<Record<string, unknown>>
  saving: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  save: [cases: Array<Record<string, unknown>>]
}>()

const priorityOptions = [
  { label: 'P0 严重', value: 'P0' },
  { label: 'P1 重要', value: 'P1' },
  { label: 'P2 一般', value: 'P2' },
  { label: 'P3 轻微', value: 'P3' },
]

const typeOptions = [
  { label: '功能测试', value: 'functional' },
  { label: '性能测试', value: 'performance' },
  { label: '安全测试', value: 'security' },
  { label: '兼容性测试', value: 'compatibility' },
  { label: 'UI 测试', value: 'ui' },
  { label: '接口测试', value: 'api' },
]

const localCases = ref<PreviewCase[]>([])

// 当外部 cases 变化时同步到 localCases
watch(() => props.cases, (newCases) => {
  if (newCases && newCases.length > 0) {
    localCases.value = newCases.map(c => ({
      title: String(c.title || ''),
      priority: String(c.priority || 'P2'),
      case_type: String(c.case_type || 'functional'),
      preconditions: String(c.preconditions || ''),
      steps: String(c.steps || ''),
      expected_results: String(c.expected_results || ''),
      tags: Array.isArray(c.tags) ? [...c.tags] : ['ai-generated'],
      _selected: true,
    }))
  } else {
    localCases.value = []
  }
}, { immediate: true, deep: true })

const selectedCount = computed(() => localCases.value.filter(c => c._selected).length)

function selectAll() {
  localCases.value.forEach(c => { c._selected = true })
}

function deselectAll() {
  localCases.value.forEach(c => { c._selected = false })
}

function onClose() {
  emit('update:show', false)
}

function handleSave() {
  const selected = localCases.value
    .filter(c => c._selected)
    .map(c => ({
      title: c.title,
      priority: c.priority,
      case_type: c.case_type,
      preconditions: c.preconditions,
      steps: c.steps,
      expected_results: c.expected_results,
      tags: c.tags,
    }))
  emit('save', selected)
}
</script>

<style scoped>
.empty-state {
  padding: 40px 0;
  display: flex;
  justify-content: center;
}
.preview-case-card {
  border: 1px solid #e8e4e0;
}
.case-index {
  font-size: 13px;
  font-weight: 600;
  color: #7A6855;
  min-width: 24px;
}
.field-label {
  font-size: 12px;
  color: #7A6855;
  min-width: 56px;
  flex-shrink: 0;
}
</style>
