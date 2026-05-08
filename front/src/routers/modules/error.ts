import { RouteRecordRaw } from 'vue-router'

export default [
    {
        path: '/403',
        component: () => import('@/views/error/Forbidden.vue'),
        meta: { title: '无权访问' }
    }
] as RouteRecordRaw[]
