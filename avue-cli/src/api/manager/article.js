import request from '@/axios'

export const getList = params => {
    return request({
        url: '/api/articles',
        method: 'get',
        params
    })
}

export const getDetail = id => {
    return request({
        url: `/api/articles/${id}`,
        method: 'get'
    })
}

export const add = row => {
    return request({
        url: '/api/articles',
        method: 'post',
        data: row
    })
}

export const update = row => {
    return request({
        url: `/api/articles/${row.id}`,
        method: 'put',
        data: row
    })
}

export const del = row => {
    return request({
        url: `/api/articles/${row.id}`,
        method: 'delete'
    })
}
