<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">用户管理</h1>
        <span class="page-count">{{ pagination.itemCount }} 个用户</span>
      </div>
      <n-button type="primary" @click="openCreate">新建用户</n-button>
    </header>

    <!-- 表格 -->
    <div class="table-card">
      <n-data-table
        :columns="columns"
        :data="users"
        :loading="loading"
        :bordered="false"
        :single-line="false"
        striped
      />

      <div v-if="pagination.itemCount > 0" class="pagination-wrap">
        <n-pagination
          v-model:page="pagination.page"
          :page-count="Math.ceil(pagination.itemCount / pagination.pageSize)"
          :page-size="pagination.pageSize"
          :page-slot="7"
          show-size-picker
          :page-sizes="[10, 20, 50]"
          @update:page="(p: number) => { pagination.page = p; fetchUsers() }"
          @update:page-size="(s: number) => { pagination.pageSize = s; pagination.page = 1; fetchUsers() }"
        />
      </div>
    </div>

    <!-- 用户表单弹窗 -->
    <n-modal v-model:show="showModal" :title="isEditing ? '编辑用户' : '新建用户'" preset="card" style="width:520px">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="form.username" :disabled="isEditing" />
        </n-form-item>
        <n-form-item v-if="!isEditing" label="密码" path="password">
          <n-input v-model:value="form.password" type="password" show-password-on="click" />
        </n-form-item>
        <n-form-item label="显示名称" path="display_name">
          <n-input v-model:value="form.display_name" />
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input v-model:value="form.email" />
        </n-form-item>
        <n-form-item label="部门" path="department">
          <n-input v-model:value="form.department" />
        </n-form-item>
        <n-form-item label="职位" path="position">
          <n-input v-model:value="form.position" />
        </n-form-item>
        <n-form-item label="角色" path="role_ids">
          <n-select v-model:value="form.role_ids" :options="roleOptions" multiple />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="handleSave">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { h, ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { DataTableColumn, FormInst, FormRules } from 'naive-ui'
import { NButton, NSwitch, NTag, useMessage } from 'naive-ui'
import { listUsers, createUser, updateUser, deleteUser, toggleUserActive, listRoles, setUserRoles } from '@/modules/system/api/system'
import type { UserItem, RoleItem } from '@/modules/system/types/system'

const router = useRouter()
const message = useMessage()
const users = ref<UserItem[]>([])
const roles = ref<RoleItem[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref('')
const formRef = ref<FormInst | null>(null)
const pagination = reactive({ page: 1, pageSize: 20, showSizePicker: true, pageSizes: [10, 20, 50], itemCount: 0 })

const form = reactive({
  username: '',
  password: '',
  display_name: '',
  email: '',
  department: '',
  position: '',
  role_ids: [] as string[],
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请设置密码', trigger: 'blur' }],
}

const roleOptions = computed(() => roles.value.map(r => ({ label: `${r.name}${r.description ? ' - ' + r.description : ''}`, value: r.id })))

async function fetchUsers() {
  loading.value = true
  try {
    const res: any = await listUsers(pagination.page, pagination.pageSize)
    users.value = res.data?.items || []
    pagination.page = res.data?.page || 1
    pagination.pageSize = res.data?.page_size || 20
    pagination.itemCount = res.data?.total || 0
  } catch { message.error('加载用户列表失败') } finally { loading.value = false }
}

async function fetchRoles() {
  try {
    const res: any = await listRoles()
    roles.value = res.data || []
  } catch { /* ignore */ }
}

function openCreate() {
  isEditing.value = false
  editingId.value = ''
  form.username = ''; form.password = ''; form.display_name = ''; form.email = ''
  form.department = ''; form.position = ''; form.role_ids = []
  showModal.value = true
}

async function openEdit(row: UserItem) {
  isEditing.value = true
  editingId.value = row.id
  form.username = row.username
  form.password = ''
  form.display_name = row.display_name || ''
  form.email = row.email || ''
  form.department = row.department || ''
  form.position = row.position || ''
  try {
    const res: any = await (await import('@/modules/system/api/system')).getUserRoles(row.id)
    form.role_ids = (res.data || []).map((r: RoleItem) => r.id)
  } catch { form.role_ids = [] }
  showModal.value = true
}

async function handleSave() {
  try { await formRef.value?.validate() } catch { return }
  saving.value = true
  try {
    if (isEditing.value) {
      await updateUser(editingId.value, {
        display_name: form.display_name || undefined,
        email: form.email || undefined,
        department: form.department || undefined,
        position: form.position || undefined,
      })
      if (form.role_ids.length) {
        await setUserRoles(editingId.value, form.role_ids)
      }
      message.success('用户更新成功')
    } else {
      const res: any = await createUser({
        username: form.username,
        password: form.password,
        display_name: form.display_name || undefined,
        email: form.email || undefined,
        department: form.department || undefined,
        position: form.position || undefined,
        role_ids: form.role_ids.length ? form.role_ids : undefined,
      })
      message.success('用户创建成功')
    }
    showModal.value = false
    fetchUsers()
  } catch (err: any) {
    message.error(err?.response?.data?.detail || '操作失败')
  } finally { saving.value = false }
}

async function handleToggleActive(row: UserItem) {
  try {
    await toggleUserActive(row.id, !row.is_active)
    message.success(row.is_active ? '已禁用' : '已启用')
    fetchUsers()
  } catch { message.error('操作失败') }
}

async function handleDelete(row: UserItem) {
  const dialog = await (await import('naive-ui')).useDialog()
  dialog.warning({
    title: '确认删除',
    content: `确定要删除用户「${row.username}」吗？`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteUser(row.id)
        message.success('用户已删除')
        fetchUsers()
      } catch { message.error('删除失败') }
    },
  })
}

const columns: DataTableColumn<UserItem>[] = [
  { title: '用户名', key: 'username', width: 120 },
  { title: '显示名称', key: 'display_name', width: 120, render: r => r.display_name || '-' },
  { title: '邮箱', key: 'email', ellipsis: { tooltip: true }, render: r => r.email || '-' },
  { title: '部门', key: 'department', width: 120, render: r => r.department || '-' },
  { title: '状态', key: 'is_active', width: 80, render: r => h(NTag, { type: r.is_active ? 'success' : 'error', size: 'small' }, () => r.is_active ? '启用' : '禁用') },
  { title: '创建时间', key: 'created_at', width: 170 },
  {
    title: '操作', key: 'actions', width: 220,
    render: (row) => [
      h(NButton, { size: 'small', quaternary: true, onClick: () => openEdit(row) }, () => '编辑'),
      h(NSwitch, { value: row.is_active, 'onUpdate:value': () => handleToggleActive(row), style: 'margin: 0 8px' }),
      h(NButton, { size: 'small', quaternary: true, type: 'error', onClick: () => handleDelete(row) }, () => '删除'),
    ],
  },
]

onMounted(() => { fetchUsers(); fetchRoles() })
</script>

<style scoped>
.page-wrap { max-width: 1120px; margin: 0 auto; padding: 32px 24px 64px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.header-left { display: flex; align-items: baseline; gap: 12px; }
.page-title { font-size: 24px; font-weight: 700; color: #3D2E1F; letter-spacing: -0.02em; margin: 0; }
.page-count { font-size: 13px; color: #7A6855; }
.table-card { background: #FFFDF9; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 12px; overflow: hidden; }
.pagination-wrap { display: flex; justify-content: flex-end; padding: 16px 20px; border-top: 1px solid rgba(0, 0, 0, 0.04); }
@media (max-width: 768px) { .page-wrap { padding: 16px 12px 48px; } .page-header { flex-wrap: wrap; gap: 10px; } }
</style>
