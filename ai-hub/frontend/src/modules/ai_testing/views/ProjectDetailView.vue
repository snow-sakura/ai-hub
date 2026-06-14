<template>
  <div class="page-wrap">
    <!-- 返回导航 -->
    <div class="back-nav" @click="router.push('/ai-testing/projects')">
      <span class="back-arrow">←</span>
      <span>返回项目列表</span>
    </div>

    <div v-if="store.currentProject" class="detail-content">
      <!-- 项目 Tabs -->
      <n-tabs v-model:value="activeTab" type="line" animated>
        <n-tab-pane name="info" tab="项目信息">
          <div class="info-card">
            <div class="card-header">
              <div class="card-header-left">
                <h2 class="project-name">{{ store.currentProject.name }}</h2>
                <StatusTag :status="store.currentProject.status" />
              </div>
              <n-button text type="primary" style="color: #C67B5C;" @click="handleEdit">编辑</n-button>
            </div>
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
        </n-tab-pane>

        <n-tab-pane name="versions" tab="版本管理">
          <div class="tab-toolbar">
            <span v-if="versions.length" class="tab-count">{{ versions.length }} 个版本</span>
            <n-button size="small" type="primary" @click="showVersionModal = true">+ 新建版本</n-button>
          </div>

          <n-spin :show="versionLoading">
            <div v-if="versions.length === 0" class="tab-empty">暂无版本</div>
            <div v-else class="table-card">
              <n-list>
                <n-list-item v-for="v in versions" :key="v.id">
                  <template #prefix>
                    <n-tag
                      :type="v.status === 'active' ? 'success' : v.status === 'released' ? 'info' : 'default'"
                      size="tiny" round bordered
                    >{{ versionStatusLabel(v.status) }}</n-tag>
                  </template>

                  <div class="version-info">
                    <span class="version-name">{{ v.name }}</span>
                    <span class="version-date">{{ formatTime(v.created_at) }}</span>
                  </div>
                  <div v-if="v.description" class="version-desc">{{ v.description }}</div>

                  <template #suffix>
                    <div class="version-actions">
                      <!-- 版本流转按钮（仅保留归档） -->
                      <n-button
                        v-if="v.status === 'released'"
                        size="tiny" text style="color: #D4745C;"
                        @click="handleVersionTransition(v, 'archived', '归档')"
                      >归档</n-button>
                      <n-button size="tiny" text style="color: #C67B5C;" @click="openVersionEdit(v)">编辑</n-button>
                      <n-button size="tiny" text type="error" @click="handleDeleteVersion(v)">删除</n-button>
                    </div>
                  </template>
                </n-list-item>
              </n-list>
            </div>
          </n-spin>
        </n-tab-pane>

        <n-tab-pane name="members" tab="项目成员">
          <div class="tab-toolbar">
            <span v-if="store.members.length" class="tab-count">{{ store.members.length }} 个成员</span>
            <n-button size="small" type="primary" @click="showMemberModal = true">+ 添加成员</n-button>
          </div>

          <div v-if="store.members.length === 0" class="tab-empty">暂无成员</div>
          <div v-else class="table-card">
            <div class="member-list">
              <div v-for="member in store.members" :key="member.id" class="member-item">
                <div class="member-info">
                  <span class="member-name">{{ (member.name || '').trim() }}</span>
                  <n-tag
                    v-if="editingRoleId !== member.id"
                    size="small" :bordered="false"
                    :style="{
                      cursor: 'pointer', alignSelf: 'flex-start',
                      background: `${roleColors[member.role] || '#C67B5C'}18`,
                      color: roleColors[member.role] || '#C67B5C',
                      border: `1px solid ${roleColors[member.role] || '#C67B5C'}30`,
                      fontWeight: 500,
                    }"
                    @click="startEditRole(member)"
                  >{{ roleLabel(member.role) }}</n-tag>
                  <n-select
                    v-else
                    v-model:value="editingRoleValue"
                    size="tiny"
                    :options="roleOptions"
                    :style="{ width: '90px' }"
                    @blur="saveRole(member.id)"
                  />
                </div>
                <n-button text size="small" type="error" @click="handleRemoveMember(member)">移除</n-button>
              </div>
            </div>
          </div>
        </n-tab-pane>
      </n-tabs>
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

    <!-- 版本新建/编辑弹窗 -->
    <n-modal
      v-model:show="showVersionModal"
      preset="card"
      :title="editingVersion ? '编辑版本' : '新建版本'"
      :style="{ maxWidth: '520px' }"
      @after-leave="resetVersionForm"
    >
      <n-form :model="versionForm" label-placement="top">
        <n-form-item label="版本名称">
          <n-input v-model:value="versionForm.name" placeholder="如 v1.0.0" :maxlength="200" />
        </n-form-item>
        <n-form-item label="版本描述">
          <n-input v-model:value="versionForm.description" type="textarea" :rows="3" placeholder="版本说明..." />
        </n-form-item>
        <n-form-item v-if="editingVersion" label="版本状态">
          <n-select v-model:value="versionForm.status" :options="versionStatusOptions" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-actions">
          <n-button @click="showVersionModal = false">取消</n-button>
          <n-button type="primary" :loading="versionSubmitting" @click="handleVersionSave">
            {{ editingVersion ? '保存' : '创建' }}
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 状态变更确认 -->
    <n-modal v-model:show="showVersionTransitionConfirm" preset="dialog" type="warning" title="变更版本状态">
      <p>确定要将版本「{{ transitionVersion?.name }}」{{ transitionLabel }}吗？</p>
      <template #action>
        <n-button @click="showVersionTransitionConfirm = false">取消</n-button>
        <n-button type="warning" :loading="isTransitioning" @click="confirmVersionTransition">确认{{ transitionLabel }}</n-button>
      </template>
    </n-modal>

    <!-- 删除版本确认 -->
    <n-modal v-model:show="showDeleteVersionConfirm" preset="dialog" type="error" title="删除版本">
      <p>确定要删除版本「{{ deletingVersion?.name }}」吗？此操作不可撤销。</p>
      <template #action>
        <n-button @click="showDeleteVersionConfirm = false">取消</n-button>
        <n-button type="error" :loading="isDeletingVersion" @click="confirmDeleteVersion">确认删除</n-button>
      </template>
    </n-modal>

    <!-- 添加成员弹窗 -->
    <n-modal
      v-model:show="showMemberModal"
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
          <n-button @click="showMemberModal = false">取消</n-button>
          <n-button type="primary" :disabled="!newMemberName.trim()" :loading="memberSubmitting" @click="handleAddMember">添加</n-button>
        </div>
      </template>
    </n-modal>

    <!-- 移除成员确认 -->
    <n-modal v-model:show="showRemoveMemberConfirm" preset="dialog" type="warning" title="移除成员">
      <p>确定要移除成员「{{ removingMember?.name }}」吗？</p>
      <template #action>
        <n-button @click="showRemoveMemberConfirm = false">取消</n-button>
        <n-button type="error" :loading="isRemovingMember" @click="confirmRemoveMember">确认移除</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NModal, NInput, NSpin, NSpace, NTabs, NTabPane, NList, NListItem, NTag, NSelect, NForm, NFormItem, useMessage } from 'naive-ui'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import { useVersionStore } from '@/modules/ai_testing/stores/version'
import type { MemberRole } from '@/modules/ai_testing/types/project'
import type { VersionStatus } from '@/modules/ai_testing/types/version'
import StatusTag from '@/modules/ai_testing/components/common/StatusTag.vue'
import ProjectForm from '@/modules/ai_testing/components/project/ProjectForm.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const store = useProjectStore()
const versionStore = useVersionStore()

const projectId = computed(() => route.params.id as string)
const activeTab = ref('info')
const showEditModal = ref(false)

// ── 角色颜色 ──
const roleColors: Record<string, string> = {
  owner: '#C67B5C',
  tester: '#7BA87D',
  viewer: '#8B9DC3',
}

// ── 描述编辑 ──
const isEditingDesc = ref(false)
const editDesc = ref('')

function startEditDesc() {
  editDesc.value = store.currentProject?.description || ''
  isEditingDesc.value = true
}

async function handleSaveDesc() {
  if (!store.currentProject) return
  try {
    await store.updateProject(store.currentProject.id, { description: editDesc.value })
    message.success('描述已更新')
    isEditingDesc.value = false
  } catch (e) {
    message.error('保存失败')
    console.error('保存描述失败:', e)
  }
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

function handleEdit() { showEditModal.value = true }

async function refreshData() {
  await store.fetchProject(projectId.value)
}

// ── 版本管理 ──
const versions = computed(() => versionStore.versions)
const versionLoading = computed(() => versionStore.loading)
const showVersionModal = ref(false)
const editingVersion = ref<any>(null)
const versionSubmitting = ref(false)

const versionForm = ref({ name: '', description: '', status: 'active' })

const versionStatusOptions = [
  { label: '活跃', value: 'active' },
  { label: '已发布', value: 'released' },
  { label: '已归档', value: 'archived' },
]

function versionStatusLabel(status: string): string {
  const map: Record<string, string> = { active: '活跃', released: '已发布', archived: '已归档' }
  return map[status] || status
}

function resetVersionForm() {
  editingVersion.value = null
  versionForm.value = { name: '', description: '', status: 'active' }
}

function openVersionEdit(v: any) {
  editingVersion.value = v
  versionForm.value = {
    name: v.name,
    description: v.description,
    status: v.status || 'active',
  }
  showVersionModal.value = true
}

async function handleVersionSave() {
  if (!versionForm.value.name.trim() || !projectId.value) return
  versionSubmitting.value = true
  try {
    if (editingVersion.value) {
      const ok = await versionStore.update(editingVersion.value.id, {
        name: versionForm.value.name,
        description: versionForm.value.description,
        status: versionForm.value.status as VersionStatus,
      })
      if (ok) message.success('版本已更新')
      else message.error('版本更新失败')
    } else {
      const ok = await versionStore.createWithProject(projectId.value, {
        name: versionForm.value.name,
        description: versionForm.value.description,
        status: 'active',
      })
      if (ok) message.success('版本已创建')
      else message.error('版本创建失败')
    }
    showVersionModal.value = false
  } catch (e) {
    message.error('保存版本异常')
    console.error('保存版本失败:', e)
  } finally {
    versionSubmitting.value = false
  }
}

// ── 版本状态流转 ──
const showVersionTransitionConfirm = ref(false)
const transitionVersion = ref<any>(null)
const transitionTarget = ref<VersionStatus>('released')
const transitionLabel = ref('')
const isTransitioning = ref(false)

function handleVersionTransition(v: any, target: VersionStatus, label: string) {
  transitionVersion.value = v
  transitionTarget.value = target
  transitionLabel.value = label
  showVersionTransitionConfirm.value = true
}

async function confirmVersionTransition() {
  if (!transitionVersion.value) return
  isTransitioning.value = true
  try {
    await versionStore.update(transitionVersion.value.id, { status: transitionTarget.value })
    const label = versionStatusLabel(transitionTarget.value)
    message.success(`版本「${transitionVersion.value.name}」已${label}`)
    showVersionTransitionConfirm.value = false
  } catch (e) {
    message.error('状态变更失败')
    console.error('状态变更失败:', e)
  } finally {
    isTransitioning.value = false
  }
}

// ── 删除版本 ──
const showDeleteVersionConfirm = ref(false)
const deletingVersion = ref<any>(null)
const isDeletingVersion = ref(false)

function handleDeleteVersion(v: any) {
  deletingVersion.value = v
  showDeleteVersionConfirm.value = true
}

async function confirmDeleteVersion() {
  if (!deletingVersion.value) return
  isDeletingVersion.value = true
  try {
    await versionStore.remove(deletingVersion.value.id)
    message.success(`版本「${deletingVersion.value.name}」已删除`)
    showDeleteVersionConfirm.value = false
  } catch (e) {
    message.error('删除版本异常')
    console.error('删除版本失败:', e)
  } finally {
    isDeletingVersion.value = false
  }
}

// ── 成员管理 ──
const showMemberModal = ref(false)
const showRemoveMemberConfirm = ref(false)
const newMemberName = ref('')
const newMemberRole = ref('tester')
const memberSubmitting = ref(false)
const editingRoleId = ref<string | null>(null)
const editingRoleValue = ref('tester')
const removingMember = ref<any>(null)
const isRemovingMember = ref(false)

const roleOptions = [
  { label: '负责人', value: 'owner' },
  { label: '测试员', value: 'tester' },
  { label: '观察者', value: 'viewer' },
]

function roleLabel(role: string): string {
  const map: Record<string, string> = { owner: '负责人', tester: '测试员', viewer: '观察者' }
  return map[role] || role
}

function startEditRole(member: any) {
  editingRoleValue.value = member.role
  editingRoleId.value = member.id
}

async function saveRole(memberId: string) {
  if (!editingRoleId.value) return
  editingRoleId.value = null
  try {
    await store.updateMemberRole(memberId, editingRoleValue.value)
  } catch (e) {
    message.error('角色更新失败')
    console.error('更新角色失败:', e)
  }
}

async function handleAddMember() {
  if (!newMemberName.value.trim() || !projectId.value) return
  memberSubmitting.value = true
  try {
    const ok = await store.addMember(projectId.value, newMemberName.value.trim(), newMemberRole.value as MemberRole)
    if (ok) {
      message.success(`成员「${newMemberName.value}」已添加`)
      newMemberName.value = ''
      newMemberRole.value = 'tester'
      showMemberModal.value = false
    } else { message.error('添加失败') }
  } catch (e) {
    message.error('添加成员异常')
    console.error('添加成员失败:', e)
  } finally { memberSubmitting.value = false }
}

function handleRemoveMember(member: any) {
  removingMember.value = member
  showRemoveMemberConfirm.value = true
}

async function confirmRemoveMember() {
  if (!removingMember.value || !projectId.value) return
  isRemovingMember.value = true
  try {
    const ok = await store.removeMember(removingMember.value.id, projectId.value)
    if (ok) message.success(`成员「${removingMember.value.name}」已移除`)
    else message.error('移除失败')
    showRemoveMemberConfirm.value = false
  } catch (e) {
    message.error('移除成员异常')
    console.error('移除成员失败:', e)
  } finally {
    isRemovingMember.value = false
  }
}

// ── 切换 tab 时懒加载 ──
watch(activeTab, (tab) => {
  if (tab === 'versions' && versions.value.length === 0 && !versionLoading.value) {
    versionStore.fetchVersions(projectId.value)
  }
  if (tab === 'members' && store.members.length === 0) {
    store.fetchMembers(projectId.value)
  }
})

function formatTime(iso: string) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.page-wrap {
  max-width: 900px;
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
.back-nav:hover { color: #C67B5C; }
.back-arrow { font-size: 16px; }

/* ── 项目信息卡片 ── */
.info-card {
  background: #FFFDF9;
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
  color: #3D2E1F;
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
.project-desc:hover { color: #C67B5C; }
.desc-edit { margin-bottom: 20px; }
.stats-row {
  display: flex;
  gap: 32px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}
.stat-item { display: flex; flex-direction: column; gap: 2px; }
.stat-value { font-size: 18px; font-weight: 600; color: #3D2E1F; }
.stat-label { font-size: 12px; color: #7A6855; }

/* ── tab toolbar ── */
.tab-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.tab-count { font-size: 13px; color: #7A6855; }
.tab-empty {
  text-align: center;
  padding: 48px 24px;
  font-size: 14px;
  color: #7A6855;
}

/* ── 版本列表 ── */
.table-card {
  background: #FFFDF9;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  overflow: hidden;
}
.version-info { display: flex; align-items: center; gap: 12px; }
.version-name { font-size: 14px; font-weight: 600; color: #3D2E1F; }
.version-date { font-size: 12px; color: #7A6855; }
.version-desc { font-size: 12px; color: #7A6855; margin-top: 2px; line-height: 1.5; }
.version-actions { display: flex; gap: 8px; }

/* ── 成员列表 ── */
.member-list { display: flex; flex-direction: column; }
.member-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}
.member-item:last-child { border-bottom: none; }
.member-info { flex: 1; display: flex; gap: 12px; align-items: center; }
.member-name { font-size: 14px; font-weight: 500; color: #3D2E1F; }

/* ── loading ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 64px 0;
  color: #7A6855;
  font-size: 14px;
}

/* ── modal ── */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .page-wrap { padding: 16px 12px 48px; }
  .stats-row { flex-wrap: wrap; gap: 16px; }
  .stat-item { flex: 1 1 calc(50% - 16px); }
}
</style>
