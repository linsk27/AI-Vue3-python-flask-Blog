import { RouteRecordRaw } from 'vue-router'

export default [
  {
    path: '/dashboard',
    component: () => import('@/views/dashboard/index.vue'),
    meta: {
      title: '数据分析看板'
    },
    children: [
      {
        path: 'personal',
        component: () => import('@/views/dashboard/personal.vue'),
        meta: {
          title: '个人数据看板'
        }
      },
      {
        path: 'team',
        component: () => import('@/views/dashboard/team.vue'),
        meta: {
          title: '团队数据看板'
        }
      }
    ]
  }
] as RouteRecordRaw[]
