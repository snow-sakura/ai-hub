<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">测试用例</h1>
        <span class="page-count">{{ store.total }} 条用例</span>
      </div>
      <div class="header-actions">
        <n-button
          v-if="store.selectedIds.length > 0"
          type="error"
          ghost
          @click="handleBatchDelete"
        >
          删除选中 ({{ store.selectedIds.length }})
        </n-button>
        <n-button ghost @click="handleExport">
          📥 导出 Excel
        </n-button>
        <n-button ghost @click="triggerImport">
          📤 导入 Excel
        </n-button>
        <input
          ref="fileInput"
          type="file"
          accept=".xlsx,.xls"
          style="display: none;"
          @change="handleImport"
        />
        <n-button type="primary" @click="router.push('/ai-testing/testcases/create')">
          + 新建用例
        </n-button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <n-card size="small" class="stat-card">
        <div class="stat-value">{{ store.stats.total }}</div>
        <div class="stat-label">总用例数</div>
      </n-card>
      <n-card size="small" class="stat-card pri-p0">
        <div class="stat-value">{{ store.stats.by_priority.P0 || 0 }}</div>
        <div class="stat-label">P0 严重</div>
      </n-card>
      <n-card size="small" class="stat-card pri-p1">
        <div class="stat-value">{{ store.stats.by_priority.P1 || 0 }}</div>
        <div class="stat-label">P1 重要</div>
      </n-card>
      <n-card size="small" class="stat-card">
        <div class="stat-value">{{ store.stats.by_type.functional || 0 }}</div>
        <div class="stat-label">功能用例</div>
      </n-card>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-section">
      <n-input
        v-model:value="keyword"
        placeholder="搜索用例标题..."
        clearable
        :style="{ width: '240px' }"
        @update:value="handleSearch"
        @keyup.enter="() => handleSearch(keyword)"
      />
      <n-select
        v-model:value="store.filters.project_id"
        placeholder="全部项目"
        clearable
        :style="{ width: '160px' }"
        :options="projectOptions"
        @update:value="handleFilterChange"
      />
      <n-select
        v-model:value="store.filters.priority"
        placeholder="优先级"
        clearable
        :style="{ width: '120px' }"
        :options="priorityOptions"
        @update:value="handleFilterChange"
      />
      <n-select
        v-model:value="store.filters.case_type"
        placeholder="用例类型"
        clearable
        :style="{ width: '120px' }"
        :options="caseTypeOptions"
        @update:value="handleFilterChange"
      />
      <n-select
        v-model:value="store.filters.status"
        placeholder="状态"
        clearable
        :style="{ width: '120px' }"
        :options="caseStatusOptions"
        @update:value="handleFilterChange"
      />
    </div>

    <!-- 用例表格 -->
    <div class="table-card">
      <n-data-table
        :columns="columns"
        :data="store.cases"
        :loading="store.isLoading"
        :row-key="(row: any) => row.id"
        :scroll-x="960"
        :row-props="rowProps"
        @update:checked-row-keys="handleCheckedChange"
      />

      <div v-if="store.total > 0" class="pagination-wrap">
        <n-pagination
          :page="store.page"
          :page-size="store.pageSize"
          :page-count="Math.ceil(store.total / store.pageSize)"
          show-size-picker
          :page-sizes="[10, 20, 50]"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton, NInput, NSelect, NDataTable, NPagination, NCheckbox,
  NTag, useMessage, useDialog,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import type { TestCase } from '@/modules/ai_testing/types/testcase'
import { useTestCaseStore } from '@/modules/ai_testing/stores/testcase'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import PriorityBadge from '@/modules/ai_testing/components/common/PriorityBadge.vue'
import { importCases } from '@/modules/ai_testing/api/testcase'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const store = useTestCaseStore()
const projectStore = useProjectStore()

const fileInput = ref<HTMLInputElement | null>(null)
const keyword = ref('')

const priorityOptions = [
  { label: 'P0 严重', value: 'P0' },
  { label: 'P1 重要', value: 'P1' },
  { label: 'P2 一般', value: 'P2' },
  { label: 'P3 轻微', value: 'P3' },
]

const caseStatusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '启用', value: 'active' },
  { label: '废弃', value: 'deprecated' },
]

const caseTypeOptions = [
  { label: '功能', value: 'functional' },
  { label: '性能', value: 'performance' },
  { label: '安全', value: 'security' },
  { label: '兼容性', value: 'compatibility' },
  { label: 'UI', value: 'ui' },
  { label: 'API', value: 'api' },
]

const projectOptions = ref<Array<{ label: string; value: string }>>([])

const columns: DataTableColumns<TestCase> = [
  {
    type: 'selection',
    fixed: 'left',
    width: 40,
  },
  {
    title: '标题',
    key: 'title',
    width: 240,
    ellipsis: { tooltip: true },
    render(row) {
      return h('a', {
        style: 'color: var(--text-primary); font-weight: 500; text-decoration: none; cursor: pointer;',
        onClick: () => router.push(`/ai-testing/testcases/${row.id}`),
      }, row.title)
    },
  },
  {
    title: '项目',
    key: 'project_name',
    width: 140,
    ellipsis: { tooltip: true },
    render(row) {
      return h('span', { style: 'color: #5C4A38; font-size: 13px;' }, row.project_name || '—')
    },
  },
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    render(row) {
      return h(PriorityBadge, { priority: row.priority })
    },
  },
  {
    title: '类型',
    key: 'case_type',
    width: 90,
    render(row) {
      return h(NTag, { size: 'small', round: true, bordered: false }, { default: () => row.case_type })
    },
  },
  {
    title: '来源',
    key: 'source',
    width: 70,
    render(row) {
      return h('span', {
        style: row.source === 'ai'
          ? 'color: #7c3aed; font-size: 12px; font-weight: 500;'
          : 'color: #7A6855; font-size: 12px;'
      }, row.source === 'ai' ? '🤖 AI' : '手动')
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 80,
    render(row) {
      const map: Record<string, { label: string; type: 'default' | 'info' | 'warning' }> = {
        draft: { label: '草稿', type: 'default' },
        active: { label: '启用', type: 'info' },
        deprecated: { label: '废弃', type: 'warning' },
      }
      const s = map[row.status] || { label: row.status, type: 'default' as const }
      return h(NTag, { size: 'small', type: s.type, round: true, bordered: false }, { default: () => s.label })
    },
  },
  {
    title: '更新时间',
    key: 'updated_at',
    width: 120,
    render(row) {
      const d = new Date(row.updated_at)
      return h('span', { style: 'color: #7A6855; font-size: 12px;' },
        isNaN(d.getTime()) ? row.updated_at : d.toLocaleDateString('zh-CN'))
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 140,
    fixed: 'right',
    render(row) {
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        h(NButton, {
          text: true, size: 'small',
          onClick: () => router.push(`/ai-testing/testcases/${row.id}/edit`),
        }, { default: () => '编辑' }),
        h(NButton, {
          text: true, size: 'small', type: 'error',
          onClick: () => handleDelete(row),
        }, { default: () => '删除' }),
      ])
    },
  },
]

function rowProps(row: TestCase): Record<string, string> {
  return {
    'data-row-id': row.id,
  }
}

function handleCheckedChange(keys: (string | number)[]) {
  store.selectedIds = keys.map(String)
}

const handleSearch = useDebounceFn((val: string) => {
  store.setFilter('keyword', val || null)
  store.fetchCases()
}, 300)

function handleFilterChange() {
  store.fetchCases()
  store.fetchStats()
}

function handlePageChange(p: number) {
  store.page = p
  store.fetchCases()
}

function handlePageSizeChange(size: number) {
  store.pageSize = size
  store.page = 1
  store.fetchCases()
}

function handleDelete(row: TestCase) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除用例「${row.title}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      const ok = await store.deleteCase(row.id)
      if (ok) message.success('用例已删除')
    },
  })
}

function handleBatchDelete() {
  dialog.warning({
    title: '批量删除',
    content: `确定要删除选中的 ${store.selectedIds.length} 条用例吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      const count = await store.batchDelete()
      if (count > 0) message.success(`已删除 ${count} 条用例`)
    },
  })
}

// ── Excel 导出 ──────────────────────────────────────────────
function handleExport() {
  const projectId = store.filters.project_id || ''
  const ids = store.selectedIds.length > 0 ? store.selectedIds.join(',') : ''
  const params = new URLSearchParams()
  if (projectId) params.set('project_id', projectId)
  if (ids) params.set('ids', ids)

  const url = `/api/v1/testing/cases/export?${params.toString()}`
  const a = document.createElement('a')
  a.href = url
  a.download = 'test_cases.xlsx'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  message.success('开始下载 Excel 文件')
}

// ── Excel 导入 ──────────────────────────────────────────────
function triggerImport() {
  fileInput.value?.click()
}

async function handleImport(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  const projectId = store.filters.project_id || ''

  try {
    const res = await importCases(file, projectId || undefined)
    const count = res.data?.imported_count || 0
    message.success(`已导入 ${count} 条用例`)
    store.fetchCases()
  } catch (err) {
    message.error('导入失败，请检查文件格式')
  } finally {
    // 重置 input 以便重复选同一文件
    input.value = ''
  }
}

onMounted(async () => {
  store.fetchCases()
  store.fetchStats()
  await projectStore.fetchProjects()
  projectOptions.value = projectStore.projects.map(p => ({
    label: p.name,
    value: p.id,
  }))
})
</script>

<style scoped>
.page-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  margin: 0;
}

.page-count {
  font-size: 13px;
  color: #7A6855;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-card :deep(.n-card-header) {
  padding: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #7A6855;
  margin-top: 4px;
}

.pri-p0 .stat-value { color: #d03050; }
.pri-p1 .stat-value { color: #d4870e; }

.filter-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.table-card {
  background: var(--bg-card, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  overflow: hidden;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

@media (max-width: 768px) {
  .page-wrap { padding: 16px 12px 48px; }
  .page-header { flex-wrap: wrap; gap: 10px; }
  .stats-row { gap: 10px; }
  .filter-section { flex-direction: column; align-items: stretch; }
  .filter-section > * { width: 100%; }
  :deep(.n-data-table-wrapper) { overflow-x: auto; }
}
</style>
