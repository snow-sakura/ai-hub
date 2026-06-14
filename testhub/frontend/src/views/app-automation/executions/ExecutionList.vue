<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">APP 执行记录</h1>
        <p class="app-page-subtitle">查看移动端自动化测试执行历史</p>
      </div>
      <div class="header-actions">
        <select v-model="filterSuite" class="app-input" style="width:160px;height:34px">
          <option value="">全部套件</option>
          <option v-for="s in suiteOptions" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
    </div>

    <div class="app-card app-fade-in">
      <div class="app-card-body" style="padding:0">
        <div style="overflow-x:auto">
          <table class="app-data-table">
            <thead>
              <tr><th>套件名称</th><th>设备</th><th>系统</th><th>总数</th><th>通过</th><th>失败</th><th>耗时</th><th>状态</th><th>操作</th></tr>
            </thead>
            <tbody>
              <tr v-for="(rec, i) in filteredRecords" :key="i">
                <td style="font-weight:600">{{ rec.suite }}</td>
                <td>{{ rec.device }}</td>
                <td>{{ rec.os }}</td>
                <td>{{ rec.total }}</td>
                <td>{{ rec.passed }}</td>
                <td>{{ rec.failed }}</td>
                <td>{{ rec.duration }}</td>
                <td><span :class="['app-tag', getStatusClass(rec.status)]">{{ rec.status }}</span></td>
                <td>
                  <button class="app-btn app-btn-ghost app-btn-xs" @click="showLogDrawer(rec)">📋 日志</button>
                  <button class="app-btn app-btn-ghost app-btn-xs" @click="$router.push('/app-automation/reports')">📊 报告</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 日志抽屉 -->
    <div class="app-drawer-overlay" :class="{ active: drawerVisible }" @click.self="drawerVisible = false">
      <div class="app-drawer">
        <div class="app-drawer-head">
          <h3>📋 执行日志</h3>
          <button class="app-drawer-close" @click="drawerVisible = false">✕</button>
        </div>
        <div class="app-drawer-body">
          <div v-if="currentLog" style="margin-bottom:14px;display:flex;align-items:center;gap:12px;padding:10px 14px;background:var(--app-primary-bg);border-radius:8px;font-size:13px">
            <span style="font-weight:600">{{ currentLog.suite }}</span>
            <span :class="['app-tag', getStatusClass(currentLog.status)]">{{ currentLog.status }}</span>
            <span style="color:var(--app-text-muted)">{{ currentLog.device }} · {{ currentLog.os }} · {{ currentLog.duration }}</span>
          </div>
          <div v-for="(log, i) in logEntries" :key="i" class="log-item">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-icon">{{ log.icon }}</span>
            <span class="log-content">
              <span :class="log.result === '通过' ? 'pass' : 'fail'">{{ log.result }}</span>
              {{ log.message }}
            </span>
          </div>
          <div style="margin-top:14px;display:flex;gap:8px">
            <button class="app-btn app-btn-primary app-btn-sm" @click="rerunExecution">🔄 重新执行</button>
            <button class="app-btn app-btn-ghost app-btn-sm" @click="debugExecution">🔧 调试</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const filterSuite = ref('')
const drawerVisible = ref(false)
const currentLog = ref(null)

const suiteOptions = ['登录模块回归', '支付流程验证', '搜索功能验证']

const records = ref([
  { suite: '登录模块回归', device: 'iPhone 15', os: 'iOS 17', total: 12, passed: 11, failed: 1, duration: '2m18s', status: '通过' },
  { suite: '支付流程验证', device: 'Pixel 7', os: 'Android 14', total: 8, passed: 7, failed: 1, duration: '1m45s', status: '通过' },
  { suite: '注册流程冒烟', device: 'Galaxy S23', os: 'Android 13', total: 6, passed: 6, failed: 0, duration: '58s', status: '通过' },
  { suite: '首页加载性能', device: 'iPhone 15', os: 'iOS 17', total: 5, passed: 3, failed: 2, duration: '3m12s', status: '失败' },
  { suite: '搜索功能验证', device: 'Pixel 7', os: 'Android 14', total: 10, passed: 9, failed: 1, duration: '2m05s', status: '通过' }
])

const logEntries = ref([
  { time: '14:00:01', icon: '📱', result: '', message: '启动 APP — 电商APP' },
  { time: '14:00:05', icon: '✅', result: '通过', message: '点击"我的"Tab (0.8s)' },
  { time: '14:00:08', icon: '✅', result: '通过', message: '输入用户名 (1.2s)' },
  { time: '14:00:11', icon: '✅', result: '通过', message: '输入密码 (0.9s)' },
  { time: '14:00:14', icon: '✅', result: '通过', message: '点击登录按钮 (1.5s)' },
  { time: '14:00:18', icon: '✅', result: '通过', message: '验证个人中心显示 (2.1s)' },
  { time: '14:00:22', icon: '✅', result: '通过', message: '验证用户名匹配 (0.5s)' },
  { time: '14:00:25', icon: '✅', result: '通过', message: '验证头像加载 (1.3s)' },
  { time: '14:00:28', icon: '✅', result: '通过', message: '验证订单数量 (0.7s)' },
  { time: '14:00:31', icon: '✅', result: '通过', message: '验证退出登录按钮 (0.6s)' },
  { time: '14:00:34', icon: '✅', result: '通过', message: '验证设置入口 (1.0s)' },
  { time: '14:00:37', icon: '✅', result: '通过', message: '验证通知开关 (0.8s)' },
  { time: '14:00:40', icon: '❌', result: '失败', message: '验证客服入口 — 元素未找到: content-desc="customer_service" (3.0s)' }
])

const filteredRecords = computed(() => {
  if (!filterSuite.value) return records.value
  return records.value.filter(r => r.suite === filterSuite.value)
})

function getStatusClass(status) {
  if (status === '通过') return 'app-tag-pass'
  if (status === '失败') return 'app-tag-fail'
  if (status === '执行中') return 'app-tag-running'
  return 'app-tag-pending'
}

function showLogDrawer(rec) {
  currentLog.value = rec
  drawerVisible.value = true
}

function rerunExecution() {
  ElMessage.info('重新执行中...')
  drawerVisible.value = false
}

function debugExecution() {
  ElMessage.info('调试模式已启动')
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
