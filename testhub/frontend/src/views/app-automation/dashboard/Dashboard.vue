<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">APP 自动化测试</h1>
        <p class="app-page-subtitle">移动端自动化测试数据概览 · 最后更新：{{ lastUpdateTime }}</p>
      </div>
      <div class="header-actions">
        <button class="app-btn app-btn-primary" @click="$router.push('/app-automation/test-cases')">+ 新建用例</button>
      </div>
    </div>

    <div class="app-stats-row app-fade-in">
      <div class="app-stat-card">
        <div class="app-stat-icon" style="background:rgba(91,141,239,0.12);color:var(--app-info)">📱</div>
        <div class="app-stat-body">
          <div class="app-stat-value">{{ stats.testCases }}</div>
          <div class="app-stat-label">APP 用例数</div>
          <div class="app-stat-change stat-up">↑ 12% 较上周</div>
        </div>
      </div>
      <div class="app-stat-card">
        <div class="app-stat-icon" style="background:rgba(123,168,125,0.12);color:var(--app-success)">▶️</div>
        <div class="app-stat-body">
          <div class="app-stat-value">{{ stats.totalExecutions }}</div>
          <div class="app-stat-label">总执行次数</div>
          <div class="app-stat-change stat-up">↑ 8% 较上周</div>
        </div>
      </div>
      <div class="app-stat-card">
        <div class="app-stat-icon" style="background:rgba(212,165,116,0.12);color:#B8860B">✅</div>
        <div class="app-stat-body">
          <div class="app-stat-value">{{ stats.passRate }}%</div>
          <div class="app-stat-label">通过率</div>
          <div class="app-stat-change stat-down">↓ 2.1% 较上周</div>
        </div>
      </div>
      <div class="app-stat-card">
        <div class="app-stat-icon" style="background:rgba(212,116,92,0.12);color:var(--app-danger)">📟</div>
        <div class="app-stat-body">
          <div class="app-stat-value">{{ stats.devices }}</div>
          <div class="app-stat-label">设备数</div>
          <div class="app-stat-change stat-up">↑ 2 较上周</div>
        </div>
      </div>
    </div>

    <div class="app-row-2col app-fade-in">
      <div class="app-card">
        <div class="app-card-header">📈 近 7 日执行趋势</div>
        <div class="app-card-body">
          <div class="app-chart-bar">
            <div v-for="(day, i) in trendData" :key="i" class="app-chart-col">
              <div class="bar" :style="{ background: 'var(--app-primary)', height: day.height + '%' }"></div>
              <span class="day-label">{{ day.label }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="app-card">
        <div class="app-card-header">📊 设备分布</div>
        <div class="app-card-body">
          <div class="app-bar-chart">
            <div class="app-bar-item">
              <span class="app-bar-label">Android</span>
              <div class="app-bar-track"><div class="app-bar-fill" style="background:#7BA87D;width:55%"></div></div>
              <span class="app-bar-value">55%</span>
            </div>
            <div class="app-bar-item">
              <span class="app-bar-label">iOS</span>
              <div class="app-bar-track"><div class="app-bar-fill" style="background:var(--app-primary);width:35%"></div></div>
              <span class="app-bar-value">35%</span>
            </div>
            <div class="app-bar-item">
              <span class="app-bar-label">模拟器</span>
              <div class="app-bar-track"><div class="app-bar-fill" style="background:var(--app-accent);width:10%"></div></div>
              <span class="app-bar-value">10%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="app-card app-fade-in">
      <div class="app-card-header">📋 最近执行记录</div>
      <div style="overflow-x:auto">
        <table class="app-data-table">
          <thead>
            <tr><th>套件名称</th><th>设备</th><th>系统</th><th>用例数</th><th>通过</th><th>失败</th><th>耗时</th><th>状态</th></tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in recentExecutions" :key="i">
              <td style="font-weight:600;cursor:pointer" @click="$router.push('/app-automation/reports')">{{ row.suite }}</td>
              <td>{{ row.device }}</td>
              <td>{{ row.os }}</td>
              <td>{{ row.total }}</td>
              <td>{{ row.passed }}</td>
              <td>{{ row.failed }}</td>
              <td>{{ row.duration }}</td>
              <td><span :class="['app-tag', row.status === '通过' ? 'app-tag-pass' : 'app-tag-fail']">{{ row.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const stats = ref({ testCases: 36, totalExecutions: 428, passRate: 88.6, devices: 8 })
const lastUpdateTime = ref(new Date().toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }))

const trendData = [
  { label: '06-06', height: 60 },
  { label: '06-07', height: 45 },
  { label: '06-08', height: 70 },
  { label: '06-09', height: 55 },
  { label: '06-10', height: 80 },
  { label: '06-11', height: 65 },
  { label: '06-12', height: 90 }
]

const recentExecutions = [
  { suite: '登录模块回归', device: 'iPhone 15', os: 'iOS 17', total: 12, passed: 11, failed: 1, duration: '2m18s', status: '通过' },
  { suite: '支付流程验证', device: 'Pixel 7', os: 'Android 14', total: 8, passed: 7, failed: 1, duration: '1m45s', status: '通过' },
  { suite: '注册流程冒烟', device: 'Galaxy S23', os: 'Android 13', total: 6, passed: 6, failed: 0, duration: '58s', status: '通过' },
  { suite: '首页加载性能', device: 'iPhone 15', os: 'iOS 17', total: 5, passed: 3, failed: 2, duration: '3m12s', status: '失败' },
  { suite: '搜索功能验证', device: 'Pixel 7', os: 'Android 14', total: 10, passed: 9, failed: 1, duration: '2m05s', status: '通过' }
]
</script>

<style scoped>
.app-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.app-data-table th {
  text-align: left;
  padding: 10px 12px;
  font-weight: 600;
  color: var(--app-text-secondary);
  border-bottom: var(--app-border);
  white-space: nowrap;
  background: var(--app-sidebar-bg);
  font-size: 12px;
}

.app-data-table td {
  padding: 10px 12px;
  border-bottom: var(--app-border);
  color: var(--app-text);
}

.app-data-table tr:nth-child(even) td {
  background: rgba(180, 150, 120, 0.03);
}

.app-data-table tr:hover td {
  background: var(--app-primary-bg);
}
</style>
