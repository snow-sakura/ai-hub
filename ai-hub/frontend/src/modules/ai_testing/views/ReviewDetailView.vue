<template>
  <div class="page-wrap">
    <div v-if="!review" class="loading-wrap">
      <n-spin size="small" />
      <span class="loading-text">加载中...</span>
    </div>

    <template v-else>
      <!-- 返回导航 -->
      <div class="back-nav">
        <span class="back-arrow" @click="router.push('/ai-testing/reviews')">←</span>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-link" @click="router.push('/ai-testing/reviews')">评审列表</span>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">{{ review.title }}</span>
      </div>

      <!-- 头部 -->
      <div class="detail-header">
        <div class="header-left">
          <h1 class="page-title">{{ review.title }}</h1>
          <n-tag :type="statusConf.type" size="small" round :bordered="false">
            {{ statusConf.label }}
          </n-tag>
          <n-tag
            :type="review.priority === 'P0' ? 'error' : review.priority === 'P1' ? 'warning' : 'info'"
            size="small" round :bordered="false"
          >
            {{ review.priority }}
          </n-tag>
        </div>
        <div class="header-actions" v-if="review.status === 'pending' || review.status === 'in_progress'">
          <n-button ghost size="small" @click="handleEdit">编辑</n-button>
          <n-button type="error" ghost size="small" @click="handleCancel">取消评审</n-button>
        </div>
      </div>

      <!-- 评审信息 -->
      <div class="info-bar">
        <div class="info-item">
          <span class="info-label">项目</span>
          <span class="info-value">{{ review.project_name || '—' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">创建人</span>
          <span class="info-value">{{ review.creator || '—' }}</span>
        </div>
        <div class="info-item" v-if="review.due_date">
          <span class="info-label">截止日期</span>
          <span class="info-value">{{ review.due_date.slice(0, 10) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">用例数</span>
          <span class="info-value">{{ review.case_count || 0 }}</span>
        </div>
      </div>

      <!-- 左右两栏 -->
      <div class="detail-columns">
        <!-- 左栏：评审用例列表 -->
        <div class="left-column">
          <h3 class="section-title">评审用例</h3>
          <div class="table-card">
            <n-table :bordered="false" :single-line="false" size="small">
              <thead>
                <tr>
                  <th style="width: 60px;">序号</th>
                  <th>用例标题</th>
                  <th style="width: 80px;">优先级</th>
                  <th>评审意见</th>
                  <th style="width: 90px;">状态</th>
                  <th style="width: 160px;">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="reviewCases.length === 0">
                  <td colspan="6" class="cell-center" style="color: #8B7355; padding: 32px;">暂无关联用例</td>
                </tr>
                <template v-for="(tc, idx) in reviewCases" :key="tc.id">
                  <tr>
                    <td class="cell-center">{{ idx + 1 }}</td>
                    <td>
                      <span class="case-title-link" @click="toggleExpand(tc.id)">
                        {{ tc.case_title || tc.case_id }}
                        <span class="expand-icon">{{ expandedId === tc.id ? '▲' : '▼' }}</span>
                      </span>
                    </td>
                    <td class="cell-center">
                      <n-tag v-if="tc.case_priority"
                        :type="tc.case_priority === 'P0' ? 'error' : tc.case_priority === 'P1' ? 'warning' : tc.case_priority === 'P2' ? 'info' : 'default'"
                        size="tiny" round :bordered="false"
                      >
                        {{ tc.case_priority }}
                      </n-tag>
                      <span v-else style="color: #8B7355;">—</span>
                    </td>
                    <td>
                      <div class="comment-cell">
                        <n-input
                          v-if="editCommentId === tc.id"
                          v-model:value="inlineComment"
                          type="textarea"
                          :rows="2"
                          placeholder="输入评审意见..."
                          size="small"
                          @keydown.escape="editCommentId = null"
                        />
                        <span
                          v-else
                          class="comment-text editable"
                          @click="startEditComment(tc)"
                          :title="'点击编辑评审意见'"
                        >{{ tc.comment || '—' }}</span>
                        <div v-if="editCommentId === tc.id" class="comment-edit-actions">
                          <n-button size="tiny" text type="primary" @click="saveComment(tc)">保存</n-button>
                          <n-button size="tiny" text @click="editCommentId = null">取消</n-button>
                        </div>
                      </div>
                    </td>
                    <td class="cell-center">
                      <n-tag
                        :type="reviewCaseStatusMap[tc.status]?.type || 'default'"
                        size="tiny" round :bordered="false"
                      >
                        {{ reviewCaseStatusMap[tc.status]?.label || tc.status }}
                      </n-tag>
                    </td>
                    <td class="cell-center">
                      <div class="case-actions" v-if="review.status === 'in_progress'">
                        <n-button
                          size="tiny"
                          type="success"
                          ghost
                          :disabled="tc.status === 'approved'"
                          @click="handleReviewCase(tc, 'approved')"
                        >
                          通过
                        </n-button>
                        <n-button
                          size="tiny"
                          type="error"
                          ghost
                          :disabled="tc.status === 'rejected'"
                          @click="handleReviewCase(tc, 'rejected')"
                        >
                          拒绝
                        </n-button>
                      </div>
                    </td>
                  </tr>
                  <!-- 展开的用例详情行 -->
                  <tr v-if="expandedId === tc.id" class="expanded-row">
                    <td colspan="6">
                      <div class="case-detail-panel">
                        <div class="detail-section" v-if="tc.preconditions">
                          <span class="detail-label">前置条件</span>
                          <p class="detail-content">{{ tc.preconditions }}</p>
                        </div>
                        <div class="detail-section" v-if="tc.steps">
                          <span class="detail-label">测试步骤</span>
                          <p class="detail-content" style="white-space: pre-wrap;">{{ tc.steps }}</p>
                        </div>
                        <div class="detail-section" v-if="tc.expected_results">
                          <span class="detail-label">预期结果</span>
                          <p class="detail-content">{{ tc.expected_results }}</p>
                        </div>
                        <div v-if="!tc.preconditions && !tc.steps && !tc.expected_results" class="detail-empty">
                          暂无详细描述
                        </div>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </n-table>
          </div>
        </div>

        <!-- 右栏：评审进度 -->
        <div class="right-column">
          <h3 class="section-title">评审进度</h3>
          <n-card size="small" class="progress-card">
            <div class="overall-progress">
              <span class="progress-title">整体评审进度</span>
              <n-progress
                :percentage="review.progress"
                :height="10"
                :border-radius="5"
                indicator-placement="inside"
                processing
              />
            </div>
            <div class="progress-stats">
              <span>已评审：{{ reviewedCount }} / {{ reviewCases.length }}</span>
            </div>
          </n-card>

          <div class="bottom-actions">
            <n-button v-if="review.status === 'pending'" type="primary" size="large" @click="handleStartReview">
              开始评审
            </n-button>
            <n-button v-if="review.status === 'in_progress'" type="success" size="large" @click="handleApprove">
              通过评审
            </n-button>
            <n-button v-if="review.status === 'in_progress'" type="error" size="large" @click="handleReject">
              拒绝评审
            </n-button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useReviewStore } from '@/modules/ai_testing/stores/review'
import * as reviewApi from '@/modules/ai_testing/api/review'
import type { ReviewCase } from '@/modules/ai_testing/types/review'

const route = useRoute()
const router = useRouter()
const store = useReviewStore()
const message = useMessage()

const review = computed(() => store.currentReview)
const reviewCases = ref<ReviewCase[]>([])
const expandedId = ref<string | null>(null)
const editCommentId = ref<string | null>(null)
const inlineComment = ref('')

const reviewedCount = computed(() =>
  reviewCases.value.filter(tc => tc.status === 'approved' || tc.status === 'rejected').length
)

const statusConf = computed(() => {
  const map: Record<string, { label: string; type: 'warning' | 'success' | 'error' | 'default' }> = {
    pending: { label: '待评审', type: 'default' },
    in_progress: { label: '评审中', type: 'warning' },
    approved: { label: '已通过', type: 'success' },
    rejected: { label: '已拒绝', type: 'error' },
    cancelled: { label: '已取消', type: 'default' },
  }
  return map[review.value?.status || ''] || { label: review.value?.status || '', type: 'default' }
})

const reviewCaseStatusMap: Record<string, { label: string; type: 'success' | 'error' | 'default' }> = {
  approved: { label: '批准', type: 'success' },
  rejected: { label: '拒绝', type: 'error' },
  pending: { label: '待定', type: 'default' },
}

async function loadData() {
  const id = route.params.id as string
  await store.fetchReview(id)
  try {
    const res = await reviewApi.getReviewCases(id)
    if (res.data) reviewCases.value = res.data
  } catch (e) {
    console.error('获取评审用例失败:', e)
    reviewCases.value = []
  }
}

// ── 展开/折叠用例详情 ──
function toggleExpand(id: string) {
  expandedId.value = expandedId.value === id ? null : id
}

// ── 行内评论编辑 ──
function startEditComment(tc: ReviewCase) {
  editCommentId.value = tc.id
  inlineComment.value = tc.comment || ''
}

async function saveComment(tc: ReviewCase) {
  try {
    await reviewApi.updateReviewCaseStatus(route.params.id as string, tc.case_id, tc.status || 'pending', inlineComment.value)
    tc.comment = inlineComment.value
    editCommentId.value = null
    message.success('评审意见已保存')
  } catch (e) {
    console.error('保存评审意见失败:', e)
    message.error('保存失败')
  }
}

// ── 逐例评审 ──
async function handleReviewCase(tc: ReviewCase, status: 'approved' | 'rejected') {
  const comment = editCommentId.value === tc.id ? inlineComment.value : tc.comment
  try {
    await reviewApi.updateReviewCaseStatus(route.params.id as string, tc.case_id, status, comment || '')
    // 更新本地状态
    tc.status = status
    tc.comment = comment || ''
    editCommentId.value = null
    inlineComment.value = ''
    message.success(status === 'approved' ? '已批准该用例' : '已拒绝该用例')
    // 刷新评审进度
    await store.fetchReview(route.params.id as string)
  } catch (e) {
    console.error('更新评审状态失败:', e)
    message.error('操作失败')
  }
}

// ── 页面操作 ──
function handleEdit() {
  router.push(`/ai-testing/reviews/create?edit=${route.params.id}`)
}

async function handleCancel() {
  if (!review.value) return
  try {
    await store.updateReview(review.value.id, { status: 'cancelled' })
    message.success('已取消评审')
    await loadData()
  } catch (e) {
    console.error('取消评审失败:', e)
    message.error('操作失败')
  }
}

async function handleStartReview() {
  if (!review.value) return
  try {
    await store.updateReview(review.value.id, { status: 'in_progress', progress: 50 })
    message.success('评审已开始')
    await loadData()
  } catch (e) {
    console.error('开始评审失败:', e)
    message.error('操作失败')
  }
}

async function handleApprove() {
  if (!review.value) return
  try {
    await store.updateReview(review.value.id, { status: 'approved', progress: 100 })
    message.success('评审已通过')
    await loadData()
  } catch (e) {
    console.error('通过评审失败:', e)
    message.error('操作失败')
  }
}

async function handleReject() {
  if (!review.value) return
  try {
    await store.updateReview(review.value.id, { status: 'rejected', progress: 100 })
    message.success('评审已拒绝')
    await loadData()
  } catch (e) {
    console.error('拒绝评审失败:', e)
    message.error('操作失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}
.loading-wrap {
  display: flex; align-items: center; justify-content: center;
  gap: 8px; padding: 64px 0;
}
.loading-text { font-size: 14px; color: #8B7355; }
.back-nav {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: #7A6855; margin-bottom: 20px;
}
.back-arrow {
  font-size: 16px; cursor: pointer; transition: color 0.15s ease;
  color: var(--accent, #C67B5C);
}
.back-arrow:hover { color: var(--accent-light, #D49472); }
.breadcrumb-link { cursor: pointer; transition: color 0.15s ease; }
.breadcrumb-link:hover { color: var(--accent, #C67B5C); }
.breadcrumb-sep { color: rgba(180, 150, 120, 0.3); }
.breadcrumb-current { color: var(--text-primary, #3D2E1F); font-weight: 500; }
.detail-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
}
.header-left {
  display: flex; align-items: center; gap: 12px;
}
.page-title {
  font-size: 22px; font-weight: 700; color: var(--text-primary, #3D2E1F);
  letter-spacing: -0.02em; margin: 0;
}
.header-actions { display: flex; gap: 8px; }
.info-bar {
  display: flex; align-items: center; gap: 32px;
  padding: 16px 20px; background: var(--bg-card, #FFFDF9);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 10px; margin-bottom: 24px;
}
.info-item { display: flex; align-items: center; gap: 8px; }
.info-label { font-size: 12px; color: #7A6855; }
.info-value { font-size: 13px; font-weight: 500; color: var(--text-primary, #3D2E1F); }
.detail-columns { display: flex; gap: 20px; align-items: flex-start; }
.left-column { flex: 3; min-width: 0; }
.right-column { flex: 2; min-width: 0; }
.section-title {
  font-size: 16px; font-weight: 600; color: var(--text-primary, #3D2E1F);
  margin: 0 0 12px;
}
.table-card {
  background: var(--bg-card, #FFFDF9);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 12px; overflow: hidden;
}
.cell-center { text-align: center; }
.case-title-link {
  color: var(--accent, #C67B5C); cursor: pointer; font-weight: 500; font-size: 13px;
  display: inline-flex; align-items: center; gap: 4px;
}
.case-title-link:hover { color: var(--accent-light, #D49472); }
.expand-icon { font-size: 10px; color: #bbb5aa; }
.comment-cell { min-width: 120px; }
.comment-text { font-size: 13px; color: var(--text-secondary, #5C4A38); }
.comment-text.editable { cursor: pointer; border-bottom: 1px dashed transparent; transition: border-color 0.15s ease; }
.comment-text.editable:hover { border-color: var(--accent, #C67B5C); }
.comment-edit-actions { display: flex; gap: 4px; margin-top: 4px; }
.case-actions {
  display: flex; gap: 4px; justify-content: center;
}
/* 展开的用例详情行 */
.expanded-row td {
  background: rgba(198, 123, 92, 0.03);
  padding: 0 !important;
}
.case-detail-panel {
  padding: 12px 24px 16px;
  border-top: 1px dashed rgba(180, 150, 120, 0.2);
}
.detail-section { margin-bottom: 10px; }
.detail-label {
  font-size: 11px; font-weight: 600; color: #7A6855;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.detail-content {
  margin: 4px 0 0; font-size: 13px; line-height: 1.6;
  color: var(--text-primary, #3D2E1F);
}
.detail-empty {
  font-size: 12px; color: #bbb5aa; padding: 8px 0;
}
.progress-card { margin-bottom: 12px; }
.overall-progress { margin-bottom: 8px; }
.progress-title { font-size: 13px; font-weight: 500; color: var(--text-primary, #3D2E1F); }
.progress-stats { font-size: 12px; color: #7A6855; }
.bottom-actions {
  display: flex; justify-content: center; gap: 12px;
  margin-top: 24px; padding-top: 20px;
  border-top: 1px solid rgba(180, 150, 120, 0.12);
}
  @media (max-width: 768px) {
    .page-wrap { padding: 16px 12px 48px; }
    .detail-header { flex-direction: column; align-items: flex-start; gap: 12px; }
    .info-bar { flex-wrap: wrap; gap: 12px; }
    .detail-columns { flex-direction: column; }
    .left-column, .right-column { width: 100%; }
    .bottom-actions { flex-direction: column; align-items: stretch; }
    .case-detail-panel { padding: 12px 16px; }
    :deep(.n-table-wrapper) { overflow-x: auto; }
  }
</style>
