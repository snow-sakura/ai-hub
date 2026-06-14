<template>
  <div class="register-container">
    <!-- 左栏：品牌展示区 -->
    <div class="showcase-section">
      <div class="showcase-content">
        <!-- 品牌标题 -->
        <div class="brand-header">
          <div class="logo-wrapper">
            <div class="logo-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <rect x="3" y="3" width="18" height="18" rx="4" stroke="currentColor" stroke-width="2"/>
                <path d="M9 8L15 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M9 12L13 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M9 16L11 16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <h1 class="brand-title">AI-HUB</h1>
          </div>
          <p class="brand-subtitle">智能测试平台 · AI-Powered Testing Platform</p>
        </div>

        <!-- 加入理由 -->
        <div class="benefits-list">
          <div class="benefit-item" v-for="(item, index) in benefits" :key="index">
            <span class="benefit-icon">{{ item.icon }}</span>
            <div class="benefit-text">
              <h4>{{ item.title }}</h4>
              <p>{{ item.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 装饰元素 -->
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
    </div>

    <!-- 右栏：注册表单 -->
    <div class="register-section">
      <div class="register-form-wrapper">
        <div class="form-header">
          <h2>创建账号</h2>
          <p>注册 AI-HUB 智能测试平台，开启高效测试之旅</p>
        </div>

        <n-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleRegister"
          class="register-form"
        >
          <n-form-item label="用户名" path="username">
            <n-input
              v-model:value="form.username"
              placeholder="请输入用户名（必填）"
              size="large"
              :disabled="loading"
            />
          </n-form-item>

          <div class="form-row">
            <n-form-item label="密码" path="password" class="form-row-item">
              <n-input
                v-model:value="form.password"
                type="password"
                show-password-on="click"
                placeholder="至少6位"
                size="large"
                :disabled="loading"
              />
            </n-form-item>
            <n-form-item label="确认密码" path="confirmPassword" class="form-row-item">
              <n-input
                v-model:value="form.confirmPassword"
                type="password"
                show-password-on="click"
                placeholder="再次输入"
                size="large"
                :disabled="loading"
              />
            </n-form-item>
          </div>

          <n-form-item label="显示名称" path="displayName">
            <n-input
              v-model:value="form.displayName"
              placeholder="选填，您的昵称"
              size="large"
              :disabled="loading"
            />
          </n-form-item>

          <n-form-item label="邮箱" path="email">
            <n-input
              v-model:value="form.email"
              placeholder="选填，用于找回密码"
              size="large"
              :disabled="loading"
            />
          </n-form-item>

          <n-button
            type="primary"
            size="large"
            attr-type="submit"
            :loading="loading"
            :disabled="loading"
            class="register-button"
          >
            {{ loading ? '注册中...' : '注 册' }}
          </n-button>
        </n-form>

        <div class="form-footer">
          <router-link to="/login" class="login-link">
            已有账号？<span>立即登录</span>
          </router-link>
        </div>

        <div v-if="errorMsg" class="auth-error">{{ errorMsg }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInst, FormRules } from 'naive-ui'
import { register } from '@/shared/api/auth'

const router = useRouter()
const formRef = ref<FormInst | null>(null)
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  displayName: '',
  email: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule, value: string) => value === form.password,
      message: '两次密码输入不一致',
      trigger: 'blur',
    },
  ],
}

const benefits = [
  {
    icon: '🤖',
    title: 'AI 驱动测试',
    description: '基于大模型自动生成高质量测试用例',
  },
  {
    icon: '🔗',
    title: '多类型支持',
    description: 'API / UI / APP 自动化测试全覆盖',
  },
  {
    icon: '📊',
    title: '数据看板',
    description: '实时统计报告，质量趋势一目了然',
  },
  {
    icon: '⚡',
    title: '高效协作',
    description: '团队协作、项目管理和版本控制',
  },
]

async function handleRegister() {
  errorMsg.value = ''
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const result = await register({
      username: form.username,
      password: form.password,
      display_name: form.displayName || undefined,
      email: form.email || undefined,
    })
    localStorage.setItem('access_token', result.access_token)
    router.push('/')
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    errorMsg.value = typeof detail === 'string' ? detail : '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  height: 100vh;
  display: flex;
  background: #f5f7fa;
  overflow: hidden;
}

/* ── 左栏品牌展示 ────────────────────────────────── */
.showcase-section {
  flex: 1;
  background: linear-gradient(135deg, #7BA87D 0%, #9CC49E 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 60px;
}

.showcase-content {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 600px;
  color: white;
}

.brand-header {
  margin-bottom: 50px;
  animation: fadeInDown 0.8s ease-out;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.logo-icon {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.logo-icon svg {
  width: 32px;
  height: 32px;
  color: white;
}

.brand-title {
  font-size: 42px;
  font-weight: 700;
  margin: 0;
  color: white;
  letter-spacing: -1px;
}

.brand-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
  font-weight: 300;
  letter-spacing: 1px;
}

/* 加入理由列表 */
.benefits-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
  animation: fadeInUp 0.8s ease-out;
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.benefit-item:hover {
  transform: translateX(5px);
  background: rgba(255, 255, 255, 0.15);
}

.benefit-icon {
  font-size: 32px;
  line-height: 1;
  flex-shrink: 0;
}

.benefit-text h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: white;
}

.benefit-text p {
  font-size: 13px;
  margin: 0;
  opacity: 0.8;
  line-height: 1.5;
}

/* 装饰元素 */
.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite;
}

.shape-1 {
  width: 250px;
  height: 250px;
  top: -80px;
  right: -80px;
  animation-delay: 0s;
}

.shape-2 {
  width: 180px;
  height: 180px;
  bottom: -60px;
  left: -60px;
  animation-delay: 7s;
}

.shape-3 {
  width: 120px;
  height: 120px;
  top: 40%;
  left: 10%;
  animation-delay: 14s;
}

/* ── 右栏注册表单 ────────────────────────────────── */
.register-section {
  width: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 40px 60px;
  position: relative;
}

.register-form-wrapper {
  width: 100%;
  max-width: 420px;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
  animation: fadeIn 0.8s ease-out;
}

.form-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #3D2E1F;
  margin: 0 0 12px 0;
}

.form-header p {
  font-size: 14px;
  color: #8B7355;
  margin: 0;
  line-height: 1.6;
}

.register-form :deep(.n-form-item) {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row-item {
  flex: 1;
}

.register-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  margin-top: 8px;
}

.form-footer {
  text-align: center;
  margin-top: 24px;
}

.login-link {
  color: #8B7355;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
}

.login-link span {
  color: #C67B5C;
  font-weight: 600;
}

.login-link:hover {
  color: #C67B5C;
}

.auth-error {
  margin-top: 16px;
  padding: 10px 16px;
  background: rgba(212, 116, 92, 0.08);
  border: 1px solid rgba(212, 116, 92, 0.2);
  border-radius: 8px;
  color: #D4745C;
  font-size: 13px;
  text-align: center;
}

/* ── 动画 ─────────────────────────────────────────── */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(30px, -30px) rotate(90deg); }
  50% { transform: translate(-20px, 20px) rotate(180deg); }
  75% { transform: translate(20px, 10px) rotate(270deg); }
}

/* ── 响应式 ───────────────────────────────────────── */
@media (max-width: 1200px) {
  .showcase-section {
    padding: 40px;
  }
}

@media (max-width: 768px) {
  .register-container {
    flex-direction: column;
  }
  .showcase-section {
    min-height: 40vh;
    padding: 30px;
  }
  .showcase-section .brand-header {
    margin-bottom: 30px;
  }
  .showcase-section .logo-wrapper .brand-title {
    font-size: 32px;
  }
  .benefits-list {
    display: none;
  }
  .register-section {
    width: 100%;
    padding: 24px;
  }
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>
