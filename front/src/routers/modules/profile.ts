import { RouteRecordRaw } from 'vue-router'
const personalCenterRouters: Array<RouteRecordRaw> = [
    {
        path: '/profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人中心', requiresAuth: true }
    }
]
export default personalCenterRouters
