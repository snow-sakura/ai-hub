<template>
  <div class="project-form-wrap">
    <h3 class="form-title">{{ isEdit ? '编辑项目' : '新建项目' }}</h3>
    <n-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-placement="top"
      :style="{ maxWidth: '480px' }"
    >
      <n-form-item label="项目名称" path="name">
        <n-input
          v-model:value="formData.name"
          placeholder="输入项目名称（2-200字符）"
          :maxlength="200"
          show-count
        />
      </n-form-item>
      <n-form-item label="项目描述" path="description">
        <n-input
          v-model:value="formData.description"
          type="textarea"
          placeholder="简要描述项目目标和范围..."
          :rows="4"
          :maxlength="2000"
          show-count
        />
      </n-form-item>
      <n-form-item label="项目状态" path="status">
        <n-select
          v-model:value="formData.status"
          :options="statusOptions"
        />
      </n-form-item>

      <!-- 创建模式：初始版本和成员（可选） -->
      <template v-if="!isEdit">
        <n-divider />
        <n-form-item label="初始版本名（可选）">
          <n-input
            v-model:value="initialVersionName"
            placeholder="创建项目时同时创建初始版本"
            clearable
          />
        </n-form-item>
        <n-form-item label="初始成员（可选）">
          <div class="init-members">
            <div v-for="(m, i) in initialMembers" :key="i" class="init-member-row">
              <n-input
                v-model:value="m.name"
                placeholder="成员姓名"
                :style="{ width: '160px' }"
                size="small"
              />
              <n-select
                v-model:value="m.role"
                :options="roleOptions"
                :style="{ width: '110px' }"
                size="small"
              />
              <n-button size="tiny" text type="error" @click="initialMembers.splice(i, 1)">
                删除
              </n-button>
            </div>
            <n-button v-if="initialMembers.length < 10" size="tiny" text @click="initialMembers.push({ name: '', role: 'tester' })">
              + 添加成员
            </n-button>
          </div>
        </n-form-item>
      </template>
    </n-form>

    <!-- 编辑模式：关联版本和成员 -->
    <div v-if="isEdit" class="assoc-section">
      <n-divider />

      <div class="assoc-row">
        <span class="assoc-label">关联版本</span>
        <div class="assoc-tags">
          <n-tag
            v-for="v in versionStore.versions"
            :key="v.id"
            closable
            :bordered="false"
            size="small"
            style="cursor: pointer"
            @click="openVersionEdit(v)"
            @close.stop="handleRemoveVersion(v.id)"
          >
            {{ v.name }}
          </n-tag>
          <span v-if="versionStore.versions.length === 0" class="assoc-empty">暂无版本</span>
        </div>
        <div class="assoc-add">
          <template v-if="showVersionInput">
            <n-input
              v-model:value="newVersionName"
              size="small"
              placeholder="输入版本名"
              :style="{ width: '180px' }"
            />
            <n-button size="tiny" type="primary" @click="handleQuickAddVersion">添加</n-button>
            <n-button size="tiny" @click="showVersionInput = false; newVersionName = ''">取消</n-button>
          </template>
          <n-button v-else size="tiny" text @click="showVersionInput = true">
            + 快速创建版本
          </n-button>
        </div>
      </div>

      <div class="assoc-row">
        <span class="assoc-label">关联成员</span>
        <div class="assoc-tags">
          <n-tag
            v-for="m in store.members"
            :key="m.id"
            closable
            :bordered="false"
            size="small"
            @close="handleRemoveMember(m.id)"
          >
            {{ m.name }}（{{ roleLabel(m.role) }}）
          </n-tag>
          <span v-if="store.members.length === 0" class="assoc-empty">暂无成员</span>
        </div>
        <div class="assoc-add">
          <template v-if="showMemberInput">
            <n-input
              v-model:value="newMemberName"
              size="small"
              placeholder="成员姓名"
              :style="{ width: '140px' }"
            />
            <n-select
              v-model:value="newMemberRole"
              size="small"
              :options="roleOptions"
              :style="{ width: '100px' }"
            />
            <n-button size="tiny" type="primary" @click="handleQuickAddMember">添加</n-button>
            <n-button size="tiny" @click="showMemberInput = false; newMemberName = ''">取消</n-button>
          </template>
          <n-button v-else size="tiny" text @click="showMemberInput = true">
            + 快速添加成员
          </n-button>
        </div>
      </div>
    </div>

    <!-- 版本编辑弹窗 -->
    <n-modal
      v-model:show="showVersionEditModal"
      preset="card"
      title="编辑版本"
      :style="{ maxWidth: '480px' }"
      @after-leave="editingVersion = null"
    >
      <n-form label-placement="top">
        <n-form-item label="版本名称">
          <n-input v-model:value="versionEditForm.name" placeholder="版本名称" :maxlength="200" />
        </n-form-item>
        <n-form-item label="版本描述">
          <n-input
            v-model:value="versionEditForm.description"
            type="textarea"
            :rows="3"
            placeholder="版本说明..."
          />
        </n-form-item>
        <n-form-item label="版本状态">
          <n-select v-model:value="versionEditForm.status" :options="versionStatusOptions" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-actions">
          <n-button @click="showVersionEditModal = false">取消</n-button>
          <n-button type="primary" :loading="isVersionSaving" @click="handleSaveVersionEdit">
            保存
          </n-button>
        </div>
      </template>
    </n-modal>

    <div class="form-actions">
      <n-button @click="$emit('cancel')">取消</n-button>
      <n-button
        type="primary"
        :loading="isSubmitting"
        @click="handleSubmit"
      >
        {{ isEdit ? '保存修改' : '创建项目' }}
      </n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { NDivider, NTag, useMessage } from 'naive-ui'
import type { FormInst } from 'naive-ui'
import type { ProjectStatus } from '@/modules/ai_testing/types/project'
import type { ProjectVersion } from '@/modules/ai_testing/types/version'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import { useVersionStore } from '@/modules/ai_testing/stores/version'

const props = defineProps<{
  editData?: { id: string; name: string; description: string; status: ProjectStatus }
}>()

const emit = defineEmits<{
  cancel: []
  saved: []
}>()

const message = useMessage()
const store = useProjectStore()
const versionStore = useVersionStore()
const formRef = ref<FormInst | null>(null)
const isSubmitting = ref(false)
const isEdit = !!props.editData

const formData = reactive({
  name: props.editData?.name || '',
  description: props.editData?.description || '',
  status: (props.editData?.status || 'active') as ProjectStatus,
})

const statusOptions = [
  { label: '进行中', value: 'active' },
  { label: '已暂停', value: 'paused' },
  { label: '已完成', value: 'completed' },
  { label: '已归档', value: 'archived' },
]

const rules = {
  name: {
    required: true,
    message: '项目名称不能为空',
    trigger: ['blur', 'input'],
  },
}

// ── 创建模式：初始版本和成员 ─────────────────────────────────
const initialVersionName = ref('')
const initialMembers = ref<Array<{ name: string; role: string }>>([])

const roleOptions = [
  { label: '负责人', value: 'owner' },
  { label: '测试员', value: 'tester' },
  { label: '观察者', value: 'viewer' },
]

function roleLabel(role: string): string {
  const map: Record<string, string> = { owner: '负责人', tester: '测试员', viewer: '观察者' }
  return map[role] || role
}

// ── 编辑模式：关联版本 ─────────────────────────────────────
const showVersionInput = ref(false)
const newVersionName = ref('')

async function handleQuickAddVersion() {
  if (!newVersionName.value.trim() || !props.editData?.id) return
  await versionStore.create(props.editData.id, { name: newVersionName.value.trim() })
  newVersionName.value = ''
  showVersionInput.value = false
}

async function handleRemoveVersion(versionId: string) {
  await versionStore.remove(versionId)
}

// ── 编辑模式：版本编辑弹窗 ─────────────────────────────────
const showVersionEditModal = ref(false)
const editingVersion = ref<ProjectVersion | null>(null)
const isVersionSaving = ref(false)

const versionEditForm = reactive({
  name: '',
  description: '',
  status: 'active' as string,
})

const versionStatusOptions = [
  { label: '活跃', value: 'active' },
  { label: '已发布', value: 'released' },
  { label: '已归档', value: 'archived' },
]

function openVersionEdit(v: ProjectVersion) {
  editingVersion.value = v
  versionEditForm.name = v.name
  versionEditForm.description = v.description
  versionEditForm.status = v.status
  showVersionEditModal.value = true
}

async function handleSaveVersionEdit() {
  if (!editingVersion.value || !versionEditForm.name.trim()) return
  isVersionSaving.value = true
  try {
    const ok = await versionStore.update(editingVersion.value.id, {
      name: versionEditForm.name,
      description: versionEditForm.description,
      status: versionEditForm.status as any,
    })
    if (ok) message.success('版本已更新')
    showVersionEditModal.value = false
  } finally {
    isVersionSaving.value = false
  }
}

// ── 编辑模式：关联成员 ─────────────────────────────────────
const showMemberInput = ref(false)
const newMemberName = ref('')
const newMemberRole = ref('tester')

async function handleQuickAddMember() {
  if (!newMemberName.value.trim() || !props.editData?.id) return
  const ok = await store.addMember(props.editData.id, newMemberName.value.trim(), newMemberRole.value)
  if (ok) {
    newMemberName.value = ''
    showMemberInput.value = false
  }
}

async function handleRemoveMember(memberId: string) {
  if (!props.editData?.id) return
  await store.removeMember(memberId, props.editData.id)
}

// ── 编辑模式初始化：加载关联数据 ───────────────────────────
onMounted(() => {
  if (isEdit && props.editData?.id) {
    versionStore.fetchVersions(props.editData.id)
    store.fetchMembers(props.editData.id)
  }
})

// ── 表单提交 ────────────────────────────────────────────────
async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  isSubmitting.value = true
  try {
    if (isEdit && props.editData) {
      const ok = await store.updateProject(props.editData.id, { ...formData })
      if (ok) message.success('项目已更新')
      else message.error('更新失败')
      emit('saved')
    } else {
      const project = await store.createProject(formData)
      if (project) {
        // 创建成功后，添加初始版本和成员
        if (initialVersionName.value.trim()) {
          try { await versionStore.create(project.id, { name: initialVersionName.value.trim() }) }
          catch { /* 版本创建失败不影响项目创建 */ }
        }
        for (const m of initialMembers.value) {
          if (m.name.trim()) {
            try { await store.addMember(project.id, m.name.trim(), m.role) }
            catch { /* 成员添加失败不影响项目创建 */ }
          }
        }
        message.success('项目已创建')
        emit('saved')
      } else {
        message.error('创建失败')
      }
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.project-form-wrap {
  padding: 4px 0;
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #1a1a2e);
  margin: 0 0 24px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 初始成员 */
.init-members {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.init-member-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 关联区域 */
.assoc-section {
  margin: 20px 0 0;
}

.assoc-row {
  margin-bottom: 16px;
}

.assoc-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #5C4A38;
  margin-bottom: 8px;
}

.assoc-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.assoc-empty {
  font-size: 12px;
  color: #7A6855;
}

.assoc-add {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
