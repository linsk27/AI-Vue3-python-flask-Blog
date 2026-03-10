import { useElMessage } from './../hooks/useMessage'
import axios, { AxiosRequestConfig, AxiosResponse } from 'axios'
import { useGlobalStore } from '@/store'
import { createVueRouter } from '@/routers/router'
const { message } = useElMessage()
const router = createVueRouter()
// 环境变量配置
const baseURL = import.meta.env.VITE_API_BASE_URL
const AppId = import.meta.env.VITE_APP_ID

class RequestHttp {
    service

    // 构造函数
    constructor(config: AxiosRequestConfig) {
        this.service = axios.create({
            baseURL,
            timeout: 120000, // 增加超时时间到120秒，以适应长文本AI生成
            withCredentials: true,
            ...config
        })

        // 请求拦截
        this.service.interceptors.request.use(
            config => {
                const globalStore = useGlobalStore()
                Object.assign(config.headers, {
                    Authorization: globalStore.token,
                    'APP-ID': AppId,
                    'Content-Type': 'application/json'
                })
                return config
            },
            error => Promise.reject(error)
        )

        // 响应拦截
        this.service.interceptors.response.use(
            (response: AxiosResponse) => {
                const { data, status } = response
                if (status === 200) return this.handleBusinessCode(data)
                return response
            },
            error => this.handleNetworkError(error)
        )
    }

    private handleBusinessCode(data: any) {
        // 处理新的返回格式 { status: number, msg: string, data?: any }
        if (data.status !== undefined) {
            if (data.status === 0) {
                return data.data || data // 成功
            } else {
                // 业务错误
                message.error(data.msg || '请求失败')
                return Promise.reject(data)
            }
        }

        // 处理旧的返回格式 { response: string, success: boolean }
        if (data.success !== undefined) {
            return data
        }

        // 默认返回数据
        return data
    }

    private async handleNetworkError(error: any) {
        if (error.message.includes('timeout')) {
            message.error('请求超时')
        } else if (!window.navigator.onLine) {
            ;(await router).replace('/500')
        }
        return Promise.reject(error)
    }

    private async jumpToLogin() {
        const globalStore = useGlobalStore()
        globalStore.setLoginInfo('', null)
        ;(await router).replace(`/login`)
    }

    // 请求方法封装
    get<T>(url: string, params?: object): Promise<T> {
        return this.service.get(url, { params }) as Promise<T>
    }
    post<T>(url: string, data?: object): Promise<T> {
        return this.service.post(url, data) as Promise<T>
    }
    put<T>(url: string, data?: object): Promise<T> {
        return this.service.put(url, data) as Promise<T>
    }
    delete<T>(url: string, params?: object): Promise<T> {
        return this.service.delete(url, { params }) as Promise<T>
    }
}
// 导出实例化的请求对象
export default new RequestHttp({})
