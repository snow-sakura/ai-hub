<template>
  <div class="page-wrap">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <n-card size="small" class="stat-card">
        <div class="stat-value pending">{{ stats.pending }}</div>
        <div class="stat-label">待评审</div>
      </n-card>
      <n-card size="small" class="stat-card">
        <div class="stat-value reviewing">{{ stats.in_progress }}</div>
        <div class="stat-label">评审中</div>
      </n-card>
      <n-card size="small" class="stat-card">
        <div class="stat-value passed">{{ stats.approved }}</div>
        <div class="stat-label">已通过</div>
      </n-card>
      <n-card size="small" class="stat-card">
        <div class="stat-value rejected">{{ stats.rejected }}</div>
        <div class="stat-label">已拒绝</div>
      </n-card>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-section">
      <n-select
        v-model:value="filters.project_id"
        :options="projectOptions"
        placeholder="全部项目"
        clearable
        :style="{ width: '160px' }"
        @update:value="handleSearch"
      />
      <n-select
        v-model:value="filters.status"
        :options="statusOptions"
        placeholder="全部状态"
        clearable
        :style="{ width: '140px' }"
        @update:value="handleSearch"
      />
      <n-input
        v-model:value="filters.keyword"
        placeholder="搜索评审标题..."
        clearable
        :style="{ width: '260px' }"
        @keyup.enter="handleSearch"
      />
      <div class="filter-actions">
        <n-button type="primary" @click="router.push('/ai-testing/reviews/create')">
          + 新建评审
        </n-button>
      </div>
    </div>

    <!-- 加载态 -->
    <div v-if="store.isLoading" class="loading-wrap">
      <n-spin size="small" />
      <span class="loading-text">加载中...</span>
    </div>

    <!-- 错误态 -->
    <div v-else-if="loadError" class="error-wrap">
      <n-empty description="加载评审列表失败">
        <template #extra>
          <n-button type="primary" ghost @click="loadData">重新加载</n-button>
        </template>
      </n-empty>
    </div>

    <!-- 空态 -->
    <div v-else-if="store.reviews.length === 0" class="empty-wrap">
      <span class="empty-text">暂无评审记录</span>
    </div>

    <!-- 评审卡片列表 -->
    <div v-else class="review-list">
      <n-card
        v-for="item in store.reviews"
        :key="item.id"
        class="review-card"
        size="small"
        hoverable
        @click="router.push(`/ai-testing/reviews/${item.id}`)"
      >
        <div class="card-body">
          <div class="card-main">
            <div class="card-title-row">
              <span class="review-title">{{ item.title }}</span>
              <n-tag
                :type="item.priority === 'P0' ? 'error' : item.priority === 'P1' ? 'warning' : 'info'"
                size="small"
                round
                :bordered="false"
              >
                {{ item.priority }}
              </n-tag>
              <n-tag
                :type="statusTagType(item.status)"
                size="small"
                :bordered="false"
              >
                {{ statusLabel(item.status) }}
              </n-tag>
            </div>
            <div class="card-meta">
              <span class="meta-item" v-if="item.due_date">截止日期：{{ item.due_date.slice(0, 10) }}</span>
              <span class="meta-item" v-if="item.case_count">用例数：{{ item.case_count }}</span>
            </div>
            <div class="progress-row">
              <n-progress
                :percentage="item.progress"
                :height="8"
                :border-radius="4"
                indicator-placement="inside"
                processing
              />
              <span class="progress-label">{{ item.progress }}%</span>
            </div>
          </div>
        </div>
      </n-card>

      <!-- 分页 -->
      <div v-if="store.total > store.pageSize" class="pagination-wrap">
        <n-pagination
          :page="store.page"
          :page-size="store.pageSize"
          :item-count="store.total"
          @update:page="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useReviewStore } from '@/modules/ai_testing/stores/review'
import { useProjectStore } from '@/modules/ai_testing/stores/project'

const router = useRouter()
const store = useReviewStore()
const projectStore = useProjectStore()

const filters = reactive({
  project_id: null as string | null,
  status: null as string | null,
  keyword: '',
})

const projectOptions = ref<Array<{ label: string; value: string }>>([])

const statusOptions = [
  { label: '待评审', value: 'pending' },
  { label: '评审中', value: 'in_progress' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已取消', value: 'cancelled' },
]

const { stats } = storeToRefs(store)
const loadError = ref(false)

function statusTagType(status: string): 'warning' | 'info' | 'success' | 'error' | 'default' {
  const map: Record<string, 'warning' | 'info' | 'success' | 'error' | 'default'> = {
    pending: 'warning', in_progress: 'info', approved: 'success', rejected: 'error', cancelled: 'default',
  }
  return map[status] || 'default'
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    pending: '待评审', in_progress: '评审中', approved: '已通过', rejected: '已拒绝', cancelled: '已取消',
  }
  return map[status] || status
}

function handleSearch() {
  store.page = 1
  loadData()
}

function handlePageChange(p: number) {
  store.page = p
  loadData()
}

async function loadData() {
  loadError.value = false
  try {
    await store.fetchReviews({
      project_id: filters.project_id,
      status: filters.status,
      keyword: filters.keyword || undefined,
      page: store.page,
      page_size: store.pageSize,
    })
  } catch {
    loadError.value = true
  }
}

onMounted(async () => {
  loadData()
  store.fetchStats()
  await projectStore.fetchProjects()
  projectOptions.value = projectStore.projects.map(p => ({
    label: p.name,
    value: p.id,
  }))
})
</script>

<style scoped>
.page-wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}
.stat-card { text-align: center; }
.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}
.stat-value.pending { color: var(--accent, #C67B5C); }
.stat-value.reviewing { color: var(--warning, #D4A574); }
.stat-value.passed { color: var(--success, #7BA87D); }
.stat-value.rejected { color: var(--danger, #D4745C); }
.stat-label {
  font-size: 12px;
  color: #7A6855;
  margin-top: 4px;
}
.filter-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.filter-actions { margin-left: auto; }
.review-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.review-card { border-radius: 12px; cursor: pointer; }
.card-body {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}
.card-main {
  flex: 1;
  min-width: 0;
}
.card-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.review-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #3D2E1F);
}
.card-meta {
  font-size: 12px;
  color: #7A6855;
  margin-bottom: 12px;
  display: flex;
  gap: 16px;
}
.progress-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.progress-row :deep(.n-progress) { flex: 1; }
.progress-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #5C4A38);
  white-space: nowrap;
}
.loading-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 64px 0;
}
.loading-text { font-size: 14px; color: #8B7355; }
.empty-wrap {
  text-align: center;
  padding: 64px 0;
}
.empty-text { font-size: 14px; color: #8B7355; }
.error-wrap {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}
.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 24px 0 0;
}

@media (max-width: 768px) {
  .page-wrap { padding: 16px 12px 48px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .filter-section { flex-direction: column; align-items: stretch; }
  .filter-section > * { width: 100%; }
}
</style>
