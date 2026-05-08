import { createApp } from 'vue'
import App from './App.vue'
import { createVueRouter } from './routers/router'
import { setupRouterGuards } from './routers/index'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import {
    ElAvatar,
    ElBadge,
    ElButton,
    ElCard,
    ElDatePicker,
    ElDialog,
    ElDropdown,
    ElDropdownItem,
    ElDropdownMenu,
    ElEmpty,
    ElIcon,
    ElInput,
    ElLoading,
    ElOption,
    ElPopconfirm,
    ElPopover,
    ElSelect,
    ElSlider,
    ElSwitch,
    ElTable,
    ElTableColumn,
    ElTag
} from 'element-plus'
import './assets/main.css'
import './assets/libs.css'
import 'nprogress/nprogress.css'

document.documentElement.dataset.theme = 'light'
localStorage.removeItem('theme')

const elementComponents = [
    ElAvatar,
    ElBadge,
    ElButton,
    ElCard,
    ElDatePicker,
    ElDialog,
    ElDropdown,
    ElDropdownItem,
    ElDropdownMenu,
    ElEmpty,
    ElIcon,
    ElInput,
    ElOption,
    ElPopconfirm,
    ElPopover,
    ElSelect,
    ElSlider,
    ElSwitch,
    ElTable,
    ElTableColumn,
    ElTag
]

const setupApp = async () => {
    const app = createApp(App)

    elementComponents.forEach(component => app.use(component))
    app.use(ElLoading)

    const pinia = createPinia()
    pinia.use(piniaPluginPersistedstate)
    app.use(pinia)

    const router = await createVueRouter()
    app.use(router)
    setupRouterGuards(router)

    app.mount('#app')
}

setupApp()
