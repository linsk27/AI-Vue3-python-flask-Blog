/*
 * @Author: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @Date: 2025-07-16 15:40:02
 * @LastEditors: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @LastEditTime: 2025-07-22 22:08:05
 * @FilePath: \performance\src\routers\router.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
// src/routers/router.ts
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const modules = import.meta.glob('./modules/*.ts')

export const createVueRouter = async () => {
    const routerArray: RouteRecordRaw[] = []
    for (const key of Object.keys(modules)) {
        const mod = (await modules[key]()) as { default: RouteRecordRaw[] }
        if (Array.isArray(mod.default)) {
            routerArray.push(...mod.default)
        }
    }

    const routes: Array<RouteRecordRaw> = [
        {
            path: '/',
            component: () => import('@/views/index.vue'),
            alias: ['/index', '/home']
        },
        ...routerArray
    ]

    const router = createRouter({
        history: createWebHistory(),
        routes,
        scrollBehavior(to, from, savedPosition) {
            if (savedPosition) {
                return savedPosition
            } else {
                return { top: 0 }
            }
        }
    })
    return router
}
