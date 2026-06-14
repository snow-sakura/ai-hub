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

      <n-divider />

      <!-- 关联已有版本/成员（创建和编辑均显示） -->
      <n-form-item label="关联已有版本（可选）">
        <n-select
          v-model:value="selectedVersionIds"
          multiple
          :options="standaloneVersionOptions"
          placeholder="选择已有版本关联到此项目"
          clearable
          filterable
        />
      </n-form-item>

      <n-form-item label="关联已有成员（可选）">
        <n-select
          v-model:value="selectedMemberIds"
          multiple
          :options="standaloneMemberOptions"
          placeholder="选择已有成员关联到此项目"
          clearable
          filterable
        />
      </n-form-item>
    </n-form>

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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useMessage } from 'naive-ui'
import type { FormInst } from 'naive-ui'
import type { ProjectStatus } from '@/modules/ai_testing/types/project'
import type { ProjectVersion } from '@/modules/ai_testing/types/version'
import type { SelectOption } from 'naive-ui'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import { useVersionStore } from '@/modules/ai_testing/stores/version'
import * as memberApi from '@/modules/ai_testing/api/project'
import * as versionApi from '@/modules/ai_testing/api/version'

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

// ── 监听 editData 变化（编辑时回显数据） ──
watch(() => props.editData, (val) => {
  formData.name = val?.name || ''
  formData.description = val?.description || ''
  formData.status = (val?.status || 'active') as ProjectStatus
}, { immediate: true })

const rules = {
  name: {
    required: true,
    message: '项目名称不能为空',
    trigger: ['blur', 'input'],
  },
}

// ── 创建模式：关联已有版本/成员 ─────────────────────────────
const standaloneVersions = ref<ProjectVersion[]>([])
const standaloneMembers = ref<Array<{ id: string; name: string; role: string }>>([])
const selectedVersionIds = ref<string[]>([])
const selectedMemberIds = ref<string[]>([])
// 记录编辑模式初始关联的成员 ID（保存时对比需要解绑的成员）
const originalMemberIds = ref<string[]>([])

const standaloneVersionOptions = computed<SelectOption[]>(() =>
  standaloneVersions.value.map(v => ({ label: `${v.name}`, value: v.id }))
)

const standaloneMemberOptions = computed<SelectOption[]>(() =>
  standaloneMembers.value.map(m => ({ label: `${m.name}（${roleLabel(m.role)}）`, value: m.id }))
)


const roleOptions = [
  { label: '负责人', value: 'owner' },
  { label: '测试员', value: 'tester' },
  { label: '观察者', value: 'viewer' },
]

function roleLabel(role: string): string {
  const map: Record<string, string> = { owner: '负责人', tester: '测试员', viewer: '观察者' }
  return map[role] || role
}

// ── 初始化：加载关联数据或全部版本/成员列表 ────────────────
onMounted(async () => {
  if (isEdit && props.editData?.id) {
    await Promise.all([
      versionStore.fetchVersions(props.editData.id),
      store.fetchMembers(props.editData.id),
      versionApi.getAllVersions().then(r => { standaloneVersions.value = r.data || [] }).catch(() => {}),
      memberApi.getAllMembers().then(r => { standaloneMembers.value = r.data || [] }).catch(() => {}),
    ])
    // 预选中已关联的版本和成员
    selectedVersionIds.value = versionStore.versions.map(v => v.id)
    selectedMemberIds.value = store.members.map(m => m.id)
    // 保存初始成员关联，编辑保存时对比解除不再关联的成员
    originalMemberIds.value = [...selectedMemberIds.value]
  } else {
    // 创建模式：加载全部已有版本和成员供选择
    try {
      const res = await versionApi.getAllVersions()
      standaloneVersions.value = res.data || []
    } catch (e) { console.warn('获取版本列表失败:', e) }
    try {
      const res = await memberApi.getAllMembers()
      standaloneMembers.value = res.data || []
    } catch (e) { console.warn('获取成员列表失败:', e) }
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
      if (ok) {
        // 关联选中的已有版本到项目
        for (const vid of selectedVersionIds.value) {
          try { await memberApi.linkVersionToProject(vid, props.editData.id) } catch (e) { console.warn(`关联版本 ${vid} 到项目失败:`, e) }
        }
        // 多对多成员关联：解绑取消的成员，绑定新增的成员
        const newMemberIds = selectedMemberIds.value
        const oldMemberIds = originalMemberIds.value
        const toUnlink = oldMemberIds.filter(id => !newMemberIds.includes(id))
        const toLink = newMemberIds.filter(id => !oldMemberIds.includes(id))
        for (const mid of toUnlink) {
          try { await memberApi.unlinkMemberFromProject(mid, props.editData.id) } catch (e) { console.warn(`解绑成员 ${mid} 失败:`, e) }
        }
        for (const mid of toLink) {
          try { await memberApi.linkMemberToProject(mid, props.editData.id) } catch (e) { console.warn(`关联成员 ${mid} 到项目失败:`, e) }
        }
        message.success('项目已更新')
      } else {
        message.error('更新失败')
      }
      emit('saved')
    } else {
      const project = await store.createProject(formData)
      if (project) {
        // 关联已有版本到项目
        for (const vid of selectedVersionIds.value) {
          try { await memberApi.linkVersionToProject(vid, project.id) } catch (e) { console.warn(`关联版本 ${vid} 到项目失败:`, e) }
        }
        // 关联已有成员到项目
        for (const mid of selectedMemberIds.value) {
          try { await memberApi.linkMemberToProject(mid, project.id) } catch (e) { console.warn(`关联成员 ${mid} 到项目失败:`, e) }
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

</style>
