<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">设备管理</h1>
        <p class="app-page-subtitle">管理已接入的移动设备 · 共 {{ devices.length }} 台设备</p>
      </div>
      <div class="header-actions">
        <button class="app-btn app-btn-secondary" @click="showAddModal = true">+ 添加设备</button>
        <button class="app-btn app-btn-primary" @click="refreshStatus">🔄 刷新状态</button>
      </div>
    </div>

    <div class="device-grid app-fade-in">
      <div v-for="(d, i) in devices" :key="i" class="device-card">
        <div class="device-icon" :style="{ background: d.bg }">{{ d.icon }}</div>
        <div class="device-name">{{ d.name }}</div>
        <div class="device-info">{{ d.os }} · {{ d.res }}</div>
        <div class="device-tags">
          <span :class="['app-tag', getDeviceStatusClass(d.status)]">{{ getDeviceStatusText(d.status) }}</span>
          <span :class="['app-tag', d.platform === 'ios' ? 'app-tag-ios' : 'app-tag-android']">
            {{ d.platform === 'ios' ? 'iOS' : 'Android' }}
          </span>
        </div>
        <div class="device-footer">
          <span :title="'UDID: ' + d.udid" style="font-family:var(--app-font-mono)">{{ d.udid.substring(0, 8) }}...</span>
          <span>{{ d.lastUsed }}</span>
        </div>
      </div>
    </div>

    <!-- 添加设备弹窗 -->
    <div class="app-modal-overlay" :class="{ active: showAddModal }" @click.self="showAddModal = false">
      <div class="app-modal-box">
        <div class="app-modal-head">
          <h3>📱 添加设备</h3>
          <button class="app-modal-close" @click="showAddModal = false">✕</button>
        </div>
        <div class="app-modal-body">
          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">设备名称</label>
          <input v-model="newDevice.name" class="app-input" style="margin-bottom:12px" placeholder="例如：iPhone 15 Pro">

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">平台</label>
          <select v-model="newDevice.platform" class="app-input" style="margin-bottom:12px">
            <option value="ios">iOS</option>
            <option value="android">Android</option>
          </select>

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">系统版本</label>
          <input v-model="newDevice.os" class="app-input" style="margin-bottom:12px" placeholder="例如：17.0">

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">设备 UDID / 序列号</label>
          <input v-model="newDevice.udid" class="app-input app-input-mono" style="margin-bottom:12px" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx">

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">Appium 端口</label>
          <input v-model.number="newDevice.port" type="number" class="app-input" value="4723">
        </div>
        <div class="app-modal-footer">
          <button class="app-btn app-btn-secondary" @click="showAddModal = false">取消</button>
          <button class="app-btn app-btn-primary" @click="addDevice">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const showAddModal = ref(false)

const newDevice = reactive({
  name: '', platform: 'ios', os: '', udid: '', port: 4723
})

const devices = ref([
  { name: 'iPhone 15 Pro', os: 'iOS 17.0', udid: '00008110-xxxxxxxxxxxx', res: '1179×2556', status: 'online', platform: 'ios', lastUsed: '2026-06-12 14:30', icon: '📱', bg: 'rgba(60,40,20,0.08)' },
  { name: 'iPhone 15', os: 'iOS 17.0', udid: '00008110-yyyyyyyyyyyy', res: '1179×2556', status: 'online', platform: 'ios', lastUsed: '2026-06-12 13:00', icon: '📱', bg: 'rgba(60,40,20,0.08)' },
  { name: 'iPhone 13', os: 'iOS 16.5', udid: '00008110-zzzzzzzzzzzz', res: '1170×2532', status: 'busy', platform: 'ios', lastUsed: '2026-06-12 14:00', icon: '📱', bg: 'rgba(60,40,20,0.08)' },
  { name: 'Pixel 7', os: 'Android 14', udid: 'ABCDEF123456', res: '1080×2400', status: 'online', platform: 'android', lastUsed: '2026-06-12 12:30', icon: '🤖', bg: 'rgba(123,168,125,0.12)' },
  { name: 'Galaxy S23', os: 'Android 13', udid: 'GHIJKL789012', res: '1080×2340', status: 'online', platform: 'android', lastUsed: '2026-06-12 11:00', icon: '🤖', bg: 'rgba(123,168,125,0.12)' },
  { name: 'Xiaomi 14', os: 'Android 14', udid: 'MNOPQR345678', res: '1220×2670', status: 'offline', platform: 'android', lastUsed: '2026-06-11 18:00', icon: '🤖', bg: 'rgba(123,168,125,0.12)' },
  { name: 'iPad Air', os: 'iOS 17.0', udid: '00008110-aaaaaaaaaaaa', res: '1640×2360', status: 'online', platform: 'ios', lastUsed: '2026-06-12 10:00', icon: '📟', bg: 'rgba(91,141,239,0.12)' },
  { name: 'OnePlus 12', os: 'Android 14', udid: 'STUVWX901234', res: '1440×3168', status: 'offline', platform: 'android', lastUsed: '2026-06-10 16:00', icon: '🤖', bg: 'rgba(123,168,125,0.12)' }
])

function getDeviceStatusClass(status) {
  if (status === 'online') return 'app-tag-online'
  if (status === 'busy') return 'app-tag-busy'
  return 'app-tag-offline'
}

function getDeviceStatusText(status) {
  if (status === 'online') return '在线'
  if (status === 'busy') return '忙碌'
  return '离线'
}

function refreshStatus() {
  ElMessage.info('设备状态已刷新')
}

function addDevice() {
  if (!newDevice.name) {
    ElMessage.warning('请输入设备名称')
    return
  }
  devices.value.push({
    name: newDevice.name,
    os: newDevice.platform === 'ios' ? `iOS ${newDevice.os}` : `Android ${newDevice.os}`,
    udid: newDevice.udid,
    res: '-',
    status: 'offline',
    platform: newDevice.platform,
    lastUsed: '-',
    icon: newDevice.platform === 'ios' ? '📱' : '🤖',
    bg: newDevice.platform === 'ios' ? 'rgba(60,40,20,0.08)' : 'rgba(123,168,125,0.12)'
  })
  showAddModal.value = false
  ElMessage.success('设备已添加')
}
</script>

<style scoped>
.device-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.device-card {
  background: var(--app-card-bg);
  border: var(--app-border);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.device-card:hover {
  box-shadow: var(--app-shadow);
  transform: translateY(-1px);
}

.device-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-bottom: 10px;
}

.device-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text);
  margin-bottom: 4px;
}

.device-info {
  font-size: 12px;
  color: var(--app-text-muted);
  margin-bottom: 2px;
}

.device-tags {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}

.device-footer {
  margin-top: 8px;
  padding-top: 8px;
  border-top: var(--app-border);
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--app-text-muted);
}

@media (max-width: 1100px) {
  .device-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 900px) {
  .device-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .device-grid { grid-template-columns: 1fr; }
}
</style>
