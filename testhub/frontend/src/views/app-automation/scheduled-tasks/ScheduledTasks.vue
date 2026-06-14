<template>
  <div class="app-auto">
    <div class="app-page-header">
      <div>
        <h1 class="page-title">APP 定时任务</h1>
        <p class="page-sub">移动端自动化定时执行 · 共 {{ pagination.total }} 个任务</p>
      </div>
      <el-button class="app-btn-primary" @click="handleCreate">
        + 新建任务
      </el-button>
    </div>

    <div class="app-card app-fade-in">
      <div class="table-wrap">
        <el-table :data="tasks" v-loading="loading" style="width: 100%" @sort-change="handleSortChange">
          <el-table-column prop="name" label="任务名" min-width="150" sortable="custom">
            <template #default="{ row }">
              <span style="font-weight: 600">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="suite_name" label="关联套件" min-width="130" />
          <el-table-column prop="cron_expression" label="Cron" min-width="130">
            <template #default="{ row }">
              <code class="cron-text">{{ row.cron_expression || '-' }}</code>
            </template>
          </el-table-column>
          <el-table-column label="目标平台" min-width="120">
            <template #default="{ row }">
              <template v-if="row.platforms && row.platforms.length">
                <span v-for="p in row.platforms" :key="p" class="app-tag-platform" style="margin-right: 4px">{{ p }}</span>
              </template>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="trigger_type_display" label="触发方式" width="80">
            <template #default="{ row }">
              <span class="app-tag-auto">自动</span>
            </template>
          </el-table-column>
          <el-table-column prop="next_run_time" label="下次执行" width="160" sortable="custom">
            <template #default="{ row }">
              <span class="text-muted">{{ formatDateTime(row.next_run_time) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="70">
            <template #default="{ row }">
              <label class="app-switch">
                <input type="checkbox" :checked="row.status === 'ACTIVE'" @change="toggleTask(row)">
                <span class="switch-slider"></span>
              </label>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="{ row }">
              <el-button class="app-btn-ghost btn-xs" @click="runNow(row)" :loading="row._running">执行</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 分页 -->
    <div class="app-pagination">
      <el-pagination
        v-model:current-page="pagination.current"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadTasks"
        @current-change="loadTasks"
      />
    </div>

    <!-- 新建任务弹窗 -->
    <div class="app-modal-overlay" :class="{ active: showDialog }" @click.self="showDialog = false">
      <div class="app-modal-box">
        <div class="modal-head">
          <h3>{{ editingTask ? '编辑定时任务' : '新建定时任务' }}</h3>
          <button class="modal-close" @click="showDialog = false">✕</button>
        </div>
        <div class="modal-body">
          <label>任务名称</label>
          <el-input class="app-input mb-2" v-model="form.name" placeholder="每日 APP 回归" />

          <label>关联套件</label>
          <el-select class="app-input mb-2" v-model="form.test_suite" placeholder="选择套件" filterable>
            <el-option v-for="s in suites" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>

          <label>目标平台</label>
          <div style="display:flex;gap:12px;margin-bottom:12px">
            <label class="app-checkbox-label">
              <input type="checkbox" v-model="form.platforms" value="iOS" style="accent-color:#C67B5C"> iOS
            </label>
            <label class="app-checkbox-label">
              <input type="checkbox" v-model="form.platforms" value="Android" style="accent-color:#C67B5C"> Android
            </label>
          </div>

          <label>Cron 表达式</label>
          <el-input class="app-input mb-2" v-model="form.cron_expression" placeholder="0 3 * * *" />
          <div style="display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap">
            <button class="app-btn-ghost btn-xs" @click="applyCron('*/30 * * * *')">每 30 分钟</button>
            <button class="app-btn-ghost btn-xs" @click="applyCron('0 * * * *')">每小时</button>
            <button class="app-btn-ghost btn-xs" @click="applyCron('0 3 * * *')">每天 3:00</button>
            <button class="app-btn-ghost btn-xs" @click="applyCron('0 6 * * 1')">每周一 6:00</button>
          </div>
        </div>
        <div class="modal-footer">
          <button class="app-btn-secondary" @click="showDialog = false">取消</button>
          <button class="app-btn-primary" @click="submitForm" :loading="submitting">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getAppScheduledTasks,
  createAppScheduledTask,
  updateAppScheduledTask,
  runAppScheduledTask,
  getTestSuiteList,
} from '@/api/app-automation.js'

const tasks = ref([])
const suites = ref([])
const loading = ref(false)
const submitting = ref(false)
const showDialog = ref(false)
const editingTask = ref(null)

const pagination = reactive({ current: 1, size: 10, total: 0 })

const defaultForm = {
  name: '', test_suite: '', platforms: [], cron_expression: '0 3 * * *',
}
const form = reactive({ ...defaultForm })

onMounted(() => {
  loadTasks()
  loadOptions()
})

const loadTasks = async () => {
  loading.value = true
  try {
    const params = { page: pagination.current, page_size: pagination.size }
    const res = await getAppScheduledTasks(params)
    tasks.value = (res.data.results || []).map(t => ({ ...t, _running: false }))
    pagination.total = res.data.count || 0
  } catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const loadOptions = async () => {
  try {
    const s = await getTestSuiteList({ page_size: 200 })
    suites.value = s.data.results || s.data || []
  } catch (e) { console.error('加载选项失败', e) }
}

const handleCreate = () => {
  editingTask.value = null
  Object.assign(form, { ...defaultForm })
  showDialog.value = true
}

const applyCron = (expr) => {
  form.cron_expression = expr
}

const submitForm = async () => {
  if (!form.name) return ElMessage.warning('请输入任务名称')
  if (!form.cron_expression) return ElMessage.warning('请输入Cron表达式')

  submitting.value = true
  try {
    const data = {
      name: form.name,
      test_suite: form.test_suite,
      platforms: form.platforms,
      cron_expression: form.cron_expression,
      trigger_type: 'CRON',
    }

    if (editingTask.value) {
      await updateAppScheduledTask(editingTask.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createAppScheduledTask(data)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    loadTasks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.response?.data?.message || '操作失败')
  } finally { submitting.value = false }
}

const runNow = async (task) => {
  task._running = true
  try {
    await runAppScheduledTask(task.id)
    ElMessage.success('任务已开始执行')
    setTimeout(loadTasks, 2000)
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '执行失败')
  } finally { task._running = false }
}

const toggleTask = async (task) => {
  try {
    if (task.status === 'ACTIVE') {
      const { pauseAppScheduledTask } = await import('@/api/app-automation.js')
      await pauseAppScheduledTask(task.id)
      task.status = 'PAUSED'
      ElMessage.success('已暂停')
    } else {
      const { resumeAppScheduledTask } = await import('@/api/app-automation.js')
      await resumeAppScheduledTask(task.id)
      task.status = 'ACTIVE'
      ElMessage.success('已启用')
    }
  } catch { ElMessage.error('操作失败') }
}

const handleSortChange = () => {
  loadTasks()
}

const formatDateTime = (s) => {
  if (!s) return '-'
  return new Date(s).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  }).replace(/\//g, '-')
}
</script>

<style scoped>
.table-wrap {
  overflow-x: auto;
}
:deep(.cron-text) {
  font-family: var(--font-mono, ui-monospace, 'SF Mono', 'Fira Code', 'Consolas', monospace);
  font-size: 12px;
  background: rgba(180,150,120,0.08);
  padding: 2px 6px;
  border-radius: 4px;
}
:deep(.text-muted) {
  color: var(--app-text-muted, #8B7355);
}
:deep(.app-switch) {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
  flex-shrink: 0;
}
:deep(.app-switch input) {
  opacity: 0;
  width: 0;
  height: 0;
}
:deep(.app-switch .switch-slider) {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #ccc;
  border-radius: 20px;
  transition: 0.3s;
}
:deep(.app-switch .switch-slider:before) {
  position: absolute;
  content: '';
  height: 16px;
  width: 16px;
  left: 2px;
  bottom: 2px;
  background: white;
  border-radius: 50%;
  transition: 0.3s;
}
:deep(.app-switch input:checked + .switch-slider) {
  background: var(--app-primary, #C67B5C);
}
:deep(.app-switch input:checked + .switch-slider:before) {
  transform: translateX(16px);
}
:deep(.app-tag-platform) {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  background: rgba(91,141,239,0.12);
  color: var(--app-info, #5B8DEF);
}
:deep(.app-tag-auto) {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  background: rgba(91,141,239,0.12);
  color: var(--app-info, #5B8DEF);
}
:deep(.app-checkbox-label) {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  cursor: pointer;
}
:deep(.btn-xs) {
  height: 24px;
  padding: 0 8px;
  font-size: 11px;
}
:deep(.mb-2) {
  margin-bottom: 12px;
}
:deep(.app-pagination) {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
