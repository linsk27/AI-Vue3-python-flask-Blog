import { RouteRecordRaw } from 'vue-router'

export default [
  {
    path: '/ai-center',
    component: () => import('@/views/ai-center/index.vue'),
    meta: {
      title: 'AI Center',
      requiresAuth: true,
      anyPermissions: ['ai:access', 'ai:manage']
    },
    children: [
      {
        path: 'chat',
        component: () => import('@/views/ai-center/chat.vue'),
        meta: {
          title: 'AI Chat',
          requiresAuth: true,
          permissions: ['ai:access']
        }
      },
      {
        path: 'summary',
        component: () => import('@/views/ai-center/summary.vue'),
        meta: {
          title: 'AI Summary',
          requiresAuth: true,
          permissions: ['ai:access']
        }
      }
    ]
  }
] as RouteRecordRaw[]