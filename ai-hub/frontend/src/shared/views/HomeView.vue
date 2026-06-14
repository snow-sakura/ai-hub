<template>
  <div class="home-page">
    <!-- 顶部栏 -->
    <header class="topbar">
      <div class="topbar-left">
        <div class="topbar-logo">AI</div>
        <div class="topbar-title">AI-HUB</div>
      </div>
      <div class="topbar-right">
        <div class="lang-switch">
          <button
            class="lang-btn"
            :class="{ active: locale === 'zh-CN' }"
            @click="setLanguage('zh-CN')"
          >中文</button>
          <button
            class="lang-btn"
            :class="{ active: locale === 'en-US' }"
            @click="setLanguage('en-US')"
          >English</button>
        </div>
        <template v-if="isLoggedIn">
          <div class="user-info" @click.stop="userMenuOpen = !userMenuOpen" ref="userInfoRef">
            <div class="user-avatar">{{ avatarText }}</div>
            <span class="user-name">{{ userName }}</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--text-muted)"><path d="M6 9l6 6 6-6"/></svg>
            <div class="user-dropdown" v-if="userMenuOpen">
              <div class="user-dropdown-item" @click="router.push('/system')">系统管理</div>
              <div class="user-dropdown-divider"></div>
              <div class="user-dropdown-item alert" @click="handleLogout">退出登录</div>
            </div>
          </div>
        </template>
        <template v-else>
          <n-button size="small" @click="router.push('/login')">登录</n-button>
          <n-button size="small" secondary @click="router.push('/register')">注册</n-button>
        </template>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main">
      <!-- 欢迎区 -->
      <section class="welcome">
        <h1><span class="gradient-text">AI-HUB</span> 智能工作台</h1>
        <p>{{ welcomeMsg }}</p>
      </section>

      <!-- 统计卡片 -->
      <section class="stats">
        <div class="stat-card" v-for="s in stats" :key="s.label">
          <div class="stat-icon" :style="{ background: s.iconBg, color: s.iconColor }" v-html="s.icon"></div>
          <div class="stat-body">
            <div class="stat-number">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
            <div class="stat-trend" :class="s.trendDir">{{ s.trend }}</div>
          </div>
        </div>
      </section>

      <!-- 功能模块 -->
      <h2 class="section-title">功能模块</h2>
      <div class="module-grid">
        <div
          v-for="m in modules"
          :key="m.name"
          class="module-card"
          @click="navigate(m.route)"
        >
          <div class="module-card-icon" :style="{ background: m.color + '18', color: m.color }" v-html="m.icon"></div>
          <h3>{{ m.name }}</h3>
          <p>{{ m.desc || '与AI对话，获取智能测试建议与实时帮助' }}</p>
          <div class="module-card-meta">
            <span>{{ m.subs || '实时对话' }}</span>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部 -->
    <footer class="footer">AI-HUB 智能测试平台 &copy; 2026</footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '@/locales'
import { getSystemStats } from '@/shared/api/system'

const router = useRouter()
const { locale, setLocale } = useI18n()

// ── 用户 ─────────────────────────────────────────
const token = localStorage.getItem('access_token')
const userName = ref('未登录')
const avatarText = ref('?')
const userInfoRef = ref<HTMLElement | null>(null)
const userMenuOpen = ref(false)
const welcomeMsg = ref('欢迎回来！')
const isLoggedIn = computed(() => !!token)

async function loadUserInfo() {
  if (!token) return
  try {
    const res: any = await (await fetch('/api/v1/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })).json()
    if (res.code === 200 && res.data) {
      const u = res.data
      userName.value = u.display_name || u.username || '用户'
      avatarText.value = userName.value.charAt(0)
      welcomeMsg.value = `欢迎回来，${userName.value}！`
    }
  } catch { /* ignore */ }
}

function handleLogout() {
  localStorage.removeItem('access_token')
  window.location.reload()
}

function setLanguage(lang: string) {
  setLocale(lang as any)
}

// ── 统计卡片 ─────────────────────────────────────
interface StatItem {
  icon: string
  iconBg: string
  iconColor: string
  value: string
  label: string
  trend: string
  trendDir: string
}

const stats = reactive<StatItem[]>([
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>', iconBg: 'rgba(198,123,92,0.12)', iconColor: '#C67B5C', value: '-', label: '项目总数', trend: '加载中...', trendDir: 'up' },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>', iconBg: 'rgba(212,165,116,0.12)', iconColor: '#D4A574', value: '-', label: '用例总数', trend: '加载中...', trendDir: 'up' },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>', iconBg: 'rgba(212,165,116,0.12)', iconColor: '#D4A574', value: '-', label: '今日执行', trend: '加载中...', trendDir: 'up' },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>', iconBg: 'rgba(198,123,92,0.12)', iconColor: '#C67B5C', value: '-', label: '通过率', trend: '加载中...', trendDir: 'up' },
])

async function loadStats() {
  try {
    const data = await getSystemStats()
    stats[0].value = String(data.user_count || 0)
    stats[0].trend = `共 ${data.role_count} 个角色`
    // 剩余统计暂为静态占位
    stats[1].value = '-'
    stats[1].trend = '需接入数据'
    stats[2].value = '-'
    stats[2].trend = '需接入数据'
    stats[3].value = '-'
    stats[3].trend = '需接入数据'
  } catch {
    stats.forEach(s => { s.trend = '加载失败' })
  }
}

// ── 模块卡片 ─────────────────────────────────────
interface ModuleDef {
  name: string
  desc: string
  subs: string
  color: string
  icon: string
  route: string
}

const modules: ModuleDef[] = [
  { name: 'AI智能测试', desc: 'AI用例生成、项目管理、版本管理、用例评审', subs: '6个子模块', color: '#C67B5C', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2a4 4 0 014 4c0 1.5-.8 2.8-2 3.5V12a2 2 0 01-2 2h-1v2"/><circle cx="12" cy="22" r="2"/><circle cx="7" cy="20" r="2"/><circle cx="17" cy="20" r="2"/><path d="M12 6v2m-3 0a3 3 0 00-3 3v6"/></svg>', route: '/ai-testing' },
  { name: '配置中心', desc: '全局配置、环境变量与第三方集成', subs: '3个子模块', color: '#D4A574', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>', route: '/ai-testing/config/model' },
  { name: 'AI聊天室', desc: '与AI对话，获取智能测试建议与实时帮助', subs: '实时对话', color: '#C67B5C', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>', route: '/chat' },
  { name: '知识库', desc: '测试知识沉淀与经验分享', subs: '4个子模块', color: '#D4A574', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>', route: '/knowledge' },
  { name: '系统管理', desc: '用户管理、权限控制与审计日志', subs: '5个子模块', color: '#C67B5C', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>', route: '/system' },
]

function navigate(path: string) {
  router.push(path)
}

// 点击外部关闭用户菜单
function onClickOutside(e: MouseEvent) {
  if (userInfoRef.value && !userInfoRef.value.contains(e.target as Node)) {
    userMenuOpen.value = false
  }
}

// ── 初始化 ───────────────────────────────────────
onMounted(() => {
  loadUserInfo()
  loadStats()
  document.addEventListener('click', onClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside)
})
</script>

<style scoped>
.home-page {
  --primary: #C67B5C;
  --primary-light: #D49472;
  --accent: #D4A574;
  --bg: #FBF7F0;
  --card-bg: #FFFDF9;
  --sidebar-bg: #F6F0E7;
  --text: #3D2E1F;
  --text-secondary: #5C4A38;
  --text-muted: #8B7355;
  --border: 1px solid rgba(180,150,120,0.12);
  --radius: 8px;
  --radius-lg: 12px;

  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ═══ 顶部栏 ═══ */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
  background: var(--card-bg);
  border-bottom: var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar-logo {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 18px;
}

.topbar-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.5px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.lang-switch {
  display: flex;
  background: var(--bg);
  border-radius: 6px;
  padding: 2px;
  border: var(--border);
}

.lang-btn {
  padding: 4px 12px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  border-radius: 4px;
  color: var(--text-muted);
  transition: all 0.2s;
  font-family: inherit;
}

.lang-btn.active {
  background: var(--primary);
  color: #fff;
}

.lang-btn:hover:not(.active) {
  color: var(--text);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  position: relative;
  padding: 4px 12px;
  border-radius: var(--radius);
  transition: background 0.2s;
}

.user-info:hover {
  background: var(--bg);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-light), var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--card-bg);
  border: var(--border);
  border-radius: var(--radius);
  box-shadow: 0 8px 24px rgba(60,45,30,0.1);
  min-width: 140px;
  padding: 4px;
  margin-top: 4px;
  z-index: 200;
}

.user-dropdown-item {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  border-radius: 4px;
  color: var(--text-secondary);
  transition: background 0.2s;
}

.user-dropdown-item:hover {
  background: var(--bg);
}

.user-dropdown-item.alert {
  color: #C67B5C;
}

.user-dropdown-divider {
  height: 1px;
  background: var(--border);
  margin: 4px 8px;
}

/* ═══ 主内容 ═══ */
.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* ═══ 欢迎区 ═══ */
.welcome {
  margin-bottom: 32px;
}

.welcome h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 6px;
}

.gradient-text {
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome p {
  color: var(--text-muted);
  font-size: 15px;
}

/* ═══ 统计卡片 ═══ */
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: 20px;
  border: var(--border);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.25s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(180,150,120,0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon :deep(svg) {
  width: 24px;
  height: 24px;
}

.stat-body {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 2px;
}

.stat-trend {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  margin-top: 4px;
  display: inline-block;
}

.stat-trend.up {
  background: rgba(198,123,92,0.1);
  color: var(--primary);
}

.stat-trend.down {
  background: rgba(180,150,120,0.1);
  color: var(--text-muted);
}

/* ═══ 功能模块 ═══ */
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.module-card {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: var(--border);
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.module-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  opacity: 0;
  transition: opacity 0.3s;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(180,150,120,0.12);
}

.module-card:hover::before {
  opacity: 1;
}

.module-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}

.module-card-icon :deep(svg) {
  width: 22px;
  height: 22px;
}

.module-card h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 6px;
  color: var(--text);
}

.module-card p {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0 0 12px;
}

.module-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.module-card-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ═══ 底部 ═══ */
.footer {
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
  font-size: 13px;
  border-top: var(--border);
  margin-top: 32px;
}

/* ═══ 响应式 ═══ */
@media (max-width: 900px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
  .module-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .topbar {
    padding: 0 16px;
  }
  .main {
    padding: 20px 16px;
  }
  .stats {
    grid-template-columns: 1fr;
  }
  .module-grid {
    grid-template-columns: 1fr;
  }
  .welcome h1 {
    font-size: 22px;
  }
  .lang-switch {
    display: none;
  }
}
</style>
