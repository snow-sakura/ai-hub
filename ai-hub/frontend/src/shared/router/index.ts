import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/shared/views/HomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/shared/views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/shared/views/RegisterView.vue'),
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('@/modules/chat/views/ChatView.vue'),
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: () => import('@/modules/knowledge/views/KnowledgeView.vue'),
    },
    {
      path: '/comfort',
      name: 'comfort',
      component: () => import('@/modules/comfort/views/ComfortView.vue'),
    },
    {
      path: '/emotion-dashboard',
      name: 'emotion-dashboard',
      component: () => import('@/modules/comfort/views/EmotionDashboardView.vue'),
    },
    // ── AI 测试管理模块路由（嵌套于侧栏布局） ──────────────
    {
      path: '/ai-testing',
      component: () => import('@/modules/ai_testing/components/layout/TestingLayout.vue'),
      children: [
        { path: '', redirect: '/ai-testing/dashboard' },
        {
          path: 'dashboard',
          name: 'testing-dashboard',
          component: () => import('@/modules/ai_testing/views/DashboardView.vue'),
        },
        // ── 项目管理 ─────────────────────────────────────
        {
          path: 'projects',
          name: 'testing-projects',
          component: () => import('@/modules/ai_testing/views/ProjectListView.vue'),
        },
        {
          path: 'projects/versions',
          name: 'testing-project-versions',
          component: () => import('@/modules/ai_testing/views/ProjectVersionsView.vue'),
        },
        {
          path: 'projects/members',
          name: 'testing-project-members',
          component: () => import('@/modules/ai_testing/views/ProjectMembersView.vue'),
        },
        {
          path: 'projects/:id',
          name: 'testing-project-detail',
          component: () => import('@/modules/ai_testing/views/ProjectDetailView.vue'),
        },
        // ── 用例管理 ─────────────────────────────────────
        {
          path: 'testcases',
          name: 'testing-testcases',
          component: () => import('@/modules/ai_testing/views/TestCaseListView.vue'),
        },
        {
          path: 'testcases/create',
          name: 'testing-testcase-create',
          component: () => import('@/modules/ai_testing/views/TestCaseFormView.vue'),
        },
        {
          path: 'testcases/:id',
          name: 'testing-testcase-detail',
          component: () => import('@/modules/ai_testing/views/TestCaseDetailView.vue'),
        },
        {
          path: 'testcases/:id/edit',
          name: 'testing-testcase-edit',
          component: () => import('@/modules/ai_testing/views/TestCaseFormView.vue'),
        },
        // ── 评审管理 ─────────────────────────────────────
        {
          path: 'reviews',
          name: 'testing-reviews',
          component: () => import('@/modules/ai_testing/views/ReviewListView.vue'),
        },
        {
          path: 'reviews/create',
          name: 'testing-review-create',
          component: () => import('@/modules/ai_testing/views/ReviewFormView.vue'),
        },
        {
          path: 'reviews/:id',
          name: 'testing-review-detail',
          component: () => import('@/modules/ai_testing/views/ReviewDetailView.vue'),
        },
        // ── AI 智能生成 ──────────────────────────────────
        {
          path: 'generate',
          name: 'testing-generate',
          component: () => import('@/modules/ai_testing/views/GenerationView.vue'),
        },
        {
          path: 'generate/tasks/:id',
          name: 'testing-task-detail',
          component: () => import('@/modules/ai_testing/views/TaskDetailView.vue'),
        },
        {
          path: 'generate/records',
          name: 'testing-generate-records',
          component: () => import('@/modules/ai_testing/views/GenerationRecordsView.vue'),
        },
        // ── AI 评测师 ────────────────────────────────────
        {
          path: 'ai-tester',
          name: 'testing-ai-tester',
          component: () => import('@/modules/ai_testing/views/AITesterView.vue'),
        },
        {
          path: 'ai-tester/config',
          name: 'testing-ai-tester-config',
          component: () => import('@/modules/ai_testing/views/AITesterConfigView.vue'),
        },
        // ── 测试报告 ─────────────────────────────────────
        {
          path: 'reports',
          name: 'testing-reports',
          component: () => import('@/modules/ai_testing/views/TestReportView.vue'),
        },
        // ── 配置中心（独立模块，Phase 3 实现） ──────────────
        {
          path: 'config',
          redirect: '/ai-testing/config/model',
        },
      ],
    },
    // ── 配置中心模块路由（嵌套于侧栏布局） ─────────────────
    {
      path: '/config',
      component: () => import('@/modules/config_center/ConfigLayout.vue'),
      children: [
        { path: '', redirect: '/config/ai-model' },
        {
          path: 'ai-model',
          name: 'config-ai-model',
          component: () => import('@/modules/config_center/views/AIModelConfigView.vue'),
        },
        {
          path: 'prompt',
          name: 'config-prompt',
          component: () => import('@/modules/config_center/views/PromptConfigView.vue'),
        },
        {
          path: 'generation',
          name: 'config-generation',
          component: () => import('@/modules/config_center/views/GenerationBehaviorView.vue'),
        },
        {
          path: 'chat',
          name: 'config-chat',
          component: () => import('@/modules/config_center/views/ConfigChatView.vue'),
        },
        {
          path: 'ui-env',
          name: 'config-ui-env',
          component: () => import('@/modules/config_center/views/UiEnvConfigView.vue'),
        },
        {
          path: 'app-env',
          name: 'config-app-env',
          component: () => import('@/modules/config_center/views/AppEnvConfigView.vue'),
        },
      ],
    },

    // ── 系统管理模块路由（嵌套子路由） ──────────────────────
    {
      path: '/system',
      component: () => import('@/modules/system/components/layout/SystemLayout.vue'),
      children: [
        { path: '', name: 'system', component: () => import('@/modules/system/views/DashboardView.vue') },
        { path: 'users', name: 'system-users', component: () => import('@/modules/system/views/UserListView.vue') },
        { path: 'roles', name: 'system-roles', component: () => import('@/modules/system/views/RoleListView.vue') },
        { path: 'audit-logs', name: 'system-audit-logs', component: () => import('@/modules/system/views/AuditLogView.vue') },
        { path: 'operation-logs', name: 'system-operation-logs', component: () => import('@/modules/system/views/OperationLogView.vue') },
        { path: 'settings', name: 'system-settings', component: () => import('@/modules/system/views/SettingsView.vue') },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/shared/views/NotFoundView.vue'),
    },
  ],
})

// ── 路由守卫：未登录自动跳转登录页 ──────────────────────────
const WHITE_LIST = ['/login', '/register']

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (token || WHITE_LIST.includes(to.path)) {
    next()
  } else {
    next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
  }
})

export default router
