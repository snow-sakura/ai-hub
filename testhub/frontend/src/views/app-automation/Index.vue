<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">📱 APP 自动化</h1>
        <p class="app-page-subtitle">移动端 APP 自动化测试 · 覆盖 10 个功能模块</p>
      </div>
    </div>

    <div class="app-stats-row app-fade-in">
      <div class="app-stat-card">
        <div class="app-stat-value">36</div>
        <div class="app-stat-label">测试用例</div>
      </div>
      <div class="app-stat-card">
        <div class="app-stat-value">428</div>
        <div class="app-stat-label">总执行次数</div>
      </div>
      <div class="app-stat-card">
        <div class="app-stat-value">88.6%</div>
        <div class="app-stat-label">通过率</div>
      </div>
      <div class="app-stat-card">
        <div class="app-stat-value">8</div>
        <div class="app-stat-label">注册设备</div>
      </div>
    </div>

    <div class="mod-grid app-fade-in">
      <div v-for="mod in modules" :key="mod.name" class="mod-entry" @click="navigate(mod.path)">
        <div class="mod-entry-icon" :style="{ background: mod.bg, color: mod.color }">{{ mod.icon }}</div>
        <div class="mod-entry-name">{{ mod.name }}</div>
        <div class="mod-entry-desc">{{ mod.desc }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const modules = [
  { name: '数据看板', icon: '📊', color: 'var(--app-primary)', bg: 'rgba(198,123,92,0.12)', desc: 'APP 测试执行统计与趋势', path: '/app-automation/dashboard' },
  { name: '测试用例', icon: '📋', color: '#5B8DEF', bg: 'rgba(91,141,239,0.12)', desc: 'APP 操作步骤编排', path: '/app-automation/test-cases' },
  { name: '元素管理', icon: '🔧', color: 'var(--app-success)', bg: 'rgba(123,168,125,0.12)', desc: '原生元素定位管理', path: '/app-automation/elements' },
  { name: '用例录制', icon: '⏺️', color: 'var(--app-danger)', bg: 'rgba(212,116,92,0.12)', desc: 'APP 操作录制与回放', path: '/app-automation/recorder' },
  { name: '测试套件', icon: '📦', color: '#B8860B', bg: 'rgba(212,165,116,0.12)', desc: 'APP 套件与多机编排', path: '/app-automation/test-suites' },
  { name: '执行记录', icon: '▶️', color: '#5B8DEF', bg: 'rgba(91,141,239,0.12)', desc: '执行历史与日志调试', path: '/app-automation/executions' },
  { name: '测试报告', icon: '📈', color: 'var(--app-success)', bg: 'rgba(123,168,125,0.12)', desc: '跨平台报告分析', path: '/app-automation/reports' },
  { name: '设备管理', icon: '📱', color: 'var(--app-text-muted)', bg: 'rgba(180,150,120,0.12)', desc: '真机与模拟器管理', path: '/app-automation/devices' },
  { name: '定时任务', icon: '⏰', color: 'var(--app-danger)', bg: 'rgba(212,116,92,0.12)', desc: 'APP 自动化定时回归', path: '/app-automation/scheduled-tasks' },
  { name: '通知配置', icon: '🔔', color: 'var(--app-success)', bg: 'rgba(123,168,125,0.12)', desc: '多渠道告警通知设置', path: '/app-automation/notifications' }
]

function navigate(path) {
  router.push(path)
}
</script>

<style scoped>
.mod-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.mod-entry {
  background: var(--app-card-bg);
  border: var(--app-border);
  border-radius: 12px;
  padding: 18px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
  cursor: pointer;
}

.mod-entry:hover {
  box-shadow: var(--app-shadow);
  border-color: var(--app-primary-light);
  transform: translateY(-2px);
}

.mod-entry-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-bottom: 10px;
}

.mod-entry-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text);
  margin-bottom: 4px;
}

.mod-entry-desc {
  font-size: 12px;
  color: var(--app-text-muted);
}

@media (max-width: 1000px) {
  .mod-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 768px) {
  .mod-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
