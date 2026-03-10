import { RouteRecordRaw } from 'vue-router'

const performanceRouters: Array<RouteRecordRaw> = [
    {
        path: '/performance',
        component: () => import('@/views/performance/index.vue'),
        children: [
            {
                path: 'VirtualList',
                // 路由命名
                name: 'member',
                component: () => import('@/views/performance/components/VirtualList.vue'),
                meta: { title: '虚拟列表示例' }
            },
            {
                path: 'KeepAlive',
                component: () => import('@/views/performance/components/KeepAlive.vue'),
                meta: { title: '缓存组件示例' }
            },
            {
                path: 'ImageCompression',
                component: () => import('@/views/performance/components/ImageCompression.vue'),
                meta: { title: '图片压缩示例' }
            }
        ]
    }
]
export default performanceRouters
