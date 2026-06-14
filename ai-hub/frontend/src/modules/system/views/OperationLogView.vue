<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">操作日志</h1>
        <span class="page-count">{{ pagination.itemCount }} 条记录</span>
      </div>
      <div class="filter-section" style="margin-bottom:0">
        <n-input v-model:value="filters.module" placeholder="模块" style="width:120px" clearable @keyup.enter="fetchLogs" />
        <n-input v-model:value="filters.action" placeholder="操作" style="width:120px" clearable @keyup.enter="fetchLogs" />
        <n-input v-model:value="filters.keyword" placeholder="关键字搜索" style="width:180px" clearable @keyup.enter="fetchLogs" />
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
import { listOperationLogs } from '@/modules/system/api/system'
import type { OperationLogItem } from '@/modules/system/types/system'

const message = useMessage()
const logs = ref<OperationLogItem[]>([])
const loading = ref(false)
const filters = reactive({ module: '', action: '', keyword: '' })
const pagination = reactive({ page: 1, pageSize: 20, showSizePicker: true, pageSizes: [10, 20, 50], itemCount: 0 })

async function fetchLogs() {
  loading.value = true
  try {
    const res: any = await listOperationLogs({
      page: pagination.page,
      page_size: pagination.pageSize,
      module: filters.module || undefined,
      action: filters.action || undefined,
      keyword: filters.keyword || undefined,
    })
    logs.value = res.data?.items || []
    pagination.itemCount = res.data?.total || 0
  } catch { message.error('加载操作日志失败') } finally { loading.value = false }
}

const columns: DataTableColumn<OperationLogItem>[] = [
  { title: '时间', key: 'timestamp', width: 170 },
  { title: '模块', key: 'module', width: 100 },
  { title: '操作', key: 'action', width: 80, render: r => h(NTag, { size: 'small' }, () => r.action) },
  { title: '用户', key: 'username', width: 90 },
  { title: '资源类型', key: 'resource_type', width: 90, render: r => r.resource_type || '-' },
  { title: '资源名称', key: 'resource_name', ellipsis: { tooltip: true }, render: r => r.resource_name || '-' },
  { title: '详情', key: 'detail', ellipsis: { tooltip: true }, render: r => r.detail || '-' },
  { title: '耗时', key: 'duration_ms', width: 80, render: r => r.duration_ms ? `${r.duration_ms}ms` : '-' },
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
