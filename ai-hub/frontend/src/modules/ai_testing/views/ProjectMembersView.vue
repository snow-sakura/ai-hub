<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">项目成员</h1>
      </div>
      <n-button v-if="selectedProjectId" type="primary" @click="showAddModal = true">
        + 添加成员
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
      <div class="empty-desc">从上方下拉框选择项目后，即可管理该项目的成员</div>
    </div>

    <!-- 加载中 -->
    <div v-else-if="loading" class="loading-wrap">
      <n-spin size="small" />
      <span class="loading-text">加载中...</span>
    </div>

    <!-- 空成员 -->
    <div v-else-if="members.length === 0" class="empty-state">
      <div class="empty-title">暂无成员</div>
      <div class="empty-desc">点击「添加成员」邀请成员加入项目</div>
    </div>

    <!-- 成员列表 -->
    <div v-else class="table-card">
      <div class="member-list">
        <div v-for="member in members" :key="member.id" class="member-item">
          <div class="member-avatar">{{ member.name.charAt(0).toUpperCase() }}</div>
          <div class="member-info">
            <span class="member-name">{{ member.name }}</span>
            <!-- 角色编辑：点击标签切换为下拉 -->
            <n-tag
              v-if="editingRoleId !== member.id"
              size="small"
              :bordered="false"
              style="cursor: pointer; align-self: flex-start;"
              @click="startEditRole(member)"
            >
              {{ roleLabel(member.role) }}
            </n-tag>
            <n-select
              v-else
              v-model:value="editingRoleValue"
              size="tiny"
              :options="roleOptions"
              :style="{ width: '90px' }"
              @blur="saveRole(member.id)"
              @update:value="saveRole(member.id)"
            />
          </div>
          <n-button
            text
            size="small"
            type="error"
            @click="handleRemoveMember(member.id)"
          >
            移除
          </n-button>
        </div>
      </div>
    </div>

    <!-- 添加成员弹窗 -->
    <n-modal
      v-model:show="showAddModal"
      preset="card"
      title="添加成员"
      :style="{ maxWidth: '400px' }"
    >
      <n-form label-placement="top">
        <n-form-item label="成员姓名">
          <n-input v-model:value="newMemberName" placeholder="输入成员姓名" />
        </n-form-item>
        <n-form-item label="角色">
          <n-select v-model:value="newMemberRole" :options="roleOptions" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-actions">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button
            type="primary"
            :disabled="!newMemberName.trim()"
            :loading="isAdding"
            @click="handleAddMember"
          >
            添加
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { NButton, NSelect, NSpin, NModal, NForm, NFormItem, NInput, NTag, useMessage } from 'naive-ui'
import { useProjectStore } from '@/modules/ai_testing/stores/project'

const route = useRoute()
const message = useMessage()
const store = useProjectStore()

const selectedProjectId = ref<string | null>(null)
const loading = ref(false)
const showAddModal = ref(false)
const isAdding = ref(false)
const newMemberName = ref('')
const newMemberRole = ref('tester')

const editingRoleId = ref<string | null>(null)
const editingRoleValue = ref('tester')

const roleOptions = [
  { label: '负责人', value: 'owner' },
  { label: '测试员', value: 'tester' },
  { label: '观察者', value: 'viewer' },
]

const projectOptions = computed(() =>
  store.projects.map(p => ({ label: p.name, value: p.id }))
)

const members = computed(() => store.members)

function roleLabel(role: string): string {
  const map: Record<string, string> = { owner: '负责人', tester: '测试员', viewer: '观察者' }
  return map[role] || role
}

function startEditRole(member: { id: string; role: string }) {
  editingRoleValue.value = member.role
  editingRoleId.value = member.id
}

async function saveRole(memberId: string) {
  if (!editingRoleId.value) return
  editingRoleId.value = null
  await store.updateMemberRole(memberId, editingRoleValue.value)
}

async function handleProjectChange(val: string | null) {
  if (!val) {
    store.members.splice(0)
    return
  }
  loading.value = true
  try {
    await store.fetchMembers(val)
  } finally {
    loading.value = false
  }
}

async function handleAddMember() {
  if (!newMemberName.value.trim() || !selectedProjectId.value) return
  isAdding.value = true
  try {
    const ok = await store.addMember(selectedProjectId.value, newMemberName.value.trim(), newMemberRole.value)
    if (ok) {
      message.success('成员已添加')
      newMemberName.value = ''
      newMemberRole.value = 'tester'
      showAddModal.value = false
    } else {
      message.error('添加失败')
    }
  } finally {
    isAdding.value = false
  }
}

async function handleRemoveMember(memberId: string) {
  if (!selectedProjectId.value) return
  const ok = await store.removeMember(memberId, selectedProjectId.value)
  if (ok) {
    message.success('成员已移除')
  } else {
    message.error('移除失败')
  }
}

onMounted(async () => {
  await store.fetchProjects()
  const projectId = route.query.projectId as string
  if (projectId) {
    selectedProjectId.value = projectId
    loading.value = true
    try {
      await store.fetchMembers(projectId)
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
  padding: 4px 0;
}

.member-list {
  display: flex;
  flex-direction: column;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}
.member-item:last-child {
  border-bottom: none;
}

.member-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(198, 123, 92, 0.1);
  color: #C67B5C;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.member-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.member-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #1a1a2e);
}

.member-role {
  font-size: 12px;
  color: #7A6855;
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
