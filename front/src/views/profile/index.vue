<template>
    <div class="profile-container">
        <section class="profile-hero">
            <div class="profile-identity">
                <div class="profile-avatar">
                    <img v-if="userInfo?.avatar" :src="userInfo.avatar" alt="Avatar" />
                    <span v-else>{{ avatarInitial }}</span>
                </div>
                <div class="profile-heading">
                    <span class="eyebrow">Account</span>
                    <h1>{{ userInfo?.username || '用户' }}</h1>
                    <p>{{ userInfo?.role === 'admin' ? '管理员' : '普通用户' }}</p>
                    <div v-if="displayPermissions.length" class="permission-list">
                        <span v-for="permission in displayPermissions" :key="permission.code">{{ permission.label }}</span>
                        <span v-if="remainingPermissionCount > 0" class="more-permission">+{{ remainingPermissionCount }}</span>
                    </div>
                </div>
            </div>
            <div class="profile-summary">
                <span>个人中心</span>
                <strong>{{ userStats.articles }}</strong>
                <small>发布文章</small>
            </div>
        </section>

        <main class="profile-content">
            <section class="profile-grid top-grid">
                <article class="profile-card info-card">
                    <div class="card-heading">
                        <span class="card-index">01</span>
                        <h2>账号信息</h2>
                    </div>
                    <div class="info-list">
                        <div class="info-item">
                            <span>用户名</span>
                            <strong>{{ userInfo?.username || '未设置' }}</strong>
                        </div>
                        <div class="info-item">
                            <span>邮箱</span>
                            <strong>{{ userInfo?.email || '未设置' }}</strong>
                        </div>
                        <div class="info-item">
                            <span>注册时间</span>
                            <strong>{{ userInfo?.created_at || '未设置' }}</strong>
                        </div>
                        <div class="info-item">
                            <span>角色</span>
                            <strong>{{ userInfo?.role || '未设置' }}</strong>
                        </div>
                    </div>
                </article>

                <article class="profile-card stats-card">
                    <div class="card-heading">
                        <span class="card-index">02</span>
                        <h2>数据概览</h2>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <strong>{{ userStats.articles || 0 }}</strong>
                            <span>发布文章</span>
                        </div>
                        <div class="stat-item">
                            <strong>{{ userStats.views || 0 }}</strong>
                            <span>文章阅读</span>
                        </div>
                        <div class="stat-item">
                            <strong>{{ userStats.likes || 0 }}</strong>
                            <span>收到点赞</span>
                        </div>
                        <div class="stat-item">
                            <strong>{{ userStats.comments || 0 }}</strong>
                            <span>收到评论</span>
                        </div>
                    </div>
                </article>
            </section>

            <section class="profile-card ai-analysis-card">
                <div class="card-heading">
                    <span class="card-index">03</span>
                    <h2>内容洞察</h2>
                </div>
                <div v-if="isLoading" class="loading-container">
                    <span class="loading-spinner"></span>
                    <p>正在整理真实内容数据...</p>
                </div>
                <div v-else-if="aiAnalysis" class="analysis-grid">
                    <article class="analysis-item">
                        <span>最热门文章</span>
                        <p>{{ aiAnalysis.topArticle || '暂无数据' }}</p>
                    </article>
                    <article class="analysis-item">
                        <span>近期关注主题</span>
                        <p>{{ aiAnalysis.pastFocus || '暂无数据' }}</p>
                    </article>
                    <article class="analysis-item">
                        <span>热门标签</span>
                        <p>{{ aiAnalysis.hotTags || '暂无数据' }}</p>
                    </article>
                    <article class="analysis-item">
                        <span>未来趋势</span>
                        <p>{{ aiAnalysis.futureTrends || '暂无数据' }}</p>
                    </article>
                </div>
                <div v-else class="empty-state">暂无可分析内容</div>
            </section>

            <section class="profile-grid bottom-grid">
                <article class="profile-card articles-card">
                    <div class="card-heading">
                        <span class="card-index">04</span>
                        <h2>我的文章</h2>
                    </div>
                    <div v-if="userArticles.length" class="articles-list">
                        <article v-for="article in userArticles" :key="article.id" class="article-item">
                            <h3>{{ article.title }}</h3>
                            <div class="article-meta">
                                <span>{{ formatDate(article.created_at) }}</span>
                                <span>{{ article.likes || 0 }} 点赞</span>
                                <span>{{ article.views || 0 }} 阅读</span>
                            </div>
                        </article>
                    </div>
                    <div v-else class="empty-state">暂无文章</div>
                </article>

                <article class="profile-card activity-card">
                    <div class="card-heading">
                        <span class="card-index">05</span>
                        <h2>最近活动</h2>
                    </div>
                    <div v-if="recentActivities.length" class="activity-list">
                        <div v-for="(activity, index) in recentActivities" :key="index" class="activity-item">
                            <span class="activity-index">{{ String(index + 1).padStart(2, '0') }}</span>
                            <div>
                                <strong>{{ activity.text }}</strong>
                                <small>{{ activity.time }}</small>
                            </div>
                        </div>
                    </div>
                    <div v-else class="empty-state">暂无活动记录</div>
                </article>
            </section>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useGlobalStore } from '@/store'
import { useCacheStore } from '@/store/cache'
import authApi from '@/api/modules/auth'
import articleApi from '@/api/modules/article'
import type { IArticle } from '@/api/modules/article/interface'
import contextPackApi, { type ContextPack } from '@/api/modules/contextPacks'

const globalStore = useGlobalStore()
const cacheStore = useCacheStore()
const userInfo = ref(globalStore.userInfo)
const userStats = ref({ articles: 0, views: 0, likes: 0, comments: 0 })
const userArticles = ref<IArticle[]>([])
const likedArticles = ref<IArticle[]>([])
const userContextPacks = ref<ContextPack[]>([])
const recentActivities = ref<{ text: string; time: string; timestamp: number }[]>([])
const aiAnalysis = ref<any>(null)
const isLoading = ref(false)

const avatarInitial = computed(() => (userInfo.value?.username || 'U').slice(0, 1).toUpperCase())
const currentUserId = computed(() => userInfo.value?.id ? String(userInfo.value.id) : 'guest')
const permissionNameMap: Record<string, string> = {
    'ai:manage': 'AI 配置',
    'article:manage': '文章管理',
    'role:manage': '角色管理',
    'user:manage': '用户管理'
}
const permissionItems = computed(() => {
    return (userInfo.value?.permissions || []).map((code: string) => ({
        code,
        label: permissionNameMap[code] || code
    }))
})
const displayPermissions = computed(() => permissionItems.value.slice(0, 3))
const remainingPermissionCount = computed(() => Math.max(permissionItems.value.length - displayPermissions.value.length, 0))

const formatDate = (dateString: string) => {
    if (!dateString) return '未知'
    return new Date(dateString).toLocaleDateString('zh-CN')
}

const cacheKey = (name: string) => `profile.${currentUserId.value}.${name}`

const normalizeArray = <T,>(payload: unknown): T[] => {
    if (Array.isArray(payload)) return payload as T[]
    const data = (payload as any)?.data
    return Array.isArray(data) ? data as T[] : []
}

const toTimestamp = (value?: string) => {
    if (!value) return 0
    const timestamp = new Date(value).getTime()
    return Number.isFinite(timestamp) ? timestamp : 0
}

const formatRelativeTime = (value?: string) => {
    const timestamp = toTimestamp(value)
    if (!timestamp) return '时间未知'

    const diff = Date.now() - timestamp
    const minute = 60 * 1000
    const hour = 60 * minute
    const day = 24 * hour

    if (diff < minute) return '刚刚'
    if (diff < hour) return `${Math.floor(diff / minute)} 分钟前`
    if (diff < day) return `${Math.floor(diff / hour)} 小时前`
    if (diff < day * 30) return `${Math.floor(diff / day)} 天前`
    return formatDate(value || '')
}

const articleScore = (article: IArticle) => {
    return (article.views || 0) + (article.likes || 0) * 3 + (article.comments_count || 0) * 2
}

const getUserStats = async (forceRefresh = false) => {
    try {
        if (!forceRefresh) {
            const cachedArticles = cacheStore.getCache<IArticle[]>(cacheKey('articles'))
            const cachedLikedArticles = cacheStore.getCache<IArticle[]>(cacheKey('likedArticles'))
            const cachedContextPacks = cacheStore.getCache<ContextPack[]>(cacheKey('contextPacks'))
            const cachedStats = cacheStore.getCache<typeof userStats.value>(cacheKey('stats'))
            if (cachedArticles && cachedLikedArticles && cachedContextPacks && cachedStats) {
                userArticles.value = cachedArticles.slice(0, 5)
                likedArticles.value = cachedLikedArticles
                userContextPacks.value = cachedContextPacks
                userStats.value = cachedStats
                buildRecentActivities(cachedArticles, cachedLikedArticles, cachedContextPacks)
                buildContentInsights(cachedArticles)
                return
            }
        }

        const [articlePayload, likedPayload, packPayload] = await Promise.all([
            articleApi.getList({ author_id: userInfo.value?.id }),
            articleApi.getMyLikes().catch(() => []),
            contextPackApi.getList().catch(() => [])
        ])

        const articles = normalizeArray<IArticle>(articlePayload)
            .sort((left, right) => toTimestamp(right.created_at) - toTimestamp(left.created_at))
        const liked = normalizeArray<IArticle>(likedPayload)
        const packs = normalizeArray<ContextPack>(packPayload)
            .filter(pack => String(pack.user_id || '') === currentUserId.value)
            .sort((left, right) => toTimestamp(right.updated_at || right.created_at) - toTimestamp(left.updated_at || left.created_at))

        if (articles) {
            userArticles.value = articles.slice(0, 5)
            likedArticles.value = liked
            userContextPacks.value = packs

            const totals = articles.reduce((acc, article) => {
                acc.views += article.views || 0
                acc.likes += article.likes || 0
                acc.comments += article.comments_count || 0
                return acc
            }, { views: 0, likes: 0, comments: 0 })

            userStats.value = {
                articles: articles.length,
                views: totals.views,
                likes: totals.likes,
                comments: totals.comments
            }

            buildRecentActivities(articles, liked, packs)
            buildContentInsights(articles)

            cacheStore.setCache(cacheKey('articles'), articles)
            cacheStore.setCache(cacheKey('likedArticles'), liked)
            cacheStore.setCache(cacheKey('contextPacks'), packs)
            cacheStore.setCache(cacheKey('stats'), userStats.value)
        }
    } catch (error) {
        console.error('获取用户统计数据失败:', error)
    }
}

const buildRecentActivities = (articles: IArticle[], liked: IArticle[], packs: ContextPack[]) => {
    const events: { text: string; time: string; timestamp: number }[] = []

    articles.forEach(article => {
        if (article.created_at) {
            events.push({
                text: `发布了《${article.title}》`,
                time: formatRelativeTime(article.created_at),
                timestamp: toTimestamp(article.created_at)
            })
        }

        const updatedAt = toTimestamp(article.updated_at)
        const createdAt = toTimestamp(article.created_at)
        if (updatedAt && updatedAt - createdAt > 60 * 1000) {
            events.push({
                text: `更新了《${article.title}》`,
                time: formatRelativeTime(article.updated_at),
                timestamp: updatedAt
            })
        }
    })

    liked.forEach(article => {
        const likedAt = article.liked_at || article.updated_at || article.created_at
        events.push({
            text: `收藏了《${article.title}》`,
            time: formatRelativeTime(likedAt),
            timestamp: toTimestamp(likedAt)
        })
    })

    packs.forEach(pack => {
        const packTime = pack.updated_at || pack.created_at
        events.push({
            text: `维护了上下文包「${pack.name}」`,
            time: formatRelativeTime(packTime),
            timestamp: toTimestamp(packTime)
        })
    })

    recentActivities.value = events
        .filter(event => event.timestamp > 0)
        .sort((left, right) => right.timestamp - left.timestamp)
        .slice(0, 6)
}

const buildContentInsights = (articles: IArticle[]) => {
    isLoading.value = true
    try {
        if (!articles.length) {
            aiAnalysis.value = {
                topArticle: '暂无数据',
                pastFocus: '暂无数据',
                hotTags: '暂无数据',
                futureTrends: '先发布文章，再形成趋势'
            }
            return
        }

        const topArticle = [...articles].sort((left, right) => articleScore(right) - articleScore(left))[0]
        const tagCounts = new Map<string, number>()
        articles.forEach(article => {
            ;(article.tags || []).forEach(tag => {
                const normalized = String(tag).trim()
                if (normalized) tagCounts.set(normalized, (tagCounts.get(normalized) || 0) + 1)
            })
        })

        const hotTags = Array.from(tagCounts.entries())
            .sort((left, right) => right[1] - left[1])
            .slice(0, 5)
            .map(([tag]) => tag)

        const recentTypes = Array.from(new Set(
            articles
                .slice(0, 5)
                .map(article => article.resource_type || article.category)
                .filter(Boolean)
        ))

        aiAnalysis.value = {
            topArticle: topArticle
                ? `《${topArticle.title}》互动最高，${topArticle.views || 0} 阅读、${topArticle.likes || 0} 点赞`
                : '暂无数据',
            pastFocus: recentTypes.length ? `近期主要沉淀：${recentTypes.join('、')}` : '暂无分类数据',
            hotTags: hotTags.length ? hotTags.join('、') : '暂无标签数据',
            futureTrends: userContextPacks.value.length
                ? `已有 ${userContextPacks.value.length} 个上下文包，可继续补齐资料来源和 RAG 索引`
                : '建议把高价值文章加入上下文包，形成可复用资料'
        }
    } finally {
        isLoading.value = false
    }
}

onMounted(async () => {
    try {
        const res = await authApi.getUserInfo()
        if (res) {
            userInfo.value = res
            globalStore.setLoginInfo(globalStore.token, res)
        }
        await getUserStats()
    } catch (error) {
        console.error(error)
    }
})
</script>

<style scoped>
.profile-container {
    width: 100%;
    min-height: calc(100vh - 140px);
    padding: 56px 0 80px;
    color: var(--text-primary);
    background: transparent;
}

.profile-hero,
.profile-content {
    width: var(--page-width);
    margin: 0 auto;
}

.profile-hero {
    display: flex;
    align-items: stretch;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 16px;
}

.profile-identity,
.profile-summary,
.profile-card {
    border-radius: 12px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.profile-identity {
    flex: 1;
    min-width: 0;
    padding: 32px;
    display: flex;
    align-items: center;
    gap: 24px;
}

.profile-avatar {
    width: 96px;
    height: 96px;
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 50%;
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
    font-family: var(--font-mono);
    font-size: 32px;
    font-weight: 600;
}

.profile-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.eyebrow,
.card-index,
.permission-list span,
.profile-summary span,
.profile-summary small,
.activity-index {
    font-family: var(--font-mono);
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 500;
}

.profile-heading h1 {
    margin: 16px 0 8px;
    font-size: clamp(40px, 6vw, 64px);
    font-weight: 600;
    line-height: 1;
    letter-spacing: 0;
}

.profile-heading p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 18px;
}

.permission-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 18px;
}

.permission-list span {
    height: 26px;
    display: inline-flex;
    align-items: center;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    white-space: nowrap;
}

.permission-list .more-permission {
    color: var(--text-primary);
    background: var(--surface);
}

.profile-summary {
    width: 220px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.profile-summary span,
.profile-summary small {
    color: var(--text-muted);
    font-size: 12px;
    text-transform: uppercase;
}

.profile-summary strong {
    color: var(--text-primary);
    font-size: 56px;
    font-weight: 600;
    line-height: 1;
    letter-spacing: 0;
}

.profile-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.profile-grid {
    display: grid;
    gap: 16px;
}

.top-grid,
.bottom-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

.profile-card {
    padding: 24px;
}

.card-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 20px;
}

.card-heading h2 {
    margin: 0;
    color: var(--text-primary);
    font-size: 24px;
    font-weight: 600;
    line-height: 1.25;
    letter-spacing: 0;
}

.card-index,
.activity-index {
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 500;
}

.info-list {
    display: grid;
    gap: 10px;
}

.info-item,
.article-item,
.activity-item,
.analysis-item {
    border-radius: 10px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.info-item {
    min-height: 48px;
    padding: 0 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.info-item span,
.stat-item span,
.article-meta,
.activity-item small,
.analysis-item span {
    color: var(--text-muted);
    font-size: 13px;
}

.info-item strong {
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 500;
    text-align: right;
}

.stats-grid,
.analysis-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
}

.stat-item {
    min-height: 112px;
    padding: 18px;
    border-radius: 10px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.stat-item strong {
    color: var(--text-primary);
    font-size: 36px;
    font-weight: 600;
    line-height: 1;
    letter-spacing: 0;
}

.loading-container,
.empty-state {
    min-height: 140px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: var(--text-secondary);
    border-radius: 10px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.loading-spinner {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid var(--surface-hover);
    border-top-color: var(--text-primary);
    animation: spin 800ms linear infinite;
}

.analysis-item {
    min-height: 126px;
    padding: 16px;
}

.analysis-item p {
    margin: 10px 0 0;
    color: var(--text-primary);
    line-height: 1.7;
}

.articles-list,
.activity-list {
    display: grid;
    gap: 10px;
}

.article-item {
    padding: 16px;
}

.article-item h3 {
    margin: 0 0 10px;
    color: var(--text-primary);
    font-size: 16px;
    font-weight: 600;
    line-height: 1.4;
}

.article-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.activity-item {
    padding: 14px;
    display: grid;
    grid-template-columns: 32px minmax(0, 1fr);
    gap: 12px;
    align-items: start;
}

.activity-item strong {
    display: block;
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 500;
}

.activity-item small {
    display: block;
    margin-top: 4px;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@media (max-width: 980px) {
    .profile-hero,
    .top-grid,
    .bottom-grid {
        grid-template-columns: 1fr;
    }

    .profile-hero {
        display: grid;
    }

    .profile-summary {
        width: 100%;
        min-height: 132px;
    }
}

@media (max-width: 640px) {
    .profile-container {
        padding: 32px 0 56px;
    }

    .profile-identity {
        padding: 24px;
        align-items: flex-start;
        flex-direction: column;
    }

    .profile-avatar {
        width: 76px;
        height: 76px;
        font-size: 26px;
    }

    .stats-grid,
    .analysis-grid {
        grid-template-columns: 1fr;
    }

    .info-item {
        align-items: flex-start;
        flex-direction: column;
        padding: 12px 14px;
    }

    .info-item strong {
        text-align: left;
    }
}

:where(h1, h2, h3) {
    font-family: var(--font-serif);
    font-weight: 500;
    letter-spacing: 0;
}

:where(p, li, small) {
    line-height: 1.6;
}

:where(button, .el-button, a) {
    letter-spacing: 0;
}

</style>
