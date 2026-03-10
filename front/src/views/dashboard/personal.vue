<template>
    <div class="personal-dashboard-container">
        <!-- 页面头部 -->
        <header class="dashboard-header">
            <div class="header-left">
                <div class="header-icon">👤</div>
                <div class="header-info">
                    <h1 class="dashboard-title">个人数据看板</h1>
                    <p class="dashboard-subtitle">追踪您的创作、阅读和互动数据</p>
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
                            <div class="card-icon">📄</div>
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ personalData.totalArticles }}</div>
                            <div class="card-change" :class="personalData.articleChange >= 0 ? 'positive' : 'negative'">
                                {{ personalData.articleChange >= 0 ? '+' : '' }}{{ personalData.articleChange }}%
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
                            <div class="card-value">{{ formatNumber(personalData.totalReads) }}</div>
                            <div class="card-change" :class="personalData.readChange >= 0 ? 'positive' : 'negative'">
                                {{ personalData.readChange >= 0 ? '+' : '' }}{{ personalData.readChange }}%
                                <span>较上月</span>
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-header">
                            <h3 class="card-title">总点赞数</h3>
                            <div class="card-icon">👍</div>
                        </div>
                        <div class="card-content">
                            <div class="card-value">{{ personalData.totalLikes }}</div>
                            <div class="card-change" :class="personalData.likeChange >= 0 ? 'positive' : 'negative'">
                                {{ personalData.likeChange >= 0 ? '+' : '' }}{{ personalData.likeChange }}%
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
                            <div class="card-value">{{ personalData.aiUsage }}</div>
                            <div class="card-change" :class="personalData.aiChange >= 0 ? 'positive' : 'negative'">
                                {{ personalData.aiChange >= 0 ? '+' : '' }}{{ personalData.aiChange }}%
                                <span>较上月</span>
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
                                <div class="read-trend-placeholder">
                                    <div class="trend-line-container">
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
                    </div>

                    <!-- 文章类型分布 -->
                    <div class="chart-card">
                        <div class="chart-header">
                            <h3 class="chart-title">文章类型分布</h3>
                        </div>
                        <div class="chart-content">
                            <div ref="articleTypeChartRef" class="chart-container">
                                <div class="article-type-placeholder">
                                    <div class="type-pie-chart"></div>
                                    <div class="type-legend">
                                        <div class="type-legend-item">
                                            <div class="type-legend-color"></div>
                                            <span>前端开发</span>
                                        </div>
                                        <div class="type-legend-item">
                                            <div class="type-legend-color"></div>
                                            <span>TypeScript</span>
                                        </div>
                                        <div class="type-legend-item">
                                            <div class="type-legend-color"></div>
                                            <span>性能优化</span>
                                        </div>
                                        <div class="type-legend-item">
                                            <div class="type-legend-color"></div>
                                            <span>状态管理</span>
                                        </div>
                                        <div class="type-legend-item">
                                            <div class="type-legend-color"></div>
                                            <span>设计</span>
                                        </div>
                                    </div>
                                </div>
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
                        <el-icon-plus /> 写文章
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
                    <h2 class="section-title">我的阅读偏好</h2>
                </div>
                <div class="preferences-grid">
                    <div class="preference-card">
                        <div class="card-header">
                            <h3 class="card-title">常读分类</h3>
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
                            <h3 class="card-title">阅读时长</h3>
                        </div>
                        <div class="card-content">
                            <div class="reading-time">
                                <div class="time-item">
                                    <div class="time-value">{{ readingPreferences.dailyAverage }}分钟</div>
                                    <div class="time-label">日均阅读</div>
                                </div>
                                <div class="time-item">
                                    <div class="time-value">{{ readingPreferences.weeklyTotal }}小时</div>
                                    <div class="time-label">本周总阅读</div>
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
import { useElMessage } from '@/hooks/useMessage'

const { message } = useElMessage()

const router = useRouter()

// 时间范围
const dateRange = ref(['2026-01-01', '2026-01-31'])
const selectedRange = ref('month')

// 个人数据
const personalData = ref({
    totalArticles: 28,
    articleChange: 18.5,
    totalReads: 5892,
    readChange: 12.3,
    totalLikes: 456,
    likeChange: 22.7,
    aiUsage: 125,
    aiChange: 35.2
})

// 我的文章
const myArticles = ref([
    {
        id: 1,
        title: 'Vue 3 组合式 API 最佳实践',
        category: '前端开发',
        reads: 1234,
        likes: 89,
        comments: 23,
        createTime: '2026-01-28'
    },
    {
        id: 2,
        title: 'TypeScript 类型系统深度解析',
        category: 'TypeScript',
        reads: 987,
        likes: 67,
        comments: 15,
        createTime: '2026-01-25'
    },
    {
        id: 3,
        title: '前端性能优化实战指南',
        category: '性能优化',
        reads: 1567,
        likes: 123,
        comments: 45,
        createTime: '2026-01-20'
    },
    {
        id: 4,
        title: 'Vuex 4 与 Pinia 对比分析',
        category: '状态管理',
        reads: 892,
        likes: 56,
        comments: 18,
        createTime: '2026-01-15'
    },
    {
        id: 5,
        title: '响应式设计的艺术',
        category: '设计',
        reads: 678,
        likes: 43,
        comments: 12,
        createTime: '2026-01-10'
    }
])

// 阅读偏好
const readingPreferences = ref({
    categories: [
        { name: '前端开发', count: 45 },
        { name: 'TypeScript', count: 32 },
        { name: '性能优化', count: 28 },
        { name: '状态管理', count: 22 },
        { name: '设计', count: 18 }
    ],
    dailyAverage: 45,
    weeklyTotal: 5.2
})

// 图表引用
const readTrendChartRef = ref<HTMLElement | null>(null)
const articleTypeChartRef = ref<HTMLElement | null>(null)

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

// 获取分类类型
function getCategoryType(category: string): string {
    const typeMap: Record<string, string> = {
        '前端开发': 'primary',
        'TypeScript': 'success',
        '性能优化': 'warning',
        '状态管理': 'info',
        '设计': 'danger'
    }
    return typeMap[category] || 'default'
}

// 去写文章
function goToWriteArticle() {
    router.push('/write')
}

// 查看文章
function viewArticle(id: number) {
    router.push(`/article/${id}`)
}

// 编辑文章
function editArticle(id: number) {
    router.push(`/article/${id}/edit`)
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

/* 文章阅读趋势图表模拟 */
.read-trend-placeholder {
    position: relative;
    width: 100%;
    height: 100%;
}

.trend-line-container {
    position: absolute;
    bottom: 0;
    left: 0;
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

/* 文章类型分布图表模拟 */
.article-type-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.type-pie-chart {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: conic-gradient(#FF7F50 0% 35%,
            #FFD700 35% 60%,
            #98FB98 60% 75%,
            #87CEEB 75% 85%,
            #FF6347 85% 100%);
    position: relative;
    box-shadow: 0 4px 15px rgba(255, 127, 80, 0.2);
}

.type-pie-chart::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 120px;
    height: 120px;
    background: white;
    border-radius: 50%;
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