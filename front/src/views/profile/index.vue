<template>
    <div class="profile-container">
        <!-- 顶部封面区域 -->
        <div class="profile-cover">
            <div class="cover-overlay"></div>
            <div class="profile-header">
                <div class="profile-avatar">
                    <img v-if="userInfo?.avatar" :src="userInfo.avatar" alt="Avatar"
                        style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover; border: 4px solid white;" />
                    <svg v-else width="120" height="120" viewBox="0 0 120 120" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <circle cx="60" cy="60" r="58" fill="#FF7F50" stroke="white" stroke-width="4" />
                        <path d="M40 70 C40 55 55 45 60 45 C65 45 80 55 80 70 C80 85 65 95 60 95 C55 95 40 85 40 70 Z"
                            fill="white" />
                        <path d="M45 60 C45 65 55 65 55 60 C55 55 45 55 45 60 Z" fill="#FF7F50" />
                        <path d="M65 60 C65 65 75 65 75 60 C75 55 65 55 65 60 Z" fill="#FF7F50" />
                        <path d="M45 80 L75 80" stroke="#FF7F50" stroke-width="3" stroke-linecap="round" />
                    </svg>
                </div>
                <div class="profile-info">
                    <h1 class="profile-name">{{ userInfo?.username || '用户' }}</h1>
                    <p class="profile-title">{{ userInfo?.role === 'admin' ? '管理员' : '普通用户' }}</p>
                    <div v-if="userInfo?.permissions && userInfo.permissions.length > 0" class="profile-bio">
                        权限: {{ userInfo.permissions.join(', ') }}
                    </div>
                </div>
            </div>
        </div>

        <!-- 主体内容区域 -->
        <div class="profile-content">
            <div class="content-wrapper">
                <!-- 左侧：个人信息卡片 -->
                <div class="profile-card info-card">
                    <h2 class="card-title">
                        <span class="title-icon">📋</span>
                        个人信息
                    </h2>
                    <div class="info-list">
                        <div class="info-item">
                            <span class="info-label">用户名</span>
                            <span class="info-value">{{ userInfo?.username }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">邮箱</span>
                            <span class="info-value">{{ userInfo?.email || '未设置' }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">注册时间</span>
                            <span class="info-value">{{ userInfo?.created_at || '未设置' }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">角色</span>
                            <span class="info-value">{{ userInfo?.role || '未设置' }}</span>
                        </div>
                    </div>
                </div>

                <!-- 右侧：统计数据卡片 -->
                <div class="profile-card stats-card">
                    <h2 class="card-title">
                        <span class="title-icon">📊</span>
                        统计数据
                    </h2>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">{{ userStats.articles || 0 }}</div>
                            <div class="stat-label">发布文章</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ userStats.views || 0 }}</div>
                            <div class="stat-label">文章阅读</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ userStats.likes || 0 }}</div>
                            <div class="stat-label">收到点赞</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ userStats.comments || 0 }}</div>
                            <div class="stat-label">发表评论</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI热点分析卡片 -->
            <div class="profile-card ai-analysis-card">
                <h2 class="card-title">
                    <span class="title-icon">🤖</span>
                    AI热点分析
                </h2>
                <div v-if="isLoading" class="loading-container">
                    <div class="loading-spinner"></div>
                    <p>AI正在分析热点数据...</p>
                </div>
                <div v-else-if="aiAnalysis" class="ai-analysis-content">
                    <div class="analysis-item">
                        <h3>🔥 最热门文章</h3>
                        <p>{{ aiAnalysis.topArticle || '暂无数据' }}</p>
                    </div>
                    <div class="analysis-item">
                        <h3>� 过去人们更关注</h3>
                        <p>{{ aiAnalysis.pastFocus || '暂无数据' }}</p>
                    </div>
                    <div class="analysis-item">
                        <h3>🏷️ 文章热门标签</h3>
                        <p>{{ aiAnalysis.hotTags || '暂无数据' }}</p>
                    </div>
                    <div class="analysis-item">
                        <h3>🔮 未来热点</h3>
                        <p>{{ aiAnalysis.futureTrends || '暂无数据' }}</p>
                    </div>
                </div>
                <div v-else class="error-message">
                    <p>AI分析失败，请稍后重试</p>
                </div>
            </div>

            <div class="content-wrapper">
                <!-- 左侧：用户文章列表 -->
                <div class="profile-card articles-card">
                    <h2 class="card-title">
                        <span class="title-icon">📝</span>
                        我的文章
                    </h2>
                    <div v-if="userArticles.length > 0" class="articles-list">
                        <div class="article-item" v-for="article in userArticles" :key="article.id">
                            <h3 class="article-title">{{ article.title }}</h3>
                            <div class="article-meta">
                                <span class="article-date">{{ formatDate(article.created_at) }}</span>
                                <span class="article-likes">👍 {{ article.likes || 0 }}</span>
                                <span class="article-views">👁️ {{ article.views || 0 }}</span>
                            </div>
                        </div>
                    </div>
                    <div v-else class="empty-message">
                        <p>暂无文章</p>
                    </div>
                </div>

                <!-- 右侧：最近活动卡片 -->
                <div class="profile-card activity-card">
                    <h2 class="card-title">
                        <span class="title-icon">📅</span>
                        最近活动
                    </h2>
                    <div v-if="recentActivities.length > 0" class="activity-list">
                        <div class="activity-item" v-for="(activity, index) in recentActivities" :key="index">
                            <div class="activity-icon">{{ activity.icon }}</div>
                            <div class="activity-content">
                                <div class="activity-text">{{ activity.text }}</div>
                                <div class="activity-time">{{ activity.time }}</div>
                            </div>
                        </div>
                    </div>
                    <div v-else class="empty-message">
                        <p>暂无活动记录</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useGlobalStore } from '@/store'
import { useCacheStore } from '@/store/cache'
import authApi from '@/api/modules/auth'
import articleApi from '@/api/modules/article'
import { aiChatService } from '@/api/modules/ai'

const globalStore = useGlobalStore()
const cacheStore = useCacheStore()
const userInfo = ref(globalStore.userInfo)
const userStats = ref({
    articles: 0,
    views: 0,
    likes: 0,
    comments: 0
})
const userArticles = ref<any[]>([])
const recentActivities = ref<any[]>([])
const aiAnalysis = ref<any>(null)
const isLoading = ref(false)

const formatDate = (dateString: string) => {
    if (!dateString) return '未知'
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN')
}

const getUserStats = async (forceRefresh = false) => {
    try {
        if (!forceRefresh) {
            const cachedArticles = cacheStore.getCache<any[]>('userArticles')
            const cachedStats = cacheStore.getCache<{
                articles: number
                views: number
                likes: number
                comments: number
            }>('userStats')

            if (cachedArticles && cachedStats) {
                userArticles.value = cachedArticles.slice(0, 5)
                userStats.value = cachedStats
                return
            }
        }

        const articles = await articleApi.getList({ author_id: userInfo.value.id })
        if (articles && Array.isArray(articles)) {
            userArticles.value = articles.slice(0, 5)

            let totalViews = 0
            let totalLikes = 0

            articles.forEach((article: any) => {
                totalViews += article.views || 0
                totalLikes += article.likes || 0
            })

            userStats.value = {
                articles: articles.length,
                views: totalViews,
                likes: totalLikes,
                comments: 0
            }

            cacheStore.setCache('userArticles', articles)
            cacheStore.setCache('userStats', userStats.value)
        }
    } catch (e) {
        console.error('获取用户统计数据失败:', e)
    }
}

const getRecentActivities = async () => {
    recentActivities.value = [
        { icon: '✍️', text: '发布了新文章', time: '2天前' },
        { icon: '❤️', text: '收到了新点赞', time: '3天前' },
        { icon: '💬', text: '发表了评论', time: '1周前' },
        { icon: '📖', text: '阅读了文章', time: '2周前' }
    ]
}

const analyzeHotTopics = async (forceRefresh = false) => {
    if (!forceRefresh) {
        const cachedAnalysis = cacheStore.getCache<{
            topArticle: string
            pastFocus: string
            hotTags: string
            futureTrends: string
        }>('aiAnalysis')

        if (cachedAnalysis) {
            aiAnalysis.value = cachedAnalysis
            return
        }
    }

    isLoading.value = true
    try {
        let articles = cacheStore.getCache<any[]>('articles')

        if (!articles) {
            const articlesRes = await articleApi.getList()
            if (articlesRes && Array.isArray(articlesRes)) {
                articles = articlesRes
                cacheStore.setCache('articles', articles)
            }
        }

        if (articles && Array.isArray(articles)) {
            const topArticles = articles
                .sort((a: any, b: any) => (b.likes || 0) - (a.likes || 0))
                .slice(0, 5)

            const articleTitles = topArticles.map((article: any) => article.title).join('\n')

            const aiPrompt = `请对以下热门文章标题进行简单分析，输出四个方面：
1. 最热门文章（直接输出标题）
2. 过去人们更关注的主题
3. 文章热门标签
4. 未来可能的热点趋势

文章标题：
${articleTitles}

请简洁回答，每个方面不超过一句话。`

            const aiResponse = await aiChatService.sendMessage({
                message: aiPrompt,
                max_tokens: 300,
                temperature: 0.3,
                user_id: String(userInfo.value.id),
                reset_context: true
            })

            if (aiResponse && aiResponse.reply) {
                const reply = aiResponse.reply
                const lines = reply.split('\n').filter((line: string) => line.trim())

                aiAnalysis.value = {
                    topArticle: lines[0]?.replace(/^1\.\s*/, '') || '暂无数据',
                    pastFocus: lines[1]?.replace(/^2\.\s*/, '') || '暂无数据',
                    hotTags: lines[2]?.replace(/^3\.\s*/, '') || '暂无数据',
                    futureTrends: lines[3]?.replace(/^4\.\s*/, '') || '暂无数据'
                }

                cacheStore.setCache('aiAnalysis', aiAnalysis.value, 10 * 60 * 1000)
            }
        }
    } catch (e) {
        console.error('AI分析失败:', e)
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

            await getUserStats()
            await getRecentActivities()
            await analyzeHotTopics()
        }
    } catch (e) {
        console.error(e)
    }
})
</script>

<style scoped>
.profile-container {
    min-height: 100vh;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(255, 248, 245, 0.85) 100%);
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 封面区域 */
.profile-cover {
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    padding: 60px 0 30px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.3);
}

.cover-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url('data:image/svg+xml,<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="25" cy="25" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="25" cy="75" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="25" r="2" fill="rgba(255,255,255,0.1)"/></svg>');
    animation: float 20s linear infinite;
}

@keyframes float {
    from {
        transform: translateY(0) rotate(0deg);
    }

    to {
        transform: translateY(-100px) rotate(360deg);
    }
}

.profile-header {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    display: flex;
    align-items: center;
    gap: 2rem;
    position: relative;
    z-index: 1;
}

.profile-avatar {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    overflow: hidden;
    border: 5px solid white;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    animation: slideUp 0.8s ease-out;
}

.profile-info {
    flex: 1;
    animation: slideUp 0.8s ease-out 0.2s both;
}

.profile-name {
    font-size: 2.5rem;
    font-weight: 700;
    color: white;
    margin: 0 0 0.5rem;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.profile-title {
    font-size: 1.25rem;
    color: rgba(255, 255, 255, 0.9);
    margin: 0 0 1rem;
}

.profile-bio {
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.85);
    max-width: 700px;
    line-height: 1.6;
}

/* 主体内容 */
.profile-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 30px 20px;
}

.content-wrapper {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
}

/* 卡片样式 */
.profile-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
    transition: all 0.3s ease;
    animation: cardSlideUp 0.8s ease-out both;

    &:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(255, 127, 80, 0.15);
    }
}

.card-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.25rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 1.5rem;
}

.title-icon {
    font-size: 1.5rem;
}

/* 信息卡片 */
.info-card {
    flex: 1;
}

.info-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: rgba(255, 127, 80, 0.05);
    border-radius: 10px;
    transition: all 0.3s ease;

    &:hover {
        background: rgba(255, 127, 80, 0.1);
    }
}

.info-label {
    font-weight: 500;
    color: #666;
    font-size: 0.95rem;
}

.info-value {
    font-weight: 600;
    color: #333;
    font-size: 0.95rem;
}

/* 统计卡片 */
.stats-card {
    flex: 1;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}

.stat-item {
    text-align: center;
    padding: 1rem;
    background: rgba(255, 127, 80, 0.05);
    border-radius: 12px;
    transition: all 0.3s ease;

    &:hover {
        background: rgba(255, 127, 80, 0.1);
        transform: translateY(-3px);
    }
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: #FF7F50;
    margin-bottom: 0.25rem;
}

.stat-label {
    font-size: 0.9rem;
    color: #666;
}

/* AI分析卡片 */
.ai-analysis-card {
    margin-bottom: 2rem;
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
}

.loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid rgba(255, 127, 80, 0.1);
    border-left-color: #FF7F50;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.ai-analysis-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.analysis-item {
    padding: 1rem;
    background: rgba(255, 127, 80, 0.05);
    border-radius: 12px;
    transition: all 0.3s ease;

    &:hover {
        background: rgba(255, 127, 80, 0.1);
    }
}

.analysis-item h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 0.5rem;
}

.analysis-item p {
    font-size: 0.9rem;
    color: #666;
    margin: 0;
    line-height: 1.5;
}

.error-message {
    text-align: center;
    padding: 2rem;
    color: #ff4757;
}

/* 文章卡片 */
.articles-card {
    flex: 1;
}

.articles-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.article-item {
    padding: 1rem;
    background: rgba(255, 127, 80, 0.05);
    border-radius: 12px;
    transition: all 0.3s ease;

    &:hover {
        background: rgba(255, 127, 80, 0.1);
    }
}

.article-title {
    font-size: 1rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 0.5rem;
}

.article-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.85rem;
    color: #999;
}

/* 活动卡片 */
.activity-card {
    flex: 1;
}

.activity-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.activity-item {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: rgba(255, 127, 80, 0.05);
    border-radius: 12px;
    transition: all 0.3s ease;

    &:hover {
        background: rgba(255, 127, 80, 0.1);
    }
}

.activity-icon {
    font-size: 1.5rem;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 127, 80, 0.15);
    border-radius: 8px;
}

.activity-content {
    flex: 1;
}

.activity-text {
    font-weight: 500;
    color: #333;
    margin-bottom: 0.25rem;
    line-height: 1.4;
}

.activity-time {
    font-size: 0.85rem;
    color: #999;
}

/* 空状态 */
.empty-message {
    text-align: center;
    padding: 2rem;
    color: #999;
}

/* 动画 */
@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes cardSlideUp {
    from {
        opacity: 0;
        transform: translateY(40px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 响应式设计 */
@media (max-width: 992px) {
    .content-wrapper {
        flex-direction: column;
    }

    .ai-analysis-content {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .profile-header {
        flex-direction: column;
        text-align: center;
        gap: 1.5rem;
    }

    .profile-name {
        font-size: 2rem;
    }

    .profile-title {
        font-size: 1.1rem;
    }

    .profile-bio {
        margin: 0 auto;
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }

    .profile-content {
        padding: 20px 15px;
    }

    .profile-card {
        padding: 1.25rem;
    }
}

@media (max-width: 480px) {
    .profile-avatar {
        width: 120px;
        height: 120px;
    }

    .profile-name {
        font-size: 1.75rem;
    }

    .card-title {
        font-size: 1.1rem;
    }

    .activity-item {
        flex-direction: column;
        text-align: center;
    }
}
</style>
