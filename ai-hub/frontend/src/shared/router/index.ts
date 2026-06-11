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
    // ── AI Testing 模块路由（嵌套于侧栏布局） ──────────────
    {
      path: '/ai-testing',
      component: () => import('@/modules/ai_testing/components/layout/TestingLayout.vue'),
      children: [
        { path: '', redirect: '/ai-testing/projects' },
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
        {
          path: 'generate',
          name: 'testing-generate',
          component: () => import('@/modules/ai_testing/views/GenerationView.vue'),
        },
        {
          path: 'settings',
          name: 'testing-settings',
          component: () => import('@/modules/ai_testing/views/SettingsView.vue'),
        },
        {
          path: 'config/model',
          name: 'testing-config-model',
          component: () => import('@/modules/ai_testing/views/config/AIModelConfigView.vue'),
        },
        {
          path: 'config/prompt',
          name: 'testing-config-prompt',
          component: () => import('@/modules/ai_testing/views/config/PromptConfigView.vue'),
        },
        {
          path: 'config/generation',
          name: 'testing-config-generation',
          component: () => import('@/modules/ai_testing/views/config/GenerationConfigView.vue'),
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
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/shared/views/NotFoundView.vue'),
    },
  ],
})

export default router
