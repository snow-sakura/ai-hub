<template>
  <div class="page-wrap">
    <n-space vertical :size="16" style="max-width: 1120px; margin: 0 auto;">
      <!-- 页头 -->
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">定时任务配置</h1>
          <n-spin v-if="loading" size="small" />
          <span v-else class="page-count">{{ tasks.length }} 个任务</span>
        </div>
        <n-button type="primary" :disabled="loading" @click="openCreateModal">+ 新建任务</n-button>
      </div>

      <!-- 错误提示 -->
      <n-alert v-if="error" type="error" :bordered="false" closable @close="error = ''">
        {{ error }}
      </n-alert>

      <!-- 模块 Tab -->
      <n-tabs v-model:value="activeTab" type="line" animated>
        <n-tab-pane name="all" tab="全部" />
        <n-tab-pane name="api" tab="API 测试" />
        <n-tab-pane name="ui" tab="UI 自动化" />
        <n-tab-pane name="app" tab="APP 自动化" />
      </n-tabs>

      <!-- 空状态 -->
      <n-empty v-if="!loading && filteredTasks.length === 0" description="暂无定时任务">
        <template #extra>
          <n-button size="small" @click="openCreateModal">新建任务</n-button>
        </template>
      </n-empty>

      <!-- 任务表格 -->
      <n-card v-if="filteredTasks.length > 0" size="small" :bordered="false" class="tasks-card">
        <n-data-table
          :columns="columns"
          :data="filteredTasks"
          :row-key="(row: ScheduledTask) => row.id"
          :scroll-x="1100"
          :loading="loading"
        />
      </n-card>
    </n-space>

    <!-- 新建/编辑弹窗 -->
    <n-modal v-model:show="showModal" preset="card" :title="isEditing ? '编辑任务' : '新建定时任务'"
      :style="{ width: '540px' }" :bordered="false" :segmented="false"
      @positive-click="handleModalSubmit"
    >
      <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="top">
        <n-form-item label="任务名称" path="name">
          <n-input v-model:value="formData.name" placeholder="输入任务名称" />
        </n-form-item>
        <n-grid :cols="2" :x-gap="16">
          <n-grid-item>
            <n-form-item label="所属模块" path="module">
              <n-select v-model:value="formData.module" :options="moduleOptions" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
        <n-form-item label="Cron 表达式" path="cron_expr">
          <n-input v-model:value="formData.cron_expr" placeholder="如 0 8 * * *（每天 8:00）" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="submitting" @click="handleModalSubmit">保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 执行日志弹窗 -->
    <n-modal v-model:show="showLogModal" preset="card" title="执行日志"
      :style="{ width: '480px' }" :bordered="false">
      <n-timeline v-if="currentLogs.length > 0">
        <n-timeline-item v-for="log in currentLogs" :key="log.id"
          :type="log.status === 'success' ? 'success' : log.status === 'failed' ? 'error' : 'info'"
          :time="log.started_at">
          <template #header>
            {{ log.status === 'success' ? '执行成功' : log.status === 'failed' ? '执行失败' : '执行中' }}
          </template>
          {{ log.duration ? `耗时: ${log.duration}` : '' }}
        </n-timeline-item>
      </n-timeline>
      <n-empty v-else description="暂无执行记录" />
      <template #footer>
        <n-button @click="showLogModal = false">关闭</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, h, onMounted } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import type { DataTableColumns, FormInst, FormRules } from 'naive-ui'
import {
  listScheduledTasks, createScheduledTask, updateScheduledTask,
  deleteScheduledTask, executeScheduledTask, getScheduledTaskLogs,
} from '@/modules/ai_testing/api/scheduledTask'
import type { ScheduledTask, ScheduledTaskCreate, TaskModule } from '@/modules/ai_testing/types/scheduledTask'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const tasks = ref<ScheduledTask[]>([])
const activeTab = ref('all')
const showModal = ref(false)
const showLogModal = ref(false)
const isEditing = ref(false)
const editingId = ref('')
const currentLogs = ref<any[]>([])
const formRef = ref<FormInst | null>(null)

const moduleOptions = [
  { label: 'API 测试', value: 'api' },
  { label: 'UI 自动化', value: 'ui' },
  { label: 'APP 自动化', value: 'app' },
]

const formData = reactive({
  name: '',
  module: 'api' as TaskModule,
  cron_expr: '0 8 * * *',
})

const formRules: FormRules = {
  name: { required: true, message: '请输入任务名称', trigger: 'blur' },
  module: { required: true, message: '请选择所属模块', trigger: 'change' },
  cron_expr: { required: true, message: '请输入 Cron 表达式', trigger: 'blur' },
}

const moduleTagMap: Record<string, { color: string }> = {
  api: { color: '#C67B5C' },
  ui: { color: '#D4A574' },
  app: { color: '#7BA87D' },
}

const filteredTasks = computed(() => {
  if (activeTab.value === 'all') return tasks.value
  return tasks.value.filter(t => t.module === activeTab.value)
})

async function loadTasks() {
  loading.value = true
  error.value = ''
  try {
    const res = await listScheduledTasks()
    tasks.value = res.data ?? []
  } catch (e: any) {
    error.value = '加载定时任务失败: ' + (e?.message || '请检查网络')
    console.error('加载定时任务失败:', e)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  isEditing.value = false
  editingId.value = ''
  formData.name = ''
  formData.module = 'api'
  formData.cron_expr = '0 8 * * *'
  showModal.value = true
}

function openEditModal(task: ScheduledTask) {
  isEditing.value = true
  editingId.value = task.id
  formData.name = task.name
  formData.module = task.module
  formData.cron_expr = task.cron_expr
  showModal.value = true
}

async function handleModalSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    if (isEditing.value) {
      await updateScheduledTask(editingId.value, {
        name: formData.name,
        module: formData.module,
        cron_expr: formData.cron_expr,
      })
      message.success('任务已更新')
    } else {
      await createScheduledTask({
        name: formData.name,
        module: formData.module,
        cron_expr: formData.cron_expr,
      })
      message.success('任务已创建')
    }
    showModal.value = false
    await loadTasks()
  } catch (e: any) {
    message.error(isEditing.value ? '更新失败' : '创建失败')
    console.error('保存定时任务失败:', e)
  } finally {
    submitting.value = false
  }
}

async function handleToggleEnabled(task: ScheduledTask) {
  try {
    await updateScheduledTask(task.id, { enabled: !task.enabled })
    task.enabled = !task.enabled
    message.success(task.enabled ? '任务已启用' : '任务已禁用')
  } catch (e) {
    console.error('更新状态失败:', e)
    message.error('操作失败')
  }
}

async function handleRunNow(task: ScheduledTask) {
  try {
    const res = await executeScheduledTask(task.id)
    if (res.data?.status === 'success' || res.data?.status === 'completed') {
      message.success(`任务「${task.name}」已触发执行`)
    } else {
      message.success(`任务「${task.name}」已加入执行队列`)
    }
    await loadTasks()
  } catch (e: any) {
    message.error(`执行失败: ${e?.message || '请稍后重试'}`)
  }
}

function handleDelete(task: ScheduledTask) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除定时任务「${task.name}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteScheduledTask(task.id)
        tasks.value = tasks.value.filter(t => t.id !== task.id)
        message.success('任务已删除')
      } catch (e) {
        message.error('删除失败')
        console.error('删除定时任务失败:', e)
      }
    },
  })
}

async function handleViewLogs(task: ScheduledTask) {
  try {
    const res = await getScheduledTaskLogs(task.id, { limit: 20 })
    currentLogs.value = res.data ?? []
    showLogModal.value = true
  } catch (e) {
    message.error('加载执行日志失败')
  }
}

const columns: DataTableColumns<ScheduledTask> = [
  {
    title: '任务名称',
    key: 'name',
    width: 180,
    ellipsis: { tooltip: true },
    render(row) {
      return h('span', {
        style: 'font-weight: 500; color: var(--text-primary, #3D2E1F);',
      }, row.name)
    },
  },
  {
    title: '所属模块',
    key: 'module',
    width: 110,
    render(row) {
      const cfg = moduleTagMap[row.module] || moduleTagMap.api
      return h('span', {
        style: {
          display: 'inline-block',
          padding: '2px 10px',
          borderRadius: '4px',
          fontSize: '12px',
          fontWeight: 500,
          background: cfg.color + '18',
          color: cfg.color,
        },
      }, moduleOptions.find(m => m.value === row.module)?.label || row.module)
    },
  },
  {
    title: 'Cron 表达式',
    key: 'cron_expr',
    width: 140,
    render(row) {
      return h('code', {
        style: {
          background: 'rgba(180, 150, 120, 0.08)',
          padding: '2px 8px',
          borderRadius: '4px',
          fontSize: '12px',
          color: 'var(--accent, #C67B5C)',
          fontFamily: 'monospace',
        },
      }, row.cron_expr)
    },
  },
  {
    title: '上次执行',
    key: 'last_run_at',
    width: 160,
    render(row) {
      return row.last_run_at || '-'
    },
  },
  {
    title: '状态',
    key: 'enabled',
    width: 80,
    align: 'center',
    render(row) {
      return h('div', { style: 'display: flex; justify-content: center;' }, [
        h('n-switch', {
          value: row.enabled,
          'onUpdate:value': () => handleToggleEnabled(row),
        }),
      ])
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 220,
    fixed: 'right',
    render(row) {
      return h('div', { style: 'display: flex; gap: 8px; justify-content: center;' }, [
        h('n-button', {
          text: true, size: 'small', type: 'primary',
          onClick: () => openEditModal(row),
        }, { default: () => '编辑' }),
        h('n-button', {
          text: true, size: 'small', type: 'success',
          onClick: () => handleRunNow(row),
        }, { default: () => '立即执行' }),
        h('n-button', {
          text: true, size: 'small', type: 'default',
          onClick: () => handleViewLogs(row),
        }, { default: () => '日志' }),
        h('n-button', {
          text: true, size: 'small', type: 'error',
          onClick: () => handleDelete(row),
        }, { default: () => '删除' }),
      ])
    },
  },
]

onMounted(() => {
  loadTasks()
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
  margin-bottom: 8px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #3D2E1F);
  letter-spacing: -0.02em;
  margin: 0;
}

.page-count {
  font-size: 13px;
  color: var(--text-muted, #8B7355);
  font-weight: 400;
}

.tasks-card {
  background: var(--bg-card, #FFFDF9);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 12px;
  overflow: hidden;
}

@media (max-width: 768px) {
  .page-wrap {
    padding: 16px 12px 48px;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .page-title {
    font-size: 20px;
  }
  :deep(.n-data-table-wrapper) {
    overflow-x: auto;
  }
}
</style>
