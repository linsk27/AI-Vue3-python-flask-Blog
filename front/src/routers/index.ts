/*
 * @Author: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @Date: 2025-05-02 18:46:53
 * @LastEditors: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @LastEditTime: 2025-07-22 22:06:44
 * @FilePath: \performance\src\routers\index.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */

import { useGlobalStore } from '@/store'
import NProgress from 'nprogress'
import { useElMessage } from '@/hooks/useMessage'
import { NavigationGuardNext, RouteLocationNormalized, Router } from 'vue-router'

export const setupRouterGuards = (router: Router) => {
    const { message } = useElMessage()

    router.beforeEach((to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
        NProgress.start()
        // 在这里使用 Pinia store 是安全的，因为 Pinia 已经在 main.ts 中 use() 了
        const globalStore = useGlobalStore()

        // 检查是否需要登录
        // if (!globalStore.token && to.path !== '/login') {
        //     console.log(123)
        //     // 如果没有登录，重定向到登录页面
        //     message.warning('请先登录')
        //     next({ path: '/login' })
        //     NProgress.done()
        //     return
        // }
        // ... 你的守卫逻辑 ...
        if (to.path === '/login' && globalStore?.token) {
            next({ path: '/' })
            NProgress.done()
            return
        }
        next()
    })

    router.afterEach(() => {
        NProgress.done()
    })
}
