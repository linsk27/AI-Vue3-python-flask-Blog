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
                    <div class="profile-bio">专注于Web性能优化、Vue.js技术栈和用户体验设计</div>
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
                            <span class="info-value">{{ userInfo?.created_at || '2025-08-01' }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">所在地</span>
                            <span class="info-value">中国 · 杭州</span>
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
                            <div class="stat-value">24</div>
                            <div class="stat-label">发布文章</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">1.2k</div>
                            <div class="stat-label">文章阅读</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">89</div>
                            <div class="stat-label">收到点赞</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">15</div>
                            <div class="stat-label">技术分享</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="content-wrapper">
                <!-- 左侧：技能标签卡片 -->
                <div class="profile-card skills-card">
                    <h2 class="card-title">
                        <span class="title-icon">🛠️</span>
                        技术技能
                    </h2>
                    <div class="skills-grid">
                        <div class="skill-tag" v-for="skill in skills" :key="skill">
                            {{ skill }}
                        </div>
                    </div>
                </div>

                <!-- 右侧：最近活动卡片 -->
                <div class="profile-card activity-card">
                    <h2 class="card-title">
                        <span class="title-icon">📝</span>
                        最近活动
                    </h2>
                    <div class="activity-list">
                        <div class="activity-item" v-for="(activity, index) in recentActivities" :key="index">
                            <div class="activity-icon">{{ activity.icon }}</div>
                            <div class="activity-content">
                                <div class="activity-text">{{ activity.text }}</div>
                                <div class="activity-time">{{ activity.time }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 底部：贡献展示卡片 -->
            <div class="profile-card contributions-card">
                <h2 class="card-title">
                    <span class="title-icon">🌟</span>
                    平台贡献
                </h2>
                <div class="contributions-grid">
                    <div class="contribution-item">
                        <div class="contribution-icon">📚</div>
                        <div class="contribution-content">
                            <h3>知识库文章</h3>
                            <p>撰写技术文章，分享前端开发经验和性能优化技巧</p>
                        </div>
                    </div>
                    <div class="contribution-item">
                        <div class="contribution-icon">⚡</div>
                        <div class="contribution-content">
                            <h3>性能优化示例</h3>
                            <p>创建交互式性能优化演示，帮助开发者理解优化原理</p>
                        </div>
                    </div>
                    <div class="contribution-item">
                        <div class="contribution-icon">💡</div>
                        <div class="contribution-content">
                            <h3>技术讨论</h3>
                            <p>参与技术讨论，解答社区问题，分享最佳实践</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// 引入 IconPark 图标
import { ref, onMounted } from 'vue'
import { User as IconUser } from '@icon-park/vue-next'
import { useGlobalStore } from '@/store'
import authApi from '@/api/modules/auth'

const globalStore = useGlobalStore()
const userInfo = ref(globalStore.userInfo)

onMounted(async () => {
    try {
        const res = await authApi.getUserInfo()
        if (res) {
            userInfo.value = res
            // Update store
            globalStore.setLoginInfo(globalStore.token, res)
        }
    } catch (e) {
        console.error(e)
    }
})

// 技能列表
const skills = ref([
    'HTML5', 'CSS3', 'JavaScript', 'TypeScript',
    'Vue.js', 'React', 'Node.js', 'Webpack',
    'Vite', 'Tailwind CSS', '性能优化', '响应式设计',
    'Git', 'UI/UX设计', '单元测试', 'CI/CD'
])

// 最近活动
const recentActivities = ref([
    { icon: '✍️', text: '发布了新文章：《Vue3 性能优化实战》', time: '2天前' },
    { icon: '⚡', text: '更新了性能优化示例：虚拟列表实现', time: '5天前' },
    { icon: '💬', text: '回复了讨论：《CSS 动画性能优化》', time: '1周前' },
    { icon: '📊', text: '分享了性能测试报告：大型列表渲染对比', time: '2周前' },
    { icon: '🌟', text: '获得了 "最佳贡献者" 称号', time: '3周前' }
])
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

/* 技能卡片 */
.skills-card {
    flex: 1;
}

.skills-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.skill-tag {
    padding: 0.6rem 1.2rem;
    background: rgba(255, 127, 80, 0.1);
    color: #FF7F50;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
    border: 2px solid transparent;

    &:hover {
        background: #FF7F50;
        color: white;
        transform: translateY(-2px);
        border-color: #FF7F50;
    }
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

/* 贡献卡片 */
.contributions-card {
    margin-bottom: 2rem;
}

.contributions-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}

.contribution-item {
    display: flex;
    gap: 1rem;
    padding: 1.5rem;
    background: rgba(255, 127, 80, 0.05);
    border-radius: 12px;
    transition: all 0.3s ease;
    border: 2px solid transparent;

    &:hover {
        background: rgba(255, 127, 80, 0.1);
        transform: translateY(-3px);
        border-color: rgba(255, 127, 80, 0.3);
    }
}

.contribution-icon {
    font-size: 2rem;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 127, 80, 0.15);
    border-radius: 10px;
}

.contribution-content h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 0.5rem;
}

.contribution-content p {
    font-size: 0.9rem;
    color: #666;
    margin: 0;
    line-height: 1.5;
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

    .contributions-grid {
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

    .contribution-item {
        flex-direction: column;
        text-align: center;
    }
}
</style>
