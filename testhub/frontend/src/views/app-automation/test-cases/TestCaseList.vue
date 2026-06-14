<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">APP 测试用例</h1>
        <p class="app-page-subtitle">管理移动端自动化测试用例 · 共 {{ testCases.length }} 个用例</p>
      </div>
      <div class="header-actions">
        <button class="app-btn app-btn-secondary" @click="$router.push('/app-automation/recorder')">🎥 录制</button>
        <button class="app-btn app-btn-primary" @click="showAddModal = true">+ 新建用例</button>
      </div>
    </div>

    <div class="case-grid app-fade-in">
      <div v-for="(tc, i) in testCases" :key="i" class="case-card" @click="showDetail(tc)">
        <div class="case-name">
          <span>{{ tc.status ? '🟢' : '🟡' }}</span> {{ tc.name }}
          <span style="margin-left:auto;font-size:12px;font-weight:400;color:var(--app-text-muted)">{{ tc.app }}</span>
        </div>
        <div class="case-tags">
          <span :class="['app-tag', tc.platform === 'both' ? 'app-tag-both' : tc.platform === 'android' ? 'app-tag-android' : 'app-tag-ios']">
            {{ tc.platform === 'both' ? '双平台' : tc.platform === 'android' ? 'Android' : 'iOS' }}
          </span>
          <span :class="['app-tag', tc.status ? 'app-tag-active' : 'app-tag-offline']">
            {{ tc.status ? '启用' : '停用' }}
          </span>
          <span style="font-size:12px;color:var(--app-text-muted);margin-left:auto">{{ tc.steps }} 步</span>
        </div>
        <div class="step-flow">
          <div v-for="(step, si) in tc.stepsList.slice(0, 3)" :key="si" class="step-item">
            <span class="step-num">{{ si + 1 }}</span>
            <span :class="['step-action', getStepClass(step.action)]">{{ getStepLabel(step.action) }}</span>
            <span class="step-desc">{{ step.desc }}</span>
          </div>
          <div v-if="tc.stepsList.length > 3" style="font-size:11px;color:var(--app-text-muted);text-align:center">
            ... 还有 {{ tc.stepsList.length - 3 }} 步
          </div>
        </div>
        <div style="display:flex;gap:6px;padding-top:8px;border-top:var(--app-border)">
          <button class="app-btn app-btn-ghost app-btn-xs" @click.stop="editCase(tc)">编辑</button>
          <button class="app-btn app-btn-primary app-btn-xs" @click.stop="executeCase(tc)">▶ 执行</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const showAddModal = ref(false)

const testCases = ref([
  {
    name: '用户登录流程', app: '电商APP', steps: 5, platform: 'both', status: 1,
    stepsList: [
      { action: 'tap', desc: '点击"我的"Tab' },
      { action: 'input', desc: '输入用户名' },
      { action: 'input', desc: '输入密码' },
      { action: 'tap', desc: '点击登录按钮' },
      { action: 'assert', desc: '验证个人中心显示' }
    ]
  },
  {
    name: '商品搜索功能', app: '电商APP', steps: 4, platform: 'android', status: 1,
    stepsList: [
      { action: 'tap', desc: '点击搜索栏' },
      { action: 'input', desc: '输入搜索关键词"手机"' },
      { action: 'tap', desc: '点击搜索按钮' },
      { action: 'assert', desc: '验证搜索结果列表' }
    ]
  },
  {
    name: '购物车结算', app: '电商APP', steps: 6, platform: 'both', status: 1,
    stepsList: [
      { action: 'tap', desc: '点击购物车图标' },
      { action: 'swipe', desc: '滑动查看商品列表' },
      { action: 'tap', desc: '点击"去结算"' },
      { action: 'input', desc: '填写收货地址' },
      { action: 'tap', desc: '确认支付' },
      { action: 'assert', desc: '验证订单状态' }
    ]
  },
  {
    name: '注册表单验证', app: '电商APP', steps: 4, platform: 'ios', status: 1,
    stepsList: [
      { action: 'tap', desc: '点击注册按钮' },
      { action: 'input', desc: '输入手机号' },
      { action: 'input', desc: '输入验证码' },
      { action: 'assert', desc: '验证注册成功提示' }
    ]
  },
  {
    name: '支付页面跳转', app: '金融APP', steps: 5, platform: 'both', status: 0,
    stepsList: [
      { action: 'tap', desc: '点击立即支付' },
      { action: 'input', desc: '输入支付密码' },
      { action: 'tap', desc: '确认支付' },
      { action: 'assert', desc: '验证支付结果页面' },
      { action: 'assert', desc: '验证余额变动' }
    ]
  },
  {
    name: '个人中心展示', app: '电商APP', steps: 3, platform: 'ios', status: 1,
    stepsList: [
      { action: 'tap', desc: '点击个人中心' },
      { action: 'swipe', desc: '向下滑动页面' },
      { action: 'assert', desc: '验证用户信息展示完整' }
    ]
  }
])

function getStepClass(action) {
  const map = { tap: 'step-tap', input: 'step-input', swipe: 'step-swipe', assert: 'step-assert' }
  return map[action] || 'step-tap'
}

function getStepLabel(action) {
  const map = { tap: '点击', input: '输入', swipe: '滑动', assert: '断言' }
  return map[action] || action
}

function showDetail(tc) {
  ElMessage.info(`查看用例详情: ${tc.name}`)
}

function editCase(tc) {
  ElMessage.info(`编辑用例: ${tc.name}`)
}

function executeCase(tc) {
  ElMessage.info(`开始执行: ${tc.name}`)
}
</script>

<style scoped>
.case-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.case-card {
  background: var(--app-card-bg);
  border: var(--app-border);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.case-card:hover {
  box-shadow: var(--app-shadow);
  transform: translateY(-1px);
}

.case-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text);
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.case-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

@media (max-width: 900px) {
  .case-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .case-grid {
    grid-template-columns: 1fr;
  }
}
</style>
