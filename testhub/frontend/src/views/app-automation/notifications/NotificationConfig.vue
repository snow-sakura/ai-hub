<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">APP 通知配置</h1>
        <p class="app-page-subtitle">移动端自动化测试结果通知设置</p>
      </div>
      <div class="header-actions">
        <button class="app-btn app-btn-primary" @click="saveSettings">💾 保存设置</button>
      </div>
    </div>

    <!-- 通知渠道 -->
    <div class="app-card app-fade-in">
      <div class="app-card-header">📬 通知渠道</div>
      <div class="app-card-body">
        <div
          v-for="(channel, index) in channels"
          :key="channel.key"
          class="notif-item"
        >
          <div class="notif-icon" :style="{ background: channel.bg, color: channel.color }">
            {{ channel.icon }}
          </div>
          <div class="notif-info">
            <div class="title">{{ channel.title }}</div>
            <div class="desc">{{ channel.desc }}</div>
          </div>
          <label class="app-switch">
            <input type="checkbox" v-model="channel.enabled">
            <span class="slider"></span>
          </label>
        </div>
      </div>
    </div>

    <!-- 告警规则 -->
    <div class="app-card app-fade-in">
      <div class="app-card-header">⚙️ APP 告警规则</div>
      <div class="app-card-body">
        <div class="grid-2" style="margin-bottom:12px">
          <div>
            <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">失败率阈值 (%)</label>
            <input v-model.number="alertRules.failRate" type="number" class="app-input">
            <div class="app-hint">当失败率超过此百分比时触发告警</div>
          </div>
          <div>
            <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">Crash 率阈值 (%)</label>
            <input v-model.number="alertRules.crashRate" type="number" class="app-input">
            <div class="app-hint">APP 崩溃率超过此值时触发告警</div>
          </div>
        </div>
        <div class="grid-2" style="margin-bottom:12px">
          <div>
            <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">单步超时时间（秒）</label>
            <input v-model.number="alertRules.stepTimeout" type="number" class="app-input">
            <div class="app-hint">APP 操作单步执行超时阈值</div>
          </div>
          <div>
            <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">静默周期（分钟）</label>
            <input v-model.number="alertRules.silentPeriod" type="number" class="app-input">
            <div class="app-hint">同一任务连续告警的最小间隔</div>
          </div>
        </div>
        <div>
          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">失败截图保留天数</label>
          <input v-model.number="alertRules.screenshotRetention" type="number" class="app-input" style="max-width:300px">
          <div class="app-hint">超过期限自动清理截图文件</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const channels = reactive([
  { key: 'email', icon: '📧', color: '#5B8DEF', bg: 'rgba(91,141,239,0.12)', title: '邮件通知', desc: '执行完成后发送 APP 测试报告到指定邮箱', enabled: true },
  { key: 'feishu', icon: '💬', color: 'var(--app-danger)', bg: 'rgba(212,116,92,0.12)', title: '飞书机器人', desc: '通过飞书 Webhook 推送 APP 测试结果卡片', enabled: true },
  { key: 'wechat', icon: '💚', color: 'var(--app-success)', bg: 'rgba(123,168,125,0.12)', title: '企业微信', desc: '通过企业微信机器人发送 APP 测试报告', enabled: false },
  { key: 'sms', icon: '🔔', color: '#B8860B', bg: 'rgba(212,165,116,0.12)', title: '短信通知', desc: '仅发送失败告警到指定手机号', enabled: false },
  { key: 'push', icon: '📲', color: 'var(--app-primary)', bg: 'rgba(198,123,92,0.12)', title: 'APP Push', desc: '发送 Push 通知到内部 APP', enabled: false }
])

const alertRules = reactive({
  failRate: 20,
  crashRate: 5,
  stepTimeout: 30,
  silentPeriod: 60,
  screenshotRetention: 30
})

function saveSettings() {
  ElMessage.success('配置已保存')
}
</script>

<style scoped>
.notif-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 0;
}

.notif-item + .notif-item {
  border-top: var(--app-border);
}

.notif-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.notif-info {
  flex: 1;
}

.notif-info .title {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text);
}

.notif-info .desc {
  font-size: 12px;
  color: var(--app-text-muted);
  margin-top: 2px;
}

.app-hint {
  font-size: 12px;
  color: var(--app-text-muted);
  margin-top: 4px;
}
</style>
