import { RouteRecordRaw } from 'vue-router'

export default [
  {
    path: '/ai-center',
    component: () => import('@/views/ai-center/index.vue'),
    meta: {
      title: 'AI中心'
    },
    children: [
      {
        path: 'chat',
        component: () => import('@/views/ai-center/chat.vue'),
        meta: {
          title: 'AI聊天'
        }
      },
      {
        path: 'summary',
        component: () => import('@/views/ai-center/summary.vue'),
        meta: {
          title: '智能摘要'
        }
      }
    ]
  }
] as RouteRecordRaw[]
