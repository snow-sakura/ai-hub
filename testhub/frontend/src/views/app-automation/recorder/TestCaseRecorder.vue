<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">🎥 APP 用例录制</h1>
        <p class="app-page-subtitle">连接移动设备或模拟器，录制操作并自动生成测试用例</p>
      </div>
      <div class="header-actions">
        <button class="app-btn app-btn-secondary" @click="importScript">📥 导入脚本</button>
      </div>
    </div>

    <div class="recorder-layout app-fade-in">
      <div class="recorder-main">
        <div class="app-card" style="margin-bottom:0">
          <div class="app-card-header">
            <span>📱 移动设备录制</span>
            <div>
              <select v-model="engine" class="app-input" style="width:120px;height:28px;font-size:12px">
                <option>Appium</option>
                <option>XCUITest</option>
                <option>Espresso</option>
              </select>
            </div>
          </div>
          <div class="app-card-body">
            <div class="device-selector">
              <div
                v-for="dev in availableDevices"
                :key="dev.name"
                class="device-option"
                :class="{ active: selectedDevice === dev.name }"
                @click="selectedDevice = dev.name"
              >
                {{ dev.icon }} {{ dev.name }} · {{ dev.os }}
              </div>
            </div>

            <div class="recording-indicator">
              <span class="rec-dot" :class="{ inactive: !isRecording }"></span>
              <span :style="{ fontSize: '13px', color: isRecording ? 'var(--app-danger)' : 'var(--app-text-muted)', fontWeight: 500 }">
                {{ isRecording ? '录制中...' : '录制已暂停' }}
              </span>
              <span style="font-size:12px;color:var(--app-text-muted);margin-left:auto">{{ formattedTime }}</span>
            </div>

            <div class="phone-frame">
              <div class="phone-notch"></div>
              <div class="screen-content">
                <div style="font-size:48px;margin-bottom:12px">{{ selectedDevice?.includes('iPhone') ? '📱' : '🤖' }}</div>
                <p>点击「开始录制」后在设备上操作</p>
                <p style="font-size:12px;color:var(--app-text-muted);margin-top:4px">所有操作将被自动记录为测试步骤</p>
              </div>
              <div class="phone-home-indicator"></div>
            </div>

            <div style="display:flex;gap:8px;margin-top:14px;flex-wrap:wrap">
              <button
                class="app-btn"
                :class="isRecording ? 'app-btn-ghost' : 'app-btn-rec'"
                style="font-weight:600"
                @click="toggleRecording"
              >
                {{ isRecording ? '⏹️ 停止录制' : '🔴 开始录制' }}
              </button>
              <button class="app-btn app-btn-secondary" @click="pauseRecording">⏸️ 暂停</button>
              <button class="app-btn app-btn-ghost" @click="stopRecording">⏹️ 停止</button>
              <button class="app-btn app-btn-ghost" @click="takeScreenshot">📸 截图</button>
              <button class="app-btn app-btn-primary" style="margin-left:auto" @click="saveAsTestCase">💾 保存为用例</button>
            </div>
          </div>
        </div>
      </div>

      <div class="recorder-side">
        <div class="app-card" style="margin-bottom:0">
          <div class="app-card-header">📋 录制步骤</div>
          <div class="app-card-body">
            <div class="steps-list">
              <div
                v-for="(step, index) in recordedSteps"
                :key="index"
                class="step-item"
              >
                <span class="step-idx">{{ index + 1 }}</span>
                <span :class="['step-action-tag', getStepClass(step.action)]">{{ getStepLabel(step.action) }}</span>
                <span class="step-target">{{ step.target }}</span>
              </div>
              <div v-if="recordedSteps.length === 0" style="text-align:center;padding:20px;color:var(--app-text-muted)">
                <p>暂无录制步骤</p>
                <p style="font-size:12px;margin-top:4px">开始录制后在设备上操作</p>
              </div>
            </div>
            <div v-if="recordedSteps.length > 0" style="margin-top:10px;padding-top:10px;border-top:var(--app-border);display:flex;gap:6px">
              <button class="app-btn app-btn-ghost app-btn-xs" @click="moveStep(-1)">↑</button>
              <button class="app-btn app-btn-ghost app-btn-xs" @click="moveStep(1)">↓</button>
              <button class="app-btn app-btn-ghost app-btn-xs" @click="deleteStep">🗑️</button>
              <button class="app-btn app-btn-ghost app-btn-xs" style="margin-left:auto" @click="aiOptimize">🤖 AI 优化</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const engine = ref('Appium')
const selectedDevice = ref('iPhone 15')
const isRecording = ref(false)
const recordingTime = ref(0)
const recordedSteps = ref([])
let timer = null

const availableDevices = [
  { name: 'iPhone 15', os: 'iOS 17', icon: '📱' },
  { name: 'Pixel 7', os: 'Android 14', icon: '🤖' },
  { name: 'Galaxy S23', os: 'Android 13', icon: '📲' }
]

const formattedTime = computed(() => {
  const m = String(Math.floor(recordingTime.value / 60)).padStart(2, '0')
  const s = String(recordingTime.value % 60).padStart(2, '0')
  return `${m}:${s}`
})

function getStepClass(action) {
  const map = { tap: 'step-tap', input: 'step-input', swipe: 'step-swipe', assert: 'step-assert' }
  return map[action] || 'step-tap'
}

function getStepLabel(action) {
  const map = { tap: '点击', input: '输入', swipe: '滑动', assert: '断言' }
  return map[action] || action
}

function toggleRecording() {
  isRecording.value = !isRecording.value
  if (isRecording.value) {
    timer = setInterval(() => { recordingTime.value++ }, 1000)
    ElMessage.info('录制已开始，请在设备上操作')
  } else {
    clearInterval(timer)
    ElMessage.info('录制已停止')
  }
}

function pauseRecording() {
  if (isRecording.value) {
    clearInterval(timer)
    isRecording.value = false
  }
  ElMessage.info('已暂停')
}

function stopRecording() {
  clearInterval(timer)
  isRecording.value = false
  recordingTime.value = 0
  ElMessage.info('录制已停止')
}

function takeScreenshot() {
  ElMessage.info('已截图')
}

function importScript() {
  ElMessage.success('已导入脚本')
}

function saveAsTestCase() {
  ElMessage.success('用例已保存')
}

function moveStep(dir) {
  ElMessage.info(dir < 0 ? '上移' : '下移')
}

function deleteStep() {
  ElMessage.info('已删除')
}

function aiOptimize() {
  ElMessage.info('AI 优化中...')
}
</script>

<style scoped>
.recorder-layout {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.recorder-main {
  flex: 1;
  min-width: 0;
}

.recorder-side {
  width: 340px;
  flex-shrink: 0;
}

.rec-dot.inactive {
  animation: none;
  background: #ccc;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 400px;
  overflow-y: auto;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 6px;
  font-size: 12px;
  transition: all 0.15s;
  background: rgba(180, 150, 120, 0.04);
}

.step-item:hover {
  background: rgba(180, 150, 120, 0.06);
}

.step-idx {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--app-primary-bg);
  color: var(--app-primary);
  font-size: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-action-tag {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 5px;
  border-radius: 3px;
  flex-shrink: 0;
}

.step-target {
  color: var(--app-text-secondary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.screen-content {
  text-align: center;
}

@media (max-width: 900px) {
  .recorder-layout {
    flex-direction: column;
  }
  .recorder-side {
    width: 100%;
  }
}
</style>
