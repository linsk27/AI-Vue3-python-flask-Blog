<template>
    <div class="personal-dashboard-container">
        <!-- 页面头部 -->
        <header class="dashboard-header">
            <div class="header-left">
                <User class="header-icon" />
                <div class="header-info">
                    <h1 class="dashboard-title">个人数据看板</h1>
                    <p class="dashboard-subtitle">追踪您的创作、上下文包和互动数据</p>
                </div>
            </div>
            <div class="header-right">
                <div class="date-range">
                    <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                        end-placeholder="结束日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
                </div>
            </div>
        </header>

        <!-- 主要内容区域 -->
        <main class="dashboard-content">
            <!-- 个人数据概览卡片 -->
            <section class="overview-section">
                <div class="overview-grid">
                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">我的文章数</h3>
                            <Document class="card-icon" />
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ personalData.totalArticles }}</div>
                            <div class="card-change neutral">
                                <span>来自真实文章</span>
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">总阅读量</h3>
                            <View class="card-icon" />
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ formatNumber(personalData.totalReads) }}</div>
                            <div class="card-change neutral">
                                <span>按浏览量汇总</span>
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">总点赞数</h3>
                            <Star class="card-icon" />
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ personalData.totalLikes }}</div>
                            <div class="card-change neutral">
                                <span>按收藏数汇总</span>
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">上下文包</h3>
                            <Collection class="card-icon" />
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ personalData.contextPacks }}</div>
                            <div class="card-change neutral">
                                <span>可用于上下文问答</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 数据可视化图表 -->
            <section class="charts-section">
                <div class="chart-grid">
                    <!-- 文章阅读趋势 -->
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3 class="chart-title">文章阅读趋势</h3>
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
                            <div ref="readTrendChartRef" class="chart-container">
                                <div v-if="readTrendData.length" class="read-trend-bars">
                                    <div v-for="item in readTrendData" :key="item.id" class="trend-bar-item">
                                        <div class="trend-bar-track">
                                            <div class="trend-bar-fill" :style="{ height: `${item.percent}%` }"></div>
                                        </div>
                                        <div class="trend-bar-value">{{ formatNumber(item.reads) }}</div>
                                        <div class="trend-bar-label" :title="item.title">{{ item.title }}</div>
                                    </div>
                                </div>
                                <div v-else class="empty-chart">暂无文章阅读数据</div>
                            </div>
                        </div>
                    </div>

                    <!-- 文章类型分布 -->
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3 class="chart-title">文章类型分布</h3>
                        </div>
                        <div class="chart-content">
                            <div ref="articleTypeChartRef" class="chart-container">
                                <div v-if="categoryDistribution.length" class="article-type-list">
                                    <div v-for="item in categoryDistribution" :key="item.name" class="type-row">
                                        <div class="type-row-header">
                                            <span>{{ item.name }}</span>
                                            <strong>{{ item.count }} 篇</strong>
                                        </div>
                                        <div class="type-row-track">
                                            <div class="type-row-fill" :style="{ width: `${item.percent}%` }"></div>
                                        </div>
                                    </div>
                                </div>
                                <div v-else class="empty-chart">暂无分类数据</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 我的文章表现 -->
            <section class="articles-section">
                <div class="section-header">
                    <h2 class="section-title">我的文章表现</h2>
                    <el-button type="primary" size="small" @click="goToWriteArticle">
                        <Plus /> 写文章
                    </el-button>
                </div>
                <div class="articles-table">
                    <el-table :data="myArticles" stripe style="width: 100%">
                        <el-table-column prop="title" label="文章标题" min-width="300">
                            <template #default="scope">
                                <div class="article-title">{{ scope.row.title }}</div>
                            </template>
                        </el-table-column>
                        <el-table-column prop="category" label="分类" width="120">
                            <template #default="scope">
                                <el-tag :type="getCategoryType(scope.row.category)">{{ scope.row.category }}</el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column prop="reads" label="阅读量" width="100" align="right">
                            <template #default="scope">
                                <span>{{ formatNumber(scope.row.reads) }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="likes" label="点赞数" width="100" align="right">
                            <template #default="scope">
                                <span>{{ scope.row.likes }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="comments" label="评论数" width="100" align="right">
                            <template #default="scope">
                                <span>{{ scope.row.comments }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="createTime" label="发布时间" width="180">
                            <template #default="scope">
                                <span>{{ scope.row.createTime }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column label="操作" width="150" fixed="right">
                            <template #default="scope">
                                <el-button type="primary" size="small" @click="viewArticle(scope.row.id)">
                                    查看
                                </el-button>
                                <el-button size="small" @click="editArticle(scope.row.id)">
                                    编辑
                                </el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
            </section>

            <!-- 阅读偏好 -->
            <section class="preferences-section">
                <div class="section-header">
                    <h2 class="section-title">我的内容偏好</h2>
                </div>
                <div class="preferences-grid">
                    <div class="preference-card">
                        <div class="card-header">
                            <h3 class="card-title">创作分类</h3>
                        </div>
                        <div class="card-content">
                            <div class="category-tags">
                                <el-tag v-for="category in readingPreferences.categories" :key="category.name"
                                    :size="'large'" :type="getCategoryType(category.name)" :effect="'dark'"
                                    :style="{ margin: '0 0.5rem 0.5rem 0' }">
                                    {{ category.name }} <span class="tag-count">({{ category.count }})</span>
                                </el-tag>
                            </div>
                        </div>
                    </div>

                    <div class="preference-card">
                        <div class="card-header">
                            <h3 class="card-title">发布状态</h3>
                        </div>
                        <div class="card-content">
                            <div class="reading-time">
                                <div class="time-item">
                                    <div class="time-value">{{ personalData.publishedArticles }}篇</div>
                                    <div class="time-label">已发布</div>
                                </div>
                                <div class="time-item">
                                    <div class="time-value">{{ personalData.draftArticles }}篇</div>
                                    <div class="time-label">草稿/待审核</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Collection, Document, Plus, Star, User, View } from '@element-plus/icons-vue'
import { useGlobalStore } from '@/store'
import articleApi from '@/api/modules/article'
import { IArticle } from '@/api/modules/article/interface'
import contextPackApi, { type ContextPack } from '@/api/modules/contextPacks'
import { useElMessage } from '@/hooks/useMessage'

const { message } = useElMessage()

const router = useRouter()
const globalStore = useGlobalStore()

interface PersonalArticleRow {
    id: number
    title: string
    category: string
    reads: number
    likes: number
    comments: number
    createTime: string
}

interface DistributionItem {
    name: string
    count: number
    percent: number
}

interface TrendItem {
    id: number
    title: string
    reads: number
    percent: number
}

// 时间范围
const dateRange = ref(getCurrentMonthRange())
const selectedRange = ref('month')

// 个人数据
const personalData = ref({
    totalArticles: 0,
    totalReads: 0,
    totalLikes: 0,
    contextPacks: 0,
    publishedArticles: 0,
    draftArticles: 0
})

// 我的文章
const myArticles = ref<PersonalArticleRow[]>([])
const readTrendData = ref<TrendItem[]>([])
const categoryDistribution = ref<DistributionItem[]>([])

// 内容偏好
const readingPreferences = ref({
    categories: [] as Array<{ name: string; count: number }>
})

// 图表引用
const readTrendChartRef = ref<HTMLElement | null>(null)
const articleTypeChartRef = ref<HTMLElement | null>(null)

// 选择时间范围
function selectTimeRange(range: 'week' | 'month' | 'year') {
    selectedRange.value = range
    message.info(`已切换到${range === 'week' ? '周' : range === 'month' ? '月' : '年'}度数据`)
}

// 格式化数字
function formatNumber(num: number): string {
    if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万'
    }
    return num.toString()
}

// 获取分类类型
function getCategoryType(category: string): string {
    const types = ['primary', 'success', 'warning', 'info', 'danger']
    const hash = category.split('').reduce((sum, char) => sum + char.charCodeAt(0), 0)
    return types[hash % types.length]
}

function getCurrentMonthRange(): [string, string] {
    const now = new Date()
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    return [formatDateInput(start), formatDateInput(now)]
}

function formatDateInput(date: Date): string {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
}

function formatDate(value?: string): string {
    if (!value) return '未知'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return value
    return formatDateInput(date)
}

function normalizeCategory(article: IArticle): string {
    return article.category || article.resource_type || '未分类'
}

function buildDistribution(articles: IArticle[]): DistributionItem[] {
    const counts = new Map<string, number>()
    articles.forEach(article => {
        const category = normalizeCategory(article)
        counts.set(category, (counts.get(category) || 0) + 1)
    })

    const max = Math.max(...Array.from(counts.values()), 1)
    return Array.from(counts.entries())
        .map(([name, count]) => ({
            name,
            count,
            percent: Math.max(8, Math.round((count / max) * 100))
        }))
        .sort((a, b) => b.count - a.count)
}

function buildTrend(articles: IArticle[]): TrendItem[] {
    const recent = [...articles]
        .sort((a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime())
        .slice(-7)
    const maxReads = Math.max(...recent.map(article => article.views || 0), 1)

    return recent.map(article => ({
        id: article.id,
        title: article.title,
        reads: article.views || 0,
        percent: Math.max(8, Math.round(((article.views || 0) / maxReads) * 100))
    }))
}

async function fetchPersonalData() {
    try {
        const currentUserId = globalStore.userInfo?.id
        const params = currentUserId ? { author_id: currentUserId } : undefined
        const [articles, contextPacks] = await Promise.all([
            articleApi.getList(params),
            contextPackApi.getList().catch(() => [] as ContextPack[])
        ])
        const distribution = buildDistribution(articles)
        const ownedContextPacks = currentUserId
            ? contextPacks.filter(pack => pack.user_id === currentUserId)
            : []

        myArticles.value = articles.map(article => ({
            id: article.id,
            title: article.title,
            category: normalizeCategory(article),
            reads: article.views || 0,
            likes: article.likes || 0,
            comments: article.comments_count || 0,
            createTime: formatDate(article.created_at)
        }))

        categoryDistribution.value = distribution
        readTrendData.value = buildTrend(articles)
        readingPreferences.value.categories = distribution.map(({ name, count }) => ({ name, count }))

        personalData.value = {
            totalArticles: articles.length,
            totalReads: articles.reduce((sum, article) => sum + (article.views || 0), 0),
            totalLikes: articles.reduce((sum, article) => sum + (article.likes || 0), 0),
            contextPacks: ownedContextPacks.length,
            publishedArticles: articles.filter(article => article.status === 'published').length,
            draftArticles: articles.filter(article => article.status !== 'published').length
        }
    } catch (error) {
        console.error('获取个人看板数据失败', error)
        message.error('获取个人看板数据失败')
    }
}

// 去写文章
function goToWriteArticle() {
    router.push('/essays/write')
}

// 查看文章
function viewArticle(id: number) {
    router.push(`/essays/${id}`)
}

// 编辑文章
function editArticle(id: number) {
    router.push(`/essays/edit/${id}`)
}

// 生命周期钩子
onMounted(() => {
    fetchPersonalData()
})
</script>

<style scoped>
.personal-dashboard-container {
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: linear-gradient(135deg, #fff 0%, #fff8f5 100%);
    min-height: 100vh;
}

/* 页面头部 */
.dashboard-header {
    background: white;
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
    background: rgba(255, 127, 80, 0.02);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    position: relative;
    overflow: hidden;
}

.read-trend-bars {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    padding: 1rem 1.25rem;
    box-sizing: border-box;
}

.trend-bar-item {
    min-width: 0;
    flex: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    gap: 0.45rem;
}

.trend-bar-track {
    width: 100%;
    max-width: 42px;
    height: 180px;
    border-radius: 8px;
    background: rgba(255, 127, 80, 0.12);
    display: flex;
    align-items: flex-end;
    overflow: hidden;
}

.trend-bar-fill {
    width: 100%;
    min-height: 8px;
    background: linear-gradient(180deg, #FFB347 0%, #FF7F50 100%);
    border-radius: 8px 8px 0 0;
}

.trend-bar-value {
    font-size: 0.8rem;
    color: #555;
    font-weight: 700;
}

.trend-bar-label {
    width: 100%;
    color: #777;
    font-size: 0.75rem;
    text-align: center;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.article-type-list {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 1rem;
    padding: 1.25rem;
    box-sizing: border-box;
}

.type-row {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
}

.type-row-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    color: #333;
    font-size: 0.9rem;
}

.type-row-track {
    width: 100%;
    height: 10px;
    background: rgba(255, 127, 80, 0.12);
    border-radius: 999px;
    overflow: hidden;
}

.type-row-fill {
    height: 100%;
    background: linear-gradient(90deg, #FF7F50 0%, #FFB347 100%);
    border-radius: inherit;
}

.empty-chart {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    font-size: 0.95rem;
}

/* 文章部分 */
.articles-section {
    margin-bottom: 2rem;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #333;
    margin: 0;
}

.articles-table {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    padding: 1rem;
    overflow-x: auto;
}

.article-title {
    font-weight: 600;
    color: #333;
    cursor: pointer;
    transition: color 0.2s ease;
}

.article-title:hover {
    color: #FF7F50;
}

/* 阅读偏好 */
.preferences-section {
    margin-bottom: 2rem;
}

.preferences-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.preference-card {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.category-tags {
    display: flex;
    flex-wrap: wrap;
}

.tag-count {
    font-size: 0.8rem;
    opacity: 0.8;
    margin-left: 0.5rem;
}

.reading-time {
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 2rem 0;
}

.time-item {
    text-align: center;
}

.time-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #FF7F50;
    margin-bottom: 0.5rem;
}

.time-label {
    font-size: 0.9rem;
    color: #666;
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
    .chart-grid,
    .preferences-grid {
        grid-template-columns: 1fr;
    }

    .chart-container {
        height: 250px;
    }

    .card-value {
        font-size: 2rem;
    }

    .section-header {
        flex-direction: column;
        align-items: stretch;
    }

    .reading-time {
        flex-direction: column;
        gap: 2rem;
    }
}
</style>
