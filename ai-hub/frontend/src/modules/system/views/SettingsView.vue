<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统设置</h1>
        <span class="page-count">{{ settings.length }} 项配置</span>
      </div>
      <n-button @click="fetchSettings">刷新</n-button>
    </header>

    <!-- 表格 -->
    <div class="table-card">
      <n-data-table
        :columns="columns"
        :data="settings"
        :loading="loading"
        :bordered="false"
        :single-line="false"
        striped
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { h, ref, reactive, onMounted } from 'vue'
import type { DataTableColumn } from 'naive-ui'
import { NButton, NInput, useMessage } from 'naive-ui'
import { listSettings, updateSetting } from '@/modules/system/api/system'
import type { SystemSetting } from '@/modules/system/types/system'

const message = useMessage()
const settings = ref<SystemSetting[]>([])
const loading = ref(false)
const editing = reactive<Record<string, string>>({})

async function fetchSettings() {
  loading.value = true
  try {
    const res: any = await listSettings()
    settings.value = res.data || []
    settings.value.forEach(s => { editing[s.key] = s.value })
  } catch { message.error('加载设置失败') } finally { loading.value = false }
}

async function handleSave(key: string) {
  try {
    await updateSetting(key, editing[key])
    message.success('设置更新成功')
    fetchSettings()
  } catch { message.error('更新失败') }
}

const columns: DataTableColumn<SystemSetting>[] = [
  { title: '键', key: 'key', width: 200 },
  { title: '值', key: 'value', render: (row) => h(NInput, {
    value: editing[row.key] ?? row.value,
    'onUpdate:value': (v: string) => editing[row.key] = v,
    placeholder: '请输入值',
  })},
  { title: '描述', key: 'description', render: r => r.description || '-' },
  {
    title: '操作', key: 'actions', width: 80,
    render: (row) => h(NButton, {
      size: 'small', type: 'primary',
      onClick: () => handleSave(row.key),
    }, () => '保存'),
  },
]

onMounted(fetchSettings)
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
