<template>
    <div class="team-dashboard-container">
        <!-- 页面头部 -->
        <header class="dashboard-header">
            <div class="header-left">
                <UserFilled class="header-icon" />
                <div class="header-info">
                    <h1 class="dashboard-title">团队数据看板</h1>
                    <p class="dashboard-subtitle">团队知识产出与协作数据分析</p>
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
            <!-- 团队概览卡片 -->
            <section class="overview-section">
                <div class="overview-grid">
                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">团队总文章数</h3>
                            <Document class="card-icon" />
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ teamData.totalArticles }}</div>
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
                            <div class="card-value">{{ formatNumber(teamData.totalReads) }}</div>
                            <div class="card-change neutral">
                                <span>按浏览量汇总</span>
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">活跃成员</h3>
                            <User class="card-icon" />
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ teamData.activeMembers }}</div>
                            <div class="card-change neutral">
                                <span>有文章贡献的成员</span>
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">上下文包数</h3>
                            <Collection class="card-icon" />
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ teamData.contextPacks }}</div>
                            <div class="card-change neutral">
                                <span>可用于 AI 对话</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 团队协作图表 -->
            <section class="charts-section">
                <div class="chart-grid">
                    <!-- 成员贡献分布 -->
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3 class="chart-title">成员贡献分布</h3>
                        </div>
                        <div class="chart-content">
                            <div ref="contributionChartRef" class="chart-container">
                                <div v-if="memberContributionData.length" class="contribution-list">
                                    <div v-for="member in memberContributionData" :key="member.id" class="contribution-row">
                                        <div class="contribution-row-header">
                                            <span>{{ member.name }}</span>
                                            <strong>{{ member.articles }} 篇</strong>
                                        </div>
                                        <div class="contribution-track">
                                            <div class="contribution-fill" :style="{ width: `${member.percent}%` }"></div>
                                        </div>
                                    </div>
                                </div>
                                <div v-else class="empty-chart">暂无成员贡献数据</div>
                            </div>
                        </div>
                    </div>

                    <!-- 文章分类分布 -->
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3 class="chart-title">文章分类分布</h3>
                        </div>
                        <div class="chart-content">
                            <div ref="categoryChartRef" class="chart-container">
                                <div v-if="categoryDistribution.length" class="category-list">
                                    <div v-for="item in categoryDistribution" :key="item.name" class="category-row">
                                        <div class="category-row-header">
                                            <span>{{ item.name }}</span>
                                            <strong>{{ item.count }} 篇</strong>
                                        </div>
                                        <div class="category-track">
                                            <div class="category-fill" :style="{ width: `${item.percent}%` }"></div>
                                        </div>
                                    </div>
                                </div>
                                <div v-else class="empty-chart">暂无分类数据</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 团队成员表现 -->
            <section class="members-section">
                <div class="section-header">
                    <h2 class="section-title">团队成员表现</h2>
                </div>
                <div class="members-table">
                    <el-table :data="teamMembers" stripe style="width: 100%">
                        <el-table-column prop="name" label="成员姓名" width="150">
                            <template #default="scope">
                                <div class="member-info">
                                    <el-avatar :size="32" :src="scope.row.avatar" />
                                    <span class="member-name">{{ scope.row.name }}</span>
                                </div>
                            </template>
                        </el-table-column>
                        <el-table-column prop="articles" label="发布文章" width="120" align="right">
                            <template #default="scope">
                                <el-badge :value="scope.row.articles"
                                    :type="scope.row.articles > 10 ? 'success' : 'info'" />
                            </template>
                        </el-table-column>
                        <el-table-column prop="reads" label="总阅读量" width="120" align="right">
                            <template #default="scope">
                                <span>{{ formatNumber(scope.row.reads) }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="likes" label="获赞数" width="100" align="right">
                            <template #default="scope">
                                <span>{{ scope.row.likes }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="contribution" label="贡献占比" width="120" align="right">
                            <template #default="scope">
                                <span>{{ scope.row.contribution }}%</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
            </section>

            <!-- 团队热门文章 -->
            <section class="articles-section">
                <div class="section-header">
                    <h2 class="section-title">团队热门文章</h2>
                </div>
                <div class="hot-articles">
                    <div class="hot-article-item" v-for="article in hotArticles" :key="article.id"
                        @click="viewArticle(article.id)">
                        <div class="article-rank">{{ article.rank }}</div>
                        <div class="article-info">
                            <div class="article-title">{{ article.title }}</div>
                            <div class="article-meta">
                                <span class="article-author">{{ article.author }}</span>
                                <span class="article-reads">{{ formatNumber(article.reads) }}次阅读</span>
                            </div>
                        </div>
                        <div class="article-likes">
                            <Star class="inline-icon" />
                            <span>{{ article.likes }}</span>
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
import { Collection, Document, Star, User, UserFilled, View } from '@element-plus/icons-vue'
import articleApi from '@/api/modules/article'
import { IArticle } from '@/api/modules/article/interface'
import contextPackApi from '@/api/modules/contextPacks'
import { useElMessage } from '@/hooks/useMessage'

const { message } = useElMessage()

const router = useRouter()

interface TeamMemberRow {
    id: number
    name: string
    avatar: string
    articles: number
    reads: number
    likes: number
    contribution: number
    percent: number
}

interface HotArticleRow {
    id: number
    title: string
    author: string
    reads: number
    likes: number
    rank: number
}

interface DistributionItem {
    name: string
    count: number
    percent: number
}

// 时间范围
const dateRange = ref(getCurrentMonthRange())

// 团队数据
const teamData = ref({
    totalArticles: 0,
    totalReads: 0,
    activeMembers: 0,
    contextPacks: 0
})

// 团队成员数据
const teamMembers = ref<TeamMemberRow[]>([])
const memberContributionData = ref<TeamMemberRow[]>([])
const categoryDistribution = ref<DistributionItem[]>([])

// 热门文章数据
const hotArticles = ref<HotArticleRow[]>([])

// 图表引用
const contributionChartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)

// 格式化数字
function formatNumber(num: number): string {
    if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万'
    }
    return num.toString()
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

function normalizeCategory(article: IArticle): string {
    return article.category || article.resource_type || '未分类'
}

function buildTeamMembers(articles: IArticle[]): TeamMemberRow[] {
    const memberMap = new Map<number, TeamMemberRow>()

    articles.forEach(article => {
        const memberId = article.author_id || 0
        const current = memberMap.get(memberId) || {
            id: memberId,
            name: article.author_name || `用户 ${memberId || '未知'}`,
            avatar: article.author_avatar || '',
            articles: 0,
            reads: 0,
            likes: 0,
            contribution: 0,
            percent: 0
        }

        current.articles += 1
        current.reads += article.views || 0
        current.likes += article.likes || 0
        memberMap.set(memberId, current)
    })

    const totalArticles = Math.max(articles.length, 1)
    const maxArticles = Math.max(...Array.from(memberMap.values()).map(member => member.articles), 1)

    return Array.from(memberMap.values())
        .map(member => ({
            ...member,
            contribution: Math.round((member.articles / totalArticles) * 100),
            percent: Math.max(8, Math.round((member.articles / maxArticles) * 100))
        }))
        .sort((a, b) => b.articles - a.articles || b.reads - a.reads)
}

function buildCategoryDistribution(articles: IArticle[]): DistributionItem[] {
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

function buildHotArticles(articles: IArticle[]): HotArticleRow[] {
    return [...articles]
        .sort((a, b) => (b.views || 0) - (a.views || 0))
        .slice(0, 5)
        .map((article, index) => ({
            id: article.id,
            title: article.title,
            author: article.author_name || `用户 ${article.author_id || '未知'}`,
            reads: article.views || 0,
            likes: article.likes || 0,
            rank: index + 1
        }))
}

async function fetchTeamData() {
    try {
        const [articles, contextStats] = await Promise.all([
            articleApi.getList(),
            contextPackApi.getStats().catch(() => null)
        ])
        const members = buildTeamMembers(articles)

        teamMembers.value = members
        memberContributionData.value = members.slice(0, 6)
        categoryDistribution.value = buildCategoryDistribution(articles)
        hotArticles.value = buildHotArticles(articles)

        teamData.value = {
            totalArticles: articles.length,
            totalReads: articles.reduce((sum, article) => sum + (article.views || 0), 0),
            activeMembers: members.length,
            contextPacks: contextStats?.packs || 0
        }
    } catch (error) {
        console.error('获取团队看板数据失败', error)
        message.error('获取团队看板数据失败')
    }
}

function viewArticle(id: number) {
    router.push(`/essays/${id}`)
}

// 生命周期钩子
onMounted(() => {
    fetchTeamData()
})
</script>

<style scoped>
.team-dashboard-container {
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
}

.chart-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #333;
    margin: 0;
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

.contribution-list,
.category-list {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 1rem;
    padding: 1.25rem;
    box-sizing: border-box;
}

.contribution-row,
.category-row {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
}

.contribution-row-header,
.category-row-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    color: #333;
    font-size: 0.9rem;
}

.contribution-track,
.category-track {
    width: 100%;
    height: 10px;
    background: rgba(255, 127, 80, 0.12);
    border-radius: 999px;
    overflow: hidden;
}

.contribution-fill,
.category-fill {
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

/* 成员表格 */
.members-section {
    margin-bottom: 2rem;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #333;
    margin: 0;
}

.members-table {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    padding: 1rem;
    overflow-x: auto;
}

.member-info {
    display: flex;
    align-items: center;
    gap: 10px;
}

.member-name {
    font-weight: 600;
    color: #333;
}

/* 热门文章 */
.articles-section {
    margin-bottom: 2rem;
}

.hot-articles {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.hot-article-item {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    cursor: pointer;
}

.hot-article-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.article-rank {
    width: 30px;
    height: 30px;
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
}

.article-info {
    flex: 1;
}

.article-title {
    font-weight: 600;
    color: #333;
    margin-bottom: 0.5rem;
    transition: color 0.2s ease;
}

.article-title:hover {
    color: #FF7F50;
}

.article-meta {
    display: flex;
    gap: 1.5rem;
    font-size: 0.85rem;
    color: #666;
}

.article-likes {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-weight: 600;
    color: #FF7F50;
    font-size: 1.1rem;
}

.inline-icon {
    width: 1rem;
    height: 1rem;
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
    .chart-grid {
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

    .hot-article-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .article-meta {
        flex-direction: column;
        gap: 0.5rem;
    }
}
</style>
