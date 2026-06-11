<template>
  <div class="testing-layout">
    <!-- 侧边栏 -->
    <aside
      class="testing-sidebar"
      :class="{ 'sidebar-mobile-open': isMobile && mobileSidebarOpen }"
    >
      <!-- 品牌区 -->
      <div class="sidebar-brand">
        <span class="brand-icon">📋</span>
        <span class="brand-text">AI 测试助手</span>
      </div>

      <!-- 菜单组 -->
      <div class="sidebar-menu">
        <div v-for="group in menuGroups" :key="group.key" class="menu-group">
          <div class="menu-group-header" @click="toggleGroup(group.key)">
            <span class="group-icon">{{ group.icon }}</span>
            <span class="group-label">{{ group.label }}</span>
            <span class="group-arrow" :class="{ expanded: expandedGroups[group.key] }">▸</span>
          </div>
          <transition name="menu-slide">
            <div v-show="expandedGroups[group.key]" class="menu-items">
              <router-link
                v-for="item in group.items"
                :key="item.path"
                :to="item.path"
                class="menu-item"
                :class="{ active: isActive(item.path) }"
                @click="onMenuItemClick"
              >
                <span class="item-icon">{{ item.icon }}</span>
                <span class="item-label">{{ item.label }}</span>
              </router-link>
            </div>
          </transition>
        </div>
      </div>

      <!-- 底部：返回首页 -->
      <div class="sidebar-footer">
        <router-link to="/" class="sidebar-home-link">
          <span class="home-icon">⌂</span>
          <span class="home-label">返回首页</span>
        </router-link>
      </div>
    </aside>

    <!-- 移动端遮罩 -->
    <div
      v-if="isMobile && mobileSidebarOpen"
      class="sidebar-overlay"
      @click="mobileSidebarOpen = false"
    />

    <!-- 主内容区 -->
    <main class="testing-main">
      <!-- 顶部栏（面包屑 + 移动端菜单按钮） -->
      <div class="main-topbar">
        <n-button
          v-if="isMobile"
          text
          class="hamburger-btn"
          @click="mobileSidebarOpen = !mobileSidebarOpen"
        >
          <span class="hamburger-icon">☰</span>
        </n-button>
        <n-breadcrumb>
          <n-breadcrumb-item
            v-for="(crumb, idx) in breadcrumbs"
            :key="idx"
          >
            <router-link
              v-if="crumb.path"
              :to="crumb.path"
              class="breadcrumb-link"
            >
              {{ crumb.label }}
            </router-link>
            <span v-else class="breadcrumb-current">{{ crumb.label }}</span>
          </n-breadcrumb-item>
        </n-breadcrumb>
      </div>

      <!-- 子路由视图 -->
      <div class="main-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useResponsive } from '@/shared/composables/useResponsive'

const route = useRoute()
const { isMobile } = useResponsive()

const mobileSidebarOpen = ref(false)

// ── 菜单定义 ────────────────────────────────────────────────
interface MenuItem {
  icon: string
  label: string
  path: string
}

interface MenuGroup {
  key: string
  icon: string
  label: string
  items: MenuItem[]
}

const menuGroups: MenuGroup[] = [
  {
    key: 'project',
    icon: '📁',
    label: '项目管理',
    items: [
      { icon: '📋', label: '项目列表', path: '/ai-testing/projects' },
      { icon: '🔖', label: '版本管理', path: '/ai-testing/projects/versions' },
      { icon: '👥', label: '项目成员', path: '/ai-testing/projects/members' },
    ],
  },
  {
    key: 'testcase',
    icon: '📋',
    label: '用例管理',
    items: [
      { icon: '📋', label: '所有用例', path: '/ai-testing/testcases' },
      { icon: '➕', label: '创建用例', path: '/ai-testing/testcases/create' },
    ],
  },
  {
    key: 'generation',
    icon: '🤖',
    label: 'AI 智能生成',
    items: [
      { icon: '⚡', label: 'AI 用例生成', path: '/ai-testing/generate' },
      { icon: '📊', label: 'AI 生成记录', path: '/ai-testing/generate/records' },
      { icon: '⚙️', label: 'AI 生成配置', path: '/ai-testing/settings' },
    ],
  },
]

// ── 展开/折叠状态 ───────────────────────────────────────────
const expandedGroups = reactive<Record<string, boolean>>({
  project: true,
  testcase: true,
  generation: true,
})

function toggleGroup(key: string) {
  expandedGroups[key] = !expandedGroups[key]
}

// 当前路由变化时自动展开所在组
watch(
  () => route.path,
  (path) => {
    if (path.startsWith('/ai-testing/projects')) expandedGroups.project = true
    else if (path.startsWith('/ai-testing/testcases')) expandedGroups.testcase = true
    else if (path.startsWith('/ai-testing/generate') || path.startsWith('/ai-testing/settings'))
      expandedGroups.generation = true
  },
  { immediate: true },
)

// ── 菜单高亮 ────────────────────────────────────────────────
function isActive(itemPath: string): boolean {
  // 特殊处理"创建用例"：仅精确匹配
  if (itemPath === '/ai-testing/testcases/create') {
    return route.path === itemPath
  }
  // 其他菜单项：匹配前缀
  return route.path.startsWith(itemPath)
}

// ── 移动端菜单点击后关闭 ─────────────────────────────────────
function onMenuItemClick() {
  if (isMobile.value) {
    mobileSidebarOpen.value = false
  }
}

// ── 面包屑 ──────────────────────────────────────────────────
interface BreadcrumbItem {
  label: string
  path?: string
}

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
  const path = route.path
  const items: BreadcrumbItem[] = [
    { label: 'AI 测试助手', path: '/ai-testing/projects' },
  ]

  if (path.startsWith('/ai-testing/projects')) {
    items.push({ label: '项目管理', path: '/ai-testing/projects' })
    if (path === '/ai-testing/projects') {
      items.push({ label: '项目列表' })
    } else if (path === '/ai-testing/projects/versions') {
      items.push({ label: '版本管理' })
    } else if (path === '/ai-testing/projects/members') {
      items.push({ label: '项目成员' })
    } else {
      items.push({ label: '项目详情' })
    }
  } else if (path.startsWith('/ai-testing/testcases')) {
    items.push({ label: '用例管理', path: '/ai-testing/testcases' })
    if (path === '/ai-testing/testcases') {
      items.push({ label: '所有用例' })
    } else if (path === '/ai-testing/testcases/create') {
      items.push({ label: '创建用例' })
    } else if (path.endsWith('/edit')) {
      items.push({ label: '编辑用例' })
    } else {
      items.push({ label: '用例详情' })
    }
  } else if (path.startsWith('/ai-testing/generate')) {
    items.push({ label: 'AI 智能生成', path: '/ai-testing/generate' })
    if (path === '/ai-testing/generate/records') {
      items.push({ label: 'AI 生成记录' })
    } else {
      items.push({ label: 'AI 用例生成' })
    }
  } else if (path.startsWith('/ai-testing/settings')) {
    items.push({ label: 'AI 智能生成', path: '/ai-testing/generate' })
    items.push({ label: 'AI 生成配置' })
  }

  return items
})
</script>

<style scoped>
/* ── 布局容器 ───────────────────────────────────────────── */
.testing-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #fbf7f0;
}

/* ── 侧边栏 ─────────────────────────────────────────────── */
.testing-sidebar {
  width: 240px;
  min-width: 240px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  color: #e0e0e0;
  overflow-y: auto;
  z-index: 100;
}

/* 品牌区 */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}
.brand-icon {
  font-size: 24px;
}
.brand-text {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.02em;
}

/* 菜单区 */
.sidebar-menu {
  flex: 1;
  padding: 12px 0;
  overflow-y: auto;
}

/* 底部：返回首页 */
.sidebar-footer {
  flex-shrink: 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 12px 0;
}
.sidebar-home-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  transition: all 0.2s;
  cursor: pointer;
}
.sidebar-home-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}
.home-icon {
  font-size: 16px;
  width: 22px;
  text-align: center;
}
.home-label {
  font-size: 13px;
}

/* 菜单组 */
.menu-group {
  margin-bottom: 4px;
}
.menu-group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
  border-radius: 0;
}
.menu-group-header:hover {
  background: rgba(255, 255, 255, 0.06);
}
.group-icon {
  font-size: 16px;
  width: 22px;
  text-align: center;
}
.group-label {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.group-arrow {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  transition: transform 0.25s ease;
}
.group-arrow.expanded {
  transform: rotate(90deg);
}

/* 菜单项 */
.menu-items {
  padding: 2px 0;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 20px 9px 50px;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.65);
  font-size: 14px;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  cursor: pointer;
}
.menu-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}
.menu-item.active {
  color: #fff;
  background: rgba(198, 123, 92, 0.12);
  border-left-color: #c67b5c;
}
.item-icon {
  font-size: 14px;
  width: 18px;
  text-align: center;
}
.item-label {
  font-size: 14px;
}

/* ── 菜单展开/折叠动画 ──────────────────────────────────── */
.menu-slide-enter-active {
  transition: all 0.2s ease;
}
.menu-slide-leave-active {
  transition: all 0.15s ease;
}
.menu-slide-enter-from,
.menu-slide-leave-to {
  opacity: 0;
  max-height: 0;
}
.menu-slide-enter-to,
.menu-slide-leave-from {
  opacity: 1;
  max-height: 300px;
}

/* ── 移动端遮罩 ─────────────────────────────────────────── */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 99;
}

/* ── 主内容区 ───────────────────────────────────────────── */
.testing-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

/* 顶部栏 */
.main-topbar {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 48px;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
}
.hamburger-btn {
  padding: 0 4px 0 0;
}
.hamburger-icon {
  font-size: 20px;
  line-height: 1;
}
.breadcrumb-link {
  color: #666;
  text-decoration: none;
  font-size: 13px;
  transition: color 0.2s;
}
.breadcrumb-link:hover {
  color: #c67b5c;
}
.breadcrumb-current {
  color: #333;
  font-size: 13px;
  font-weight: 500;
}

/* 子视图容器 */
.main-content {
  flex: 1;
  overflow-y: auto;
  background: #fbf7f0;
}

/* ── 移动端侧栏 ──────────────────────────────────────────── */
@media (max-width: 767px) {
  .testing-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 100;
  }
  .testing-sidebar.sidebar-mobile-open {
    transform: translateX(0);
  }
}
</style>
