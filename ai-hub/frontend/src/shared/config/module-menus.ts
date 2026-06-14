/**
 * 模块侧边栏菜单配置
 *
 * 所有模块的侧边栏菜单定义集中管理。
 * 支持两种展示模式：
 *   - collapsible：可折叠分组，同一时间仅一组展开（AI测试）
 *   - flat：扁平列表，所有项平铺展示（系统管理/配置中心）
 *
 * 参考来源：
 *   - 原型设计: aihub-pic/（55个HTML页面）
 *   - 竞品testhub: testhub/frontend/src/layout/index.vue
 */

export interface MenuItem {
  icon: string
  label: string
  path: string
  /** 标记为待实现（灰色显示） */
  disabled?: boolean
}

export interface MenuGroup {
  key: string
  icon: string
  label: string
  items: MenuItem[]
  count?: number
}

export interface ModuleConfig {
  /** 模块中文名 */
  name: string
  /** 侧边栏品牌渐变色（如 '#C67B5C'） */
  accentColor: string
  /** 展示模式 */
  mode: 'collapsible' | 'flat'
  /** 菜单分组 */
  groups: MenuGroup[]
}

/** 模块菜单配置映射表（key = 路由路径的第一段） */
export const MODULE_MENUS: Record<string, ModuleConfig> = {
  // ── AI 智能测试（可折叠分组） ─────────────────────────────
  // 对应原型 01-AI智能测试 + 05-测试管理
  // 参考 testhub: ai-generation 模块
  'ai-testing': {
    name: 'AI 测试管理',
    accentColor: '#C67B5C',
    mode: 'collapsible',
    groups: [
      {
        key: 'dashboard',
        icon: '📊',
        label: '数据看板',
        items: [
          { icon: '📈', label: '测试总览', path: '/ai-testing/dashboard' },
        ],
      },
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
          { icon: '📋', label: '用例列表', path: '/ai-testing/testcases' },
          { icon: '🔍', label: '用例评审', path: '/ai-testing/reviews' },
        ],
      },
      {
        key: 'generation',
        icon: '🤖',
        label: 'AI 智能生成',
        items: [
          { icon: '⚡', label: 'AI 用例生成', path: '/ai-testing/generate' },
          { icon: '📊', label: 'AI 生成记录', path: '/ai-testing/generate/records' },
        ],
      },
      {
        key: 'evaluator',
        icon: '🧠',
        label: 'AI 评测师',
        items: [
          { icon: '🧠', label: 'AI 评测师', path: '/ai-testing/ai-tester' },
          { icon: '⚙️', label: '评测师配置', path: '/ai-testing/ai-tester/config' },
        ],
      },
      {
        key: 'report',
        icon: '📊',
        label: '测试报告',
        items: [
          { icon: '📑', label: '测试报告', path: '/ai-testing/reports' },
        ],
      },
      {
        key: 'ai-config',
        icon: '⚙️',
        label: 'AI 配置',
        items: [
          { icon: '🤖', label: 'AI 模型配置', path: '/ai-testing/config/model' },
          { icon: '📝', label: 'AI 提示词配置', path: '/ai-testing/config/prompt' },
          { icon: '⚡', label: '生成行为配置', path: '/ai-testing/config/generation' },
          { icon: '🖥️', label: '智能模式配置', path: '/ai-testing/config/ai-mode' },
        ],
      },
    ],
  },

  // ── 系统管理（扁平列表） ────────────────────────────────
  // 对应原型 09-系统管理
  'system': {
    name: '系统管理',
    accentColor: '#C67B5C',
    mode: 'flat',
    groups: [
      {
        key: 'main',
        icon: '⚙️',
        label: '系统管理',
        items: [
          { icon: '📊', label: '系统概览', path: '/system' },
          { icon: '👥', label: '用户管理', path: '/system/users' },
          { icon: '🔐', label: '角色管理', path: '/system/roles' },
          { icon: '📋', label: '审计日志', path: '/system/audit-logs' },
          { icon: '📝', label: '操作日志', path: '/system/operation-logs' },
          { icon: '⚙️', label: '系统设置', path: '/system/settings' },
        ],
      },
    ],
  },

  // ── 配置中心（扁平列表） ────────────────────────────────
  // 对应原型 06-配置中心
  'config': {
    name: '配置中心',
    accentColor: '#C67B5C',
    mode: 'flat',
    groups: [
      {
        key: 'main',
        icon: '⚙️',
        label: '配置管理',
        items: [
          { icon: '🤖', label: 'AI 模型配置', path: '/config/ai-model' },
          { icon: '📝', label: '提示词配置', path: '/config/prompt' },
          { icon: '⚡', label: '生成行为配置', path: '/config/generation' },
          { icon: '🖥️', label: 'UI 环境配置', path: '/config/ui-env' },
          { icon: '📱', label: 'APP 环境配置', path: '/config/app-env' },
          { icon: '💬', label: 'AI 聊天室配置', path: '/config/chat' },
        ],
      },
    ],
  },
}

/** 根据路由路径获取模块 key（如 '/ai-testing/dashboard' → 'ai-testing'） */
export function getModuleKeyFromPath(path: string): string | null {
  const parts = path.split('/').filter(Boolean)
  if (parts.length === 0) return null
  const key = parts[0]
  return MODULE_MENUS[key] ? key : null
}

/** 根据路由路径获取模块配置 */
export function getModuleConfigFromPath(path: string): ModuleConfig | null {
  const key = getModuleKeyFromPath(path)
  return key ? MODULE_MENUS[key] : null
}
