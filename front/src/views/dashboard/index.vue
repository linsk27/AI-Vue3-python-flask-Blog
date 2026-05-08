<template>
    <div class="dashboard-container">
        <router-view v-if="$route.path !== '/dashboard'" />
        <div v-else>
            <!-- 页面头部 -->
            <header class="dashboard-header">
                <div class="header-left">
                    <DataAnalysis class="header-icon" />
                    <div class="header-info">
                        <h1 class="dashboard-title">数据分析看板</h1>
                        <p class="dashboard-subtitle">数据驱动的知识管理与决策</p>
                    </div>
                </div>
                <div class="header-right">
                    <div class="date-range">
                        <el-date-picker v-model="dateRange" type="daterange" range-separator="至"
                            start-placeholder="开始日期" end-placeholder="结束日期" format="YYYY-MM-DD"
                            value-format="YYYY-MM-DD" />
                    </div>
                </div>
            </header>

            <!-- 主要内容区域 -->
            <main class="dashboard-content">
                <!-- 数据概览卡片 -->
                <section class="overview-section">
                    <div class="overview-grid">
                        <div v-for="card in overviewCards" :key="card.label" class="overview-card">
                            <div class="card-header">
                                <h3 class="card-title">{{ card.label }}</h3>
                                <component :is="card.icon" class="card-icon" />
                            </div>
                            <div class="card-content">
                                <div class="card-value">{{ card.value }}</div>
                                <div class="card-change neutral">
                                    <span>{{ card.helper }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- 快速导航 -->
                <section class="navigation-section">
                    <div class="navigation-grid">
                        <div class="navigation-card" @click="goToPersonalDashboard">
                            <User class="navigation-icon" />
                            <h3 class="navigation-title">个人数据看板</h3>
                            <p class="navigation-description">查看您个人的创作、阅读和互动数据</p>
                            <div class="navigation-action">
                                <span>进入</span>
                                <span class="action-icon">→</span>
                            </div>
                        </div>

                        <div class="navigation-card" @click="goToTeamDashboard">
                            <UserFilled class="navigation-icon" />
                            <h3 class="navigation-title">团队数据看板</h3>
                            <p class="navigation-description">查看团队的知识产出和协作数据</p>
                            <div class="navigation-action">
                                <span>进入</span>
                                <span class="action-icon">→</span>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- 数据可视化图表 -->
                <section class="charts-section">
                    <div class="chart-grid">
                        <!-- 文章增长趋势 -->
                        <div class="chart-card">
                            <div class="chart-header">
                                <h3 class="chart-title">文章增长趋势</h3>
                                <div class="chart-actions">
                                    <button class="chart-action-btn" @click="selectTimeRange('week')"
                                        :class="{ active: selectedRange === 'week' }">
                                        周
                                    </button>
                                    <button class="chart-action-btn" @click="selectTimeRange('month')"
                                        :class="{ active: selectedRange === 'month' }">
                                        月
                                    </button>
                                    <button class="chart-action-btn" @click="selectTimeRange('year')"
                                        :class="{ active: selectedRange === 'year' }">
                                        年
                                    </button>
                                </div>
                            </div>
                            <div class="chart-content">
                                <div class="chart-container">
                                    <div class="real-bar-chart" v-if="articleTrend.length">
                                        <div v-for="point in articleTrend" :key="point.label" class="trend-bar">
                                            <strong :style="{ height: `${point.percent}%` }"></strong>
                                            <span>{{ point.label }}</span>
                                            <small>{{ point.count }}</small>
                                        </div>
                                    </div>
                                    <div v-else class="chart-empty">所选范围内暂无文章</div>
                                </div>
                            </div>
                        </div>

                        <!-- 阅读量分布 -->
                        <div class="chart-card">
                            <div class="chart-header">
                                <h3 class="chart-title">阅读量分布</h3>
                            </div>
                            <div class="chart-content">
                                <div class="chart-container">
                                    <div class="rank-bars" v-if="readDistribution.length">
                                        <div v-for="item in readDistribution" :key="item.id" class="rank-row">
                                            <span>{{ item.title }}</span>
                                            <strong>
                                                <i :style="{ width: `${item.percent}%` }"></i>
                                            </strong>
                                            <small>{{ formatNumber(item.views) }}</small>
                                        </div>
                                    </div>
                                    <div v-else class="chart-empty">暂无阅读量数据</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- 热门标签和作者 -->
                <section class="top-section">
                    <div class="top-grid">
                        <!-- 热门标签 -->
                        <div class="top-card">
                            <div class="card-header">
                                <h3 class="card-title">热门标签</h3>
                            </div>
                            <div class="card-content">
                                <div class="tag-cloud">
                                    <div v-for="tag in topTags" :key="tag.name" class="tag-item"
                                        :style="{ fontSize: `${14 + tag.count / 10}px` }">
                                        <span class="tag-name">{{ tag.name }}</span>
                                        <span class="tag-count">({{ tag.count }})</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 活跃作者 -->
                        <div class="top-card">
                            <div class="card-header">
                                <h3 class="card-title">活跃作者</h3>
                            </div>
                            <div class="card-content">
                                <div class="author-list">
                                    <div v-for="author in topAuthors" :key="author.name" class="author-item">
                                        <div class="author-avatar">
                                            <span>{{ author.name.slice(0, 1) }}</span>
                                        </div>
                                        <div class="author-info">
                                            <div class="author-name">{{ author.name }}</div>
                                            <div class="author-stats">
                                                <span>{{ author.articles }}篇文章</span>
                                                <span>{{ author.reads }}次阅读</span>
                                            </div>
                                        </div>
                                        <div class="author-rank">{{ author.rank }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Collection, DataAnalysis, Document, User, UserFilled, View } from '@element-plus/icons-vue'
import { useElMessage } from '@/hooks/useMessage'
import http from '@/api'
import articleApi from '@/api/modules/article'
import type { IArticle } from '@/api/modules/article/interface'
import contextPackApi, { type ContextPackStats } from '@/api/modules/contextPacks'

const { message } = useElMessage()

const router = useRouter()

interface DashboardUser {
    id: number
    username: string
    created_at?: string
}

function getCurrentMonthRange() {
    const now = new Date()
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    return [formatDateValue(start), formatDateValue(now)]
}

function formatDateValue(date: Date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
}

const dateRange = ref(getCurrentMonthRange())
const selectedRange = ref('month')
const articles = ref<IArticle[]>([])
const users = ref<DashboardUser[]>([])
const contextStats = ref<ContextPackStats | null>(null)

const totalReads = computed(() => articles.value.reduce((total, article) => total + (Number(article.views) || 0), 0))

const overviewCards = computed(() => [
    { label: '总文档数', value: articles.value.length, helper: '来自 articles 表', icon: Document },
    { label: '总浏览量', value: formatNumber(totalReads.value), helper: '按真实浏览量汇总', icon: View },
    { label: '用户数', value: users.value.length, helper: '来自 users 表', icon: UserFilled },
    { label: '上下文包', value: contextStats.value?.packs ?? 0, helper: '来自 context_packs 表', icon: Collection }
])

const filteredArticles = computed(() => {
    const [start, end] = dateRange.value || []
    if (!start || !end) return articles.value
    const startTime = new Date(`${start}T00:00:00`).getTime()
    const endTime = new Date(`${end}T23:59:59`).getTime()
    return articles.value.filter(article => {
        const time = getArticleTime(article)
        return time >= startTime && time <= endTime
    })
})

const topTags = computed(() => {
    const map = new Map<string, number>()
    articles.value.forEach(article => {
        ;(article.tags || []).forEach(tag => map.set(tag, (map.get(tag) || 0) + 1))
    })
    return Array.from(map.entries())
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10)
})

const topAuthors = computed(() => {
    const map = new Map<string, { name: string; articles: number; reads: number }>()
    articles.value.forEach(article => {
        const name = article.author_name || `用户 ${article.author_id || '未知'}`
        const current = map.get(name) || { name, articles: 0, reads: 0 }
        current.articles += 1
        current.reads += Number(article.views) || 0
        map.set(name, current)
    })
    return Array.from(map.values())
        .sort((a, b) => b.articles - a.articles || b.reads - a.reads)
        .slice(0, 5)
        .map((author, index) => ({ ...author, rank: index + 1 }))
})

const articleTrend = computed(() => {
    const points = buildArticleTrend(filteredArticles.value, selectedRange.value)
    const maxCount = Math.max(...points.map(point => point.count), 1)
    return points.map(point => ({
        ...point,
        percent: point.count ? Math.max(8, Math.round((point.count / maxCount) * 100)) : 2
    }))
})

const readDistribution = computed(() => {
    const items = articles.value
        .filter(article => (Number(article.views) || 0) > 0)
        .sort((a, b) => (Number(b.views) || 0) - (Number(a.views) || 0))
        .slice(0, 5)
    const maxViews = Math.max(...items.map(article => Number(article.views) || 0), 1)
    return items.map(article => ({
        id: article.id,
        title: article.title,
        views: Number(article.views) || 0,
        percent: Math.max(6, Math.round(((Number(article.views) || 0) / maxViews) * 100))
    }))
})

function selectTimeRange(range: 'week' | 'month' | 'year') {
    selectedRange.value = range
    message.info(`已切换到${range === 'week' ? '周' : range === 'month' ? '月' : '年'}度数据`)
}

function formatNumber(num: number): string {
    if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万'
    }
    return num.toString()
}

function getArticleTime(article: IArticle) {
    const date = new Date(article.created_at || article.updated_at || '')
    return Number.isNaN(date.getTime()) ? 0 : date.getTime()
}

function buildArticleTrend(sourceArticles: IArticle[], range: string) {
    const now = new Date()
    const bucketCount = range === 'week' ? 7 : range === 'year' ? 12 : 6
    const buckets = Array.from({ length: bucketCount }, (_, index) => {
        const date = new Date(now)
        if (range === 'year') {
            date.setMonth(now.getMonth() - (bucketCount - 1 - index), 1)
            return {
                key: `${date.getFullYear()}-${date.getMonth()}`,
                label: `${date.getMonth() + 1}月`,
                count: 0
            }
        }

        date.setDate(now.getDate() - (bucketCount - 1 - index))
        return {
            key: formatDateValue(date),
            label: range === 'week' ? `${date.getMonth() + 1}/${date.getDate()}` : `${date.getDate()}日`,
            count: 0
        }
    })

    const bucketMap = new Map(buckets.map(bucket => [bucket.key, bucket]))
    sourceArticles.forEach(article => {
        const date = new Date(getArticleTime(article))
        if (Number.isNaN(date.getTime())) return
        const key = range === 'year' ? `${date.getFullYear()}-${date.getMonth()}` : formatDateValue(date)
        const bucket = bucketMap.get(key)
        if (bucket) bucket.count += 1
    })

    return buckets
}

function goToPersonalDashboard() {
    router.push('/dashboard/personal')
}

function goToTeamDashboard() {
    router.push('/dashboard/team')
}

async function loadDashboardData() {
    try {
        const [articleList, userList, stats] = await Promise.all([
            articleApi.getList(),
            http.get<DashboardUser[]>('/users'),
            contextPackApi.getStats()
        ])
        articles.value = Array.isArray(articleList) ? articleList : []
        users.value = Array.isArray(userList) ? userList : []
        contextStats.value = stats
    } catch (error) {
        console.error('Load dashboard data failed:', error)
        articles.value = []
        users.value = []
        contextStats.value = null
        message.error('真实看板数据加载失败')
    }
}

onMounted(() => {
    loadDashboardData()
})
</script>

<style scoped>
.dashboard-container {
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(255, 248, 245, 0.85) 100%);
    min-height: 100vh;
}

/* 页面头部 */
.dashboard-header {
    background: rgba(255, 255, 255, 0.9);
    padding: 1.5rem 2rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.header-icon {
    width: 2rem;
    height: 2rem;
    color: #FF7F50;
    flex-shrink: 0;
}

.header-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.dashboard-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #FF7F50;
    margin: 0;
}

.dashboard-subtitle {
    font-size: 0.9rem;
    color: #666;
    margin: 0;
}

.date-range {
    display: flex;
    gap: 1rem;
}

/* 主要内容区域 */
.dashboard-content {
    max-width: 1600px;
    margin: 0 auto;
    padding: 2rem;
}

/* 数据概览 */
.overview-section {
    margin-bottom: 2rem;
}

.overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.overview-card {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.overview-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.card-title {
    font-size: 1rem;
    font-weight: 600;
    color: #666;
    margin: 0;
}

.card-icon {
    width: 1.5rem;
    height: 1.5rem;
    color: #FF7F50;
    flex-shrink: 0;
}

.card-content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.card-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #333;
}

.card-change {
    font-size: 0.9rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-change.positive {
    color: #4CAF50;
}

.card-change.negative {
    color: #F44336;
}

.card-change.neutral {
    color: #777;
}

.card-change span {
    font-size: 0.8rem;
    color: #999;
    font-weight: 400;
}

/* 导航区域 */
.navigation-section {
    margin-bottom: 2rem;
}

.navigation-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.navigation-card {
    background: white;
    padding: 2.5rem 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    border-top: 4px solid #FF7F50;
    position: relative;
    overflow: hidden;
}

.navigation-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(255, 127, 80, 0.05) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.navigation-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 35px rgba(255, 127, 80, 0.15);
}

.navigation-card:hover::before {
    opacity: 1;
}

.navigation-icon {
    width: 3rem;
    height: 3rem;
    color: #FF7F50;
    margin-bottom: 1.5rem;
    position: relative;
    z-index: 1;
}

.navigation-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #333;
    margin: 0 0 1rem;
    position: relative;
    z-index: 1;
}

.navigation-description {
    font-size: 1rem;
    color: #666;
    margin: 0 0 2rem;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

.navigation-action {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #FF7F50;
    font-weight: 600;
    font-size: 1rem;
    position: relative;
    z-index: 1;
}

.action-icon {
    transition: transform 0.3s ease;
}

.navigation-card:hover .action-icon {
    transform: translateX(5px);
}

/* 图表区域 */
.charts-section {
    margin-bottom: 2rem;
}

.chart-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 2rem;
}

.chart-card {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.chart-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #333;
    margin: 0;
}

.chart-actions {
    display: flex;
    gap: 0.5rem;
}

.chart-action-btn {
    background: rgba(255, 127, 80, 0.1);
    color: #FF7F50;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.chart-action-btn:hover {
    background: rgba(255, 127, 80, 0.2);
}

.chart-action-btn.active {
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    color: white;
}

.chart-content {
    height: 300px;
}

.chart-container {
    width: 100%;
    height: 100%;
    background: rgba(74, 144, 226, 0.02);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    position: relative;
    overflow: hidden;
}

.chart-empty {
    color: #999;
    font-size: 0.95rem;
}

.real-bar-chart {
    width: 100%;
    height: 100%;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(52px, 1fr));
    align-items: end;
    gap: 0.75rem;
    padding: 1.25rem;
    box-sizing: border-box;
}

.trend-bar {
    min-width: 0;
    height: 100%;
    display: grid;
    grid-template-rows: minmax(0, 1fr) auto auto;
    align-items: end;
    gap: 0.45rem;
    text-align: center;
}

.trend-bar strong {
    width: 100%;
    min-height: 4px;
    border-radius: 6px 6px 2px 2px;
    background: linear-gradient(to top, #FF7F50, rgba(255, 127, 80, 0.56));
}

.trend-bar span,
.trend-bar small,
.rank-row small {
    color: #777;
    font-size: 0.78rem;
}

.rank-bars {
    width: 100%;
    display: grid;
    gap: 0.8rem;
    padding: 1.25rem;
}

.rank-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(140px, 42%) 56px;
    align-items: center;
    gap: 0.85rem;
}

.rank-row span {
    overflow: hidden;
    color: #444;
    font-size: 0.9rem;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.rank-row strong {
    height: 10px;
    overflow: hidden;
    border-radius: 999px;
    background: rgba(255, 127, 80, 0.12);
}

.rank-row i {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: #FF7F50;
}

/* 热门标签和作者 */
.top-section {
    margin-bottom: 2rem;
}

.top-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.top-card {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

/* 标签云 */
.tag-cloud {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

.tag-item {
    background: rgba(255, 127, 80, 0.1);
    color: #FF7F50;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.tag-item:hover {
    background: rgba(255, 127, 80, 0.2);
    transform: translateY(-3px);
}

.tag-count {
    font-size: 0.8rem;
    color: #999;
}

/* 作者列表 */
.author-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.author-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.author-item:hover {
    background: rgba(255, 127, 80, 0.05);
}

.author-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}

.author-info {
    flex: 1;
}

.author-name {
    font-size: 1rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 0.25rem;
}

.author-stats {
    display: flex;
    gap: 1rem;
    font-size: 0.8rem;
    color: #999;
}

.author-rank {
    font-size: 1.2rem;
    font-weight: 700;
    color: #999;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .dashboard-header {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
        padding: 1.5rem 1rem;
    }

    .dashboard-content {
        padding: 1rem;
    }

    .overview-grid,
    .navigation-grid,
    .chart-grid,
    .top-grid {
        grid-template-columns: 1fr;
    }

    .chart-grid {
        grid-template-columns: 1fr;
    }

    .chart-container {
        height: 250px;
    }

    .card-value {
        font-size: 2rem;
    }
}
</style>
