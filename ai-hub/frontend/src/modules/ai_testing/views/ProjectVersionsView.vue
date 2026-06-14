<template>
  <div class="page-wrap">
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">版本管理</h1>
        <span class="page-count">{{ allVersions.length }} 个版本</span>
      </div>
      <n-button type="primary" @click="openCreate">
        + 新建版本
      </n-button>
    </header>

    <!-- 搜索 -->
    <div class="toolbar">
      <n-input
        v-model:value="searchKeyword"
        placeholder="搜索版本名称..."
        clearable
        :style="{ width: '220px' }"
        @update:value="onSearchInput"
      />
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-wrap">
      <n-spin size="small" />
      <span class="loading-text">加载中...</span>
    </div>

    <!-- 表格 -->
    <div v-else-if="filteredVersions.length > 0" class="table-card">
      <n-data-table
        :columns="columns"
        :data="filteredVersions"
        :bordered="false"
        :single-line="false"
        size="small"
      />
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">{{ searchKeyword ? '🔍' : '🏷️' }}</div>
      <div class="empty-title">
        {{ searchKeyword ? '未匹配到版本' : '暂无版本' }}
      </div>
      <div v-if="!searchKeyword" class="empty-desc">点击「新建版本」创建第一个版本</div>
    </div>

    <!-- 创建/编辑弹窗 -->
    <n-modal
      v-model:show="showModal"
      preset="card"
      :title="editingVersion ? '编辑版本' : '新建版本'"
      :style="{ maxWidth: '520px' }"
      @after-leave="resetForm"
    >
      <n-form :model="formData" label-placement="top">
        <n-form-item label="版本名称" path="name">
          <n-input v-model:value="formData.name" placeholder="如 v1.0.0" :maxlength="200" />
        </n-form-item>
        <n-form-item label="版本描述" path="description">
          <n-input v-model:value="formData.description" type="textarea" :rows="3" placeholder="版本说明..." />
        </n-form-item>
        <n-form-item label="版本状态" path="status">
          <n-select v-model:value="formData.status" :options="statusOptions" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-actions">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="isSubmitting" @click="handleSave">
            {{ editingVersion ? '保存' : '创建' }}
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 版本状态变更确认 -->
    <n-modal v-model:show="showStatusConfirm" preset="dialog" :type="statusConfirmType" :title="statusConfirmTitle">
      <p>{{ statusConfirmMessage }}</p>
      <template #action>
        <n-button @click="showStatusConfirm = false">取消</n-button>
        <n-button
          :type="statusConfirmType === 'warning' ? 'warning' : 'primary'"
          :loading="isChangingStatus"
          @click="confirmStatusChange"
        >确认</n-button>
      </template>
    </n-modal>

    <!-- 删除确认弹窗 -->
    <n-modal v-model:show="showDeleteConfirm" preset="dialog" type="error" title="删除版本">
      <p>确定要删除版本「{{ deletingVersion?.name }}」吗？此操作不可撤销。</p>
      <template #action>
        <n-button @click="showDeleteConfirm = false">取消</n-button>
        <n-button type="error" :loading="isDeleting" @click="confirmDelete">确认删除</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { NButton, NInput, NSpin, NDataTable, NTag, NModal, NForm, NFormItem, NSelect, useMessage } from 'naive-ui'
import type { DataTableColumn } from 'naive-ui'
import { useVersionStore } from '@/modules/ai_testing/stores/version'
import type { ProjectVersion, VersionStatus } from '@/modules/ai_testing/types/version'
import { onMounted } from 'vue'

const message = useMessage()
const versionStore = useVersionStore()

const loading = ref(false)
const showModal = ref(false)
const editingVersion = ref<ProjectVersion | null>(null)
const isSubmitting = ref(false)
const searchKeyword = ref('')

// ── 状态确认弹窗 ──
const showStatusConfirm = ref(false)
const isChangingStatus = ref(false)
const statusConfirmVersion = ref<ProjectVersion | null>(null)
const statusConfirmTarget = ref<VersionStatus>('active')
const statusConfirmType = ref<'warning' | 'info' | 'success'>('info')
const statusConfirmTitle = ref('')
const statusConfirmMessage = ref('')

// ── 删除确认 ──
const showDeleteConfirm = ref(false)
const deletingVersion = ref<ProjectVersion | null>(null)
const isDeleting = ref(false)

const allVersions = ref<ProjectVersion[]>([])
let searchTimer: ReturnType<typeof setTimeout> | null = null

const formData = ref({
  name: '',
  description: '',
  status: 'active' as string,
})

const filteredVersions = computed(() => {
  let list = allVersions.value
  const kw = searchKeyword.value.toLowerCase()
  if (kw) list = list.filter(v => v.name.toLowerCase().includes(kw))
  return list
})

const statusLabels: Record<string, string> = {
  active: '活跃',
  released: '已发布',
  archived: '已归档',
}

const statusOptions = [
  { label: '活跃', value: 'active' },
  { label: '已发布', value: 'released' },
  { label: '已归档', value: 'archived' },
]

const statusType: Record<string, 'success' | 'info' | 'default'> = {
  active: 'success',
  released: 'info',
  archived: 'default',
}

function formatTime(iso: string) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function resetForm() {
  editingVersion.value = null
  formData.value = { name: '', description: '', status: 'active' }
}

function openCreate() {
  editingVersion.value = null
  formData.value = { name: '', description: '', status: 'active' }
  showModal.value = true
}

function startEdit(v: ProjectVersion) {
  editingVersion.value = v
  formData.value = { name: v.name, description: v.description, status: v.status }
  showModal.value = true
}

// ── 搜索防抖 ──
function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {}, 200)
}

// ── 版本状态变更（仅保留归档） ──
function getNextStatus(current: VersionStatus): { next: VersionStatus; label: string; type: 'warning' | 'info' | 'success'; message: string } | null {
  if (current === 'released') return { next: 'archived', label: '归档', type: 'warning', message: '归档后，该版本将标记为「已归档」，无法继续使用。' }
  return null
}

function handleStatusTransition(v: ProjectVersion) {
  const transition = getNextStatus(v.status)
  if (!transition) return
  statusConfirmVersion.value = v
  statusConfirmTarget.value = transition.next
  statusConfirmType.value = transition.type
  statusConfirmTitle.value = `${transition.label}版本`
  statusConfirmMessage.value = `确定要将版本「${v.name}」${transition.label}吗？${transition.message}`
  showStatusConfirm.value = true
}

async function confirmStatusChange() {
  if (!statusConfirmVersion.value) return
  isChangingStatus.value = true
  try {
    const ok = await versionStore.update(statusConfirmVersion.value.id, {
      status: statusConfirmTarget.value,
    })
    if (ok) {
      const label = statusLabels[statusConfirmTarget.value]
      message.success(`版本「${statusConfirmVersion.value.name}」已${label}`)
      refreshList()
    } else {
      message.error('状态变更失败')
    }
    showStatusConfirm.value = false
  } catch (e) {
    message.error('状态变更异常')
    console.error('状态变更失败:', e)
  } finally {
    isChangingStatus.value = false
  }
}

// ── 保存 ──
async function handleSave() {
  if (!formData.value.name.trim()) return
  isSubmitting.value = true
  try {
    if (editingVersion.value) {
      const ok = await versionStore.update(editingVersion.value.id, {
        name: formData.value.name,
        description: formData.value.description,
        status: formData.value.status as VersionStatus,
      })
      if (ok) {
        message.success('版本已更新')
        refreshList()
      } else {
        message.error('版本更新失败')
      }
    } else {
      const res = await versionStore.create({
        name: formData.value.name,
        description: formData.value.description,
        status: formData.value.status as VersionStatus,
      })
      if (res) {
        message.success(`版本「${res.name}」已创建`)
      } else {
        message.error('版本创建失败')
      }
    }
    showModal.value = false
  } catch (e) {
    message.error('保存版本异常')
    console.error('保存版本失败:', e)
  } finally {
    isSubmitting.value = false
  }
}

// ── 删除 ──
function handleDelete(v: ProjectVersion) {
  deletingVersion.value = v
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  if (!deletingVersion.value) return
  isDeleting.value = true
  try {
    await versionStore.remove(deletingVersion.value.id)
    message.success(`版本「${deletingVersion.value.name}」已删除`)
    refreshList()
    showDeleteConfirm.value = false
  } catch (e) {
    message.error('删除版本异常')
    console.error('删除版本失败:', e)
  } finally {
    isDeleting.value = false
  }
}

function refreshList() {
  allVersions.value = [...versionStore.versions]
}

const columns = computed<DataTableColumn<ProjectVersion>[]>(() => [
  {
    title: '状态',
    key: 'status',
    width: 90,
    align: 'center',
    render(row) {
      return h(NTag, {
        type: statusType[row.status] || 'default',
        size: 'tiny',
        round: true,
        bordered: true,
      }, { default: () => statusLabels[row.status] || row.status })
    },
  },
  {
    title: '名称',
    key: 'name',
    ellipsis: { tooltip: true },
    width: 180,
    align: 'center',
    render(row) {
      return h('span', { style: 'color: #3D2E1F; font-weight: 600;' }, row.name)
    },
  },
  {
    title: '描述',
    key: 'description',
    ellipsis: { tooltip: true },
    minWidth: 180,
    align: 'center',
    render(row) {
      return h('span', { style: 'color: #7A6855; font-size: 13px;' }, row.description || '—')
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 150,
    align: 'center',
    render(row) {
      return h('span', { style: 'color: #7A6855; font-size: 12px;' }, formatTime(row.created_at))
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    align: 'center',
    render(row) {
      const transition = getNextStatus(row.status)
      const buttons: any[] = []
      if (transition) {
        buttons.push(h(NButton, {
          size: 'tiny',
          text: true,
          type: transition.type === 'warning' ? 'warning' : 'primary',
          style: transition.type === 'warning' ? 'color: #D4745C;' : 'color: #7BA87D;',
          onClick: () => handleStatusTransition(row),
        }, { default: () => transition.label }))
        buttons.push(h('span', { class: 'action-divider' }, '|'))
      }
      buttons.push(h(NButton, {
        size: 'tiny',
        text: true,
        style: 'color: #C67B5C;',
        onClick: () => startEdit(row),
      }, { default: () => '编辑' }))
      buttons.push(h('span', { class: 'action-divider' }, '|'))
      buttons.push(h(NButton, {
        size: 'tiny',
        text: true,
        type: 'error',
        onClick: () => handleDelete(row),
      }, { default: () => '删除' }))
      return h('div', { class: 'table-actions' }, buttons)
    },
  },
])

onMounted(async () => {
  loading.value = true
  try {
    await versionStore.fetchAll()
    allVersions.value = [...versionStore.versions]
  } catch (e) {
    console.error('获取版本列表失败:', e)
    message.error('加载版本列表失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-wrap {
  max-width: 1100px;
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
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.table-card {
  background: #FFFDF9;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  overflow: hidden;
}

.table-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-divider {
  color: rgba(0, 0, 0, 0.12);
  font-size: 12px;
  user-select: none;
}

.loading-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 64px 0;
}

.loading-text {
  font-size: 14px;
  color: #7A6855;
}

.empty-state {
  text-align: center;
  padding: 80px 24px;
  background: #FFFDF9;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
}
.empty-icon {
  font-size: 36px;
  margin-bottom: 12px;
}
.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #3D2E1F;
  margin-bottom: 8px;
}
.empty-desc {
  font-size: 13px;
  color: #7A6855;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .page-wrap { padding: 16px 12px 48px; }
  .page-header { flex-wrap: wrap; gap: 10px; }
  :deep(.n-data-table-wrapper) { overflow-x: auto; }
}
</style>
