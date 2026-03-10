import request from '@/axios'

export const getList = params => {
    return request({
        url: '/api/users',
        method: 'get',
        params
    })
}

export const add = row => {
    return request({
        url: '/api/register',
        method: 'post',
        data: row
    })
}

export const update = row => {
    return request({
        url: `/api/users/${row.id}`,
        method: 'put',
        data: row
    })
}

export const del = row => {
    return request({
        url: `/api/users/${row.id}`,
        method: 'delete'
    })
}
