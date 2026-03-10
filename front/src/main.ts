/*
 * @Author: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @Date: 2025-05-02 16:46:07
 * @LastEditors: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @LastEditTime: 2025-07-22 22:07:01
 * @FilePath: \performance\src\main.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import { createVueRouter } from './routers/router'
import { setupRouterGuards } from './routers/index'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import './assets/main.css'
import './assets/libs.css'
import 'nprogress/nprogress.css' // 引入nprogress样式
import * as Icons from '@element-plus/icons-vue' // 引入所有图标
const setupApp = async () => {
    const app = createApp(App)

    // 注册element Icons组件
    Object.keys(Icons).forEach(key => {
        app.component(key, Icons[key as keyof typeof Icons])
    })
    // 1. 安装 Pinia (在路由守卫使用之前)
    const pinia = createPinia()
    pinia.use(piniaPluginPersistedstate)
    app.use(pinia)

    // 2. 创建并安装路由
    const router = await createVueRouter()
    app.use(router)

    // 3. 设置路由守卫 (在路由安装之后)
    setupRouterGuards(router)

    // 4. 安装其他插件
    app.use(ElementPlus)

    // 5. 挂载 App
    app.mount('#app')
}

setupApp()
