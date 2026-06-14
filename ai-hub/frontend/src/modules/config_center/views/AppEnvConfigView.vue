<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">APP 环境配置</h1>
        <span class="page-count">{{ envList.length }} 个环境</span>
      </div>
      <n-button type="primary" @click="openCreateModal">新建环境</n-button>
    </header>

    <!-- 环境列表 -->
    <div class="env-list">
      <n-card v-for="env in envList" :key="env.id" hoverable>
        <div class="env-header">
          <div class="env-info">
            <span class="env-name">{{ env.name }}</span>
            <span class="env-badge" :class="env.platform">
              {{ env.platform === 'android' ? 'Android' : 'iOS' }}
            </span>
          </div>
          <n-button text type="error" size="tiny" @click="handleDelete(env.id)">删除</n-button>
        </div>
        <div class="env-details">
          <div class="detail-item">
            <span class="detail-label">App Package</span>
            <span class="detail-value mono">{{ env.app_package || '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">App Activity</span>
            <span class="detail-value mono">{{ env.app_activity || '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">设备序列号</span>
            <span class="detail-value mono">{{ env.device_serial || '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Appium URL</span>
            <span class="detail-value mono">{{ env.appium_url }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">超时</span>
            <span class="detail-value">{{ env.timeout_ms }}ms</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">失败截图</span>
            <span class="detail-value">{{ env.screenshot_on_failure ? '开启' : '关闭' }}</span>
          </div>
        </div>
        <div class="env-actions-wrap">
          <n-button size="tiny" quaternary @click="openEditModal(env)">编辑</n-button>
        </div>
      </n-card>
    </div>

    <n-empty v-if="!loading && envList.length === 0" description="暂无环境配置" style="margin-top:60px" />

    <!-- 新建/编辑弹窗 -->
    <n-modal v-model:show="showModal" :mask-closable="false" preset="card" style="width:640px" title="APP 环境配置">
      <n-form label-placement="top">
        <n-form-item label="环境名称">
          <n-input v-model:value="form.name" placeholder="如: Android 模拟器" />
        </n-form-item>
        <n-form-item label="平台">
          <n-select v-model:value="form.platform" :options="platformOptions" />
        </n-form-item>
        <n-row :gutter="20">
          <n-col :span="12">
            <n-form-item label="App Package">
              <n-input v-model:value="form.app_package" placeholder="com.example.app" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="App Activity">
              <n-input v-model:value="form.app_activity" placeholder=".MainActivity" />
            </n-form-item>
          </n-col>
        </n-row>
        <n-row :gutter="20">
          <n-col :span="12">
            <n-form-item label="设备序列号">
              <n-input v-model:value="form.device_serial" placeholder="emulator-5554" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="Appium URL">
              <n-input v-model:value="form.appium_url" placeholder="http://localhost:4723" />
            </n-form-item>
          </n-col>
        </n-row>
        <n-row :gutter="20">
          <n-col :span="12">
            <n-form-item label="超时 (ms)">
              <n-input-number v-model:value="form.timeout_ms" :min="1000" :max="300000" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="失败自动截图">
              <n-switch v-model:value="form.screenshot_on_failure" />
            </n-form-item>
          </n-col>
        </n-row>
      </n-form>
      <template #footer>
        <div class="modal-actions">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" @click="handleSaveModal" :loading="modalSaving">保存</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { listAppEnvs, createAppEnv, updateAppEnv, deleteAppEnv, type AppEnvConfigItem } from '../api/config'

const message = useMessage()
const loading = ref(false)
const showModal = ref(false)
const modalSaving = ref(false)
const editingId = ref<string | null>(null)
const envList = ref<AppEnvConfigItem[]>([])

const platformOptions = [
  { label: 'Android', value: 'android' },
  { label: 'iOS', value: 'ios' },
]

const form = reactive({
  name: '', platform: 'android', app_package: '', app_activity: '',
  device_serial: '', appium_url: 'http://localhost:4723', timeout_ms: 30000, screenshot_on_failure: true,
})

async function loadData() {
  loading.value = true
  try { const res: any = await listAppEnvs(); envList.value = res.data || [] }
  catch { /* ignore */ }
  finally { loading.value = false }
}

function openCreateModal() {
  editingId.value = null
  Object.assign(form, { name: '', platform: 'android', app_package: '', app_activity: '', device_serial: '', appium_url: 'http://localhost:4723', timeout_ms: 30000, screenshot_on_failure: true })
  showModal.value = true
}

function openEditModal(env: AppEnvConfigItem) {
  editingId.value = env.id; Object.assign(form, env); showModal.value = true
}

async function handleSaveModal() {
  modalSaving.value = true
  try {
    if (editingId.value) { await updateAppEnv(editingId.value, { ...form }); message.success('更新成功') }
    else { await createAppEnv({ ...form }); message.success('创建成功') }
    showModal.value = false; await loadData()
  } catch { message.error('操作失败') }
  finally { modalSaving.value = false }
}

async function handleDelete(id: string) {
  try { await deleteAppEnv(id); envList.value = envList.value.filter(e => e.id !== id); message.success('已删除') }
  catch { message.error('删除失败') }
}

onMounted(loadData)
</script>

<style scoped>
.page-wrap { max-width: 900px; margin: 0 auto; padding: 32px 24px 64px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.header-left { display: flex; align-items: baseline; gap: 12px; }
.page-title { font-size: 24px; font-weight: 700; color: #3D2E1F; letter-spacing: -0.02em; margin: 0; }
.page-count { font-size: 13px; color: #7A6855; }
@media (max-width: 768px) { .page-wrap { padding: 16px 12px 48px; } }

.env-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
}

.env-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.env-info { display: flex; align-items: center; gap: 10px; }
.env-name { font-size: 15px; font-weight: 600; color: #3d2e1f; }

.env-badge { font-size: 11px; padding: 1px 8px; border-radius: 10px; }
.env-badge.android { background: rgba(107,158,107,0.12); color: #5a8e5a; }
.env-badge.ios { background: rgba(70,130,180,0.1); color: #2c5f8a; }

.env-details { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; }
.detail-item { display: flex; flex-direction: column; gap: 2px; }
.detail-label { font-size: 11px; color: #8b7355; text-transform: uppercase; letter-spacing: 0.05em; }
.detail-value { font-size: 14px; color: #5c4a38; }
.detail-value.mono { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; word-break: break-all; }

.env-actions-wrap { margin-top: 12px; display: flex; justify-content: flex-end; }

.modal-actions { display: flex; gap: 12px; justify-content: flex-end; }
</style>
