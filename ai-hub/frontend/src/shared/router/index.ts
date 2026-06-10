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
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/shared/views/HomeView.vue'),
    },
  ],
})

export default router
