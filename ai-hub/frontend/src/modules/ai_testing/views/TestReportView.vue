<template>
  <div class="page-wrap">
    <!-- 加载态 -->
    <div v-if="loading" class="state-wrap">
      <n-spin size="large" />
    </div>

    <!-- 错误态 -->
    <div v-else-if="error" class="state-wrap">
      <n-empty description="加载报告失败">
        <template #extra>
          <n-button type="primary" @click="loadData">重新加载</n-button>
        </template>
      </n-empty>
    </div>

    <!-- 空态 -->
    <div v-else-if="isEmpty" class="state-wrap">
      <n-empty description="暂无测试报告数据">
        <template #extra>
          <n-button type="primary" @click="loadData">刷新</n-button>
        </template>
      </n-empty>
    </div>

    <template v-else>
    <!-- 顶部 -->
    <header class="page-header">
      <div>
        <h1 class="page-title">测试报告</h1>
        <p class="page-sub">生成时间：{{ generationTime }}</p>
      </div>
      <div class="header-actions">
        <n-button ghost @click="handlePreview">👁️ 预览</n-button>
        <n-button type="primary" @click="handleExport">📥 导出报告</n-button>
      </div>
    </header>

    <!-- 摘要卡片 -->
    <n-card class="summary-card" :bordered="true">
      <div class="summary-row">
        <div class="summary-item">
          <span class="summary-icon">📋</span>
          <div class="summary-body">
            <span class="summary-value">{{ summary.total_cases }}</span>
            <span class="summary-label">总用例数</span>
          </div>
        </div>
        <div class="summary-divider" />
        <div class="summary-item">
          <span class="summary-icon">✅</span>
          <div class="summary-body">
            <span class="summary-value">{{ passRateDisplay }}</span>
            <span class="summary-label">通过率</span>
          </div>
        </div>
        <div class="summary-divider" />
        <div class="summary-item">
          <span class="summary-icon">🤖</span>
          <div class="summary-body">
            <span class="summary-value">{{ aiScore }}</span>
            <span class="summary-label">AI 评分</span>
          </div>
        </div>
      </div>
    </n-card>

    <!-- 中间：环形图 + 状态概览 -->
    <div class="row-2col">
      <!-- 环形图 -->
      <n-card title="🎯 执行结果分布" class="chart-card">
        <div class="ring-chart-wrap">
          <div class="ring-chart">
            <div
              class="ring-circle"
              :style="{ background: ringGradient }"
            >
              <div class="ring-center">
                <span class="ring-center-value">{{ passRateDisplay }}</span>
                <span class="ring-center-label">通过率</span>
              </div>
            </div>
          </div>
          <div class="ring-legend">
            <div v-for="item in ringData" :key="item.label" class="ring-legend-item">
              <span class="ring-dot" :style="{ background: item.color }" />
              <span class="ring-label">{{ item.label }}</span>
              <span class="ring-value">{{ item.value }}</span>
              <span class="ring-pct">{{ item.pct }}</span>
            </div>
          </div>
        </div>
      </n-card>

      <!-- 状态概览卡片 -->
      <n-card title="📊 状态概览" class="chart-card">
        <div class="status-bars">
          <div v-for="item in statusData" :key="item.label" class="status-bar-item">
            <div class="status-bar-header">
              <span class="status-bar-label">{{ item.label }}</span>
              <span class="status-bar-count">{{ item.count }}</span>
            </div>
            <div class="status-bar-track">
              <div
                class="status-bar-fill"
                :style="{ width: item.pct, background: item.color }"
              />
            </div>
          </div>
        </div>
      </n-card>
    </div>

    <!-- Tab 切换 -->
    <n-card class="tabs-card" :bordered="true">
      <n-tabs type="line" animated default-value="overview">
        <n-tab-pane name="overview" tab="📈 统计概览">
          <div class="tab-section">
            <h3 class="tab-title">各模块用例统计</h3>
            <div class="bar-chart">
              <div v-for="(bar, i) in barData" :key="i" class="bar-item">
                <div class="bar-label">{{ bar.label }}</div>
                <div class="bar-track">
                  <div
                    class="bar-fill"
                    :style="{ width: bar.pct, background: bar.color }"
                  />
                </div>
                <div class="bar-value">{{ bar.count }}</div>
              </div>
            </div>
          </div>
        </n-tab-pane>

        <n-tab-pane name="cases" tab="📋 用例列表">
          <n-table :single-line="false" size="small">
            <thead>
              <tr>
                <th>用例名称</th>
                <th>优先级</th>
                <th>状态</th>
                <th>执行人</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in caseListData" :key="i">
                <td>{{ row.name }}</td>
                <td>
                  <n-tag
                    :type="row.priority === 'P0' ? 'error' : row.priority === 'P1' ? 'warning' : 'default'"
                    size="small"
                    round
                    :bordered="false"
                  >
                    {{ row.priority }}
                  </n-tag>
                </td>
                <td>
                  <n-tag
                    :type="row.status === '通过' ? 'success' : row.status === '失败' ? 'error' : 'warning'"
                    size="small"
                    round
                    :bordered="false"
                  >
                    {{ row.status }}
                  </n-tag>
                </td>
                <td class="text-muted">{{ row.executor }}</td>
              </tr>
            </tbody>
          </n-table>
        </n-tab-pane>

        <n-tab-pane name="defects" tab="🐛 缺陷分布">
          <div class="tab-section">
            <h3 class="tab-title">缺陷等级分布</h3>
            <div class="defect-grid">
              <div v-for="(item, i) in defectData" :key="i" class="defect-card-item" :style="{ borderLeft: `4px solid ${item.color}` }">
                <div class="defect-level">{{ item.level }}</div>
                <div class="defect-count" :style="{ color: item.color }">{{ item.count }}</div>
                <div class="defect-desc">{{ item.desc }}</div>
              </div>
            </div>
          </div>
        </n-tab-pane>
      </n-tabs>
    </n-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import request from '@/shared/api/request'

const message = useMessage()
const loading = ref(true)
const error = ref(false)

/** 报告摘要数据 */
interface ReportSummary {
  total_cases: number
  total_reviews: number
  passed_cases: number
  failed_cases: number
  pass_rate: number
  active_reviews: number
}

const summary = ref<ReportSummary>({
  total_cases: 100,
  total_reviews: 73,
  passed_cases: 73,
  failed_cases: 18,
  pass_rate: 0.73,
  active_reviews: 5,
})

const isEmpty = computed(() => summary.value.total_cases === 0)

async function loadData() {
  loading.value = true
  error.value = false
  try {
    const res = await request.get('/testing/reports/summary')
    if (res.data) {
      summary.value = res.data
    }
  } catch (e) {
    console.error('加载报告摘要失败:', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

// 当前生成时间（动态）
const generationTime = computed(() => {
  return new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
})

// 通过率显示
const passRateDisplay = computed(() => {
  return `${(summary.value.pass_rate * 100).toFixed(0)}%`
})

// AI 评分（基于通过率加权计算）
const aiScore = computed(() => {
  return (summary.value.pass_rate * 10).toFixed(1)
})

// ── 环形图 ──
const ringData = computed(() => {
  const passed = summary.value.passed_cases
  const failed = summary.value.failed_cases
  const blocked = Math.max(0, summary.value.total_cases - passed - failed)
  const total = passed + failed + blocked || 1
  return [
    { label: '通过', value: passed, pct: `${((passed / total) * 100).toFixed(0)}%`, color: '#7BA87D' },
    { label: '失败', value: failed, pct: `${((failed / total) * 100).toFixed(0)}%`, color: '#D4745C' },
    { label: '阻塞', value: blocked, pct: `${((blocked / total) * 100).toFixed(0)}%`, color: '#D4A574' },
  ]
})

const ringGradient = computed(() => {
  const passed = summary.value.passed_cases
  const failed = summary.value.failed_cases
  const blocked = Math.max(0, summary.value.total_cases - passed - failed)
  const total = passed + failed + blocked || 1
  const passDeg = (passed / total) * 360
  const failDeg = (failed / total) * 360
  const p1 = passDeg
  const p2 = passDeg + failDeg
  return `conic-gradient(
    #7BA87D 0deg ${p1}deg,
    #D4745C ${p1}deg ${p2}deg,
    #D4A574 ${p2}deg 360deg
  )`
})

// ── 状态概览 ──
const statusData = computed(() => {
  const blocked = Math.max(0, summary.value.total_cases - summary.value.passed_cases - summary.value.failed_cases)
  const total = summary.value.total_cases || 1
  return [
    { label: '已通过', count: summary.value.passed_cases, pct: `${((summary.value.passed_cases / total) * 100).toFixed(0)}%`, color: '#7BA87D' },
    { label: '已失败', count: summary.value.failed_cases, pct: `${((summary.value.failed_cases / total) * 100).toFixed(0)}%`, color: '#D4745C' },
    { label: '阻塞', count: blocked, pct: `${((blocked / total) * 100).toFixed(0)}%`, color: '#D4A574' },
  ]
})

// ── 柱状图（示例数据） ──
const barData = [
  { label: '用户管理', count: 28, pct: '100%', color: '#C67B5C' },
  { label: '订单系统', count: 24, pct: '85.7%', color: '#D49472' },
  { label: '支付模块', count: 18, pct: '64.3%', color: '#D4A574' },
  { label: '消息推送', count: 14, pct: '50%', color: '#7BA87D' },
  { label: '数据分析', count: 10, pct: '35.7%', color: '#D4745C' },
  { label: '权限管理', count: 6, pct: '21.4%', color: '#8B7355' },
]

// ── 用例列表（示例数据） ──
const caseListData = [
  { name: '用户登录-正常流程', priority: 'P0', status: '通过', executor: '张三' },
  { name: '用户登录-密码错误', priority: 'P1', status: '通过', executor: '张三' },
  { name: '用户登录-账号锁定', priority: 'P1', status: '失败', executor: '李四' },
  { name: '订单创建-正常流程', priority: 'P0', status: '通过', executor: '李四' },
  { name: '订单创建-库存不足', priority: 'P1', status: '阻塞', executor: '王五' },
  { name: '订单取消-退款流程', priority: 'P2', status: '通过', executor: '王五' },
  { name: '支付回调-签名验证', priority: 'P0', status: '失败', executor: '赵六' },
  { name: '消息推送-批量发送', priority: 'P2', status: '通过', executor: '张三' },
  { name: '数据分析-报表导出', priority: 'P3', status: '通过', executor: '赵六' },
  { name: '权限管理-角色分配', priority: 'P1', status: '失败', executor: '李四' },
]

// ── 缺陷分布（示例数据） ──
const defectData = [
  { level: 'Critical', count: 3, color: '#D4745C', desc: '核心功能阻断，需立即修复' },
  { level: 'Major', count: 5, color: '#D4A574', desc: '主要功能异常，影响使用体验' },
  { level: 'Minor', count: 2, color: '#8B7355', desc: '次要问题，可后续优化' },
]

/** 预览报告 — 打开新窗口展示报告摘要 */
function handlePreview() {
  window.open('/#/testing/report-preview', '_blank')
}

/** 导出报告 Excel — 下载后端生成的文件 */
async function handleExport() {
  try {
    const response = await fetch('/api/v1/testing/reports/export', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `测试报告_${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    message.success('报告已导出')
  } catch (e: any) {
    console.error('导出报告失败:', e)
    message.error('导出失败，请稍后重试')
  }
}
</script>

<style scoped>
.page-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

.state-wrap {
  display: flex; justify-content: center; align-items: center;
  min-height: 400px;
}

/* ── 顶部 ── */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #3D2E1F;
  margin: 0;
  letter-spacing: -0.02em;
}
.page-sub {
  font-size: 13px;
  color: #8B7355;
  margin: 6px 0 0;
}
.header-actions {
  display: flex;
  gap: 10px;
}

/* ── 摘要卡片 ── */
.summary-card {
  margin-bottom: 20px;
}
.summary-card :deep(.n-card__content) {
  padding: 20px 24px;
}
.summary-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
}
.summary-item {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  justify-content: center;
}
.summary-icon {
  font-size: 28px;
  line-height: 1;
}
.summary-body {
  display: flex;
  flex-direction: column;
}
.summary-value {
  font-size: 26px;
  font-weight: 700;
  color: #3D2E1F;
  line-height: 1.2;
}
.summary-label {
  font-size: 12px;
  color: #8B7355;
  margin-top: 2px;
}
.summary-divider {
  width: 1px;
  height: 48px;
  background: rgba(180, 150, 120, 0.15);
}

/* ── 两栏 ── */
.row-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 20px;
}

/* ── 环形图 ── */
.ring-chart-wrap {
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 12px 0;
}
.ring-chart {
  flex-shrink: 0;
}
.ring-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ring-center {
  background: #FFFDF9;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.ring-center-value {
  font-size: 22px;
  font-weight: 700;
  color: #3D2E1F;
  line-height: 1.1;
}
.ring-center-label {
  font-size: 11px;
  color: #8B7355;
}
.ring-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}
.ring-legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.ring-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}
.ring-label {
  color: #5C4A38;
  flex: 1;
  font-size: 13px;
}
.ring-value {
  font-weight: 600;
  color: #3D2E1F;
  font-size: 14px;
}
.ring-pct {
  color: #8B7355;
  font-size: 11px;
  min-width: 36px;
  text-align: right;
}

/* ── 状态进度条 ── */
.status-bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
}
.status-bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.status-bar-header {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}
.status-bar-label {
  color: #5C4A38;
}
.status-bar-count {
  font-weight: 600;
  color: #3D2E1F;
}
.status-bar-track {
  height: 10px;
  background: rgba(180, 150, 120, 0.1);
  border-radius: 5px;
  overflow: hidden;
}
.status-bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

/* ── Tabs 卡片 ── */
.tabs-card {
  margin-bottom: 20px;
}
.tab-section {
  padding: 8px 0;
}
.tab-title {
  font-size: 15px;
  font-weight: 600;
  color: #3D2E1F;
  margin: 0 0 16px;
}

/* ── 柱状图 ── */
.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.bar-label {
  width: 80px;
  font-size: 13px;
  color: #5C4A38;
  text-align: right;
  flex-shrink: 0;
}
.bar-track {
  flex: 1;
  height: 22px;
  background: rgba(180, 150, 120, 0.08);
  border-radius: 6px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease;
  min-width: 4px;
}
.bar-value {
  width: 32px;
  font-size: 13px;
  font-weight: 600;
  color: #3D2E1F;
  text-align: right;
}

/* ── 表格 ── */
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
.text-muted {
  color: #8B7355;
}

/* ── 缺陷分布 ── */
.defect-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.defect-card-item {
  background: #FFFDF9;
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 10px;
  padding: 20px;
  text-align: center;
}
.defect-level {
  font-size: 14px;
  font-weight: 600;
  color: #3D2E1F;
  margin-bottom: 8px;
}
.defect-count {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 8px;
}
.defect-desc {
  font-size: 12px;
  color: #8B7355;
}
</style>
