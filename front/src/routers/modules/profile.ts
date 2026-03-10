import { useElMessage } from '@/hooks/useMessage'
import { useGlobalStore } from '@/store'
import { RouteRecordRaw } from 'vue-router'
const globalStore = useGlobalStore()
const { message } = useElMessage()
const personalCenterRouters: Array<RouteRecordRaw> = [
    {
        path: '/profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人中心' },
        beforeEnter: (to, from) => {
            if (!globalStore.token) {
                message.warning('请先登录')
                return { name: 'login' }
            }
            return true
        }
    }
]
export default personalCenterRouters
