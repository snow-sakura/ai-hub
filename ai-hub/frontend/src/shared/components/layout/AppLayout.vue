<template>
  <div class="app-layout">
    <!-- 侧栏导航 -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <rect width="28" height="28" rx="6" fill="url(#logoGrad)"/>
          <path d="M8 14l4 4 8-8" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          <defs><linearGradient id="logoGrad" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#C67B5C"/><stop offset="1" stop-color="#D4A574"/></linearGradient></defs>
        </svg>
        <div class="logo-text">
          <h1>AI-HUB</h1>
          <span>智能测试平台</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section">导航菜单</div>
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">AI-HUB v2.0 · 智能测试</div>
    </aside>

    <!-- 主内容区 -->
    <main class="main">
      <header class="topbar">
        <h2>{{ currentTitle }}</h2>
        <div class="topbar-right">
          <span class="user-info">
            <span>{{ username }}</span>
            <div class="avatar">{{ avatarText }}</div>
          </span>
        </div>
      </header>
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

/** 导航菜单项定义 */
interface NavItem {
  path: string
  label: string
  icon: string
}

const navItems: NavItem[] = [
  { path: '/', label: '控制台', icon: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="14" height="14" rx="2"/><path d="M6 2v14M12 2v14M2 6h14M2 12h14"/></svg>' },
  { path: '/ai-testing/dashboard', label: 'AI 智能测试', icon: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 2v14M2 9h14"/><circle cx="9" cy="9" r="6"/></svg>' },
  { path: '/chat', label: 'AI 聊天室', icon: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2h12a2 2 0 012 2v8a2 2 0 01-2 2H7l-4 3V4a2 2 0 012-2z"/></svg>' },
  { path: '/knowledge', label: '知识库', icon: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h14M2 9h14M2 15h9"/><rect x="2" y="3" width="14" height="12" rx="1.5"/></svg>' },
  { path: '/system', label: '系统管理', icon: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="9" r="2"/><path d="M9 1v3M9 14v3M1 9h3M14 9h3M3.5 3.5l2 2M12.5 12.5l2 2M3.5 14.5l2-2M12.5 5.5l2-2"/></svg>' },
]

/** 当前页面标题 */
const currentTitle = computed(() => {
  const item = navItems.find(n => route.path.startsWith(n.path))
  return item?.label || 'AI-HUB'
})

/** 用户名（后续从 auth store 获取） */
const username = computed(() => '管理员')

/** 头像文字 */
const avatarText = computed(() => username.value.charAt(0))

/** 判断当前路由是否激活 */
function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: #FBF7F0;
}

/* ===== 侧栏 ===== */
.sidebar {
  width: 220px;
  background: #F6F0E7;
  border-right: 1px solid rgba(180,150,120,0.12);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
}

.sidebar-logo {
  padding: 20px 20px;
  border-bottom: 1px solid rgba(180,150,120,0.12);
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-text h1 {
  font-size: 16px;
  font-weight: 600;
  color: #3D2E1F;
  margin: 0;
}

.logo-text span {
  font-size: 11px;
  color: #8B7355;
  display: block;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 0;
  overflow-y: auto;
}

.nav-section {
  padding: 8px 20px 4px;
  font-size: 11px;
  color: #8B7355;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 500;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  color: #5C4A38;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(180,150,120,0.08);
  color: #3D2E1F;
}

.nav-item.active {
  background: rgba(198,123,92,0.1);
  color: #C67B5C;
  border-left-color: #C67B5C;
  font-weight: 500;
}

.nav-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  opacity: 0.7;
}

.nav-item.active .nav-icon {
  opacity: 1;
}

.nav-label {
  font-size: 13px;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(180,150,120,0.12);
  font-size: 12px;
  color: #8B7355;
}

/* ===== 主内容 ===== */
.main {
  margin-left: 220px;
  flex: 1;
  min-height: 100vh;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  background: #FFFDF9;
  border-bottom: 1px solid rgba(180,150,120,0.12);
  position: sticky;
  top: 0;
  z-index: 50;
}

.topbar h2 {
  font-size: 18px;
  font-weight: 600;
  color: #3D2E1F;
  margin: 0;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #5C4A38;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #C67B5C, #D4A574);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
}

.content {
  padding: 24px 32px;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 5px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(180,150,120,0.25);
  border-radius: 3px;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }
  .logo-text,
  .nav-section,
  .nav-label,
  .sidebar-footer {
    display: none;
  }
  .nav-item {
    justify-content: center;
    padding: 12px;
    border-left: none;
  }
  .nav-item.active {
    border-left: none;
  }
  .sidebar-logo {
    padding: 12px;
    justify-content: center;
  }
  .main {
    margin-left: 60px;
  }
  .content {
    padding: 16px;
  }
  .topbar {
    padding: 12px 16px;
  }
}
</style>
