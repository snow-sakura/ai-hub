<template>
  <n-layout-content content-style="padding: 24px;">
    <n-space vertical :size="16" style="max-width: 1200px; margin: 0 auto;">

      <!-- 页头 -->
      <n-page-header title="📋 生成任务详情" @back="$router.push('/ai-testing/generate/records')">
        <template #subtitle>
          <n-text depth="3">任务 ID: {{ taskId }}</n-text>
        </template>
        <template #extra>
          <n-space :size="8">
            <n-button size="small" type="primary" ghost @click="handleSaveToLibrary">保存到用例库</n-button>
            <n-button size="small" quaternary @click="handleRetry">重新生成</n-button>
            <n-button size="small" quaternary @click="handleExport">导出 Excel</n-button>
          </n-space>
        </template>
      </n-page-header>

      <!-- 加载状态 -->
      <n-spin :show="loading">
        <template #description>加载任务详情...</template>

        <n-space vertical :size="16">
          <!-- 任务基本信息 -->
          <n-card title="任务信息" size="small" :collapsible="true">
            <n-descriptions :column="3" size="small" bordered>
              <n-descriptions-item label="状态">
                <n-tag :type="statusType" size="small">{{ task?.status }}</n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="模型">{{ modelLabel }}</n-descriptions-item>
              <n-descriptions-item label="生成用例数">{{ task?.generated_count || 0 }}</n-descriptions-item>
              <n-descriptions-item label="创建时间">{{ task?.created_at || '-' }}</n-descriptions-item>
              <n-descriptions-item label="更新时间">{{ task?.updated_at || '-' }}</n-descriptions-item>
              <n-descriptions-item label="所属项目">{{ task?.project_name || '-' }}</n-descriptions-item>
            </n-descriptions>
          </n-card>

          <!-- 需求卡片 -->
          <n-card title="📄 原始需求" size="small" :collapsible="true" :default-collapsed="true">
            <n-space vertical :size="8">
              <n-text v-if="task?.requirement_title" strong>{{ task?.requirement_title }}</n-text>
              <n-scrollbar style="max-height: 300px;">
                <pre class="requirement-text">{{ task?.input_text || '（无详细需求文本）' }}</pre>
              </n-scrollbar>
            </n-space>
          </n-card>

          <!-- 生成的用例列表 -->
          <n-card title="✅ 生成的用例" size="small">
            <GeneratedCaseTable
              :cases="generatedCases"
              :total="casesTotal"
              :page="casesPage"
              :page-size="casesPageSize"
              :selected-ids="selectedIds"
              @toggle="handleToggle"
              @toggle-all="handleToggleAll"
              @clear-all="clearSelection"
              @preview="handlePreview"
              @adopt="handleAdopt"
              @batch-adopt="handleBatchAdopt"
              @batch-discard="handleBatchDiscard"
              @change-page="handleChangePage"
              @change-page-size="handleChangePageSize"
            />
          </n-card>
        </n-space>
      </n-spin>

      <!-- 用例详情弹窗 -->
      <n-modal v-model:show="showPreviewModal" preset="card" title="用例详情" style="max-width: 700px;">
        <n-descriptions v-if="previewCase" :column="1" size="small" bordered>
          <n-descriptions-item label="标题">{{ previewCase.title || '-' }}</n-descriptions-item>
          <n-descriptions-item label="优先级">{{ previewCase.priority || 'P2' }}</n-descriptions-item>
          <n-descriptions-item label="类型">{{ previewCase.case_type || 'functional' }}</n-descriptions-item>
          <n-descriptions-item label="前置条件">
            <pre class="preview-text">{{ previewCase.preconditions || '-' }}</pre>
          </n-descriptions-item>
          <n-descriptions-item label="测试步骤">
            <pre class="preview-text">{{ previewCase.steps || '-' }}</pre>
          </n-descriptions-item>
          <n-descriptions-item label="预期结果">
            <pre class="preview-text">{{ previewCase.expected_results || '-' }}</pre>
          </n-descriptions-item>
          <n-descriptions-item label="标签">
            <n-space :size="4">
              <n-tag v-for="tag in previewCase.tags" :key="tag" size="tiny">{{ tag }}</n-tag>
            </n-space>
          </n-descriptions-item>
        </n-descriptions>
      </n-modal>

    </n-space>
  </n-layout-content>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter, useRoute } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { useTaskDetailStore } from '@/modules/ai_testing/stores/taskDetail'
import * as taskDetailApi from '@/modules/ai_testing/api/taskDetail'
import GeneratedCaseTable from '@/modules/ai_testing/components/generation/GeneratedCaseTable.vue'

const router = useRouter()
const route = useRoute()
const message = useMessage()
const dialog = useDialog()
const store = useTaskDetailStore()

const taskId = ref('')
const loading = ref(true)

const task = computed(() => store.task)

const statusType = computed(() => {
  switch (store.task?.status) {
    case 'completed': return 'success'
    case 'running': return 'info'
    case 'failed': return 'error'
    default: return 'default'
  }
})

const modelLabel = computed(() => {
  const m = store.task?.model || ''
  if (!m) return '默认'
  const parts = m.split(':')
  return parts.length > 1 ? `${parts[0]}: ${parts[1]}` : m
})

// 从 store 解构响应式状态
const {
  generatedCases, casesTotal, casesPage, casesPageSize,
  selectedIds, showPreviewModal, currentPreviewCase: previewCase,
} = storeToRefs(store)

function clearSelection() {
  store.clearSelection()
}

async function loadData() {
  const id = route.params.id as string
  if (!id) { message.error('缺少任务 ID'); return }
  taskId.value = id
  loading.value = true
  await Promise.all([
    store.fetchTask(id),
    store.fetchResults(id),
    store.fetchGeneratedCases(id),
  ])
  loading.value = false
}

function handleToggle(id: string) {
  store.toggleSelect(id)
}

function handleToggleAll() {
  store.toggleSelectAll()
}

function handlePreview(c: Record<string, unknown>) {
  store.previewCase(c)
}

async function handleAdopt(caseId: string) {
  const ok = await store.batchUpdateCases(taskId.value, [caseId], 'adopted')
  if (ok) message.success('已采用该用例')
}

async function handleBatchAdopt(ids: string[]) {
  const ok = await store.batchUpdateCases(taskId.value, ids, 'adopted')
  if (ok) {
    message.success(`已采用 ${ids.length} 条用例`)
    store.clearSelection()
  }
}

async function handleBatchDiscard(ids: string[]) {
  dialog.warning({
    title: '确认丢弃',
    content: `确定丢弃选中的 ${ids.length} 条用例吗？`,
    positiveText: '确认丢弃',
    negativeText: '取消',
    onPositiveClick: async () => {
      const ok = await store.batchUpdateCases(taskId.value, ids, 'discarded')
      if (ok) {
        message.success(`已丢弃 ${ids.length} 条用例`)
        store.clearSelection()
      }
    },
  })
}

function handleChangePage(page: number) {
  store.changePage(taskId.value, page)
}

function handleChangePageSize(size: number) {
  store.changePageSize(taskId.value, size)
}

async function handleSaveToLibrary() {
  try {
    dialog.info({
      title: '保存到用例库',
      content: '将已采用的用例保存到用例库？未采用的用例不会被保存。',
      positiveText: '确认保存',
      negativeText: '取消',
      onPositiveClick: async () => {
        const projectId = task.value?.project_id
        const res = await taskDetailApi.saveTaskCasesToLibrary(taskId.value, projectId)
        const savedCount = res.data?.saved_count || 0
        if (savedCount > 0) {
          message.success(`已保存 ${savedCount} 条用例到用例库`)
        } else {
          message.info('没有可保存的用例，请先采用用例')
        }
      },
    })
  } catch {
    message.error('保存失败')
  }
}

function handleRetry() {
  router.push(`/ai-testing/generate?task_id=${taskId.value}&retry=1`)
}

async function handleExport() {
  try {
    const url = `/api/v1/testing/generate/${taskId.value}/export`
    const response = await fetch(url)
    if (!response.ok) throw new Error('导出失败')
    const blob = await response.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `generated_cases_${Date.now()}.xlsx`
    a.click()
    URL.revokeObjectURL(a.href)
    message.success('已下载 Excel')
  } catch {
    message.error('导出失败')
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.requirement-text {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.preview-text {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}
</style>
