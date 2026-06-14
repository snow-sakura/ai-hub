<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">APP 测试套件</h1>
        <p class="app-page-subtitle">管理移动端自动化测试集合 · 共 {{ suites.length }} 个套件</p>
      </div>
      <div class="header-actions">
        <button class="app-btn app-btn-primary" @click="showAddModal = true">+ 新建套件</button>
      </div>
    </div>

    <div class="suite-grid app-fade-in">
      <div v-for="(s, i) in suites" :key="i" class="suite-card">
        <div class="suite-name">
          <span>{{ s.status === 'active' ? '🟢' : '🟡' }}</span> {{ s.name }}
          <span :class="['app-tag', s.status === 'active' ? 'app-tag-active' : 'app-tag-paused']" style="margin-left:auto">
            {{ s.status === 'active' ? '运行中' : '已暂停' }}
          </span>
        </div>
        <div class="suite-info">关联项目：<strong>{{ s.project }}</strong></div>
        <div class="suite-info">测试用例：<strong>{{ s.cases }}</strong> 个 · 设备：<strong>{{ s.devices }}</strong> 台</div>
        <div class="suite-info">最后执行：<strong>{{ s.lastRun }}</strong></div>
        <div style="display:flex;gap:6px;margin-top:10px;padding-top:10px;border-top:var(--app-border)">
          <button class="app-btn app-btn-ghost app-btn-xs" @click.stop="editSuite(s)">编辑</button>
          <button class="app-btn app-btn-primary app-btn-xs" @click.stop="runSuite(s)">▶ 执行</button>
        </div>
      </div>
    </div>

    <!-- 新建套件弹窗 -->
    <div class="app-modal-overlay" :class="{ active: showAddModal }" @click.self="showAddModal = false">
      <div class="app-modal-box">
        <div class="app-modal-head">
          <h3>📁 新建 APP 测试套件</h3>
          <button class="app-modal-close" @click="showAddModal = false">✕</button>
        </div>
        <div class="app-modal-body">
          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">套件名称</label>
          <input v-model="newSuite.name" class="app-input" style="margin-bottom:12px" placeholder="例如：登录模块回归">

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">关联项目</label>
          <select v-model="newSuite.project" class="app-input" style="margin-bottom:12px">
            <option>电商APP</option>
            <option>金融APP</option>
            <option>社交APP</option>
          </select>

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">目标平台</label>
          <div style="display:flex;gap:12px;margin-bottom:12px">
            <label style="display:flex;align-items:center;gap:4px;font-size:13px;cursor:pointer">
              <input type="checkbox" v-model="newSuite.platforms.android" style="accent-color:#C67B5C"> Android
            </label>
            <label style="display:flex;align-items:center;gap:4px;font-size:13px;cursor:pointer">
              <input type="checkbox" v-model="newSuite.platforms.ios" style="accent-color:#C67B5C"> iOS
            </label>
          </div>

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">指定设备</label>
          <select v-model="newSuite.device" class="app-input">
            <option value="">全部设备</option>
            <option>iPhone 15</option>
            <option>Pixel 7</option>
            <option>Galaxy S23</option>
          </select>
        </div>
        <div class="app-modal-footer">
          <button class="app-btn app-btn-secondary" @click="showAddModal = false">取消</button>
          <button class="app-btn app-btn-primary" @click="createSuite">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const showAddModal = ref(false)

const newSuite = reactive({
  name: '',
  project: '电商APP',
  platforms: { android: true, ios: true },
  device: ''
})

const suites = ref([
  { name: '登录模块回归', project: '电商APP', cases: 12, devices: 3, lastRun: '2026-06-12 14:00', status: 'active' },
  { name: '支付流程验证', project: '金融APP', cases: 8, devices: 2, lastRun: '2026-06-12 11:00', status: 'active' },
  { name: '注册流程冒烟', project: '电商APP', cases: 6, devices: 2, lastRun: '2026-06-12 09:30', status: 'active' },
  { name: '首页加载性能', project: '电商APP', cases: 5, devices: 3, lastRun: '2026-06-11 16:00', status: 'paused' },
  { name: '搜索功能验证', project: '电商APP', cases: 10, devices: 2, lastRun: '2026-06-10 15:00', status: 'active' },
  { name: '个人中心冒烟', project: '社交APP', cases: 7, devices: 2, lastRun: '2026-06-09 14:00', status: 'paused' }
])

function editSuite(s) {
  ElMessage.info(`编辑套件: ${s.name}`)
}

function runSuite(s) {
  ElMessage.info(`开始执行套件: ${s.name}`)
}

function createSuite() {
  if (!newSuite.name) {
    ElMessage.warning('请输入套件名称')
    return
  }
  suites.value.push({
    name: newSuite.name,
    project: newSuite.project,
    cases: 0,
    devices: newSuite.device ? 1 : 0,
    lastRun: '-',
    status: 'active'
  })
  showAddModal.value = false
  ElMessage.success('套件已创建')
}
</script>

<style scoped>
.suite-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.suite-card {
  background: var(--app-card-bg);
  border: var(--app-border);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.suite-card:hover {
  box-shadow: var(--app-shadow);
  transform: translateY(-1px);
}

.suite-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.suite-info {
  font-size: 12px;
  color: var(--app-text-muted);
  margin-bottom: 4px;
}

.suite-info strong {
  color: var(--app-text-secondary);
}

@media (max-width: 900px) {
  .suite-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .suite-grid { grid-template-columns: 1fr; }
}
</style>
