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
import authApi from '@/api/modules/auth'

export const setupRouterGuards = (router: Router) => {
    const { message } = useElMessage()

    router.beforeEach(async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
        NProgress.start()
        const globalStore = useGlobalStore()
        const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
        const requiredPermissions = to.matched.flatMap(record => {
            const permissions = record.meta.permissions
            return Array.isArray(permissions) ? permissions as string[] : []
        })
        const anyPermissions = to.matched.flatMap(record => {
            const permissions = record.meta.anyPermissions
            return Array.isArray(permissions) ? permissions as string[] : []
        })

        if (requiresAuth && !globalStore.token) {
            message.warning('请先登录')
            next({ path: '/login', query: { redirect: to.fullPath } })
            NProgress.done()
            return
        }

        const needsPermissionSnapshot = requiredPermissions.length > 0 || anyPermissions.length > 0
        if (globalStore.token && (!globalStore.userInfo?.id || !Array.isArray(globalStore.userInfo.permissions) || needsPermissionSnapshot)) {
            try {
                const userInfo = await authApi.getUserInfo()
                if (userInfo) {
                    globalStore.setLoginInfo(globalStore.token, {
                        ...userInfo,
                        token: globalStore.token
                    })
                }
            } catch (error: any) {
                globalStore.clearLoginInfo()
                if (requiresAuth) {
                    message.warning('登录状态已失效，请重新登录')
                    next({ path: '/login', query: { redirect: to.fullPath } })
                    NProgress.done()
                    return
                }
            }
        }

        const userInfo = globalStore.userInfo
        const isAdmin = userInfo?.role === 'admin'
        const permissions = userInfo?.permissions || []
        const hasAllRequired = !requiredPermissions.length || requiredPermissions.every(permission => permissions.includes(permission))
        const hasAnyRequired = !anyPermissions.length || anyPermissions.some(permission => permissions.includes(permission))

        if (globalStore.token && userInfo && !isAdmin && (!hasAllRequired || !hasAnyRequired)) {
            message.warning('当前账号无权访问该页面')
            next({ path: '/403', query: { from: to.fullPath } })
            NProgress.done()
            return
        }

        if (to.path === '/login' && globalStore?.token) {
            const redirect = typeof to.query.redirect === 'string' ? to.query.redirect : '/'
            next({ path: redirect })
            NProgress.done()
            return
        }

        next()
    })

    router.afterEach(() => {
        NProgress.done()
    })
}
