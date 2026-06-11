<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">版本管理</h1>
      </div>
      <n-button v-if="selectedProjectId" type="primary" @click="showCreateModal = true">
        + 新建版本
      </n-button>
    </header>

    <!-- 项目选择器 -->
    <div class="filter-section">
      <n-select
        v-model:value="selectedProjectId"
        placeholder="请选择项目"
        clearable
        :style="{ width: '260px' }"
        :options="projectOptions"
        @update:value="handleProjectChange"
      />
    </div>

    <!-- 未选择项目 -->
    <div v-if="!selectedProjectId" class="empty-state">
      <div class="empty-title">请先选择一个项目</div>
      <div class="empty-desc">从上方下拉框选择项目后，即可管理该项目的版本</div>
    </div>

    <!-- 加载中 -->
    <div v-else-if="loading" class="loading-wrap">
      <n-spin size="small" />
      <span class="loading-text">加载中...</span>
    </div>

    <!-- 空版本 -->
    <div v-else-if="versions.length === 0" class="empty-state">
      <div class="empty-title">暂无版本</div>
      <div class="empty-desc">点击「新建版本」开始创建</div>
    </div>

    <!-- 版本列表 -->
    <div v-else class="table-card">
      <n-list>
        <n-list-item v-for="v in versions" :key="v.id">
          <template #prefix>
            <n-tag
              :type="v.status === 'active' ? 'success' : v.status === 'released' ? 'info' : 'default'"
              size="tiny"
              round
              bordered
            >
              {{ statusLabels[v.status] || v.status }}
            </n-tag>
          </template>

          <div class="version-info">
            <span class="version-name">{{ v.name }}</span>
            <span class="version-date">{{ formatTime(v.created_at) }}</span>
          </div>

          <div v-if="v.description" class="version-desc">{{ v.description }}</div>

          <template #suffix>
            <div class="version-actions">
              <n-button size="tiny" text @click="startEdit(v)">编辑</n-button>
              <n-button size="tiny" text type="error" @click="handleDelete(v.id)">删除</n-button>
            </div>
          </template>
        </n-list-item>
      </n-list>
    </div>

    <!-- 创建/编辑弹窗 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      :title="editingVersion ? '编辑版本' : '新建版本'"
      :style="{ maxWidth: '480px' }"
      @after-leave="resetForm"
    >
      <n-form :model="formData" label-placement="top">
        <n-form-item label="版本名称" path="name">
          <n-input
            v-model:value="formData.name"
            placeholder="如 v1.0.0"
            :maxlength="200"
          />
        </n-form-item>
        <n-form-item label="版本描述" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            :rows="3"
            placeholder="版本说明..."
          />
        </n-form-item>
        <n-form-item v-if="editingVersion" label="版本状态" path="status">
          <n-select
            v-model:value="formData.status"
            :options="statusOptions"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-actions">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" :loading="isSubmitting" @click="handleSave">
            {{ editingVersion ? '保存' : '创建' }}
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NSelect, NSpin, NList, NListItem, NModal, NForm, NFormItem, NInput, NTag, useMessage } from 'naive-ui'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import { useVersionStore } from '@/modules/ai_testing/stores/version'
import type { ProjectVersion } from '@/modules/ai_testing/types/version'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const projectStore = useProjectStore()
const versionStore = useVersionStore()

const selectedProjectId = ref<string | null>(null)
const loading = ref(false)
const showCreateModal = ref(false)
const editingVersion = ref<ProjectVersion | null>(null)
const isSubmitting = ref(false)

const formData = ref({
  name: '',
  description: '',
  status: 'active' as string,
})

const statusLabels: Record<string, string> = {
  active: '活跃',
  released: '已发布',
  archived: '已归档',
}

const statusOptions = [
  { label: '活跃', value: 'active' },
  { label: '已发布', value: 'released' },
  { label: '已归档', value: 'archived' },
]

const projectOptions = computed(() =>
  projectStore.projects.map(p => ({ label: p.name, value: p.id }))
)

const versions = computed(() => versionStore.versions)

function resetForm() {
  editingVersion.value = null
  formData.value = { name: '', description: '', status: 'active' }
}

async function handleProjectChange(val: string | null) {
  if (!val) {
    versionStore.versions.splice(0)
    return
  }
  loading.value = true
  try {
    await versionStore.fetchVersions(val)
  } finally {
    loading.value = false
  }
}

function startEdit(v: ProjectVersion) {
  editingVersion.value = v
  formData.value = { name: v.name, description: v.description, status: v.status }
  showCreateModal.value = true
}

async function handleSave() {
  if (!formData.value.name.trim()) return
  isSubmitting.value = true
  try {
    if (editingVersion.value) {
      await versionStore.update(editingVersion.value.id, {
        name: formData.value.name,
        description: formData.value.description,
        status: formData.value.status as any,
      })
      message.success('版本已更新')
    } else {
      await versionStore.create(selectedProjectId.value!, {
        name: formData.value.name,
        description: formData.value.description,
        status: 'active',
      })
      message.success('版本已创建')
    }
    showCreateModal.value = false
  } finally {
    isSubmitting.value = false
  }
}

async function handleDelete(versionId: string) {
  await versionStore.remove(versionId)
  message.success('版本已删除')
}

function formatTime(iso: string) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(async () => {
  await projectStore.fetchProjects()
  const projectId = route.query.projectId as string
  if (projectId) {
    selectedProjectId.value = projectId
    loading.value = true
    try {
      await versionStore.fetchVersions(projectId)
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
.page-wrap {
  max-width: 960px;
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
  color: var(--text-primary, #1a1a2e);
  letter-spacing: -0.02em;
  margin: 0;
}

.filter-section {
  margin-bottom: 20px;
}

.table-card {
  background: var(--bg-card, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  overflow: hidden;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.version-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #1a1a2e);
}

.version-date {
  font-size: 12px;
  color: #7A6855;
}

.version-desc {
  font-size: 12px;
  color: #7A6855;
  margin-top: 2px;
  line-height: 1.5;
}

.version-actions {
  display: flex;
  gap: 8px;
}

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

.empty-state {
  text-align: center;
  padding: 80px 24px;
  background: var(--bg-card, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #1a1a2e);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 13px;
  color: #7A6855;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
