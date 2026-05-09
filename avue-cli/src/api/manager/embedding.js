import request from '@/axios'

export const getConfig = () => {
    return request({
        url: '/api/ai/embedding-config',
        method: 'get'
    })
}

export const saveConfig = data => {
    return request({
        url: '/api/ai/embedding-config',
        method: 'post',
        data
    })
}

export const validateConfig = data => {
    return request({
        url: '/api/ai/embedding-config/validate',
        method: 'post',
        data
    })
}
