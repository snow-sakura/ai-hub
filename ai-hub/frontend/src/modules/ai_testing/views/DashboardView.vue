<template>
  <div class="page-wrap">
    <!-- 顶部问候 -->
    <header class="page-header">
      <div class="greeting">
        <span class="greeting-icon">☀️</span>
        <div>
          <h1 class="greeting-text">下午好，欢迎回到 AI-HUB 测试平台</h1>
          <p class="greeting-sub">今日宜：专注执行，细心复盘</p>
        </div>
      </div>
      <n-button ghost @click="handleRefresh">
        🔄 刷新数据
      </n-button>
    </header>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-wrap">
      <n-spin size="small" />
      <span class="loading-text">加载中...</span>
    </div>

    <!-- 统计卡片 -->
    <div v-else class="stats-row">
      <n-card size="small" class="stat-card">
        <div class="stat-icon">📁</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.project_count }}</div>
          <div class="stat-label">总项目数</div>
        </div>
      </n-card>
      <n-card size="small" class="stat-card">
        <div class="stat-icon">📋</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.total_cases.toLocaleString() }}</div>
          <div class="stat-label">总用例数</div>
        </div>
      </n-card>
      <n-card size="small" class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.member_count }}</div>
          <div class="stat-label">总成员数</div>
        </div>
      </n-card>
      <n-card size="small" class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.active_versions }}</div>
          <div class="stat-label">进行中版本</div>
        </div>
      </n-card>
    </div>

    <!-- 中间两栏 -->
    <div class="row-2col">
      <!-- 月度用例趋势 -->
      <n-card title="📈 月度用例趋势" class="chart-card">
        <div class="trend-chart">
          <div class="chart-y-axis">
            <span>500</span>
            <span>400</span>
            <span>300</span>
            <span>200</span>
            <span>100</span>
            <span>0</span>
          </div>
          <div class="chart-area">
            <!-- SVG 折线图 -->
            <svg viewBox="0 0 340 160" class="chart-svg">
              <polyline
                :points="trendPoints"
                fill="none"
                stroke="#C67B5C"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                :d="trendAreaPath"
                fill="url(#trendGradient)"
                opacity="0.3"
              />
              <!-- 数据点 -->
              <circle
                v-for="(pt, i) in trendDataPoints"
                :key="i"
                :cx="pt.x"
                :cy="pt.y"
                r="3.5"
                fill="#C67B5C"
                stroke="#FFFDF9"
                stroke-width="2"
              />
              <defs>
                <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#C67B5C" />
                  <stop offset="100%" stop-color="#FFFDF9" />
                </linearGradient>
              </defs>
            </svg>
            <!-- X 轴标签 -->
            <div class="chart-x-labels">
              <span v-for="(m, i) in ['1月','2月','3月','4月','5月','6月']" :key="i">{{ m }}</span>
            </div>
          </div>
        </div>
      </n-card>

      <!-- 用例类型分布 -->
      <n-card title="🥧 用例类型分布" class="chart-card">
        <div class="pie-distribution">
          <div class="pie-visual">
            <div class="pie-ring">
              <div
                v-for="(item, i) in pieData"
                :key="i"
                class="pie-segment"
                :style="{
                  background: item.color,
                  transform: `rotate(${item.rotate}deg)`,
                  clipPath: item.clipPath,
                }"
              />
            </div>
            <div class="pie-center-text">
              <span class="pie-total">{{ totalCasesByType.toLocaleString() }}</span>
              <span class="pie-total-label">总用例</span>
            </div>
          </div>
          <div class="pie-legend">
            <div v-for="(item, i) in pieData" :key="i" class="legend-item">
              <span class="legend-dot" :style="{ background: item.color }" />
              <span class="legend-label">{{ item.label }}</span>
              <span class="legend-value">{{ item.value }}</span>
              <span class="legend-pct">{{ item.pct }}</span>
            </div>
          </div>
        </div>
      </n-card>
    </div>

    <!-- 底部两栏 -->
    <div class="row-2col">
      <!-- 最近活动 -->
      <n-card title="🕐 最近活动" class="list-card">
        <div v-if="stats.recent_activities.length === 0" class="empty-tip">暂无活动记录</div>
        <n-list v-else>
          <n-list-item v-for="act in stats.recent_activities.slice(0, 5)" :key="act.id">
            <template #prefix>
              <span class="activity-dot" />
            </template>
            <div class="activity-item">
              <span class="activity-action">{{ act.action }}</span>
              <span class="activity-type">{{ act.entity_type }}</span>
            </div>
            <template #suffix>
              <span class="text-muted">{{ formatTime(act.created_at) }}</span>
            </template>
          </n-list-item>
        </n-list>
      </n-card>

      <!-- 快速入口 -->
      <n-card title="📌 快速入口" class="list-card">
        <div class="todo-list">
          <div class="todo-item" @click="router.push('/ai-testing/projects')">
            <span class="todo-type">📁</span>
            <div class="todo-body">
              <span class="todo-text">项目列表</span>
              <span class="todo-count">{{ stats.project_count }} 个</span>
            </div>
          </div>
          <div class="todo-item" @click="router.push('/ai-testing/testcases')">
            <span class="todo-type">📋</span>
            <div class="todo-body">
              <span class="todo-text">测试用例</span>
              <span class="todo-count">{{ stats.total_cases }} 条</span>
            </div>
          </div>
          <div class="todo-item" @click="router.push('/ai-testing/projects/members')">
            <span class="todo-type">👥</span>
            <div class="todo-body">
              <span class="todo-text">团队成员</span>
              <span class="todo-count">{{ stats.member_count }} 人</span>
            </div>
          </div>
          <div class="todo-item" @click="router.push('/ai-testing/generate')">
            <span class="todo-type">🤖</span>
            <div class="todo-body">
              <span class="todo-text">AI 生成用例</span>
              <span class="todo-count">进行中 {{ stats.active_versions }} 个</span>
            </div>
          </div>
        </div>
        <div class="todo-actions">
          <n-button size="small" ghost @click="router.push('/ai-testing/testcases')">📋 查看用例</n-button>
          <n-button size="small" type="primary" @click="router.push('/ai-testing/projects')">📁 项目管理</n-button>
        </div>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardStats } from '@/modules/ai_testing/api/project'
import type { DashboardStats } from '@/modules/ai_testing/types/project'

const router = useRouter()
const loading = ref(true)
const stats = ref<DashboardStats>({
  project_count: 0,
  total_cases: 0,
  member_count: 0,
  active_versions: 0,
  case_by_priority: {},
  case_by_type: {},
  case_by_status: {},
  recent_activities: [],
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getDashboardStats()
    if (res.data) stats.value = res.data
  } catch { /* 静默处理 */ }
  finally { loading.value = false }
}

// ── 折线图数据（模拟月度趋势，后续可从后端获取） ──
const trendValues = ref<number[]>([])
const chartW = 340
const chartH = 160
const padding = { top: 10, bottom: 20, left: 0, right: 0 }
const plotW = chartW - padding.left - padding.right
const plotH = chartH - padding.top - padding.bottom
const maxVal = computed(() => Math.max(...trendValues.value, 1))

const trendDataPoints = computed(() =>
  trendValues.value.map((v, i) => ({
    x: padding.left + (plotW / Math.max(trendValues.value.length - 1, 1)) * i,
    y: padding.top + plotH - (v / maxVal.value) * plotH,
  }))
)

const trendPoints = computed(() =>
  trendDataPoints.value.map(p => `${p.x},${p.y}`).join(' ')
)

const trendAreaPath = computed(() => {
  const pts = trendDataPoints.value
  if (pts.length < 2) return ''
  const last = pts[pts.length - 1]
  const first = pts[0]
  return (
    `M ${first.x},${first.y} ` +
    pts.slice(1).map(p => `L ${p.x},${p.y}`).join(' ') +
    ` L ${last.x},${plotH + padding.top} L ${first.x},${plotH + padding.top} Z`
  )
})

// ── 饼图数据 ──
const pieColors: Record<string, string> = {
  functional: '#C67B5C',
  api: '#D49472',
  performance: '#D4A574',
  compatibility: '#7BA87D',
  security: '#D4745C',
}
const typeLabels: Record<string, string> = {
  functional: '功能测试',
  api: 'API 测试',
  performance: '性能测试',
  compatibility: '兼容性',
  security: '安全测试',
}

const pieData = computed(() => {
  const entries = Object.entries(stats.value.case_by_type)
  const total = entries.reduce((s, [, v]) => s + v, 0) || 1
  let cumAngle = 0
  return entries.map(([key, value]) => {
    const pct = value / total
    const angle = pct * 360
    const item = {
      label: typeLabels[key] || key,
      value,
      pct: (pct * 100).toFixed(1) + '%',
      color: pieColors[key] || '#C67B5C',
      rotate: cumAngle,
      clipPath: 'none',
    }
    cumAngle += angle
    return item
  })
})

const pieConicGradient = computed(() => {
  let totalAngle = 0
  return pieData.value.map(item => {
    const start = totalAngle
    const end = totalAngle + (item.value / Math.max(Object.values(stats.value.case_by_type).reduce((s, v) => s + v, 0), 1)) * 360
    totalAngle = end
    return `${item.color} ${start}deg ${end}deg`
  }).join(', ')
})

const totalCasesByType = computed(() =>
  Object.values(stats.value.case_by_type).reduce((s, v) => s + v, 0)
)

function formatTime(iso: string) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function handleRefresh() {
  fetchData()
}

onMounted(fetchData)
</script>

<style scoped>
.page-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

/* ── 加载 ── */
.loading-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 64px 0;
}
.loading-text { font-size: 14px; color: #8B7355; }
.empty-tip { text-align: center; padding: 32px 0; color: #8B7355; font-size: 13px; }

.activity-dot {
  display: inline-block;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #C67B5C;
}
.activity-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.activity-action { color: #3D2E1F; font-weight: 500; }
.activity-type { color: #8B7355; font-size: 11px; }

/* ── 顶部问候 ── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}
.greeting {
  display: flex;
  align-items: center;
  gap: 14px;
}
.greeting-icon {
  font-size: 36px;
  line-height: 1;
}
.greeting-text {
  font-size: 22px;
  font-weight: 700;
  color: #3D2E1F;
  margin: 0;
  letter-spacing: -0.02em;
}
.greeting-sub {
  font-size: 13px;
  color: #8B7355;
  margin: 4px 0 0;
}

/* ── 统计卡片 ── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
}
.stat-card :deep(.n-card-header) {
  display: none;
}
.stat-card :deep(.n-card__content) {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
}
.stat-icon {
  font-size: 30px;
  line-height: 1;
  flex-shrink: 0;
}
.stat-body {
  flex: 1;
}
.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #3D2E1F;
  line-height: 1.2;
}
.stat-label {
  font-size: 12px;
  color: #8B7355;
  margin-top: 2px;
}
.stat-trend {
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;
  padding: 2px 8px;
  border-radius: 4px;
}
.stat-trend.up {
  color: #7BA87D;
  background: rgba(123, 168, 125, 0.1);
}
.stat-trend.down {
  color: #D4745C;
  background: rgba(212, 116, 92, 0.1);
}

/* ── 两栏布局 ── */
.row-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 14px;
}

/* ── 折线图 ── */
.trend-chart {
  display: flex;
  gap: 8px;
  padding: 4px 0;
}
.chart-y-axis {
  display: flex;
  flex-direction: column-reverse;
  justify-content: space-between;
  font-size: 10px;
  color: #8B7355;
  padding-right: 6px;
  min-width: 28px;
  text-align: right;
}
.chart-area {
  flex: 1;
}
.chart-svg {
  width: 100%;
  height: 160px;
}
.chart-x-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #8B7355;
  padding: 2px 0 0;
  margin-top: -6px;
}

/* ── 饼图 ── */
.pie-distribution {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 8px 0;
}
.pie-visual {
  position: relative;
  flex-shrink: 0;
}
.pie-ring {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: v-bind(pieConicGradient);
  position: relative;
}
.pie-center-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  background: #FFFDF9;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.pie-total {
  font-size: 22px;
  font-weight: 700;
  color: #3D2E1F;
  line-height: 1.1;
}
.pie-total-label {
  font-size: 11px;
  color: #8B7355;
}
.pie-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}
.legend-label {
  color: #5C4A38;
  flex: 1;
}
.legend-value {
  color: #3D2E1F;
  font-weight: 600;
}
.legend-pct {
  color: #8B7355;
  font-size: 11px;
  min-width: 36px;
  text-align: right;
}

/* ── 表格 ── */
.list-card :deep(.n-card__content) {
  padding: 12px 0 0;
}
.text-muted {
  color: #8B7355;
  font-size: 12px;
}
.n-table th {
  color: #5C4A38;
  font-weight: 600;
  font-size: 12px;
  background: #F6F0E7;
}
.n-table td {
  color: #3D2E1F;
  font-size: 13px;
}
.rate-good {
  color: #7BA87D;
  font-weight: 600;
}
.rate-mid {
  color: #D4A574;
  font-weight: 600;
}
.rate-bad {
  color: #D4745C;
  font-weight: 600;
}

/* ── 待办事项 ── */
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 4px 0;
}
.todo-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  transition: background 0.15s ease;
  cursor: default;
}
.todo-item:hover {
  background: rgba(198, 123, 92, 0.06);
}
.todo-type {
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
}
.todo-body {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.todo-text {
  font-size: 14px;
  color: #3D2E1F;
}
.todo-count {
  font-size: 13px;
  font-weight: 600;
  color: #C67B5C;
  background: rgba(198, 123, 92, 0.1);
  padding: 1px 10px;
  border-radius: 10px;
}
.todo-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(180, 150, 120, 0.12);
}

@media (max-width: 768px) {
  .page-wrap { padding: 16px 12px 48px; }
  .page-header { flex-wrap: wrap; gap: 10px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); gap: 10px; }
}
</style>
