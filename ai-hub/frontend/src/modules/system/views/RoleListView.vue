<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">角色管理</h1>
        <span class="page-count">{{ roles.length }} 个角色</span>
      </div>
      <n-button type="primary" @click="openCreate">新建角色</n-button>
    </header>

    <!-- 表格 -->
    <div class="table-card">
      <n-data-table
        :columns="columns"
        :data="roles"
        :loading="loading"
        :bordered="false"
        :single-line="false"
        striped
      />
    </div>

    <!-- 角色表单弹窗 -->
    <n-modal v-model:show="showModal" :title="isEditing ? '编辑角色' : '新建角色'" preset="card" style="width:500px">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
        <n-form-item label="角色名称" path="name">
          <n-input v-model:value="form.name" :disabled="isEditing" placeholder="如：tester" />
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input v-model:value="form.description" type="textarea" rows="2" />
        </n-form-item>
        <n-form-item label="权限" path="permissions">
          <n-dynamic-tags v-model:value="form.permissions" />
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
import { h, ref, reactive, onMounted } from 'vue'
import type { DataTableColumn, FormInst, FormRules } from 'naive-ui'
import { NButton, NTag, useMessage } from 'naive-ui'
import { listRoles, createRole, updateRole, deleteRole } from '@/modules/system/api/system'
import type { RoleItem } from '@/modules/system/types/system'

const message = useMessage()
const roles = ref<RoleItem[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref('')
const formRef = ref<FormInst | null>(null)

const form = reactive({ name: '', description: '', permissions: [] as string[] })

const rules: FormRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
}

async function fetchRoles() {
  loading.value = true
  try {
    const res: any = await listRoles()
    roles.value = res.data || []
  } catch { message.error('加载角色列表失败') } finally { loading.value = false }
}

function openCreate() {
  isEditing.value = false; editingId.value = ''
  form.name = ''; form.description = ''; form.permissions = []
  showModal.value = true
}

function openEdit(row: RoleItem) {
  isEditing.value = true; editingId.value = row.id
  form.name = row.name
  form.description = row.description || ''
  form.permissions = [...(row.permissions || [])]
  showModal.value = true
}

async function handleSave() {
  try { await formRef.value?.validate() } catch { return }
  saving.value = true
  try {
    const data = { name: form.name, description: form.description, permissions: form.permissions }
    if (isEditing.value) {
      await updateRole(editingId.value, data)
      message.success('角色更新成功')
    } else {
      await createRole(data)
      message.success('角色创建成功')
    }
    showModal.value = false
    fetchRoles()
  } catch (err: any) {
    message.error(err?.response?.data?.detail || '操作失败')
  } finally { saving.value = false }
}

async function handleDelete(row: RoleItem) {
  if (row.is_builtin) { message.warning('内置角色不可删除'); return }
  const dialog = await (await import('naive-ui')).useDialog()
  dialog.warning({
    title: '确认删除',
    content: `确定要删除角色「${row.name}」吗？`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteRole(row.id)
        message.success('角色已删除')
        fetchRoles()
      } catch { message.error('删除失败') }
    },
  })
}

const columns: DataTableColumn<RoleItem>[] = [
  { title: '角色名称', key: 'name', width: 130 },
  { title: '描述', key: 'description', ellipsis: { tooltip: true }, render: r => r.description || '-' },
  { title: '权限', key: 'permissions', ellipsis: { tooltip: true }, render: r => {
    const perms = r.permissions || []
    return perms.length ? perms.map(p => h(NTag, { size: 'small', style: 'margin-right:4px' }, () => p)) : '-'
  }},
  { title: '内置', key: 'is_builtin', width: 70, render: r => r.is_builtin ? '是' : '否' },
  { title: '用户数', key: 'user_count', width: 70 },
  {
    title: '操作', key: 'actions', width: 140,
    render: (row) => [
      h(NButton, { size: 'small', quaternary: true, onClick: () => openEdit(row) }, () => '编辑'),
      h(NButton, { size: 'small', quaternary: true, type: 'error', style: 'margin-left:8px', onClick: () => handleDelete(row) }, () => '删除'),
    ],
  },
]

onMounted(fetchRoles)
</script>

<style scoped>
.page-wrap { max-width: 1120px; margin: 0 auto; padding: 32px 24px 64px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.header-left { display: flex; align-items: baseline; gap: 12px; }
.page-title { font-size: 24px; font-weight: 700; color: #3D2E1F; letter-spacing: -0.02em; margin: 0; }
.page-count { font-size: 13px; color: #7A6855; }
.table-card { background: #FFFDF9; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 12px; overflow: hidden; }
@media (max-width: 768px) { .page-wrap { padding: 16px 12px 48px; } .page-header { flex-wrap: wrap; gap: 10px; } }
</style>
