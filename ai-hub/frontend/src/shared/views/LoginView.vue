<template>
  <div class="login-container">
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

        <!-- 特性卡片 -->
        <div class="features-grid">
          <div
            v-for="(feature, index) in features"
            :key="index"
            class="feature-card"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <div class="feature-icon" :style="{ background: feature.color }">
              <span class="feature-icon-text">{{ feature.emoji }}</span>
            </div>
            <div class="feature-content">
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
            </div>
          </div>
        </div>

        <!-- AI 能力标签 -->
        <div class="ai-capabilities">
          <div class="capability-badge">🤖 AI 用例生成</div>
          <div class="capability-badge">🔀 多模型支持</div>
          <div class="capability-badge">📡 流式输出</div>
          <div class="capability-badge">📊 数据驱动</div>
        </div>
      </div>

      <!-- 装饰元素 -->
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>

    <!-- 右栏：登录表单 -->
    <div class="login-section">
      <div class="login-form-wrapper">
        <div class="form-header">
          <h2>欢迎回来</h2>
          <p>登录 AI-HUB 智能测试平台，开启高效测试之旅</p>
        </div>

        <n-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <n-form-item path="username">
            <n-input
              v-model:value="form.username"
              placeholder="请输入用户名"
              size="large"
              :disabled="loading"
            >
              <template #prefix>
                <svg class="input-icon" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M4 21C4 16.5817 7.58172 13 12 13C16.4183 13 20 16.5817 20 21" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="password">
            <n-input
              v-model:value="form.password"
              type="password"
              show-password-on="click"
              placeholder="请输入密码"
              :disabled="loading"
            >
              <template #prefix>
                <svg class="input-icon" viewBox="0 0 24 24" fill="none">
                  <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M8 11V7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7V11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </template>
            </n-input>
          </n-form-item>

          <n-button
            type="primary"
            size="large"
            attr-type="submit"
            :loading="loading"
            :disabled="loading"
            class="login-button"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </n-button>
        </n-form>

        <div class="form-footer">
          <router-link to="/register" class="register-link">
            还没有账号？<span>立即注册</span>
          </router-link>
        </div>

        <div v-if="errorMsg" class="auth-error">{{ errorMsg }}</div>

        <div class="bottom-info">
          <p>AI-HUB v2.0 · 智能测试平台</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { FormInst, FormRules } from 'naive-ui'
import { login } from '@/shared/api/auth'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInst | null>(null)
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

// 特性展示数据
const features = [
  {
    emoji: '🤖',
    title: 'AI 智能生成',
    description: '基于 LLM 自动分析需求文档，生成高质量测试用例',
    color: 'linear-gradient(135deg, #C67B5C 0%, #D4A574 100%)',
  },
  {
    emoji: '🔗',
    title: '多类型测试',
    description: '支持 API 接口、UI 自动化、APP 自动化全覆盖',
    color: 'linear-gradient(135deg, #7BA87D 0%, #9CC49E 100%)',
  },
  {
    emoji: '⚡',
    title: '自动化执行',
    description: '定时任务驱动，Playwright/uiautomator2 引擎执行',
    color: 'linear-gradient(135deg, #6B9BC4 0%, #8DB8D8 100%)',
  },
  {
    emoji: '📊',
    title: '数据看板',
    description: '实时统计与报告，质量趋势一目了然',
    color: 'linear-gradient(135deg, #D4A574 0%, #E8C4A0 100%)',
  },
]

async function handleLogin() {
  errorMsg.value = ''
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const result = await login(form)
    localStorage.setItem('access_token', result.access_token)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    errorMsg.value = typeof detail === 'string' ? detail : '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  background: #f5f7fa;
  overflow: hidden;
}

/* ── 左栏品牌展示 ────────────────────────────────── */
.showcase-section {
  flex: 1;
  background: linear-gradient(135deg, #C67B5C 0%, #D4A574 100%);
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
  margin-bottom: 60px;
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

/* 特性卡片网格 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 60px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  animation: fadeInUp 0.8s ease-out;
}

.feature-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.feature-icon-text {
  font-size: 24px;
  line-height: 1;
}

.feature-content h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.feature-content p {
  font-size: 13px;
  margin: 0;
  opacity: 0.8;
  line-height: 1.5;
}

/* AI 能力标签 */
.ai-capabilities {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  animation: fadeInUp 1s ease-out;
}

.capability-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 8px 18px;
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 14px;
  font-weight: 500;
}

/* 装饰浮动圆 */
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
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  bottom: -50px;
  right: -50px;
  animation-delay: 5s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 20%;
  animation-delay: 10s;
}

.shape-4 {
  width: 100px;
  height: 100px;
  bottom: 30%;
  left: 30%;
  animation-delay: 15s;
}

/* ── 右栏登录表单 ────────────────────────────────── */
.login-section {
  width: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 60px;
  position: relative;
}

.login-form-wrapper {
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
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

.login-form :deep(.n-form-item) {
  margin-bottom: 24px;
}

.login-form :deep(.n-input__input) {
  height: 48px;
}

.input-icon {
  width: 18px;
  height: 18px;
  color: #B5A590;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

.form-footer {
  text-align: center;
  margin-top: 24px;
}

.register-link {
  color: #8B7355;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
}

.register-link span {
  color: #C67B5C;
  font-weight: 600;
}

.register-link:hover {
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

.bottom-info {
  margin-top: 60px;
  text-align: center;
}

.bottom-info p {
  font-size: 12px;
  color: #c0c4cc;
  margin: 0;
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
  .features-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  .showcase-section {
    min-height: 50vh;
    padding: 30px;
  }
  .showcase-section .brand-header {
    margin-bottom: 30px;
  }
  .showcase-section .logo-wrapper .brand-title {
    font-size: 32px;
  }
  .features-grid {
    display: none;
  }
  .login-section {
    width: 100%;
    padding: 30px;
  }
}
</style>
