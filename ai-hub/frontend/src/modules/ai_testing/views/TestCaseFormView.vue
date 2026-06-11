<template>
  <div class="page-wrap">
    <!-- 返回导航 -->
    <div class="back-nav" @click="router.back()">
      <span class="back-arrow">←</span>
      <span>返回</span>
    </div>

    <header class="form-header">
      <h1 class="page-title">{{ isEdit ? '编辑用例' : '新建用例' }}</h1>
    </header>

    <div class="form-card">
      <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
        <!-- 基本信息行 -->
        <div class="form-row">
          <n-form-item label="用例标题" path="title" class="flex-grow">
            <n-input v-model:value="formData.title" placeholder="输入用例标题" :maxlength="500" show-count />
          </n-form-item>
        </div>

        <div class="form-row form-row-3">
          <n-form-item label="所属项目" path="project_id">
            <n-select
              v-model:value="formData.project_id"
              placeholder="选择项目（可选）"
              clearable
              :options="projectOptions"
            />
          </n-form-item>
          <n-form-item label="优先级" path="priority">
            <n-select v-model:value="formData.priority" :options="priorityOptions" />
          </n-form-item>
          <n-form-item label="用例类型" path="case_type">
            <n-select v-model:value="formData.case_type" :options="caseTypeOptions" />
          </n-form-item>
        </div>

        <div class="form-row form-row-2">
          <n-form-item label="版本号">
            <n-input v-model:value="formData.version" placeholder="如 v1.0" />
          </n-form-item>
          <n-form-item label="状态">
            <n-select v-model:value="formData.status" :options="statusOptions" />
          </n-form-item>
        </div>

        <!-- Markdown 编辑器区域 -->
        <div class="md-section">
          <MarkdownField v-model="formData.preconditions" label="前置条件" :height="220" />
        </div>

        <div class="md-section">
          <MarkdownField v-model="formData.steps" label="测试步骤" :height="280" />
        </div>

        <div class="md-section">
          <MarkdownField v-model="formData.expected_results" label="预期结果" :height="220" />
        </div>

        <!-- 标签 -->
        <n-form-item label="标签">
          <n-dynamic-tags v-model:value="formData.tags" />
        </n-form-item>
      </n-form>

      <div class="form-actions">
        <n-button @click="router.back()">取消</n-button>
        <n-button type="primary" :loading="isSaving" @click="handleSave">
          {{ isEdit ? '保存修改' : '创建用例' }}
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NForm, NFormItem, NInput, NSelect, NButton, NDynamicTags,
  useMessage,
} from 'naive-ui'
import type { FormInst } from 'naive-ui'
import type { CasePriority, CaseStatus } from '@/modules/ai_testing/types/testcase'
import { useTestCaseStore } from '@/modules/ai_testing/stores/testcase'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import MarkdownField from '@/modules/ai_testing/components/testcase/MarkdownField.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const store = useTestCaseStore()
const projectStore = useProjectStore()

const formRef = ref<FormInst | null>(null)
const isSaving = ref(false)
const isEdit = computed(() => route.params.id !== undefined && route.name === 'testing-testcase-edit')
const caseId = computed(() => route.params.id as string)

const projectOptions = ref<Array<{ label: string; value: string }>>([])

const priorityOptions = [
  { label: 'P0 严重', value: 'P0' },
  { label: 'P1 重要', value: 'P1' },
  { label: 'P2 一般', value: 'P2' },
  { label: 'P3 轻微', value: 'P3' },
]

const caseTypeOptions = [
  { label: '功能测试', value: 'functional' },
  { label: '性能测试', value: 'performance' },
  { label: '安全测试', value: 'security' },
  { label: '兼容性测试', value: 'compatibility' },
  { label: 'UI测试', value: 'ui' },
  { label: '接口测试', value: 'api' },
]

const statusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '启用', value: 'active' },
  { label: '废弃', value: 'deprecated' },
]

const formData = reactive({
  title: '',
  project_id: null as string | null,
  priority: 'P2' as CasePriority,
  case_type: 'functional',
  version: '',
  status: 'draft' as CaseStatus,
  preconditions: '',
  steps: '',
  expected_results: '',
  tags: [] as string[],
})

const rules = {
  title: { required: true, message: '用例标题不能为空', trigger: ['blur', 'input'] },
}

async function handleSave() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  isSaving.value = true
  try {
    if (isEdit.value) {
      const ok = await store.updateCase(caseId.value, { ...formData } as any)
      if (ok) {
        message.success('用例已更新')
        router.push(`/ai-testing/testcases/${caseId.value}`)
      } else {
        message.error('更新失败')
      }
    } else {
      const created = await store.createCase({ ...formData } as any)
      if (created) {
        message.success('用例已创建')
        router.push(`/ai-testing/testcases/${created.id}`)
      } else {
        message.error('创建失败')
      }
    }
  } finally {
    isSaving.value = false
  }
}

onMounted(async () => {
  await projectStore.fetchProjects()
  projectOptions.value = projectStore.projects.map(p => ({
    label: p.name,
    value: p.id,
  }))

  if (isEdit.value) {
    await store.fetchCase(caseId.value)
    const c = store.currentCase
    if (c) {
      formData.title = c.title
      formData.project_id = c.project_id
      formData.priority = c.priority
      formData.case_type = c.case_type
      formData.version = c.version
      formData.status = c.status
      formData.preconditions = c.preconditions
      formData.steps = c.steps
      formData.expected_results = c.expected_results
      formData.tags = c.tags
    }
  }
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
  margin-bottom: 16px;
  transition: color 0.15s ease;
}
.back-nav:hover {
  color: var(--accent, #3b82f6);
}
.back-arrow {
  font-size: 16px;
}

.form-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #1a1a2e);
  letter-spacing: -0.02em;
  margin: 0;
}

.form-card {
  background: var(--bg-card, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 28px;
}

.form-row {
  display: flex;
  gap: 16px;
}
.form-row-2 > * {
  flex: 1;
}
.form-row-3 > * {
  flex: 1;
}
.flex-grow {
  flex: 1;
}

.md-section {
  margin-top: 20px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}
</style>
