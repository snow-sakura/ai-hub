<template>
  <div class="page-wrap">
    <!-- 返回导航 -->
    <div class="back-nav" @click="router.back()">
      <span class="back-arrow">←</span>
      <span>返回</span>
    </div>

    <header class="form-header">
      <h1 class="page-title">{{ isEdit ? '编辑评审' : '创建评审' }}</h1>
      <p class="page-sub">{{ isEdit ? '修改评审信息' : '发起一次测试用例评审，邀请团队成员共同审查' }}</p>
    </header>

    <n-spin :show="pageLoading">
      <div class="form-card">
        <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
          <!-- 标题 -->
          <div class="form-row">
            <n-form-item label="评审标题" path="title" class="flex-grow">
              <n-input
                v-model:value="formData.title"
                placeholder="请输入评审标题，如「Sprint 23 用例评审」"
                :maxlength="200"
                show-count
              />
            </n-form-item>
          </div>

          <!-- 项目 + 优先级 + 截止日期 -->
          <div class="form-row form-row-3">
            <n-form-item label="关联项目" path="project_id">
              <n-select
                v-model:value="formData.project_id"
                placeholder="选择项目"
                :options="projectOptions"
                :loading="loadingProjects"
                clearable
                filterable
              />
            </n-form-item>
            <n-form-item label="优先级" path="priority">
              <n-select
                v-model:value="formData.priority"
                :options="priorityOptions"
                placeholder="选择优先级"
              />
            </n-form-item>
            <n-form-item label="截止日期" path="due_date">
              <n-date-picker
                v-model:value="formData.due_date"
                type="date"
                placeholder="选择截止日期"
                clearable
                :style="{ width: '100%' }"
              />
            </n-form-item>
          </div>

          <!-- 描述 -->
          <n-form-item label="评审描述" path="description">
            <n-input
              v-model:value="formData.description"
              type="textarea"
              placeholder="请描述本次评审的范围、目标和注意事项..."
              :rows="4"
              :maxlength="1000"
              show-count
            />
          </n-form-item>

          <!-- 选择用例（弹窗模式） -->
          <n-form-item label="选择用例" path="selected_cases">
            <div class="case-select-trigger">
              <n-button type="primary" ghost @click="openCaseModal" :disabled="!formData.project_id">
                <template #icon>📋</template>
                {{ formData.selected_cases.length > 0 ? `已选 ${formData.selected_cases.length} 条用例` : '选择用例' }}
              </n-button>
              <n-button v-if="formData.selected_cases.length > 0" text size="tiny" type="warning" @click="formData.selected_cases = []">
                清空
              </n-button>
              <n-tag v-if="!formData.project_id" size="tiny" type="warning">
                请先选择关联项目
              </n-tag>
            </div>
          </n-form-item>

          <!-- 选择评审人 -->
          <n-form-item label="选择评审人" path="reviewers">
            <n-select
              v-model:value="formData.reviewers"
              multiple
              placeholder="选择参与评审的成员"
              :options="reviewerOptions"
              :loading="loadingMembers"
              :max-tag-count="4"
              filterable
            />
          </n-form-item>
        </n-form>

        <div class="form-actions">
          <n-button @click="router.back()">取消</n-button>
          <n-button type="primary" :loading="isSaving" @click="handleSubmit">
            提交评审
          </n-button>
        </div>
      </div>
    </n-spin>

    <!-- ── 用例选择弹窗 ── -->
    <n-modal
      v-model:show="showCaseModal"
      title="选择用例"
      preset="card"
      :style="{ maxWidth: '900px', width: '90%' }"
      :mask-closable="false"
      :segmented="{ content: true }"
    >
      <!-- 筛选行 -->
      <div class="modal-filter-row">
        <n-select
          v-model:value="modalFilter.case_type"
          :options="caseTypeOptions"
          placeholder="用例类型"
          clearable
          size="small"
          style="width:130px"
          @update:value="loadModalCases"
        />
        <n-select
          v-model:value="modalFilter.version"
          :options="versionOptions"
          placeholder="版本/模块"
          clearable
          size="small"
          style="width:130px"
          @update:value="loadModalCases"
        />
        <n-input
          v-model:value="modalFilter.keyword"
          placeholder="搜索用例标题..."
          clearable
          size="small"
          style="width:180px"
          @keyup.enter="loadModalCases"
        />
        <n-button size="small" @click="loadModalCases">搜索</n-button>
        <div class="modal-filter-actions">
          <n-checkbox
            :checked="isAllPageSelected"
            :indeterminate="isPartialSelected"
            @update:checked="toggleSelectAllPage"
          >本页全选</n-checkbox>
          <n-button size="tiny" text @click="clearModalSelection">清空</n-button>
        </div>
      </div>

      <!-- 用例表格 -->
      <n-data-table
        :columns="caseColumns"
        :data="modalCaseList"
        :loading="loadingCases"
        :bordered="false"
        :single-line="false"
        size="small"
        :row-key="(row: any) => row.id"
        :checked-row-keys="modalCheckedKeys"
        @update:checked-row-keys="modalCheckedKeys = (($event || []) as any[]).map(String)"
        style="margin: 8px 0"
      />

      <!-- 分页 + 已选计数 -->
      <div class="modal-footer">
        <n-tag type="info" size="small" v-if="modalCheckedKeys.length">
          已选 {{ modalCheckedKeys.length }} / {{ modalTotal }} 条
        </n-tag>
        <n-pagination
          v-if="modalTotal > modalPageSize"
          :page="modalPage"
          :page-size="modalPageSize"
          :item-count="modalTotal"
          size="small"
          @update:page="onModalPageChange"
        />
      </div>

      <template #footer>
        <div class="modal-actions">
          <n-button @click="showCaseModal = false">取消</n-button>
          <n-button type="primary" @click="confirmCaseSelection">
            确认选择（{{ modalCheckedKeys.length }} 条）
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormInst, SelectOption, DataTableColumn } from 'naive-ui'
import { useReviewStore } from '@/modules/ai_testing/stores/review'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import * as testcaseApi from '@/modules/ai_testing/api/testcase'
import * as projectApi from '@/modules/ai_testing/api/project'
import * as reviewApi from '@/modules/ai_testing/api/review'
import type { ReviewPriority } from '@/modules/ai_testing/types/review'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const reviewStore = useReviewStore()
const projectStore = useProjectStore()

const isEdit = computed(() => !!route.query.edit)
const formRef = ref<FormInst | null>(null)
const isSaving = ref(false)
const pageLoading = ref(false)
const loadingProjects = ref(false)
const loadingCases = ref(false)
const loadingMembers = ref(false)

// ── 表单数据 ──
const formData = reactive({
  title: '',
  project_id: null as string | null,
  priority: 'P1',
  due_date: null as number | null,
  description: '',
  selected_cases: [] as string[],
  reviewers: [] as string[],
})

// ── 校验规则 ──
const rules = {
  title: { required: true, message: '评审标题不能为空', trigger: ['blur', 'input'] },
  priority: { required: true, message: '请选择优先级', trigger: 'change' },
  selected_cases: { required: true, type: 'array' as const, min: 1, message: '请至少选择一个用例', trigger: 'change' },
}

// ── 选项数据 ──
const priorityOptions: SelectOption[] = [
  { label: 'P0 - 严重', value: 'P0' },
  { label: 'P1 - 重要', value: 'P1' },
  { label: 'P2 - 一般', value: 'P2' },
  { label: 'P3 - 轻微', value: 'P3' },
]

const projectOptions = computed<SelectOption[]>(() =>
  projectStore.projects.map(p => ({ label: p.name, value: p.id }))
)

const reviewerOptions = ref<SelectOption[]>([])

const caseTypeOptions: SelectOption[] = [
  { label: '功能测试', value: 'functional' },
  { label: '接口测试', value: 'interface' },
  { label: '性能测试', value: 'performance' },
  { label: '安全测试', value: 'security' },
  { label: '兼容性测试', value: 'compatibility' },
  { label: '易用性测试', value: 'usability' },
  { label: '其他', value: 'other' },
]

// ── 弹窗状态 ──
const showCaseModal = ref(false)
const modalFilter = reactive({ case_type: null as string | null, version: null as string | null, keyword: '' })
const versionOptions = ref<SelectOption[]>([])
const modalCaseList = ref<any[]>([])
const modalCheckedKeys = ref<string[]>([])
const modalPage = ref(1)
const modalPageSize = 50
const modalTotal = ref(0)

// 弹窗表格列定义
const caseColumns: DataTableColumn[] = [
  { type: 'selection', width: 50 },
  { title: '用例标题', key: 'title', ellipsis: { tooltip: true }, minWidth: 200 },
  { title: '类型', key: 'case_type', width: 100,
    render: (row: any) => {
      const map: Record<string, string> = { functional: '功能', interface: '接口', performance: '性能', security: '安全', compatibility: '兼容', usability: '易用' }
      return map[row.case_type] || row.case_type || '-'
    }
  },
  { title: '版本', key: 'version', width: 100 },
  { title: '优先级', key: 'priority', width: 80,
    render: (row: any) => {
      const colors: Record<string, string> = { P0: '#F56C6C', P1: '#E6A23C', P2: '#909399', P3: '#C0C4CC' }
      return h('span', { style: { color: colors[row.priority] || '#909399', fontWeight: 600 } }, row.priority || '-')
    }
  },
]

// 计算：当前页是否全选
const isAllPageSelected = computed(() => {
  if (!modalCaseList.value.length) return false
  return modalCaseList.value.every((c: any) => modalCheckedKeys.value.includes(c.id))
})
const isPartialSelected = computed(() => {
  if (!modalCaseList.value.length) return false
  const some = modalCaseList.value.some((c: any) => modalCheckedKeys.value.includes(c.id))
  return some && !isAllPageSelected.value
})

function toggleSelectAllPage(checked: boolean) {
  const currentIds = modalCaseList.value.map((c: any) => c.id)
  if (checked) {
    // 合并当前页+已有选中
    const existing = new Set(modalCheckedKeys.value)
    currentIds.forEach(id => existing.add(id))
    modalCheckedKeys.value = Array.from(existing)
  } else {
    modalCheckedKeys.value = modalCheckedKeys.value.filter((id: string) => !currentIds.includes(id))
  }
}

function clearModalSelection() {
  modalCheckedKeys.value = []
}

function onModalPageChange(page: number) {
  modalPage.value = page
  loadModalCases()
}

// ── 项目变化时重置用例 ──
watch(() => formData.project_id, () => {
  formData.selected_cases = []
})

// ── 弹窗操作 ──
function openCaseModal() {
  if (!formData.project_id) return
  modalFilter.case_type = null
  modalFilter.version = null
  modalFilter.keyword = ''
  modalPage.value = 1
  modalCheckedKeys.value = [...formData.selected_cases]
  showCaseModal.value = true
  loadModalCases()
}

async function loadModalCases() {
  if (!formData.project_id) return
  loadingCases.value = true
  try {
    const params: any = {
      project_id: formData.project_id,
      page: modalPage.value,
      page_size: modalPageSize,
    }
    if (modalFilter.case_type) params.case_type = modalFilter.case_type
    if (modalFilter.version) params.version = modalFilter.version
    if (modalFilter.keyword) params.keyword = modalFilter.keyword

    const res = await testcaseApi.getTestCases(params)
    if (res.data) {
      modalCaseList.value = res.data.items || []
      modalTotal.value = res.data.total

      // 从结果中提取版本选项
      const versions = new Set<string>()
      ;(res.data.items || []).forEach((c: any) => { if (c.version) versions.add(c.version) })
      versionOptions.value = Array.from(versions).sort().map(v => ({ label: v, value: v }))
    }
  } catch (e) {
    console.error('加载用例失败:', e)
    message.error('加载用例列表失败')
    modalCaseList.value = []
  } finally {
    loadingCases.value = false
  }
}

function confirmCaseSelection() {
  formData.selected_cases = [...modalCheckedKeys.value]
  showCaseModal.value = false
}

// ── 加载选项数据 ──
async function loadProjects() {
  loadingProjects.value = true
  try {
    await projectStore.fetchProjects()
  } catch (e) {
    console.error('加载项目列表失败:', e)
  } finally {
    loadingProjects.value = false
  }
}

async function loadMembers() {
  loadingMembers.value = true
  try {
    const members = new Map<string, string>()
    for (const proj of projectStore.projects) {
      try {
        const res = await projectApi.getProjectMembers(proj.id)
        if (res.data) {
          res.data.forEach((m: any) => members.set(m.id, m.name))
        }
      } catch (e) {
        console.error(`加载项目 ${proj.id} 成员失败:`, e)
      }
    }
    reviewerOptions.value = Array.from(members.entries()).map(([id, name]) => ({
      label: name,
      value: id,
    }))
  } catch (e) {
    console.error('加载成员列表失败:', e)
    reviewerOptions.value = []
  } finally {
    loadingMembers.value = false
  }
}

// ── 编辑模式加载 ──
async function loadForEdit(reviewId: string) {
  pageLoading.value = true
  try {
    await reviewStore.fetchReview(reviewId)
    const review = reviewStore.currentReview
    if (review) {
      formData.title = review.title
      formData.project_id = review.project_id
      formData.priority = review.priority
      formData.description = review.description
      if (review.due_date) {
        formData.due_date = new Date(review.due_date).getTime()
      }
    }
    // 还原已选的用例
    const casesRes = await reviewApi.getReviewCases(reviewId)
    if (casesRes.data) {
      formData.selected_cases = casesRes.data.map((c: any) => c.case_id)
    }
    // 还原已选的评审人
    const reviewersRes = await reviewApi.getReviewReviewers(reviewId)
    if (reviewersRes.data) {
      formData.reviewers = reviewersRes.data.map((r: any) => r.id)
    }
  } catch (e) {
    console.error('加载评审信息失败:', e)
    message.error('加载评审信息失败')
  } finally {
    pageLoading.value = false
  }
}

// ── 提交 ──
async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    message.warning('请完善表单信息')
    return
  }

  isSaving.value = true
  try {
    const baseData = {
      title: formData.title,
      project_id: formData.project_id,
      priority: formData.priority as ReviewPriority,
      description: formData.description,
      due_date: formData.due_date ? new Date(formData.due_date).toISOString().slice(0, 10) : undefined,
      case_ids: formData.selected_cases,
      reviewer_ids: formData.reviewers,
    }

    if (isEdit.value) {
      await reviewStore.updateReview(route.query.edit as string, baseData)
      message.success('评审已更新')
    } else {
      await reviewStore.createReview(baseData)
      message.success('评审已创建成功')
    }
    router.push('/ai-testing/reviews')
  } catch (e: any) {
    message.error(e?.detail?.message || '操作失败')
  } finally {
    isSaving.value = false
  }
}

onMounted(async () => {
  await loadProjects()
  await Promise.all([loadMembers()])
  if (isEdit.value && route.query.edit) {
    await loadForEdit(route.query.edit as string)
  }
})
</script>

<style scoped>
.page-wrap {
  max-width: 820px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

/* ── 返回导航 ── */
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
.back-nav:hover { color: #C67B5C; }
.back-arrow { font-size: 16px; }

/* ── 表单头部 ── */
.form-header { margin-bottom: 24px; }
.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #3D2E1F;
  letter-spacing: -0.02em;
  margin: 0;
}
.page-sub {
  font-size: 13px;
  color: #8B7355;
  margin: 6px 0 0;
}

/* ── 表单卡片 ── */
.form-card {
  background: #FFFDF9;
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 12px;
  padding: 28px;
}

.form-row { display: flex; gap: 16px; }
.form-row-3 > * { flex: 1; }
.flex-grow { flex: 1; }

/* ── 用例选择触发器 ── */
.case-select-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* ── 弹窗筛选行 ── */
.modal-filter-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding-bottom: 8px;
}
.modal-filter-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── 弹窗底部 ── */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 8px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* ── 底部按钮 ── */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid rgba(180, 150, 120, 0.12);
}
  @media (max-width: 768px) {
    .page-wrap { padding: 16px 12px 48px; }
    .form-row { flex-direction: column; align-items: stretch; }
    .form-row > * { width: 100%; }
    .form-card { padding: 16px; }
    .form-actions { flex-direction: column; align-items: stretch; }
  }
</style>
