<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">项目管理</h1>
        <span class="page-count">{{ store.total }} 个项目</span>
      </div>
      <n-button type="primary" @click="showCreateModal = true">
        + 新建项目
      </n-button>
    </header>

    <!-- 筛选栏 -->
    <div class="filter-section">
      <n-input
        v-model:value="store.searchKeyword"
        placeholder="搜索项目名称..."
        clearable
        :style="{ width: '260px' }"
        @update:value="handleSearch"
      />
      <n-select
        v-model:value="store.statusFilter"
        placeholder="全部状态"
        clearable
        :style="{ width: '140px' }"
        :options="statusOptions"
        @update:value="handleFilterChange"
      />
    </div>

    <!-- 项目表格 -->
    <div class="table-card">
      <n-data-table
        :columns="columns"
        :data="store.projects"
        :loading="store.isLoading"
        :row-key="(row: any) => row.id"
        :scroll-x="800"
      />

      <!-- 分页 -->
      <div v-if="store.total > store.pageSize" class="pagination-wrap">
        <n-pagination
          v-model:page="store.page"
          :page-count="Math.ceil(store.total / store.pageSize)"
          :page-size="store.pageSize"
          @update:page="handlePageChange"
        />
      </div>
    </div>

    <!-- 新建/编辑弹窗 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      :style="{ width: '520px' }"
      :mask-closable="true"
      @after-leave="editingProject = undefined"
    >
      <ProjectForm
        :edit-data="editingProject"
        @cancel="showCreateModal = false"
        @saved="showCreateModal = false; editingProject = undefined"
      />
    </n-modal>

    <!-- 删除确认弹窗 -->
    <n-modal v-model:show="showDeleteModal" preset="dialog" type="warning" title="确认删除">
      <p>确定要删除项目「{{ deletingProject?.name }}」吗？此操作不可撤销。</p>
      <template #action>
        <n-button @click="showDeleteModal = false">取消</n-button>
        <n-button type="error" :loading="isDeleting" @click="handleDelete">删除</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton, NInput, NSelect, NDataTable, NPagination,
  NModal, useMessage,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import type { TestingProject, ProjectStatus } from '@/modules/ai_testing/types/project'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import StatusTag from '@/modules/ai_testing/components/common/StatusTag.vue'
import ProjectForm from '@/modules/ai_testing/components/project/ProjectForm.vue'

const router = useRouter()
const message = useMessage()
const store = useProjectStore()

const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const editingProject = ref<{ id: string; name: string; description: string; status: ProjectStatus } | undefined>(undefined)
const deletingProject = ref<TestingProject | null>(null)
const isDeleting = ref(false)

const statusOptions = [
  { label: '进行中', value: 'active' },
  { label: '已暂停', value: 'paused' },
  { label: '已完成', value: 'completed' },
  { label: '已归档', value: 'archived' },
]

const columns: DataTableColumns<TestingProject> = [
  {
    title: '项目名称',
    key: 'name',
    width: 200,
    ellipsis: { tooltip: true },
    render(row) {
      return h('a', {
        style: 'color: var(--text-primary, #1a1a2e); font-weight: 500; text-decoration: none; cursor: pointer;',
        onClick: () => router.push(`/ai-testing/projects/${row.id}`),
      }, row.name)
    },
  },
  {
    title: '描述',
    key: 'description',
    width: 240,
    ellipsis: { tooltip: true },
    render(row) {
      return h('span', { style: 'color: #5C4A38; font-size: 13px;' }, row.description || '—')
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render(row) {
      return h(StatusTag, { status: row.status })
    },
  },
  {
    title: '用例',
    key: 'case_count',
    width: 70,
    align: 'center',
    render(row) {
      return h('span', { style: 'color: #374151; font-weight: 500;' }, row.case_count)
    },
  },
  {
    title: '成员',
    key: 'member_count',
    width: 70,
    align: 'center',
    render(row) {
      return h('span', { style: 'color: #374151; font-weight: 500;' }, row.member_count)
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 140,
    render(row) {
      const d = new Date(row.created_at)
      return h('span', { style: 'color: #7A6855; font-size: 12px;' },
        isNaN(d.getTime()) ? row.created_at : d.toLocaleDateString('zh-CN'))
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 140,
    fixed: 'right',
    render(row) {
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        h(NButton, { text: true, size: 'small', onClick: () => handleEdit(row) },
          { default: () => '编辑' }),
        h(NButton, { text: true, size: 'small', type: 'error', onClick: () => handleDeleteConfirm(row) },
          { default: () => '删除' }),
      ])
    },
  },
]

function handleSearch() {
  store.page = 1
  store.fetchProjects()
}

function handleFilterChange() {
  store.page = 1
  store.fetchProjects()
}

function handlePageChange(p: number) {
  store.page = p
  store.fetchProjects()
}

function handleEdit(project: TestingProject) {
  editingProject.value = { id: project.id, name: project.name, description: project.description, status: project.status }
  showCreateModal.value = true
}

function handleDeleteConfirm(project: TestingProject) {
  deletingProject.value = project
  showDeleteModal.value = true
}

async function handleDelete() {
  if (!deletingProject.value) return
  isDeleting.value = true
  try {
    const ok = await store.deleteProject(deletingProject.value.id)
    if (ok) message.success('项目已删除')
    showDeleteModal.value = false
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => {
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
  color: var(--text-primary, #1a1a2e);
  letter-spacing: -0.02em;
  margin: 0;
}

.page-count {
  font-size: 13px;
  color: #7A6855;
  font-weight: 400;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
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
</style>
