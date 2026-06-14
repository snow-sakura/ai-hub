<template>
  <div class="page-wrap">
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">项目成员</h1>
        <span class="page-count">{{ allMembers.length }} 个成员</span>
      </div>
      <n-button type="primary" @click="openCreate">
        + 添加成员
      </n-button>
    </header>

    <!-- 搜索 -->
    <div class="toolbar">
      <n-input
        v-model:value="searchKeyword"
        placeholder="搜索成员姓名..."
        clearable
        :style="{ width: '240px' }"
        @update:value="onSearchInput"
      />
    </div>

    <!-- 角色筛选 -->
    <div class="role-filter-bar">
      <span
        v-for="opt in roleOptions"
        :key="opt.value"
        class="role-filter-chip"
        :class="{ 'role-filter-chip--active': roleFilter === opt.value }"
        :style="{ '--chip-color': roleColors[opt.value] }"
        @click="roleFilter = roleFilter === opt.value ? '' : opt.value"
      >
        {{ opt.label }}
      </span>
      <span v-if="roleFilter" class="clear-filter" @click="roleFilter = ''">清除筛选</span>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-wrap">
      <n-spin size="small" />
      <span class="loading-text">加载中...</span>
    </div>

    <!-- 表格 -->
    <div v-else-if="filteredMembers.length > 0" class="table-card">
      <n-data-table
        :columns="columns"
        :data="filteredMembers"
        :bordered="false"
        :single-line="false"
        size="small"
      />
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">{{ roleFilter ? '🔍' : '👥' }}</div>
      <div class="empty-title">
        {{ searchKeyword ? '未匹配到成员' : roleFilter ? '该角色暂无成员' : '暂无成员' }}
      </div>
      <div v-if="!searchKeyword && !roleFilter" class="empty-desc">点击「添加成员」邀请成员加入项目</div>
    </div>

    <!-- 添加成员弹窗 -->
    <n-modal
      v-model:show="showAddModal"
      preset="card"
      title="添加成员"
      :style="{ maxWidth: '400px' }"
      @after-leave="resetAddForm"
    >
      <n-form label-placement="top">
        <n-form-item label="成员姓名">
          <n-input v-model:value="newMemberName" placeholder="输入成员姓名" />
        </n-form-item>
        <n-form-item label="角色">
          <n-select v-model:value="newMemberRole" :options="roleOptions" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-actions">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button type="primary" :disabled="!newMemberName.trim()" :loading="isAdding" @click="handleAddMember">
            添加
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 编辑成员弹窗 -->
    <n-modal
      v-model:show="showEditModal"
      preset="card"
      title="编辑成员角色"
      :style="{ maxWidth: '400px' }"
      @after-leave="resetEditForm"
    >
      <n-alert type="info" :bordered="false" style="margin-bottom: 16px;">
        仅支持修改成员角色。如需修改姓名，请移除后重新添加。
      </n-alert>
      <n-form label-placement="top">
        <n-form-item label="成员姓名">
          <n-input :value="editForm.name" disabled />
        </n-form-item>
        <n-form-item label="角色">
          <n-select v-model:value="editForm.role" :options="roleOptions" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-actions">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" :loading="isEditing" @click="handleEditSave">
            保存
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 移除确认弹窗 -->
    <n-modal v-model:show="showRemoveConfirm" preset="dialog" type="warning" title="确认移除">
      <p>确定要移除成员「{{ removingMember?.name }}」吗？</p>
      <template #action>
        <n-button @click="showRemoveConfirm = false">取消</n-button>
        <n-button type="error" :loading="isRemoving" @click="confirmRemove">确认移除</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { NButton, NInput, NSelect, NSpin, NDataTable, NTag, NModal, NForm, NFormItem, NAlert, useMessage } from 'naive-ui'
import type { DataTableColumn } from 'naive-ui'
import * as memberApi from '@/modules/ai_testing/api/project'
import type { ProjectMember, MemberRole } from '@/modules/ai_testing/types/project'
import { onMounted } from 'vue'

const message = useMessage()

const loading = ref(false)
const searchKeyword = ref('')
const roleFilter = ref('')
let searchTimer: ReturnType<typeof setTimeout> | null = null

// ── 角色颜色 ──
const roleColors: Record<string, string> = {
  owner: '#C67B5C',
  tester: '#7BA87D',
  viewer: '#8B9DC3',
}

// ── 添加成员 ──
const showAddModal = ref(false)
const isAdding = ref(false)
const newMemberName = ref('')
const newMemberRole = ref('tester')

function resetAddForm() {
  newMemberName.value = ''
  newMemberRole.value = 'tester'
}

function openCreate() {
  resetAddForm()
  showAddModal.value = true
}

// ── 编辑成员 ──
const showEditModal = ref(false)
const isEditing = ref(false)
const editingMember = ref<ProjectMember | null>(null)
const editForm = ref({ name: '', role: 'tester' as string })

function resetEditForm() {
  editingMember.value = null
  editForm.value = { name: '', role: 'tester' }
}

function openEdit(member: ProjectMember) {
  editingMember.value = member
  editForm.value = { name: member.name, role: member.role }
  showEditModal.value = true
}

// ── 移除成员 ──
const showRemoveConfirm = ref(false)
const removingMember = ref<ProjectMember | null>(null)
const isRemoving = ref(false)

// ── 角色编辑（表格内联） ──
const editingRoleId = ref<string | null>(null)
const editingRoleValue = ref('tester')
const isSavingRole = ref(false) // 防止重复提交

const allMembers = ref<ProjectMember[]>([])

const roleOptions = [
  { label: '负责人', value: 'owner' },
  { label: '测试员', value: 'tester' },
  { label: '观察者', value: 'viewer' },
]

const filteredMembers = computed(() => {
  let list = allMembers.value
  const kw = searchKeyword.value.toLowerCase()
  if (kw) list = list.filter(m => m.name.toLowerCase().includes(kw))
  if (roleFilter.value) list = list.filter(m => m.role === roleFilter.value)
  return list
})

function roleLabel(role: string): string {
  const map: Record<string, string> = { owner: '负责人', tester: '测试员', viewer: '观察者' }
  return map[role] || role
}

// ── 搜索防抖 ──
function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {}, 200)
}

// ── 内联角色编辑（修复重复保存问题） ──
function startEditRole(member: ProjectMember) {
  editingRoleValue.value = member.role
  editingRoleId.value = member.id
}

async function saveRole(memberId: string) {
  if (!editingRoleId.value || isSavingRole.value) return
  isSavingRole.value = true
  const roles: Record<string, string> = { owner: '负责人', tester: '测试员', viewer: '观察者' }
  const prevLabel = roles[editingRoleValue.value] || editingRoleValue.value
  try {
    const res = await memberApi.updateMemberRole(memberId, { role: editingRoleValue.value as MemberRole })
    if (res.data) {
      const idx = allMembers.value.findIndex(m => m.id === memberId)
      if (idx !== -1) allMembers.value[idx].role = editingRoleValue.value as MemberRole
      message.success(`角色已变更为 ${prevLabel}`)
    } else {
      message.error('角色更新失败')
    }
  } catch (e) {
    message.error('角色更新异常')
    console.error('更新角色失败:', e)
  } finally {
    isSavingRole.value = false
    editingRoleId.value = null
  }
}

// ── 添加 ──
async function handleAddMember() {
  if (!newMemberName.value.trim()) return
  isAdding.value = true
  try {
    const res = await memberApi.addMemberStandalone({ name: newMemberName.value.trim(), role: newMemberRole.value as MemberRole })
    if (res.data) {
      allMembers.value.unshift(res.data)
      message.success(`成员「${res.data.name}」已添加`)
      showAddModal.value = false
    } else {
      message.error('添加失败，请重试')
    }
  } catch (e) {
    message.error('添加成员异常')
    console.error('添加成员失败:', e)
  } finally {
    isAdding.value = false
  }
}

// ── 编辑保存 ──
async function handleEditSave() {
  if (!editForm.value.role || !editingMember.value) return
  isEditing.value = true
  try {
    await memberApi.updateMemberRole(editingMember.value.id, { role: editForm.value.role as MemberRole })
    const idx = allMembers.value.findIndex(m => m.id === editingMember.value!.id)
    if (idx !== -1) {
      allMembers.value[idx] = {
        ...allMembers.value[idx],
        role: editForm.value.role as MemberRole,
      }
    }
    const label = roleLabel(editForm.value.role)
    message.success(`成员角色已更新为 ${label}`)
    showEditModal.value = false
  } catch (e) {
    message.error('角色更新异常')
    console.error('编辑成员失败:', e)
  } finally {
    isEditing.value = false
  }
}

// ── 移除 ──
function handleRemoveMember(member: ProjectMember) {
  removingMember.value = member
  showRemoveConfirm.value = true
}

async function confirmRemove() {
  if (!removingMember.value) return
  isRemoving.value = true
  try {
    const res = await memberApi.removeMember(removingMember.value.id)
    if (res.data !== false) {
      allMembers.value = allMembers.value.filter(m => m.id !== removingMember.value!.id)
      message.success(`成员「${removingMember.value.name}」已移除`)
    } else {
      message.error('移除失败')
    }
    showRemoveConfirm.value = false
  } catch (e) {
    message.error('移除成员异常')
    console.error('移除成员失败:', e)
  } finally {
    isRemoving.value = false
    removingMember.value = null
  }
}

const columns = computed<DataTableColumn<ProjectMember>[]>(() => [
  {
    title: '姓名',
    key: 'name',
    align: 'center',
    width: 200,
    render(row) {
      const displayName = (row.name || '').trim()
      return h('div', { class: 'member-name-cell' }, displayName)
    },
  },
  {
    title: '角色',
    key: 'role',
    align: 'center',
    width: 160,
    render(row) {
      if (editingRoleId.value === row.id) {
        return h(NSelect, {
          value: editingRoleValue.value,
          size: 'tiny',
          options: roleOptions,
          style: { width: '100px' },
          // 修复：onUpdate:value 只记录值，不提交
          'onUpdate:value': (val: string) => {
            editingRoleValue.value = val
          },
          // 修复：只在失焦时提交一次
          onBlur: () => saveRole(row.id),
        })
      }
      return h(NTag, {
        size: 'small',
        bordered: false,
        style: {
          cursor: 'pointer',
          background: `${roleColors[row.role] || '#C67B5C'}18`,
          color: roleColors[row.role] || '#C67B5C',
          border: `1px solid ${roleColors[row.role] || '#C67B5C'}30`,
          fontWeight: 500,
        },
        onClick: () => startEditRole(row),
      }, { default: () => roleLabel(row.role) })
    },
  },
  {
    title: '操作',
    key: 'actions',
    align: 'center',
    width: 160,
    render(row) {
      return h('div', { class: 'table-actions' }, [
        h(NButton, {
          text: true,
          size: 'small',
          style: 'color: #C67B5C;',
          onClick: () => openEdit(row),
        }, { default: () => '编辑' }),
        h('span', { class: 'action-divider' }, '|'),
        h(NButton, {
          text: true,
          size: 'small',
          type: 'error',
          onClick: () => handleRemoveMember(row),
        }, { default: () => '移除' }),
      ])
    },
  },
])

onMounted(async () => {
  loading.value = true
  try {
    const res = await memberApi.getAllMembers()
    allMembers.value = res.data || []
  } catch (e) {
    console.error('获取成员列表失败:', e)
    message.error('加载成员列表失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-wrap {
  max-width: 800px;
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
  margin-bottom: 12px;
}

/* ── 角色筛选 ── */
.role-filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.role-filter-chip {
  padding: 4px 14px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid rgba(0,0,0,0.08);
  color: #5C4A38;
  background: #FFFDF9;
  transition: all 0.15s ease;
  user-select: none;
}
.role-filter-chip:hover {
  border-color: var(--chip-color, #C67B5C);
  color: var(--chip-color, #C67B5C);
}
.role-filter-chip--active {
  background: var(--chip-color, #C67B5C);
  color: #fff;
  border-color: var(--chip-color, #C67B5C);
}
.clear-filter {
  font-size: 12px;
  color: #C67B5C;
  cursor: pointer;
  text-decoration: underline;
  margin-left: 4px;
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
  gap: 16px;
}

.action-divider {
  color: rgba(0, 0, 0, 0.12);
  font-size: 12px;
  user-select: none;
}

.member-name-cell {
  font-size: 14px;
  font-weight: 500;
  color: #3D2E1F;
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
