import { IArticleParams, IArticle } from './interface'
import { ARTICLE_CREATE, ARTICLE_DETAIL, ARTICLE_UPDATE, ARTICLE_LIST, ARTICLE_DELETE, ARTICLE_TOGGLE_LIKE, ARTICLE_INCREMENT_VIEW, ARTICLE_MY_LIKES } from './url.const'
import http from '@/api'

const articleApi = {
    create: (params: IArticleParams) => {
        return http.post<{ id: number; title: string }>(ARTICLE_CREATE, params)
    },
    update: (id: number | string, params: IArticleParams) => {
        return http.put(ARTICLE_UPDATE(id), params)
    },
    delete: (id: number | string) => {
        return http.delete(ARTICLE_DELETE(id))
    },
    getDetail: (id: number | string) => {
        return http.get<IArticle>(ARTICLE_DETAIL(id))
    },
    getList: (params?: any) => {
        return http.get<IArticle[]>(ARTICLE_LIST, params)
    },
    toggleLike: (id: number | string) => {
        return http.post<{ liked: boolean; likes: number }>(ARTICLE_TOGGLE_LIKE(id))
    },
    incrementView: (id: number | string) => {
        return http.post(ARTICLE_INCREMENT_VIEW(id))
    },
    getMyLikes: () => {
        return http.get<IArticle[]>(ARTICLE_MY_LIKES)
    }
}

export default articleApi
