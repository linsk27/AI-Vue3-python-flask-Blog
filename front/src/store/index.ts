import { IUserInfo } from '@/api/modules/auth/interface'
import { defineStore } from 'pinia'
import piniaPersistConfig from './config/piniaPersist'

interface GlobalState {
    token: string
    userInfo: IUserInfo | null
    created_at?: string
    themeConfig: {
        breadcrumb: boolean
        tabs: boolean
        footer: boolean
    }
}

export const useGlobalStore = defineStore('globalStore', {
    state: (): GlobalState => ({
        token: '',
        userInfo: null,
        themeConfig: {
            breadcrumb: true,
            tabs: true,
            footer: true
        }
    }),
    actions: {
        // 统一登录信息设置
        setLoginInfo(token: string, userInfo: IUserInfo | null) {
            this.token = token
            this.userInfo = userInfo
        },

        // 清除登录信息
        clearLoginInfo() {
            this.token = ''
            this.userInfo = null
        },

        // 更新主题配置
        updateThemeConfig(config: Partial<GlobalState['themeConfig']>) {
            this.themeConfig = { ...this.themeConfig, ...config }
        }
    },
    persist: piniaPersistConfig('GlobalStore')
})
