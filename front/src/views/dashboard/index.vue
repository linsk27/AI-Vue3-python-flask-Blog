<template>
    <div class="dashboard-container">
        <router-view v-if="$route.path !== '/dashboard'" />
        <div v-else>
            <!-- 页面头部 -->
            <header class="dashboard-header">
                <div class="header-left">
                    <div class="header-icon">📊</div>
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
                        <div class="overview-card">
                            <div class="card-header">
                                <h3 class="card-title">总文章数</h3>
                                <div class="card-icon">📄</div>
                            </div>
                            <div class="card-content">
                                <div class="card-value">{{ overviewData.totalArticles }}</div>
                                <div class="card-change"
                                    :class="overviewData.articleChange >= 0 ? 'positive' : 'negative'">
                                    {{ overviewData.articleChange >= 0 ? '+' : '' }}{{ overviewData.articleChange }}%
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
                                <div class="card-value">{{ formatNumber(overviewData.totalReads) }}</div>
                                <div class="card-change"
                                    :class="overviewData.readChange >= 0 ? 'positive' : 'negative'">
                                    {{ overviewData.readChange >= 0 ? '+' : '' }}{{ overviewData.readChange }}%
                                    <span>较上月</span>
                                </div>
                            </div>
                        </div>

                        <div class="overview-card">
                            <div class="card-header">
                                <h3 class="card-title">活跃用户</h3>
                                <div class="card-icon">👥</div>
                            </div>
                            <div class="card-content">
                                <div class="card-value">{{ overviewData.activeUsers }}</div>
                                <div class="card-change"
                                    :class="overviewData.userChange >= 0 ? 'positive' : 'negative'">
                                    {{ overviewData.userChange >= 0 ? '+' : '' }}{{ overviewData.userChange }}%
                                    <span>较上月</span>
                                </div>
                            </div>
                        </div>

                        <div class="overview-card">
                            <div class="card-header">
                                <h3 class="card-title">AI使用次数</h3>
                                <div class="card-icon">🤖</div>
                            </div>
                            <div class="card-content">
                                <div class="card-value">{{ overviewData.aiUsage }}</div>
                                <div class="card-change" :class="overviewData.aiChange >= 0 ? 'positive' : 'negative'">
                                    {{ overviewData.aiChange >= 0 ? '+' : '' }}{{ overviewData.aiChange }}%
                                    <span>较上月</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- 快速导航 -->
                <section class="navigation-section">
                    <div class="navigation-grid">
                        <div class="navigation-card" @click="goToPersonalDashboard">
                            <div class="navigation-icon">👤</div>
                            <h3 class="navigation-title">个人数据看板</h3>
                            <p class="navigation-description">查看您个人的创作、阅读和互动数据</p>
                            <div class="navigation-action">
                                <span>进入</span>
                                <span class="action-icon">→</span>
                            </div>
                        </div>

                        <div class="navigation-card" @click="goToTeamDashboard">
                            <div class="navigation-icon">👥</div>
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
                                <div ref="articleChartRef" class="chart-container">
                                    <div class="article-trend-placeholder">
                                        <div class="trend-line"></div>
                                        <div class="trend-points">
                                            <div class="trend-point"></div>
                                            <div class="trend-point"></div>
                                            <div class="trend-point"></div>
                                            <div class="trend-point"></div>
                                            <div class="trend-point"></div>
                                            <div class="trend-point"></div>
                                            <div class="trend-point"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 阅读量分布 -->
                        <div class="chart-card">
                            <div class="chart-header">
                                <h3 class="chart-title">阅读量分布</h3>
                            </div>
                            <div class="chart-content">
                                <div ref="readChartRef" class="chart-container">
                                    <div class="read-distribution-placeholder">
                                        <div class="distribution-chart">
                                            <div class="distribution-bar"></div>
                                            <div class="distribution-bar"></div>
                                            <div class="distribution-bar"></div>
                                            <div class="distribution-bar"></div>
                                            <div class="distribution-bar"></div>
                                        </div>
                                    </div>
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
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useElMessage } from '@/hooks/useMessage'

const { message } = useElMessage()

const router = useRouter()

// 时间范围
const dateRange = ref(['2026-01-01', '2026-01-31'])
const selectedRange = ref('month')

// 概览数据
const overviewData = ref({
    totalArticles: 125,
    articleChange: 15.2,
    totalReads: 35682,
    readChange: 8.7,
    activeUsers: 245,
    userChange: 12.3,
    aiUsage: 892,
    aiChange: 25.8
})

// 热门标签
const topTags = ref([
    { name: 'Vue3', count: 45 },
    { name: 'JavaScript', count: 38 },
    { name: 'TypeScript', count: 32 },
    { name: '前端开发', count: 28 },
    { name: '性能优化', count: 22 },
    { name: 'AI', count: 18 },
    { name: '数据可视化', count: 15 },
    { name: '组件设计', count: 12 },
    { name: '响应式设计', count: 10 },
    { name: '工程化', count: 8 }
])

// 活跃作者
const topAuthors = ref([
    { name: '张三', articles: 15, reads: 8952, rank: 1 },
    { name: '李四', articles: 12, reads: 6789, rank: 2 },
    { name: '王五', articles: 10, reads: 5421, rank: 3 },
    { name: '赵六', articles: 8, reads: 4321, rank: 4 },
    { name: '孙七', articles: 7, reads: 3892, rank: 5 }
])

// 图表引用
const articleChartRef = ref<HTMLElement | null>(null)
const readChartRef = ref<HTMLElement | null>(null)

// 选择时间范围
function selectTimeRange(range: 'week' | 'month' | 'year') {
    selectedRange.value = range
    // 在实际项目中，这里会更新图表数据
    message.info(`已切换到${range === 'week' ? '周' : range === 'month' ? '月' : '年'}度数据`)
}

// 格式化数字
function formatNumber(num: number): string {
    if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万'
    }
    return num.toString()
}

// 跳转到个人数据看板
function goToPersonalDashboard() {
    router.push('/dashboard/personal')
}

// 跳转到团队数据看板
function goToTeamDashboard() {
    router.push('/dashboard/team')
}

// 初始化图表（模拟）
function initCharts() {
    // 在实际项目中，这里会使用ECharts或D3.js初始化图表
    console.log('初始化图表')
}

// 生命周期钩子
onMounted(() => {
    initCharts()
})

// 监听时间范围变化
watch(dateRange, (newRange) => {
    // 在实际项目中，这里会根据新的时间范围更新数据
    console.log('时间范围变化:', newRange)
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
    font-size: 3rem;
    margin-bottom: 1.5rem;
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

/* 模拟图表内容 */
.chart-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    padding: 2rem;
    box-sizing: border-box;
}

/* 文章增长趋势图表模拟 */
.article-trend-placeholder {
    position: relative;
    width: 100%;
    height: 100%;
}

.trend-line {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg,
            transparent 0%, transparent 10%,
            rgba(255, 127, 80, 0.1) 10%, rgba(255, 127, 80, 0.1) 15%,
            transparent 15%, transparent 25%,
            rgba(255, 127, 80, 0.2) 25%, rgba(255, 127, 80, 0.2) 30%,
            transparent 30%, transparent 40%,
            rgba(255, 127, 80, 0.3) 40%, rgba(255, 127, 80, 0.3) 45%,
            transparent 45%, transparent 55%,
            rgba(255, 127, 80, 0.4) 55%, rgba(255, 127, 80, 0.4) 60%,
            transparent 60%, transparent 70%,
            rgba(255, 127, 80, 0.5) 70%, rgba(255, 127, 80, 0.5) 75%,
            transparent 75%, transparent 85%,
            rgba(255, 127, 80, 0.6) 85%, rgba(255, 127, 80, 0.6) 90%,
            transparent 90%, transparent 100%);
}

.trend-points {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: space-around;
    align-items: flex-end;
    padding: 0 2rem;
    box-sizing: border-box;
}

.trend-point {
    width: 12px;
    height: 12px;
    background: #FF7F50;
    border-radius: 50%;
    box-shadow: 0 2px 8px rgba(255, 127, 80, 0.3);
}

/* 阅读量分布图表模拟 */
.read-distribution-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.distribution-chart {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: flex-end;
    justify-content: space-around;
    padding: 0 2rem;
    box-sizing: border-box;
}

.distribution-bar {
    width: 15%;
    background: linear-gradient(to top, #FF7F50, rgba(255, 127, 80, 0.6));
    border-radius: 4px 4px 0 0;
    animation: pulse 2s ease-in-out infinite alternate;
}

.distribution-bar:nth-child(1) {
    height: 60%;
    animation-delay: 0s;
}

.distribution-bar:nth-child(2) {
    height: 85%;
    animation-delay: 0.2s;
}

.distribution-bar:nth-child(3) {
    height: 50%;
    animation-delay: 0.4s;
}

.distribution-bar:nth-child(4) {
    height: 75%;
    animation-delay: 0.6s;
}

.distribution-bar:nth-child(5) {
    height: 40%;
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