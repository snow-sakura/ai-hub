<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">生成记录</h1>
        <span class="page-count">{{ realtimeTasks.length > 0 ? `${realtimeTasks.length} 个进行中` : '' }}</span>
      </div>
      <div class="header-actions">
        <n-button ghost @click="refreshAll">
          刷新
        </n-button>
        <n-button type="primary" @click="router.push('/ai-testing/generate')">
          + AI 用例生成
        </n-button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <n-card size="small" class="stat-card">
        <div class="stat-value">{{ genStats.total_tasks }}</div>
        <div class="stat-label">总任务数</div>
      </n-card>
      <n-card size="small" class="stat-card stat-success">
        <div class="stat-value">{{ genStats.completed_tasks }}</div>
        <div class="stat-label">已完成</div>
      </n-card>
      <n-card size="small" class="stat-card stat-primary">
        <div class="stat-value">{{ genStats.total_cases }}</div>
        <div class="stat-label">生成用例数</div>
      </n-card>
    </div>

    <n-tabs v-model:value="activeTab" type="line" animated @update:value="handleTabChange">
      <!-- Tab 1: 实时记录 -->
      <n-tab-pane name="realtime" tab="实时记录">
        <div v-if="realtimeLoading" class="loading-wrap">
          <n-spin size="small" />
          <span class="loading-text">正在获取实时状态...</span>
        </div>

        <div v-else-if="realtimeTasks.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <div class="empty-title">暂无运行中的生成任务</div>
          <div class="empty-desc">前往 AI 用例助手创建新任务，运行中的任务将实时显示在此处</div>
          <n-button type="primary" ghost @click="router.push('/ai-testing/generate')">
            去生成用例
          </n-button>
        </div>

        <div v-else class="realtime-grid">
          <div v-for="task in realtimeTasks" :key="task.id" class="realtime-card">
            <div class="card-header">
              <span class="card-status-dot" :class="task.status === 'running' ? 'dot-running' : 'dot-pending'" />
              <n-tag :type="task.status === 'running' ? 'info' : 'default'" size="small" round bordered>
                {{ task.status === 'running' ? '运行中' : '等待中' }}
              </n-tag>
            </div>
            <div class="card-title" :title="task.requirement_title || '未命名任务'">
              {{ task.requirement_title || '未命名任务' }}
            </div>
            <div class="card-meta">
              <span class="meta-item">
                <span class="meta-label">项目</span>
                {{ task.project_name || '—' }}
              </span>
              <span class="meta-item">
                <span class="meta-label">模型</span>
                {{ task.model || '—' }}
              </span>
              <span class="meta-item">
                <span class="meta-label">创建时间</span>
                {{ formatTime(task.created_at) }}
              </span>
            </div>
            <div class="card-actions">
              <n-button text size="small" @click="goToDetail(task)">
                查看详情
              </n-button>
            </div>
          </div>
        </div>
      </n-tab-pane>

      <!-- Tab 2: 历史记录 -->
      <n-tab-pane name="history" tab="历史记录">
        <!-- 筛选栏 -->
        <div class="filter-section">
          <n-input
            v-model:value="keyword"
            placeholder="搜索任务标题..."
            clearable
            :style="{ width: '240px' }"
            @update:value="handleSearch"
          />
          <n-select
            v-model:value="store.tasksFilters.project_id"
            placeholder="全部项目"
            clearable
            :style="{ width: '160px' }"
            :options="projectOptions"
            @update:value="handleFilterChange"
          />
          <n-select
            v-model:value="store.tasksFilters.status"
            placeholder="全部状态"
            clearable
            :style="{ width: '130px' }"
            :options="statusOptions"
            @update:value="handleFilterChange"
          />
        </div>

        <!-- 任务表格 -->
        <div class="table-card">
          <n-data-table
            :columns="columns"
            :data="store.tasks"
            :loading="store.tasksLoading"
            :row-key="(row: any) => row.id"
            :scroll-x="900"
          />

          <div v-if="store.tasksTotal > 0" class="pagination-wrap">
            <n-pagination
              :page="store.tasksPage"
              :page-size="store.tasksPageSize"
              :page-count="Math.ceil(store.tasksTotal / store.tasksPageSize)"
              show-size-picker
              :page-sizes="[10, 20, 50]"
              @update:page="handlePageChange"
              @update:page-size="handlePageSizeChange"
            />
          </div>
        </div>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NTag, useDialog, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import type { GenerationTask } from '@/modules/ai_testing/types/generation'
import { useGenerationStore } from '@/modules/ai_testing/stores/generation'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import { usePolling } from '@/shared/composables/usePolling'
import * as taskDetailApi from '@/modules/ai_testing/api/taskDetail'
import { listGenerationTasks } from '@/modules/ai_testing/api/generation'

const router = useRouter()
const dialog = useDialog()
const message = useMessage()
const store = useGenerationStore()
const projectStore = useProjectStore()

const activeTab = ref('realtime')
const keyword = ref('')

// 实时记录状态
const realtimeLoading = ref(false)
const realtimeTasks = ref<GenerationTask[]>([])

const genStats = reactive({
  total_tasks: 0,
  completed_tasks: 0,
  total_cases: 0,
})

async function fetchGenStats() {
  try {
    const res = await taskDetailApi.getGenerationStats()
    Object.assign(genStats, res.data)
  } catch (e) {
    console.error('获取生成统计失败:', e)
  }
}

const statusOptions = [
  { label: '全部状态', value: '' },
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' },
  { label: '运行中', value: 'running' },
  { label: '等待中', value: 'pending' },
]

const projectOptions = computed(() =>
  projectStore.projects.map(p => ({
    label: p.name,
    value: p.id,
  }))
)

// ── 表格列定义 ──────────────────────────────────────────────
const columns: DataTableColumns<GenerationTask> = [
  {
    title: '标题',
    key: 'requirement_title',
    width: 200,
    ellipsis: { tooltip: true },
    render(row) {
      return h('a', {
        style: 'color: var(--text-primary); font-weight: 500; text-decoration: none; cursor: pointer;',
        onClick: () => goToDetail(row),
      }, row.requirement_title || '未命名任务')
    },
  },
  {
    title: '项目',
    key: 'project_name',
    width: 130,
    render(row) {
      return h('span', { style: 'color: #5C4A38; font-size: 13px;' }, row.project_name || '—')
    },
  },
  {
    title: '模型',
    key: 'model',
    width: 100,
    ellipsis: { tooltip: true },
    render(row) {
      return h('span', { style: 'color: #5C4A38; font-size: 13px;' }, row.model || '—')
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render(row) {
      const isSaved = row.has_saved_cases
      const map: Record<string, { label: string; type: 'success' | 'error' | 'info' | 'default' | 'warning' }> = {
        completed: { label: isSaved ? '已保存' : '已完成', type: isSaved ? 'success' : 'success' },
        failed: { label: '失败', type: 'error' },
        running: { label: '运行中', type: 'info' },
        pending: { label: '等待中', type: 'default' },
      }
      const s = map[row.status] || { label: row.status, type: 'default' as const }
      return h('div', { style: 'display: flex; align-items: center; gap: 4px;' }, [
        h(NTag, { size: 'small', type: s.type, round: true, bordered: false }, { default: () => s.label }),
        isSaved && row.status === 'completed'
          ? h('span', { style: 'font-size: 11px; color: #22a163; margin-left: 2px;' }, '· 已保存')
          : null,
      ])
    },
  },
  {
    title: '生成数',
    key: 'generated_count',
    width: 70,
    render(row) {
      return h('span', { style: 'color: #5C4A38; font-size: 13px;' }, String(row.generated_count ?? '—'))
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 130,
    render(row) {
      return h('span', { style: 'color: #7A6855; font-size: 12px;' }, formatTime(row.created_at))
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 160,
    fixed: 'right',
    render(row) {
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        h(NButton, {
          text: true, size: 'small',
          onClick: () => goToDetail(row),
        }, { default: () => '详情' }),
        h(NButton, {
          text: true, size: 'small',
          onClick: () => handleExport(row),
        }, { default: () => '导出' }),
        h(NButton, {
          text: true, size: 'small', type: 'error',
          onClick: () => handleDelete(row),
        }, { default: () => '删除' }),
      ])
    },
  },
]

// ── 实时记录轮询（使用通用 usePolling composable） ──────────────
const { start: startPolling, stop: stopPolling, refresh: refreshPolling } = usePolling(
  async () => {
    realtimeLoading.value = true
    try {
      const [runningRes, pendingRes] = await Promise.all([
        listGenerationTasks({ status: 'running', page: 1, page_size: 50 }),
        listGenerationTasks({ status: 'pending', page: 1, page_size: 50 }),
      ])
      const running = runningRes.data.items || []
      const pending = pendingRes.data.items || []
      realtimeTasks.value = [...running, ...pending].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
    } catch (e) {
      console.error('获取实时任务失败:', e)
    } finally {
      realtimeLoading.value = false
    }
  },
  { immediate: true },
)

// ── 事件处理 ────────────────────────────────────────────────
function handleTabChange(tab: string) {
  if (tab === 'realtime') {
    startPolling()
  } else {
    stopPolling()
    store.tasksPage = 1
    store.fetchTasks()
  }
}

const handleSearch = useDebounceFn((val: string) => {
  store.tasksFilters.keyword = val || null
  store.tasksPage = 1
  store.fetchTasks()
}, 300)

function handleFilterChange() {
  store.tasksPage = 1
  store.fetchTasks()
}

function handlePageChange(p: number) {
  store.tasksPage = p
  store.fetchTasks()
}

function handlePageSizeChange(size: number) {
  store.tasksPageSize = size
  store.tasksPage = 1
  store.fetchTasks()
}

function goToDetail(task: GenerationTask) {
  router.push(`/ai-testing/generate/tasks/${task.id}`)
}

function handleExport(task: GenerationTask) {
  const url = `/api/v1/testing/generate/${task.id}/export`
  const a = document.createElement('a')
  a.href = url
  const ts = Date.now()
  a.download = `generated_cases_${ts}.xlsx`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  message.success('开始下载 Excel 文件')
}

function handleDelete(task: GenerationTask) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除任务「${task.requirement_title || '未命名任务'}」吗？生成的用例不会受影响。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      const ok = await store.removeTask(task.id)
      if (ok) message.success('任务已删除')
      else message.error('删除失败')
    },
  })
}

function refreshAll() {
  if (activeTab.value === 'realtime') {
    refreshPolling()
  } else {
    store.fetchTasks()
  }
}

// ── 工具函数 ────────────────────────────────────────────────
function formatTime(iso: string) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

// ── 初始化 ──────────────────────────────────────────────────
onMounted(() => {
  projectStore.fetchProjects()
  fetchGenStats()
  // usePolling 的 immediate: true 会自动开始轮询
})

onUnmounted(() => {
  stopPolling()
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

.filter-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
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

.stat-success .stat-value { color: var(--success-color, #18a058); }
.stat-primary .stat-value { color: var(--primary-color); }

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

/* ── 加载 ─────────────────────────────────────────────── */
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

/* ── 空状态 ──────────────────────────────────────────── */
.empty-state {
  text-align: center;
  padding: 80px 24px;
  background: var(--bg-card, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 13px;
  color: #7A6855;
  margin-bottom: 20px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* ── 实时卡片网格 ─────────────────────────────────────── */
.realtime-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.realtime-card {
  background: var(--bg-card, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 20px;
  transition: box-shadow 0.2s;
}

.realtime-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-running {
  background: var(--primary-color, #c67b5c);
  box-shadow: 0 0 6px color-mix(in srgb, var(--primary-color, #c67b5c) 50%, transparent);
  animation: pulse-dot 1.5s ease-in-out infinite;
}

.dot-pending {
  background: #d9d9d9;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.meta-item {
  font-size: 13px;
  color: #5C4A38;
}

.meta-label {
  display: inline-block;
  width: 56px;
  color: #7A6855;
  font-size: 12px;
}

.card-actions {
  border-top: 1px solid rgba(0, 0, 0, 0.04);
  padding-top: 12px;
  display: flex;
  justify-content: flex-end;
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
