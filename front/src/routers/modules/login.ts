import { RouteRecordRaw } from 'vue-router'

const loginRouters: Array<RouteRecordRaw> = [
    {
        path: '/login',
        name: 'login',
        component: () => import('@/views/login.vue'),
        meta: { title: '登录' }
    }
]
export default loginRouters
