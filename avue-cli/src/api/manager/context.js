import request from '@/axios'

export const getList = params => {
    return request({
        url: '/api/context-packs',
        method: 'get',
        params
    })
}

export const getStats = () => {
    return request({
        url: '/api/context-packs/stats',
        method: 'get'
    })
}

export const getRagIndex = id => {
    return request({
        url: `/api/context-packs/${id}/rag-index`,
        method: 'get'
    })
}

export const rebuildRagIndex = id => {
    return request({
        url: `/api/context-packs/${id}/rag-index/rebuild`,
        method: 'post'
    })
}

export const buildEmbeddings = (id, data = {}) => {
    return request({
        url: `/api/context-packs/${id}/rag-index/embeddings`,
        method: 'post',
        data
    })
}
