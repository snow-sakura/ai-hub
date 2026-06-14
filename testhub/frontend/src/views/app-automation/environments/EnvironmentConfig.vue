<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">APP 环境配置</h1>
        <p class="app-page-subtitle">管理移动端测试环境 · 共 {{ environments.length }} 个环境</p>
      </div>
      <div class="header-actions">
        <button class="app-btn app-btn-primary" @click="showAddModal = true">+ 新建环境</button>
      </div>
    </div>

    <div class="env-grid app-fade-in">
      <div v-for="env in environments" :key="env.name" class="env-card">
        <div class="env-head" @click="env.expanded = !env.expanded">
          <div class="env-icon" :style="{ background: env.bg, color: env.color }">{{ env.icon }}</div>
          <div style="flex:1">
            <div style="display:flex;align-items:center;gap:8px;font-weight:600;font-size:14px;color:var(--app-text)">
              {{ env.name }}
              <span :class="['app-tag', env.status === 'active' ? 'app-tag-active' : 'app-tag-offline']">
                {{ env.status === 'active' ? '启用' : '停用' }}
              </span>
            </div>
            <div style="font-size:12px;color:var(--app-text-muted);margin-top:2px">{{ env.desc }}</div>
          </div>
          <span style="font-size:12px;color:var(--app-text-muted)">{{ env.expanded ? '🔼' : '🔽' }}</span>
        </div>
        <div v-show="env.expanded" class="env-body">
          <div class="env-info-row">
            <span class="env-label">APP</span>
            <span class="env-value">{{ env.app }}</span>
          </div>
          <div class="env-info-row">
            <span class="env-label">Appium Server</span>
            <span class="env-value">{{ env.server }}</span>
          </div>
          <div class="env-info-row">
            <span class="env-label">平台</span>
            <span class="env-value">{{ env.platform }}</span>
          </div>
          <div class="env-vars-section">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px">
              <span style="font-size:12px;font-weight:600;color:var(--app-text-secondary)">环境变量</span>
              <button class="app-btn app-btn-ghost app-btn-xs" @click.stop="addVariable(env)">+ 添加</button>
            </div>
            <table class="kv-table">
              <thead>
                <tr><th>变量名</th><th>值</th><th>操作</th></tr>
              </thead>
              <tbody>
                <tr v-for="(v, vi) in env.vars" :key="vi">
                  <td>{{ v.name }}</td>
                  <td style="font-family:var(--app-font-mono);font-size:12px;color:var(--app-text-muted)">{{ v.value }}</td>
                  <td><button class="app-btn app-btn-ghost app-btn-xs" @click.stop="env.vars.splice(vi, 1)">✕</button></td>
                </tr>
              </tbody>
            </table>
            <div style="margin-top:8px;display:flex;gap:6px">
              <button class="app-btn app-btn-ghost app-btn-xs" @click.stop="saveEnv(env)">💾 保存</button>
              <button class="app-btn app-btn-ghost app-btn-xs" @click.stop="testConnection(env)">📋 测试连接</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建环境弹窗 -->
    <div class="app-modal-overlay" :class="{ active: showAddModal }" @click.self="showAddModal = false">
      <div class="app-modal-box">
        <div class="app-modal-head">
          <h3>📱 新建 APP 环境</h3>
          <button class="app-modal-close" @click="showAddModal = false">✕</button>
        </div>
        <div class="app-modal-body">
          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">环境名称</label>
          <input v-model="formData.name" class="app-input" style="margin-bottom:12px" placeholder="例如：测试环境">

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">APP 包名 (Android)</label>
          <input v-model="formData.androidPackage" class="app-input app-input-mono" style="margin-bottom:12px" placeholder="com.example.app">

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">APP Bundle ID (iOS)</label>
          <input v-model="formData.iosBundleId" class="app-input app-input-mono" style="margin-bottom:12px" placeholder="com.example.app">

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">Appium Server URL</label>
          <input v-model="formData.serverUrl" class="app-input app-input-mono" style="margin-bottom:12px" placeholder="http://localhost:4723">

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">平台版本</label>
          <select v-model="formData.platform" class="app-input" style="margin-bottom:12px">
            <option>Android 14</option>
            <option>Android 13</option>
            <option>iOS 17</option>
            <option>iOS 16</option>
          </select>

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">备注</label>
          <textarea v-model="formData.remark" class="app-textarea" placeholder="环境描述..."></textarea>
        </div>
        <div class="app-modal-footer">
          <button class="app-btn app-btn-secondary" @click="showAddModal = false">取消</button>
          <button class="app-btn app-btn-primary" @click="createEnvironment">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const showAddModal = ref(false)

const formData = reactive({
  name: '',
  androidPackage: 'com.example.app',
  iosBundleId: 'com.example.app',
  serverUrl: 'http://localhost:4723',
  platform: 'Android 14',
  remark: ''
})

const environments = ref([
  {
    name: '开发环境', app: 'com.example.app.dev', server: 'http://localhost:4723',
    platform: 'Android 14', status: 'active', desc: '开发自测环境',
    icon: '🔧', color: '#5B8DEF', bg: 'rgba(91,141,239,0.12)',
    expanded: false,
    vars: [
      { name: 'APP_PACKAGE', value: 'com.example.app.dev' },
      { name: 'APPIUM_URL', value: 'http://localhost:4723' },
      { name: 'PLATFORM', value: 'Android' }
    ]
  },
  {
    name: '测试环境', app: 'com.example.app.test', server: 'http://192.168.1.100:4723',
    platform: 'Android 14 + iOS 17', status: 'active', desc: 'QA 测试执行环境',
    icon: '🧪', color: 'var(--app-success)', bg: 'rgba(123,168,125,0.12)',
    expanded: false,
    vars: [
      { name: 'APP_PACKAGE', value: 'com.example.app.test' },
      { name: 'APPIUM_URL', value: 'http://192.168.1.100:4723' },
      { name: 'PLATFORM', value: 'Android' }
    ]
  },
  {
    name: '预发布环境', app: 'com.example.app.staging', server: 'http://192.168.1.101:4723',
    platform: 'iOS 17', status: 'active', desc: '上线前验证环境',
    icon: '🚀', color: '#D4A574', bg: 'rgba(212,165,116,0.12)',
    expanded: false,
    vars: [
      { name: 'APP_PACKAGE', value: 'com.example.app.staging' },
      { name: 'APPIUM_URL', value: 'http://192.168.1.101:4723' },
      { name: 'PLATFORM', value: 'iOS' }
    ]
  },
  {
    name: '生产环境', app: 'com.example.app', server: 'http://10.0.0.1:4723',
    platform: 'Android 13', status: 'inactive', desc: '线上巡检（仅只读操作）',
    icon: '🔒', color: 'var(--app-danger)', bg: 'rgba(212,116,92,0.12)',
    expanded: false,
    vars: [
      { name: 'APP_PACKAGE', value: 'com.example.app' },
      { name: 'APPIUM_URL', value: 'http://10.0.0.1:4723' },
      { name: 'PLATFORM', value: 'Android' }
    ]
  }
])

function addVariable(env) {
  env.vars.push({ name: 'NEW_VAR', value: 'value' })
}

function saveEnv(env) {
  ElMessage.success(`环境「${env.name}」已保存`)
}

function testConnection(env) {
  ElMessage.info(`正在测试 ${env.server} 连接...`)
  setTimeout(() => ElMessage.success('连接成功'), 1000)
}

function createEnvironment() {
  if (!formData.name) {
    ElMessage.warning('请输入环境名称')
    return
  }
  environments.value.push({
    name: formData.name,
    app: formData.androidPackage,
    server: formData.serverUrl,
    platform: formData.platform,
    status: 'active',
    desc: formData.remark || '新建环境',
    icon: '🧪',
    color: 'var(--app-success)',
    bg: 'rgba(123,168,125,0.12)',
    expanded: false,
    vars: [
      { name: 'APP_PACKAGE', value: formData.androidPackage },
      { name: 'APPIUM_URL', value: formData.serverUrl },
      { name: 'PLATFORM', value: formData.platform }
    ]
  })
  showAddModal.value = false
  ElMessage.success('环境已创建')
}
</script>

<style scoped>
.env-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.env-card {
  background: var(--app-card-bg);
  border: var(--app-border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.env-card:hover {
  box-shadow: var(--app-shadow);
}

.env-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  cursor: pointer;
  border-bottom: var(--app-border);
}

.env-head:hover {
  background: var(--app-primary-bg);
}

.env-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.env-body {
  padding: 14px 16px;
}

.env-info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.env-label {
  color: var(--app-text-muted);
}

.env-value {
  color: var(--app-text);
  font-weight: 500;
  font-family: var(--app-font-mono);
  font-size: 12px;
}

.env-vars-section {
  margin-top: 10px;
  padding-top: 10px;
  border-top: var(--app-border);
}

.kv-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.kv-table th {
  text-align: left;
  padding: 8px 10px;
  font-weight: 600;
  color: var(--app-text-secondary);
  border-bottom: var(--app-border);
  font-size: 12px;
  background: var(--app-sidebar-bg);
}

.kv-table td {
  padding: 8px 10px;
  border-bottom: var(--app-border);
  color: var(--app-text);
  font-size: 12px;
}

.app-textarea {
  width: 100%;
  height: 60px;
  border: var(--app-border);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 13px;
  color: var(--app-text);
  font-family: var(--app-font-mono);
  background: var(--app-card-bg);
  outline: none;
  resize: vertical;
}

.app-textarea:focus {
  border-color: var(--app-primary);
}

@media (max-width: 900px) {
  .env-grid {
    grid-template-columns: 1fr;
  }
}
</style>
