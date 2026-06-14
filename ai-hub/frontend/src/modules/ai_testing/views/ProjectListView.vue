<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">项目列表</h1>
        <span class="page-count">{{ store.total }} 个项目</span>
      </div>
      <n-button type="primary" @click="showCreateModal = true">
        + 新建项目
      </n-button>
    </header>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-icon stat-icon--total">📋</span>
        <div class="stat-body">
          <span class="stat-value">{{ store.total }}</span>
          <span class="stat-label">全部项目</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon stat-icon--active">🟢</span>
        <div class="stat-body">
          <span class="stat-value">{{ activeCount }}</span>
          <span class="stat-label">进行中</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon stat-icon--completed">✅</span>
        <div class="stat-body">
          <span class="stat-value">{{ completedCount }}</span>
          <span class="stat-label">已完成</span>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon stat-icon--archived">📦</span>
        <div class="stat-body">
          <span class="stat-value">{{ archivedCount }}</span>
          <span class="stat-label">已归档</span>
        </div>
      </div>
    </div>

    <!-- 搜索 + 筛选 + 批量操作 -->
    <div class="filter-section">
      <n-input
        v-model:value="store.searchKeyword"
        placeholder="搜索项目名称..."
        clearable
        :style="{ width: '220px' }"
        @update:value="onSearchInput"
        @keyup.enter="onSearchInput"
      />
      <n-select
        v-model:value="store.statusFilter"
        :options="statusFilterOptions"
        placeholder="全部状态"
        clearable
        :style="{ width: '140px' }"
        @update:value="onStatusChange"
      />
      <div v-if="selectedRowIds.length > 0" class="batch-bar">
        <span class="batch-count">已选 {{ selectedRowIds.length }} 项</span>
        <n-button size="tiny" @click="clearSelection">取消选择</n-button>
        <n-button size="tiny" type="warning" @click="handleBatchStatus('active')">设为进行中</n-button>
        <n-button size="tiny" type="success" @click="handleBatchStatus('completed')">设为已完成</n-button>
        <n-button size="tiny" type="error" @click="handleBatchDelete">批量删除</n-button>
      </div>
    </div>

    <!-- 项目表格 -->
    <div class="table-card">
      <n-data-table
        :columns="columns"
        :data="store.projects"
        :loading="store.isLoading"
        :row-key="(row: any) => row.id"
        :scroll-x="900"
        @update:checked-row-keys="onSelectionChange"
      />

      <!-- 分页 - 修复边界条件 -->
      <div v-if="store.total > 0" class="pagination-wrap">
        <n-pagination
          v-model:page="store.page"
          :page-count="Math.ceil(store.total / store.pageSize)"
          :page-size="store.pageSize"
          :page-slot="7"
          show-size-picker
          :page-sizes="[10, 20, 50]"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </div>

    <!-- 新建/编辑弹窗 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      :style="{ width: editingProject ? '700px' : '520px' }"
      :mask-closable="false"
      @after-leave="editingProject = undefined"
    >
      <ProjectForm
        :edit-data="editingProject"
        @cancel="showCreateModal = false"
        @saved="handleSaved"
      />
    </n-modal>

    <!-- 删除确认弹窗 -->
    <n-modal v-model:show="showDeleteModal" preset="dialog" type="warning" title="确认删除">
      <p>确定要删除项目「{{ deletingProject?.name }}」吗？此操作不可撤销，关联的版本和成员信息也将被清除。</p>
      <template #action>
        <n-button @click="showDeleteModal = false">取消</n-button>
        <n-button type="error" :loading="isDeleting" @click="handleDelete">确认删除</n-button>
      </template>
    </n-modal>

    <!-- 批量删除确认弹窗 -->
    <n-modal v-model:show="showBatchDeleteModal" preset="dialog" type="warning" title="批量删除确认">
      <p>确定要删除已选的 {{ selectedRowIds.length }} 个项目吗？此操作不可撤销。</p>
      <template #action>
        <n-button @click="showBatchDeleteModal = false">取消</n-button>
        <n-button type="error" :loading="isBatchDeleting" @click="confirmBatchDelete">确认删除</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, h, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton, NInput, NDataTable, NPagination,
  NModal, NSelect, useMessage, useDialog,
} from 'naive-ui'
import type { DataTableColumns, DataTableRowKey } from 'naive-ui'
import type { TestingProject, ProjectStatus } from '@/modules/ai_testing/types/project'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import StatusTag from '@/modules/ai_testing/components/common/StatusTag.vue'
import ProjectForm from '@/modules/ai_testing/components/project/ProjectForm.vue'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const store = useProjectStore()

const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const showBatchDeleteModal = ref(false)
const editingProject = ref<{ id: string; name: string; description: string; status: ProjectStatus } | undefined>(undefined)
const deletingProject = ref<TestingProject | null>(null)
const isDeleting = ref(false)
const isBatchDeleting = ref(false)
const selectedRowIds = ref<string[]>([])
let searchTimer: ReturnType<typeof setTimeout> | null = null

// ── 统计数据 ──
const activeCount = computed(() => store.projects.filter(p => p.status === 'active').length)
const completedCount = computed(() => store.projects.filter(p => p.status === 'completed').length)
const archivedCount = computed(() => store.projects.filter(p => p.status === 'archived').length)

const statusFilterOptions = [
  { label: '进行中', value: 'active' },
  { label: '已暂停', value: 'paused' },
  { label: '已完成', value: 'completed' },
  { label: '已归档', value: 'archived' },
]

const columns: DataTableColumns<TestingProject> = [
  {
    type: 'selection',
    width: 40,
  },
  {
    title: '项目名称',
    key: 'name',
    width: 200,
    ellipsis: { tooltip: true },
    render(row) {
      return h('a', {
        style: 'color: #3D2E1F; font-weight: 600; text-decoration: none; cursor: pointer; transition: color 0.15s;',
        onMouseenter(e: MouseEvent) {
          (e.target as HTMLElement).style.color = '#C67B5C'
        },
        onMouseleave(e: MouseEvent) {
          (e.target as HTMLElement).style.color = '#3D2E1F'
        },
        onClick: () => router.push(`/ai-testing/projects/${row.id}`),
      }, row.name)
    },
  },
  {
    title: '描述',
    key: 'description',
    width: 220,
    ellipsis: { tooltip: true },
    render(row) {
      return h('span', { style: 'color: #7A6855; font-size: 13px;' }, row.description || '—')
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render(row) {
      return h(StatusTag, { status: row.status })
    },
  },
  {
    title: '用例',
    key: 'case_count',
    width: 60,
    align: 'center',
    render(row) {
      return h('span', { style: 'color: #5C4A38; font-weight: 600;' }, row.case_count)
    },
  },
  {
    title: '成员',
    key: 'member_count',
    width: 60,
    align: 'center',
    render(row) {
      return h('span', { style: 'color: #5C4A38; font-weight: 600;' }, row.member_count)
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 130,
    render(row) {
      const d = new Date(row.created_at)
      return h('span', { style: 'color: #7A6855; font-size: 12px;' },
        isNaN(d.getTime()) ? row.created_at : d.toLocaleDateString('zh-CN'))
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 130,
    fixed: 'right',
    render(row) {
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        h(NButton, { text: true, size: 'small', style: 'color: #C67B5C;', onClick: () => handleEdit(row) },
          { default: () => '编辑' }),
        h(NButton, { text: true, size: 'small', type: 'error', onClick: () => handleDeleteConfirm(row) },
          { default: () => '删除' }),
      ])
    },
  },
]

// ── 搜索防抖 ──
function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    store.page = 1
    store.fetchProjects()
  }, 300)
}

// ── 状态筛选 ──
function onStatusChange(val: ProjectStatus | null) {
  store.statusFilter = val
  store.page = 1
  store.fetchProjects()
}

// ── 分页 ──
function handlePageChange(p: number) {
  store.page = p
  store.fetchProjects()
}

function handlePageSizeChange(size: number) {
  store.pageSize = size
  store.page = 1
  store.fetchProjects()
}

// ── 选择/批量操作 ──
function onSelectionChange(keys: DataTableRowKey[]) {
  selectedRowIds.value = keys as string[]
}

function clearSelection() {
  selectedRowIds.value = []
}

function handleEdit(project: TestingProject) {
  editingProject.value = { id: project.id, name: project.name, description: project.description, status: project.status }
  showCreateModal.value = true
}

function handleDeleteConfirm(project: TestingProject) {
  deletingProject.value = project
  showDeleteModal.value = true
}

function handleSaved() {
  showCreateModal.value = false
  editingProject.value = undefined
  store.page = 1
  store.fetchProjects()
}

async function handleDelete() {
  if (!deletingProject.value) return
  isDeleting.value = true
  try {
    const ok = await store.deleteProject(deletingProject.value.id)
    if (ok) {
      message.success(`项目「${deletingProject.value.name}」已删除`)
    } else {
      message.error('删除失败，请重试')
    }
    showDeleteModal.value = false
  } catch (e) {
    message.error('操作异常，请稍后重试')
    console.error('删除项目失败:', e)
  } finally {
    isDeleting.value = false
  }
}

// ── 批量删除 ──
async function handleBatchDelete() {
  if (selectedRowIds.value.length === 0) return
  showBatchDeleteModal.value = true
}

async function confirmBatchDelete() {
  isBatchDeleting.value = true
  let successCount = 0
  let failCount = 0
  try {
    for (const id of selectedRowIds.value) {
      const ok = await store.deleteProject(id)
      if (ok) successCount++
      else failCount++
    }
    if (failCount === 0) {
      message.success(`成功删除 ${successCount} 个项目`)
    } else {
      message.warning(`删除完成：成功 ${successCount} 个，失败 ${failCount} 个`)
    }
    store.page = 1
    store.fetchProjects()
    selectedRowIds.value = []
    showBatchDeleteModal.value = false
  } catch (e) {
    message.error('批量删除操作异常')
    console.error('批量删除失败:', e)
  } finally {
    isBatchDeleting.value = false
  }
}

// ── 批量改状态 ──
async function handleBatchStatus(status: ProjectStatus) {
  if (selectedRowIds.value.length === 0) return
  dialog.warning({
    title: '批量修改状态',
    content: `确定将选中的 ${selectedRowIds.value.length} 个项目状态改为「${statusFilterOptions.find(o => o.value === status)?.label || status}」吗？`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      let successCount = 0
      let failCount = 0
      try {
        for (const id of selectedRowIds.value) {
          const ok = await store.updateProject(id, { status })
          if (ok) successCount++
          else failCount++
        }
        if (failCount === 0) {
          message.success(`成功更新 ${successCount} 个项目状态`)
        } else {
          message.warning(`更新完成：成功 ${successCount} 个，失败 ${failCount} 个`)
        }
        store.fetchProjects()
        selectedRowIds.value = []
      } catch (e) {
        message.error('批量更新状态异常')
        console.error('批量更新状态失败:', e)
      }
    },
  })
}

onMounted(() => {
  store.page = 1
  store.fetchProjects()
})
</script>

<style scoped>
.page-wrap {
  max-width: 1120px;
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
  color: #3D2E1F;
  letter-spacing: -0.02em;
  margin: 0;
}

.page-count {
  font-size: 13px;
  color: #7A6855;
  font-weight: 400;
}

/* ── 统计卡片 ── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #FFFDF9;
  border: 1px solid rgba(198, 123, 92, 0.12);
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.2s ease;
}
.stat-card:hover {
  border-color: rgba(198, 123, 92, 0.3);
  box-shadow: 0 2px 8px rgba(198, 123, 92, 0.08);
  transform: translateY(-1px);
}

.stat-icon {
  font-size: 24px;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-icon--total { background: rgba(198, 123, 92, 0.1); }
.stat-icon--active { background: rgba(123, 168, 125, 0.12); }
.stat-icon--completed { background: rgba(76, 175, 80, 0.1); }
.stat-icon--archived { background: rgba(158, 158, 158, 0.12); }

.stat-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #3D2E1F;
  line-height: 1.2;
}
.stat-label {
  font-size: 12px;
  color: #7A6855;
}

/* ── 筛选区 ── */
.filter-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 14px;
  background: rgba(198, 123, 92, 0.06);
  border: 1px solid rgba(198, 123, 92, 0.15);
  border-radius: 8px;
  font-size: 13px;
}
.batch-count {
  color: #C67B5C;
  font-weight: 600;
}

/* ── 表格 ── */
.table-card {
  background: #FFFDF9;
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
  .stats-row { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .filter-section { flex-direction: column; align-items: stretch; }
  .filter-section > * { width: 100%; }
  :deep(.n-data-table-wrapper) { overflow-x: auto; }
}
</style>
