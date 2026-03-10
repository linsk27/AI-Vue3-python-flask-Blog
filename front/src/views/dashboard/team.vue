<template>
    <div class="team-dashboard-container">
        <!-- 页面头部 -->
        <header class="dashboard-header">
            <div class="header-left">
                <div class="header-icon">👥</div>
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
                            <div class="card-icon">📄</div>
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ teamData.totalArticles }}</div>
                            <div class="card-change" :class="teamData.articleChange >= 0 ? 'positive' : 'negative'">
                                {{ teamData.articleChange >= 0 ? '+' : '' }}{{ teamData.articleChange }}%
                                <span>较上月</span>
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">总阅读量</h3>
                            <div class="card-icon">👁️</div>
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ formatNumber(teamData.totalReads) }}</div>
                            <div class="card-change" :class="teamData.readChange >= 0 ? 'positive' : 'negative'">
                                {{ teamData.readChange >= 0 ? '+' : '' }}{{ teamData.readChange }}%
                                <span>较上月</span>
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">活跃成员</h3>
                            <div class="card-icon">👤</div>
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ teamData.activeMembers }}</div>
                            <div class="card-change" :class="teamData.memberChange >= 0 ? 'positive' : 'negative'">
                                {{ teamData.memberChange >= 0 ? '+' : '' }}{{ teamData.memberChange }}%
                                <span>较上月</span>
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">团队AI使用次数</h3>
                            <div class="card-icon">🤖</div>
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ teamData.aiUsage }}</div>
                            <div class="card-change" :class="teamData.aiChange >= 0 ? 'positive' : 'negative'">
                                {{ teamData.aiChange >= 0 ? '+' : '' }}{{ teamData.aiChange }}%
                                <span>较上月</span>
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
                                <div class="contribution-placeholder">
                                    <div class="contribution-radar">
                                        <div class="radar-grid"></div>
                                        <div class="radar-shape"></div>
                                    </div>
                                    <div class="type-legend">
                                        <div class="type-legend-item">
                                            <div class="type-legend-color"></div>
                                            <span>文章数量</span>
                                        </div>
                                        <div class="type-legend-item">
                                            <div class="type-legend-color"></div>
                                            <span>阅读量</span>
                                        </div>
                                        <div class="type-legend-item">
                                            <div class="type-legend-color"></div>
                                            <span>点赞数</span>
                                        </div>
                                        <div class="type-legend-item">
                                            <div class="type-legend-color"></div>
                                            <span>评论数</span>
                                        </div>
                                        <div class="type-legend-item">
                                            <div class="type-legend-color"></div>
                                            <span>AI使用</span>
                                        </div>
                                    </div>
                                </div>
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
                                <div class="category-distribution-placeholder">
                                    <div class="category-bar"></div>
                                    <div class="category-bar"></div>
                                    <div class="category-bar"></div>
                                    <div class="category-bar"></div>
                                    <div class="category-bar"></div>
                                </div>
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
                        <el-table-column prop="aiUsage" label="AI使用次数" width="120" align="right">
                            <template #default="scope">
                                <span>{{ scope.row.aiUsage }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column label="操作" width="120" align="center">
                            <template #default="scope">
                                <el-button type="text" @click="viewMemberDetail(scope.row.id)">
                                    查看详情
                                </el-button>
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
                    <div class="hot-article-item" v-for="article in hotArticles" :key="article.id">
                        <div class="article-rank">{{ article.rank }}</div>
                        <div class="article-info">
                            <div class="article-title">{{ article.title }}</div>
                            <div class="article-meta">
                                <span class="article-author">{{ article.author }}</span>
                                <span class="article-reads">{{ formatNumber(article.reads) }}次阅读</span>
                            </div>
                        </div>
                        <div class="article-likes">{{ article.likes }}👍</div>
                    </div>
                </div>
            </section>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useElMessage } from '@/hooks/useMessage'

const { message } = useElMessage()

const router = useRouter()

// 时间范围
const dateRange = ref(['2026-01-01', '2026-01-31'])

// 团队数据
const teamData = ref({
    totalArticles: 156,
    articleChange: 12.8,
    totalReads: 89563,
    readChange: 9.2,
    activeMembers: 32,
    memberChange: 5.3,
    aiUsage: 1256,
    aiChange: 28.5
})

// 团队成员数据
const teamMembers = ref([
    { id: 1, name: '张三', avatar: '', articles: 28, reads: 12345, likes: 456, aiUsage: 123 },
    { id: 2, name: '李四', avatar: '', articles: 22, reads: 9876, likes: 345, aiUsage: 98 },
    { id: 3, name: '王五', avatar: '', articles: 18, reads: 15678, likes: 567, aiUsage: 145 },
    { id: 4, name: '赵六', avatar: '', articles: 15, reads: 7654, likes: 234, aiUsage: 89 },
    { id: 5, name: '孙七', avatar: '', articles: 12, reads: 8923, likes: 198, aiUsage: 67 }
])

// 热门文章数据
const hotArticles = ref([
    { id: 1, title: 'Vue 3 组合式 API 最佳实践', author: '张三', reads: 5678, likes: 234, rank: 1 },
    { id: 2, title: '前端性能优化实战指南', author: '王五', reads: 4567, likes: 198, rank: 2 },
    { id: 3, title: 'TypeScript 类型系统深度解析', author: '李四', reads: 3456, likes: 156, rank: 3 },
    { id: 4, title: '响应式设计的艺术', author: '赵六', reads: 2345, likes: 123, rank: 4 },
    { id: 5, title: 'Vuex 4 与 Pinia 对比分析', author: '张三', reads: 1890, likes: 98, rank: 5 }
])

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

// 查看成员详情
function viewMemberDetail(id: number) {
    message.info(`查看成员${id}详情`)
    // router.push(`/dashboard/member/${id}`)
}

// 初始化图表（模拟）
function initCharts() {
    // 在实际项目中，这里会使用ECharts或D3.js初始化图表
    console.log('初始化团队数据图表')
}

// 生命周期钩子
onMounted(() => {
    initCharts()
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
    font-size: 2rem;
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
    font-size: 1.5rem;
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

/* 成员贡献分布图表模拟 */
.contribution-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.contribution-radar {
    width: 200px;
    height: 200px;
    position: relative;
    transform: rotate(-90deg);
}

.radar-grid {
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    border: 2px solid rgba(255, 127, 80, 0.1);
    border-radius: 50%;
}

.radar-grid::before,
.radar-grid::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 2px;
    background: rgba(255, 127, 80, 0.1);
    top: 50%;
    left: 0;
    transform: translateY(-50%);
}

.radar-grid::after {
    width: 2px;
    height: 100%;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
}

.radar-shape {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100%;
    height: 100%;
    transform: translate(-50%, -50%);
    clip-path: polygon(50% 0%,
            80% 20%,
            100% 50%,
            80% 80%,
            50% 100%,
            20% 80%,
            0% 50%,
            20% 20%);
    background: rgba(255, 127, 80, 0.2);
}

.type-legend {
    position: absolute;
    right: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.type-legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    color: #333;
}

.type-legend-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.type-legend-color:nth-child(1) {
    background: #FF7F50;
}

.type-legend-color:nth-child(2) {
    background: #FFD700;
}

.type-legend-color:nth-child(3) {
    background: #98FB98;
}

.type-legend-color:nth-child(4) {
    background: #87CEEB;
}

.type-legend-color:nth-child(5) {
    background: #FF6347;
}

/* 文章分类分布图表模拟 */
.category-distribution-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: flex-end;
    justify-content: space-around;
    padding: 0 2rem;
    box-sizing: border-box;
}

.category-bar {
    width: 15%;
    background: linear-gradient(to top, #FF7F50, rgba(255, 127, 80, 0.6));
    border-radius: 4px 4px 0 0;
    animation: pulse 2s ease-in-out infinite alternate;
}

.category-bar:nth-child(1) {
    height: 75%;
    animation-delay: 0s;
}

.category-bar:nth-child(2) {
    height: 60%;
    animation-delay: 0.2s;
}

.category-bar:nth-child(3) {
    height: 85%;
    animation-delay: 0.4s;
}

.category-bar:nth-child(4) {
    height: 55%;
    animation-delay: 0.6s;
}

.category-bar:nth-child(5) {
    height: 70%;
    animation-delay: 0.8s;
}

@keyframes pulse {
    from {
        opacity: 0.6;
    }

    to {
        opacity: 1;
    }
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
    font-weight: 600;
    color: #FF7F50;
    font-size: 1.1rem;
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