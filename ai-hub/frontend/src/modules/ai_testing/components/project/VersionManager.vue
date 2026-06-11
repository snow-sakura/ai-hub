<template>
  <n-card size="small" title="版本管理">
    <template #header-extra>
      <n-button size="small" type="primary" @click="showCreateModal = true">
        新建版本
      </n-button>
    </template>

    <n-empty v-if="!versions.length" description="暂无版本" />

    <n-list v-else>
      <n-list-item v-for="v in versions" :key="v.id">
        <template #prefix>
          <n-tag
            :type="v.status === 'active' ? 'success' : v.status === 'released' ? 'info' : 'default'"
            size="tiny"
          >
            {{ STATUS_LABELS[v.status] || v.status }}
          </n-tag>
        </template>

        <n-space :size="8" align="center">
          <n-text strong>{{ v.name }}</n-text>
          <n-text depth="3" style="font-size: 12px;">{{ v.created_at }}</n-text>
        </n-space>

        <template v-if="v.description">
          <n-text depth="3" style="font-size: 12px;">{{ v.description }}</n-text>
        </template>

        <template #suffix>
          <n-button size="tiny" text @click="startEdit(v)">编辑</n-button>
          <n-button size="tiny" text type="error" @click="handleDelete(v.id)">删除</n-button>
        </template>
      </n-list-item>
    </n-list>

    <!-- 创建/编辑弹窗 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      :title="editingVersion ? '编辑版本' : '新建版本'"
      style="max-width: 480px;"
    >
      <n-form :model="formData" label-placement="top">
        <n-form-item label="版本名称">
          <n-input
            v-model:value="formData.name"
            placeholder="如 v1.0.0"
            :maxlength="200"
          />
        </n-form-item>
        <n-form-item label="版本描述">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            :rows="3"
            placeholder="版本说明..."
          />
        </n-form-item>
        <n-form-item v-if="editingVersion" label="版本状态">
          <n-select
            v-model:value="formData.status"
            :options="statusOptions"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end" :size="12">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" :loading="isSubmitting" @click="handleSave">
            {{ editingVersion ? '保存' : '创建' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </n-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useVersionStore } from '@/modules/ai_testing/stores/version'
import type { ProjectVersion } from '@/modules/ai_testing/types/version'

const props = defineProps<{ projectId: string }>()

const STATUS_LABELS: Record<string, string> = {
  active: '活跃',
  released: '已发布',
  archived: '已归档',
}

const versionStore = useVersionStore()
const versions = versionStore.versions
const showCreateModal = ref(false)
const editingVersion = ref<ProjectVersion | null>(null)
const isSubmitting = ref(false)

const formData = reactive({
  name: '',
  description: '',
  status: 'active' as string,
})

const statusOptions = [
  { label: '活跃', value: 'active' },
  { label: '已发布', value: 'released' },
  { label: '已归档', value: 'archived' },
]

function startEdit(v: ProjectVersion) {
  editingVersion.value = v
  formData.name = v.name
  formData.description = v.description
  formData.status = v.status
  showCreateModal.value = true
}

async function handleSave() {
  if (!formData.name.trim()) return
  isSubmitting.value = true
  try {
    if (editingVersion.value) {
      await versionStore.update(editingVersion.value.id, {
        name: formData.name,
        description: formData.description,
        status: formData.status as any,
      })
    } else {
      await versionStore.create(props.projectId, {
        name: formData.name,
        description: formData.description,
        status: 'active',
      })
    }
    showCreateModal.value = false
    editingVersion.value = null
    formData.name = ''
    formData.description = ''
    formData.status = 'active'
  } finally {
    isSubmitting.value = false
  }
}

async function handleDelete(versionId: string) {
  await versionStore.remove(versionId)
}

onMounted(() => {
  versionStore.fetchVersions(props.projectId)
})
</script>
