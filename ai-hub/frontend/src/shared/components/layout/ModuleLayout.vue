<template>
  <div class="module-layout">
    <!-- 侧边栏 -->
    <aside
      class="module-sidebar"
      :class="{ 'sidebar-mobile-open': isMobile && mobileSidebarOpen }"
    >
      <!-- 品牌区 -->
      <div class="sidebar-brand">
        <span class="brand-icon" :style="{ background: brandGradient }">{{ moduleConfig ? moduleConfig.name.charAt(0) : 'M' }}</span>
        <span class="brand-text">{{ moduleConfig?.name || '' }}</span>
        <button v-if="isMobile" class="sidebar-close" @click="mobileSidebarOpen = false">✕</button>
      </div>

      <!-- 菜单区：collapsible 模式 -->
      <div v-if="moduleConfig?.mode === 'collapsible'" class="sidebar-menu">
        <div v-for="group in (moduleConfig?.groups ?? [])" :key="group.key" class="menu-group">
          <div class="menu-group-header" :style="menuGroupHeaderStyle" @click="toggleGroup(group.key)">
            <span class="group-icon">{{ group.icon }}</span>
            <span class="group-label">{{ group.label }}</span>
            <span class="group-count" v-if="group.count" :style="{ background: countBgStyle, color: accentColor }">{{ group.count }}</span>
            <span class="group-arrow" :class="{ expanded: expandedGroups[group.key] }"></span>
          </div>
          <transition name="menu-slide">
            <div v-show="expandedGroups[group.key]" class="menu-items">
              <router-link
                v-for="item in group.items"
                :key="item.path"
                :to="item.path"
                class="menu-item"
                :class="{ active: isActive(item.path) }"
                :style="menuItemActiveStyle"
                @click="onMenuItemClick"
              >
                <span class="item-icon">{{ item.icon }}</span>
                <span class="item-label">{{ item.label }}</span>
              </router-link>
            </div>
          </transition>
        </div>
      </div>

      <!-- 菜单区：flat 模式（扁平列表） -->
      <div v-else class="sidebar-menu sidebar-flat">
        <div v-for="group in moduleConfig?.groups" :key="group.key" class="flat-group">
          <div class="flat-group-label" v-if="group.label && (moduleConfig?.groups.length ?? 0) > 1">{{ group.label }}</div>
          <router-link
            v-for="item in group.items"
            :key="item.path"
            :to="item.path"
            class="flat-item"
            :class="{ active: isActive(item.path) }"
            :style="menuItemActiveStyle"
            @click="onMenuItemClick"
          >
            <span class="item-icon">{{ item.icon }}</span>
            <span class="item-label">{{ item.label }}</span>
          </router-link>
        </div>
      </div>

      <!-- 底部：返回首页 -->
      <div class="sidebar-footer">
        <router-link to="/" class="sidebar-home-link" :style="{ color: moduleConfig?.accentColor, '--home-hover-bg': moduleConfig?.accentColor }">
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
    <main class="module-main">
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
        <div class="topbar-right">
          <n-button text size="tiny" class="lang-switch" @click="toggleLang">
            {{ currentLang === 'zh-CN' ? 'EN' : '中文' }}
          </n-button>
        </div>
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
import { useI18n } from '@/locales'
import { MODULE_MENUS, type ModuleConfig } from '@/shared/config/module-menus'

const props = withDefaults(defineProps<{
  module: string
}>(), {
  module: '',
})

const route = useRoute()
const { isMobile } = useResponsive()
const { locale: i18nLocale, setLocale } = useI18n()

const currentLang = computed(() => i18nLocale.value as string)

function toggleLang() {
  const next = currentLang.value === 'zh-CN' ? 'en-US' : 'zh-CN'
  setLocale(next as 'zh-CN' | 'en-US')
}

const mobileSidebarOpen = ref(false)

// ── 模块配置 ────────────────────────────────────────────────
const moduleConfig = computed<ModuleConfig | null>(() => {
  return MODULE_MENUS[props.module] || null
})

const accentColor = computed(() => moduleConfig.value?.accentColor || '#C67B5C')

const brandGradient = computed(() =>
  `linear-gradient(135deg, ${accentColor.value}, ${adjustColor(accentColor.value, 20)})`
)

// ── collapsible 模式的展开/折叠互斥状态 ─────────────────────
const expandedGroups = reactive<Record<string, boolean>>({})

// 初始化展开状态：所有组收起
watch(
  () => moduleConfig.value,
  (config) => {
    if (!config) return
    config.groups.forEach(g => {
      if (!(g.key in expandedGroups)) {
        expandedGroups[g.key] = false
      }
    })
  },
  { immediate: true },
)

function toggleGroup(key: string) {
  const isCurrentlyExpanded = expandedGroups[key]
  Object.keys(expandedGroups).forEach(k => { expandedGroups[k] = false })
  if (!isCurrentlyExpanded) {
    expandedGroups[key] = true
  }
}

// 路由变化时自动展开所在组（互斥，仅 collapsible 模式）
watch(
  () => route.path,
  (path) => {
    const config = moduleConfig.value
    if (!config || config.mode !== 'collapsible') return

    Object.keys(expandedGroups).forEach(k => { expandedGroups[k] = false })
    for (const group of config.groups) {
      for (const item of group.items) {
        if (path.startsWith(item.path)) {
          expandedGroups[group.key] = true
          return
        }
      }
    }
    // 默认展开第一组
    if (config.groups.length > 0) {
      expandedGroups[config.groups[0].key] = true
    }
  },
  { immediate: true },
)

// ── 菜单高亮 ────────────────────────────────────────────────
function isActive(itemPath: string): boolean {
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

function findMenuItemLabel(path: string): string | null {
  const config = moduleConfig.value
  if (!config) return null
  for (const group of config.groups) {
    for (const item of group.items) {
      if (path.startsWith(item.path) || item.path === path) {
        return item.label
      }
    }
  }
  return null
}

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
  const config = moduleConfig.value
  if (!config) return []

  const path = route.path
  const items: BreadcrumbItem[] = []

  // 第一级：模块名
  const modulePath = '/' + props.module
  items.push({ label: config.name, path: modulePath })

  // 第二级：匹配的子页面标签
  const label = findMenuItemLabel(path)
  if (label && findMenuItemLabel(modulePath) !== label) {
    items.push({ label })
  }

  return items
})

// ── 动态样式 ─────────────────────────────────────────────────
const menuGroupHeaderStyle = computed(() => ({
  '--group-hover-bg': `${accentColor.value}0f`, // 6% opacity
}))

const menuItemActiveStyle = computed(() => ({
  '--item-active-color': accentColor.value,
  '--item-active-bg': `${accentColor.value}14`, // 8% opacity
  '--item-hover-bg': `${accentColor.value}0f`, // 6% opacity
}))

const countBgStyle = computed(() => `${accentColor.value}1f`) // 12% opacity

// ── 工具函数 ─────────────────────────────────────────────────
function adjustColor(hex: string, amount: number): string {
  const num = parseInt(hex.replace('#', ''), 16)
  const r = Math.min(255, Math.max(0, (num >> 16) + amount))
  const g = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + amount))
  const b = Math.min(255, Math.max(0, (num & 0x0000FF) + amount))
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`
}
</script>

<style scoped>
/* ── 布局容器 ───────────────────────────────────────────── */
.module-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #fbf7f0;
}

/* ── 侧边栏 ──────────────────────────────────────────── */
.module-sidebar {
  width: 240px;
  min-width: 240px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #F6F0E7;
  color: #5C4A38;
  overflow-y: auto;
  z-index: 100;
  border-right: 1px solid rgba(180, 150, 120, 0.15);
}

/* 品牌区 */
.sidebar-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px 20px 16px;
  border-bottom: 1px solid rgba(180, 150, 120, 0.12);
  flex-shrink: 0;
  background: linear-gradient(135deg, #EDE4D6 0%, #F6F0E7 100%);
}
.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  flex-shrink: 0;
  box-shadow: 0 3px 8px rgba(0,0,0,0.15);
}
.brand-text {
  font-size: 17px;
  font-weight: 800;
  color: #3D2E1F;
  letter-spacing: 0.04em;
}

/* 菜单区 */
.sidebar-menu {
  flex: 1;
  padding: 8px 0;
  overflow-y: auto;
}

/* 底部：返回首页 */
.sidebar-footer {
  flex-shrink: 0;
  border-top: 1px solid rgba(180, 150, 120, 0.15);
  padding: 12px 16px;
}
.sidebar-home-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  cursor: pointer;
  border-radius: 8px;
  background: rgba(0,0,0,0.03);
}
.sidebar-home-link:hover {
  color: #fff !important;
  background: var(--home-hover-bg, #C67B5C) !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.home-icon {
  font-size: 18px;
  line-height: 1;
}
.home-label {
  font-size: 14px;
}

/* ── collapsible 模式 ─────────────────────────────────── */
.menu-group {
  margin-bottom: 2px;
}
.menu-group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
  border-radius: 0;
}
.menu-group-header:hover {
  background: var(--group-hover-bg, rgba(198, 123, 92, 0.06));
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
  color: #5C4A38;
  letter-spacing: 0.02em;
}
.group-count {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 600;
}
.group-arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  flex-shrink: 0;
}
.group-arrow::before {
  content: '';
  display: block;
  width: 7px;
  height: 7px;
  border-right: 1.5px solid #B5A590;
  border-bottom: 1.5px solid #B5A590;
  transform: rotate(-45deg);
  transition: transform 0.25s ease;
}
.group-arrow.expanded::before {
  transform: rotate(45deg);
}

/* 菜单项（collapsible 子项） */
.menu-items {
  padding: 2px 0;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 24px 9px 44px;
  text-decoration: none;
  color: #7A6855;
  font-size: 14px;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  cursor: pointer;
}
.menu-item:hover {
  color: #3D2E1F;
  background: var(--item-hover-bg, rgba(198, 123, 92, 0.06));
}
.menu-item.active {
  color: var(--item-active-color, #C67B5C);
  background: var(--item-active-bg, rgba(198, 123, 92, 0.08));
  border-left-color: var(--item-active-color, #C67B5C);
  font-weight: 500;
}
.item-icon {
  font-size: 14px;
  width: 18px;
  text-align: center;
}
.item-label {
  font-size: 14px;
}

/* ── flat 模式 ─────────────────────────────────────── */
.flat-group {
  margin-bottom: 4px;
}
.flat-group-label {
  padding: 10px 24px 4px;
  font-size: 12px;
  font-weight: 600;
  color: #8B7355;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.flat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 24px 9px 24px;
  text-decoration: none;
  color: #7A6855;
  font-size: 14px;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  cursor: pointer;
}
.flat-item:hover {
  color: #3D2E1F;
  background: var(--item-hover-bg, rgba(198, 123, 92, 0.06));
}
.flat-item.active {
  color: var(--item-active-color, #C67B5C);
  background: var(--item-active-bg, rgba(198, 123, 92, 0.08));
  border-left-color: var(--item-active-color, #C67B5C);
  font-weight: 500;
}

/* ── 菜单展开/折叠动画 ──────────────────────────────── */
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

/* ── 菜单组分隔线（collapsible 模式） ─────────────── */
.menu-group + .menu-group {
  border-top: 1px solid rgba(180, 150, 120, 0.08);
  margin-top: 4px;
  padding-top: 4px;
}

/* ── 移动端遮罩 ─────────────────────────────────────── */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 99;
}

/* ── 主内容区 ───────────────────────────────────────── */
.module-main {
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
.topbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
}
.lang-switch {
  color: var(--text-secondary, #7A6855) !important;
  font-weight: 600;
  font-size: 12px !important;
  padding: 2px 8px;
  border: 1px solid rgba(180, 150, 120, 0.2);
  border-radius: 4px;
  transition: all 0.2s;
}
.lang-switch:hover {
  border-color: var(--accent, #C67B5C) !important;
  color: var(--accent, #C67B5C) !important;
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

/* ── 移动端侧栏 ──────────────────────────────────────── */
@media (max-width: 767px) {
  .module-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 100;
  }
  .module-sidebar.sidebar-mobile-open {
    transform: translateX(0);
  }
  .sidebar-close {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border: none;
    background: rgba(0,0,0,0.06);
    border-radius: 6px;
    color: #7A6855;
    font-size: 14px;
    cursor: pointer;
    margin-left: auto;
    flex-shrink: 0;
  }
  .sidebar-close:hover {
    background: rgba(198, 123, 92, 0.15);
    color: #C67B5C;
  }
}
.sidebar-close {
  display: none;
}
</style>
