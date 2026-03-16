import { defineStore } from 'pinia'

interface CacheItem<T> {
    data: T
    timestamp: number
    expiresIn: number
}

interface CacheState {
    userArticles: CacheItem<any[]> | null
    userStats: CacheItem<{
        articles: number
        views: number
        likes: number
        comments: number
    }> | null
    aiAnalysis: CacheItem<{
        topArticle: string
        pastFocus: string
        hotTags: string
        futureTrends: string
    }> | null
    articles: CacheItem<any[]> | null
    articleDetails: Record<string, CacheItem<any>>
}

const DEFAULT_EXPIRE_TIME = 5 * 60 * 1000

export const useCacheStore = defineStore('cacheStore', {
    state: (): CacheState => ({
        userArticles: null,
        userStats: null,
        aiAnalysis: null,
        articles: null,
        articleDetails: {}
    }),
    actions: {
        setCache<T>(key: keyof CacheState, data: T, expiresIn: number = DEFAULT_EXPIRE_TIME) {
            if (key === 'articleDetails') {
                return
            }
            ;(this as any)[key] = {
                data,
                timestamp: Date.now(),
                expiresIn
            }
        },

        getCache<T>(key: keyof CacheState): T | null {
            if (key === 'articleDetails') {
                return null
            }
            const item = (this as any)[key] as CacheItem<T> | null
            if (!item) return null

            const now = Date.now()
            if (now - item.timestamp > item.expiresIn) {
                ;(this as any)[key] = null
                return null
            }

            return item.data
        },

        setArticleDetail(articleId: string | number, data: any, expiresIn: number = DEFAULT_EXPIRE_TIME) {
            this.articleDetails[String(articleId)] = {
                data,
                timestamp: Date.now(),
                expiresIn
            }
        },

        getArticleDetail(articleId: string | number): any | null {
            const key = String(articleId)
            const item = this.articleDetails[key]
            if (!item) return null

            const now = Date.now()
            if (now - item.timestamp > item.expiresIn) {
                delete this.articleDetails[key]
                return null
            }

            return item.data
        },

        clearCache(key?: keyof CacheState) {
            if (key) {
                if (key === 'articleDetails') {
                    this.articleDetails = {}
                } else {
                    ;(this as any)[key] = null
                }
            } else {
                this.userArticles = null
                this.userStats = null
                this.aiAnalysis = null
                this.articles = null
                this.articleDetails = {}
            }
        }
    }
})
