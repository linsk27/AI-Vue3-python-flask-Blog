import { RouteRecordRaw } from 'vue-router'

export default [
    {
        path: '/context-packs',
        component: () => import('@/views/context-packs/index.vue'),
        meta: {
            title: 'Context Packs',
            requiresAuth: true
        }
    }
] as RouteRecordRaw[]
