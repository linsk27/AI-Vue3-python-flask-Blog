import request from '@/axios'

export const getArticles = () => {
    return request({
        url: '/api/articles',
        method: 'get'
    })
}

export const getUsers = () => {
    return request({
        url: '/api/users',
        method: 'get'
    })
}

export const getAiConfigs = () => {
    return request({
        url: '/api/ai/configs',
        method: 'get'
    })
}

export const getContextStats = () => {
    return request({
        url: '/api/context-packs/stats',
        method: 'get'
    })
}

export const getSystemSelfCheck = () => {
    return request({
        url: '/api/system/self-check',
        method: 'get'
    })
}
