import request from '@/axios'

export const getList = () => {
    return request({
        url: '/api/ai/configs',
        method: 'get'
    })
}

export const add = data => {
    return request({
        url: '/api/ai/configs',
        method: 'post',
        data
    })
}

export const update = data => {
    if (!data || !data.id) {
        return Promise.reject(new Error('ID is required for update'))
    }
    return request({
        url: `/api/ai/configs/${data.id}`,
        method: 'put',
        data
    })
}

export const del = data => {
    if (!data || !data.id) {
        return Promise.reject(new Error('ID is required for delete'))
    }
    return request({
        url: `/api/ai/configs/${data.id}`,
        method: 'delete'
    })
}

export const activate = id => {
    if (!id) {
        return Promise.reject(new Error('ID is required for activate'))
    }
    return request({
        url: `/api/ai/configs/${id}/activate`,
        method: 'post'
    })
}

export const getModels = () => {
    return request({
        url: '/api/ai/models',
        method: 'get'
    })
}
