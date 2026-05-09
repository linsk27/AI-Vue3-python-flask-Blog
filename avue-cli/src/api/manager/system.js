import request from '@/axios'

export const runSelfCheck = () => {
    return request({
        url: '/api/system/self-check',
        method: 'post'
    })
}

export const getSelfCheck = () => {
    return request({
        url: '/api/system/self-check',
        method: 'get'
    })
}

export const getSelfCheckHistory = () => {
    return request({
        url: '/api/system/self-check/history',
        method: 'get'
    })
}
