<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">审计日志</h1>
        <span class="page-count">{{ pagination.itemCount }} 条记录</span>
      </div>
      <div class="filter-section" style="margin-bottom:0">
        <n-input v-model:value="filters.userId" placeholder="用户ID" style="width:150px" clearable @keyup.enter="fetchLogs" />
        <n-input v-model:value="filters.action" placeholder="操作类型" style="width:150px" clearable @keyup.enter="fetchLogs" />
        <n-button @click="fetchLogs">搜索</n-button>
      </div>
    </header>

    <!-- 表格 -->
    <div class="table-card">
      <n-data-table
        :columns="columns"
        :data="logs"
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
          @update:page="(p: number) => { pagination.page = p; fetchLogs() }"
          @update:page-size="(s: number) => { pagination.pageSize = s; pagination.page = 1; fetchLogs() }"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { h, ref, reactive, onMounted } from 'vue'
import type { DataTableColumn } from 'naive-ui'
import { NTag, useMessage } from 'naive-ui'
import { listAuditLogs } from '@/modules/system/api/system'
import type { AuditLogItem } from '@/modules/system/types/system'

const message = useMessage()
const logs = ref<AuditLogItem[]>([])
const loading = ref(false)
const filters = reactive({ userId: '', action: '' })
const pagination = reactive({ page: 1, pageSize: 20, showSizePicker: true, pageSizes: [10, 20, 50], itemCount: 0 })

const actionColors: Record<string, string> = {
  create: 'success', update: 'info', delete: 'error', login: 'primary', logout: 'warning',
}

async function fetchLogs() {
  loading.value = true
  try {
    const res: any = await listAuditLogs({
      page: pagination.page,
      page_size: pagination.pageSize,
      user_id: filters.userId || undefined,
      action: filters.action || undefined,
    })
    logs.value = res.data?.items || []
    pagination.itemCount = res.data?.total || 0
  } catch { message.error('加载审计日志失败') } finally { loading.value = false }
}

const columns: DataTableColumn<AuditLogItem>[] = [
  { title: '用户', key: 'username', width: 100 },
  { title: '操作', key: 'action', width: 90, render: r => h(NTag, { size: 'small', type: (actionColors[r.action] as any) || 'default' }, () => r.action) },
  { title: '资源类型', key: 'resource_type', width: 100, render: r => r.resource_type || '-' },
  { title: '资源ID', key: 'resource_id', width: 200, ellipsis: { tooltip: true }, render: r => r.resource_id || '-' },
  { title: '详情', key: 'detail', ellipsis: { tooltip: true } },
  { title: 'IP', key: 'ip', width: 130, render: r => r.ip || '-' },
  { title: '时间', key: 'created_at', width: 170 },
]

onMounted(fetchLogs)
</script>

<style scoped>
.page-wrap { max-width: 1120px; margin: 0 auto; padding: 32px 24px 64px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.header-left { display: flex; align-items: baseline; gap: 12px; }
.page-title { font-size: 24px; font-weight: 700; color: #3D2E1F; letter-spacing: -0.02em; margin: 0; }
.page-count { font-size: 13px; color: #7A6855; }
.table-card { background: #FFFDF9; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 12px; overflow: hidden; }
.pagination-wrap { display: flex; justify-content: flex-end; padding: 16px 20px; border-top: 1px solid rgba(0, 0, 0, 0.04); }
.filter-section { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
@media (max-width: 768px) { .page-wrap { padding: 16px 12px 48px; } .page-header { flex-wrap: wrap; gap: 10px; } .filter-section { flex-direction: column; align-items: stretch; } .filter-section > * { width: 100%; } }
</style>
