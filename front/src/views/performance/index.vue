<template>
    <div class="performance-container">
        <!-- 顶部标题区域 -->
        <div class="performance-header">
            <div class="header-content">
                <h1 class="page-title">
                    <span class="title-icon">⚡</span>
                    性能优化实验室
                </h1>
                <p class="page-subtitle">探索交互式性能优化示例和最佳实践</p>
                <div class="performance-stats">
                    <div class="stat-item">
                        <div class="stat-number">{{ filteredRoutes.length }}</div>
                        <div class="stat-label">优化示例</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">3</div>
                        <div class="stat-label">核心技术</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">100%</div>
                        <div class="stat-label">可交互</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 搜索区域 -->
        <div class="search-section">
            <div class="search-wrapper">
                <span class="search-icon">🔍</span>
                <input v-model="search" class="search-input" placeholder="搜索性能优化示例..." />
            </div>
        </div>

        <!-- 优化示例网格 -->
        <div class="performance-grid">
            <div class="performance-card" v-for="(route, index) in filteredRoutes" :key="route.path"
                :style="{ animationDelay: `${index * 0.1}s` }">
                <router-link :to="getRoutePath(route.path)" class="card-link">
                    <div class="card-icon">
                        <svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="60" height="60" rx="12" fill="rgba(255, 127, 80, 0.1)" />
                            <path d="M20 30 L30 20 L40 30 L30 40 Z" fill="#FF7F50" />
                            <path d="M25 30 L30 25 L35 30" stroke="#FF7F50" stroke-width="3" stroke-linecap="round" />
                            <path d="M30 35 L35 30" stroke="#FF7F50" stroke-width="3" stroke-linecap="round" />
                        </svg>
                    </div>
                    <div class="card-content">
                        <h3 class="card-title">{{ route.meta!.title }}</h3>
                        <div class="card-description">{{ route.meta!.description || '性能优化示例演示' }}</div>
                        <div class="card-tags">
                            <span class="card-tag" v-for="tag in route.meta!.tags || []" :key="tag">{{ tag }}</span>
                        </div>
                    </div>
                    <div class="card-action">
                        <span class="action-text">查看演示</span>
                        <span class="action-icon">→</span>
                    </div>
                </router-link>
            </div>

            <!-- 无搜索结果 -->
            <div class="no-results" v-if="filteredRoutes.length === 0">
                <div class="no-results-icon">🔍</div>
                <h3>未找到相关示例</h3>
                <p>尝试使用其他关键词搜索</p>
            </div>
        </div>

        <!-- 案例预览区域 -->
        <div class="case-preview-section" v-if="filteredRoutes.length > 0">
            <h2 class="section-title">
                <span class="title-icon">📊</span>
                性能优化效果预览
            </h2>
            <div class="case-preview-grid">
                <div class="case-preview-card">
                    <div class="preview-icon">📈</div>
                    <h3>加载速度提升</h3>
                    <p>通过虚拟列表技术，长列表渲染速度提升 80%</p>
                </div>
                <div class="case-preview-card">
                    <div class="preview-icon">💾</div>
                    <h3>内存占用优化</h3>
                    <p>图片压缩技术减少 70% 的内存使用</p>
                </div>
                <div class="case-preview-card">
                    <div class="preview-icon">🔄</div>
                    <h3>组件复用</h3>
                    <p>KeepAlive 组件缓存提升页面切换性能 60%</p>
                </div>
            </div>
        </div>

        <!-- 详情视图区域 -->
        <div class="detail-view-container">
            <section class="detail-view">
                <router-view />
            </section>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const router = useRouter()
// 获取性能优化相关的子路由
const routes = (router.getRoutes().find(r => r.path === '/performance')?.children || []) as RouteRecordRaw[]

// 搜索功能
const search = ref('')
const filteredRoutes = computed(() => {
    const searchTerm = search.value.toLowerCase()
    return routes.filter((route: any) => {
        const title = route.meta?.title?.toLowerCase() || ''
        const tags = (route.meta?.tags || []).join(' ').toLowerCase()
        return title.includes(searchTerm) || tags.includes(searchTerm)
    })
})

// 获取路由路径
function getRoutePath(sub: string) {
    return `/performance/${sub}`
}
</script>

<style scoped>
.performance-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #fff 0%, #fff8f5 100%);
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    padding: 0;
}

/* 顶部标题区域 */
.performance-header {
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    padding: 60px 0 40px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.3);
}

.performance-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url('data:image/svg+xml,<svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.15)"/><circle cx="60" cy="60" r="2" fill="rgba(255,255,255,0.15)"/><circle cx="20" cy="60" r="2" fill="rgba(255,255,255,0.15)"/><circle cx="60" cy="20" r="2" fill="rgba(255,255,255,0.15)"/></svg>');
    animation: float 15s linear infinite;
}

@keyframes float {
    from {
        transform: translateY(0) rotate(0deg);
    }

    to {
        transform: translateY(-80px) rotate(360deg);
    }
}

.header-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    position: relative;
    z-index: 1;
    text-align: center;
    animation: slideUp 0.8s ease-out;
}

.page-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: white;
    margin: 0 0 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.title-icon {
    font-size: 2rem;
}

.page-subtitle {
    font-size: 1.25rem;
    color: rgba(255, 255, 255, 0.9);
    margin: 0 0 2rem;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

.performance-stats {
    display: flex;
    justify-content: center;
    gap: 3rem;
    flex-wrap: wrap;
}

.stat-item {
    text-align: center;
    background: rgba(255, 255, 255, 0.15);
    padding: 1rem 2rem;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.25rem;
}

.stat-label {
    font-size: 0.95rem;
    color: rgba(255, 255, 255, 0.85);
}

/* 搜索区域 */
.search-section {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 20px;
    animation: slideUp 0.8s ease-out 0.2s both;
}

.search-wrapper {
    position: relative;
    max-width: 600px;
    margin: 0 auto;
}

.search-icon {
    position: absolute;
    left: 1.25rem;
    top: 50%;
    transform: translateY(-50%);
    color: #999;
    font-size: 1.2rem;
    z-index: 1;
}

.search-input {
    width: 100%;
    padding: 1rem 1.25rem 1rem 3.5rem;
    border: 2px solid rgba(255, 127, 80, 0.2);
    border-radius: 20px;
    font-size: 1.1rem;
    color: #333;
    background: white;
    outline: none;
    transition: all 0.3s ease;
    box-shadow: 0 2px 12px rgba(255, 127, 80, 0.1);

    &::placeholder {
        color: #999;
    }

    &:focus {
        border-color: #FF7F50;
        box-shadow: 0 0 0 3px rgba(255, 127, 80, 0.15), 0 4px 15px rgba(255, 127, 80, 0.2);
        transform: translateY(-2px);
    }
}

/* 性能优化示例网格 */
.performance-grid {
    max-width: 100%;
    margin: 0 auto;
    padding: 0 15px 2rem;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    box-sizing: border-box;
    overflow-x: hidden;
}

.performance-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    animation: cardSlideUp 0.6s ease-out both;

    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #FF7F50 0%, #FF6347 100%);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }

    &:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 30px rgba(255, 127, 80, 0.15);

        &::before {
            transform: scaleX(1);
        }
    }
}

.card-link {
    text-decoration: none;
    color: inherit;
    display: flex;
    flex-direction: column;
    height: 100%;
}

.card-icon {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.5rem;
}

.card-content {
    flex: 1;
    margin-bottom: 1.5rem;
}

.card-title {
    font-size: 1.35rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 0.75rem;
    line-height: 1.4;
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.card-description {
    font-size: 0.95rem;
    color: #666;
    margin: 0 0 1rem;
    line-height: 1.6;
}

.card-tags {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.card-tag {
    background: rgba(255, 127, 80, 0.1);
    color: #FF7F50;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 500;
}

.card-action {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.5rem;
    color: #FF7F50;
    font-weight: 500;
    transition: all 0.3s ease;

    .performance-card:hover & {
        gap: 0.75rem;
    }
}

.action-icon {
    font-size: 1.1rem;
    transition: transform 0.3s ease;

    .performance-card:hover & {
        transform: translateX(3px);
    }
}

/* 无搜索结果 */
.no-results {
    grid-column: 1 / -1;
    text-align: center;
    padding: 4rem 2rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
}

.no-results-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    color: #FF7F50;
}

.no-results h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 0.5rem;
}

.no-results p {
    font-size: 1rem;
    color: #666;
    margin: 0;
}

/* 案例预览区域 */
.case-preview-section {
    max-width: 1200px;
    margin: 0 auto;
    padding: 3rem 20px;
    animation: slideUp 0.8s ease-out 0.4s both;
}

.section-title {
    font-size: 1.75rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 2rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-align: center;
    justify-content: center;
}

.case-preview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.case-preview-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
    text-align: center;
    transition: all 0.3s ease;

    &:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(255, 127, 80, 0.15);
    }
}

.preview-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.case-preview-card h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 0.75rem;
}

.case-preview-card p {
    font-size: 0.95rem;
    color: #666;
    margin: 0;
    line-height: 1.6;
}

/* 详情视图区域 */
.detail-view-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px 4rem;
}

.detail-view {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
    animation: fadeIn 0.8s ease-out 0.6s both;
}

/* 动画效果 */
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

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .performance-header {
        padding: 40px 0 30px;
    }

    .page-title {
        font-size: 2rem;
        gap: 0.75rem;
    }

    .title-icon {
        font-size: 1.75rem;
    }

    .page-subtitle {
        font-size: 1.1rem;
    }

    .performance-stats {
        gap: 1.5rem;
    }

    .stat-item {
        padding: 0.75rem 1.5rem;
    }

    .performance-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
        padding: 0 15px 1.5rem;
    }

    .performance-card {
        padding: 1.25rem;
    }

    .card-title {
        font-size: 1.25rem;
    }

    .case-preview-grid {
        grid-template-columns: 1fr;
    }

    .detail-view-container {
        padding: 0 15px 2rem;
    }

    .detail-view {
        padding: 1.5rem;
    }
}

@media (max-width: 480px) {
    .page-title {
        flex-direction: column;
        gap: 0.5rem;
    }

    .search-input {
        padding: 0.875rem 1rem 0.875rem 3rem;
        font-size: 1rem;
    }

    .search-icon {
        left: 1rem;
        font-size: 1.1rem;
    }
}
</style>
