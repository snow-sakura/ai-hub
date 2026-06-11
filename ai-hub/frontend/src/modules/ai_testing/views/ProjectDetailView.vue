<template>
  <div class="page-wrap">
    <!-- 返回导航 -->
    <div class="back-nav" @click="router.push('/ai-testing/projects')">
      <span class="back-arrow">←</span>
      <span>返回项目列表</span>
    </div>

    <div v-if="store.currentProject" class="detail-content">
      <!-- 项目基本信息卡片 -->
      <div class="info-card">
        <div class="card-header">
          <div class="card-header-left">
            <h2 class="project-name">{{ store.currentProject.name }}</h2>
            <StatusTag :status="store.currentProject.status" />
          </div>
          <n-button text type="primary" @click="handleEdit">编辑</n-button>
        </div>
        <!-- 可编辑描述 -->
        <div v-if="isEditingDesc" class="desc-edit">
          <n-input
            v-model:value="editDesc"
            type="textarea"
            :rows="3"
            :maxlength="2000"
            show-count
          />
          <n-space :size="8" style="margin-top: 8px;">
            <n-button size="tiny" type="primary" @click="handleSaveDesc">保存</n-button>
            <n-button size="tiny" @click="isEditingDesc = false">取消</n-button>
          </n-space>
        </div>
        <p v-else class="project-desc" @click="startEditDesc">
          {{ store.currentProject.description || '暂无描述（点击编辑）' }}
        </p>
        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-value">{{ store.currentProject.case_count }}</span>
            <span class="stat-label">测试用例</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ store.currentProject.member_count }}</span>
            <span class="stat-label">项目成员</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ formatDate(store.currentProject.created_at) }}</span>
            <span class="stat-label">创建时间</span>
          </div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="quick-links">
        <n-button text @click="router.push('/ai-testing/projects/versions?projectId=' + projectId)">
          版本管理 →
        </n-button>
        <n-button text @click="router.push('/ai-testing/projects/members?projectId=' + projectId)">
          项目成员 →
        </n-button>
      </div>
    </div>

    <div v-else class="loading-state">
      <n-spin size="medium" />
      <p>加载中...</p>
    </div>

    <!-- 编辑项目弹窗 -->
    <n-modal v-model:show="showEditModal" preset="card" :style="{ width: '520px' }">
      <ProjectForm
        :edit-data="editData"
        @cancel="showEditModal = false"
        @saved="showEditModal = false; refreshData()"
      />
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NModal, NInput, NSpin, useMessage } from 'naive-ui'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import StatusTag from '@/modules/ai_testing/components/common/StatusTag.vue'
import ProjectForm from '@/modules/ai_testing/components/project/ProjectForm.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const store = useProjectStore()

const projectId = computed(() => route.params.id as string)
const showEditModal = ref(false)

// 描述编辑
const isEditingDesc = ref(false)
const editDesc = ref('')

function startEditDesc() {
  editDesc.value = store.currentProject?.description || ''
  isEditingDesc.value = true
}

async function handleSaveDesc() {
  if (!store.currentProject) return
  await store.updateProject(store.currentProject.id, { description: editDesc.value })
  message.success('描述已更新')
  isEditingDesc.value = false
}


const editData = computed(() => {
  const p = store.currentProject
  if (!p) return undefined
  return { id: p.id, name: p.name, description: p.description, status: p.status }
})


function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return isNaN(d.getTime()) ? dateStr : d.toLocaleDateString('zh-CN')
}

function handleEdit() {
  showEditModal.value = true
}

async function refreshData() {
  await store.fetchProject(projectId.value)
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.page-wrap {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

.back-nav {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #5C4A38;
  cursor: pointer;
  margin-bottom: 24px;
  transition: color 0.15s ease;
}
.back-nav:hover {
  color: var(--accent, #3b82f6);
}
.back-arrow {
  font-size: 16px;
}

.info-card {
  background: var(--bg-card, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary, #1a1a2e);
  letter-spacing: -0.02em;
  margin: 0;
}

.project-desc {
  font-size: 14px;
  color: #5C4A38;
  line-height: 1.7;
  margin: 0 0 20px;
  cursor: pointer;
}
.project-desc:hover {
  color: var(--accent, #3b82f6);
}

.desc-edit {
  margin-bottom: 20px;
}

.stats-row {
  display: flex;
  gap: 32px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #1a1a2e);
}

.stat-label {
  font-size: 12px;
  color: #7A6855;
}









.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 64px 0;
  color: #7A6855;
  font-size: 14px;
}

.quick-links {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  margin-bottom: 8px;
}
</style>
