<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">UI 环境配置</h1>
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
            <span class="env-badge" :class="env.headless ? 'headless' : 'headed'">
              {{ env.headless ? '无头模式' : '有头模式' }}
            </span>
          </div>
          <n-button text type="error" size="tiny" @click="handleDelete(env.id)">删除</n-button>
        </div>
        <div class="env-details">
          <div class="detail-item">
            <span class="detail-label">浏览器</span>
            <span class="detail-value browser-tag">{{ env.browser_type }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">基础 URL</span>
            <span class="detail-value">{{ env.base_url || '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">视口</span>
            <span class="detail-value">{{ env.viewport_width }}x{{ env.viewport_height }}</span>
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
    <n-modal v-model:show="showModal" :mask-closable="false" preset="card" style="width:640px" title="UI 环境配置">
      <n-form label-placement="top">
        <n-form-item label="环境名称">
          <n-input v-model:value="form.name" placeholder="如: 测试环境" />
        </n-form-item>
        <n-form-item label="浏览器类型">
          <n-select v-model:value="form.browser_type" :options="browserOptions" />
        </n-form-item>
        <n-form-item label="基础 URL">
          <n-input v-model:value="form.base_url" placeholder="https://example.com" />
        </n-form-item>
        <n-row :gutter="20">
          <n-col :span="8">
            <n-form-item label="视口宽度">
              <n-input-number v-model:value="form.viewport_width" :min="320" :max="3840" />
            </n-form-item>
          </n-col>
          <n-col :span="8">
            <n-form-item label="视口高度">
              <n-input-number v-model:value="form.viewport_height" :min="240" :max="2160" />
            </n-form-item>
          </n-col>
          <n-col :span="8">
            <n-form-item label="超时 (ms)">
              <n-input-number v-model:value="form.timeout_ms" :min="1000" :max="300000" />
            </n-form-item>
          </n-col>
        </n-row>
        <n-row :gutter="20">
          <n-col :span="12">
            <n-form-item label="无头模式">
              <n-switch v-model:value="form.headless" />
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
import { listUiEnvs, createUiEnv, updateUiEnv, deleteUiEnv, type UiEnvConfigItem } from '../api/config'

const message = useMessage()
const loading = ref(false)
const showModal = ref(false)
const modalSaving = ref(false)
const editingId = ref<string | null>(null)
const envList = ref<UiEnvConfigItem[]>([])

const browserOptions = [
  { label: 'Chrome', value: 'chromium' },
  { label: 'Firefox', value: 'firefox' },
  { label: 'Edge', value: 'edge' },
  { label: 'Safari', value: 'webkit' },
]

const form = reactive({
  name: '', base_url: '', browser_type: 'chromium', headless: true,
  viewport_width: 1280, viewport_height: 720, timeout_ms: 30000, screenshot_on_failure: true,
})

async function loadData() {
  loading.value = true
  try { const res: any = await listUiEnvs(); envList.value = res.data || [] }
  catch { /* ignore */ }
  finally { loading.value = false }
}

function openCreateModal() {
  editingId.value = null
  Object.assign(form, { name: '', base_url: '', browser_type: 'chromium', headless: true, viewport_width: 1280, viewport_height: 720, timeout_ms: 30000, screenshot_on_failure: true })
  showModal.value = true
}

function openEditModal(env: UiEnvConfigItem) {
  editingId.value = env.id; Object.assign(form, env); showModal.value = true
}

async function handleSaveModal() {
  modalSaving.value = true
  try {
    if (editingId.value) { await updateUiEnv(editingId.value, { ...form }); message.success('更新成功') }
    else { await createUiEnv({ ...form }); message.success('创建成功') }
    showModal.value = false; await loadData()
  } catch { message.error('操作失败') }
  finally { modalSaving.value = false }
}

async function handleDelete(id: string) {
  try { await deleteUiEnv(id); envList.value = envList.value.filter(e => e.id !== id); message.success('已删除') }
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

.env-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.env-name {
  font-size: 15px;
  font-weight: 600;
  color: #3d2e1f;
}

.env-badge {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 10px;
}

.env-badge.headless { background: rgba(107,158,107,0.12); color: #5a8e5a; }
.env-badge.headed { background: rgba(212,165,116,0.12); color: #b8894a; }

.env-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
}

.detail-item { display: flex; flex-direction: column; gap: 2px; }
.detail-label { font-size: 11px; color: #8b7355; text-transform: uppercase; letter-spacing: 0.05em; }
.detail-value { font-size: 14px; color: #5c4a38; }
.browser-tag { font-weight: 600; color: #c67b5c; }

.env-actions-wrap {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
</style>
