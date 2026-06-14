<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">APP 测试报告</h1>
        <p class="app-page-subtitle">登录模块回归 · 2026-06-12 14:30 · iPhone 15 · iOS 17</p>
      </div>
      <div class="header-actions">
        <button class="app-btn app-btn-secondary" @click="regenerateReport">🔄 重新生成</button>
        <button class="app-btn app-btn-primary" @click="exportReport">📥 导出</button>
      </div>
    </div>

    <div class="app-card app-fade-in">
      <div class="app-card-body" style="padding:0">
        <div class="summary-row">
          <div class="summary-item">
            <span class="summary-icon">📋</span>
            <div class="summary-body">
              <span class="summary-value">{{ summary.totalCases }}</span>
              <span class="summary-label">总用例数</span>
            </div>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-item">
            <span class="summary-icon">✅</span>
            <div class="summary-body">
              <span class="summary-value">{{ summary.passRate }}%</span>
              <span class="summary-label">通过率</span>
            </div>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-item">
            <span class="summary-icon">❌</span>
            <div class="summary-body">
              <span class="summary-value">{{ summary.failedCount }}</span>
              <span class="summary-label">失败用例</span>
            </div>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-item">
            <span class="summary-icon">⏱️</span>
            <div class="summary-body">
              <span class="summary-value">{{ summary.duration }}</span>
              <span class="summary-label">总耗时</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="app-row-2col app-fade-in">
      <div class="app-card">
        <div class="app-card-header">📊 平台对比</div>
        <div class="app-card-body">
          <div class="app-bar-chart">
            <div class="app-bar-item">
              <span class="app-bar-label">iOS</span>
              <div class="app-bar-track"><div class="app-bar-fill" style="background:var(--app-success);width:91.7%"></div></div>
              <span class="app-bar-value">91.7%</span>
            </div>
            <div class="app-bar-item">
              <span class="app-bar-label">Android</span>
              <div class="app-bar-track"><div class="app-bar-fill" style="background:var(--app-accent);width:85%"></div></div>
              <span class="app-bar-value">85.0%</span>
            </div>
          </div>
        </div>
      </div>
      <div class="app-card">
        <div class="app-card-header">📊 失败类型分布</div>
        <div class="app-card-body">
          <div class="app-bar-chart">
            <div class="app-bar-item">
              <span class="app-bar-label">元素未找到</span>
              <div class="app-bar-track"><div class="app-bar-fill" style="background:var(--app-danger);width:50%"></div></div>
              <span class="app-bar-value">50%</span>
            </div>
            <div class="app-bar-item">
              <span class="app-bar-label">断言失败</span>
              <div class="app-bar-track"><div class="app-bar-fill" style="background:var(--app-accent);width:30%"></div></div>
              <span class="app-bar-value">30%</span>
            </div>
            <div class="app-bar-item">
              <span class="app-bar-label">超时</span>
              <div class="app-bar-track"><div class="app-bar-fill" style="background:var(--app-info);width:20%"></div></div>
              <span class="app-bar-value">20%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="app-card app-fade-in">
      <div class="app-card-header">📋 失败用例详情</div>
      <div class="app-card-body" style="padding:0">
        <div style="overflow-x:auto">
          <table class="app-data-table">
            <thead>
              <tr><th>用例名称</th><th>设备</th><th>失败步骤</th><th>错误信息</th><th>截图</th></tr>
            </thead>
            <tbody>
              <tr v-for="(fc, i) in failedCases" :key="i">
                <td style="font-weight:600">{{ fc.name }}</td>
                <td>{{ fc.device }}</td>
                <td>{{ fc.step }}</td>
                <td style="color:var(--app-danger);font-size:12px;font-family:var(--app-font-mono)">{{ fc.error }}</td>
                <td><button class="app-btn app-btn-ghost app-btn-xs" @click="viewScreenshot">📸</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const summary = ref({ totalCases: 12, passRate: 91.7, failedCount: 1, duration: '2m18s' })

const failedCases = ref([
  { name: '验证客服入口', device: 'iPhone 15', step: '第 12 步：验证客服入口', error: 'NoSuchElementError: content-desc="customer_service"' }
])

function regenerateReport() {
  ElMessage.info('重新生成报告中...')
}

function exportReport() {
  ElMessage.info('报告导出中')
}

function viewScreenshot() {
  ElMessage.info('查看截图')
}
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
