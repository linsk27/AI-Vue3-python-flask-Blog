<template>
    <div class="home-container">
        <!-- 英雄区域 -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">
                    <span class="title-accent">智汇博客</span>
                </h1>
                <p class="hero-subtitle">智慧汇聚，洞见未来 —— 与全球开发者一起成长</p>
                <div class="hero-actions">
                    <router-link to="/essays" class="primary-btn">
                        浏览文章
                        <span class="btn-icon">→</span>
                    </router-link>
                </div>
            </div>
            <div class="hero-visual">
                <svg width="400" height="400" viewBox="0 0 400 400" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="200" cy="200" r="180" fill="rgba(255, 127, 80, 0.1)" />
                    <path d="M100 200 L200 100 L300 200 L200 300 Z" fill="#FF7F50" opacity="0.8" />
                    <path d="M150 150 L250 150 L250 250 L150 250 Z" fill="white" opacity="0.7" />
                    <circle cx="200" cy="180" r="15" fill="#FF7F50" />
                    <path d="M185 210 L215 210" stroke="#FF7F50" stroke-width="5" stroke-linecap="round" />
                </svg>
            </div>
        </section>

        <!-- 平台特色 -->
        <section class="features-section">
            <h2 class="section-title">
                <span class="title-icon">✨</span>
                平台特色
            </h2>
            <div class="features-grid">
                <div class="feature-card" data-aos="fade-up">
                    <div class="feature-icon">📚</div>
                    <h3 class="feature-title">丰富的知识内容</h3>
                    <p class="feature-description">涵盖前端开发、性能优化、UI/UX设计等多个领域的优质文章</p>
                </div>
                <div class="feature-card" data-aos="fade-up" data-aos-delay="200">
                    <div class="feature-icon">🤝</div>
                    <h3 class="feature-title">活跃的社区</h3>
                    <p class="feature-description">与全球开发者交流经验，共同成长</p>
                </div>
                <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
                    <div class="feature-icon">🎨</div>
                    <h3 class="feature-title">创意展示平台</h3>
                    <p class="feature-description">展示你的作品和创意，获得反馈和认可</p>
                </div>
            </div>
        </section>

        <!-- 案例预览 -->
        <section class="cases-section">
            <div class="section-header">
                <h2 class="section-title">
                    <span class="title-icon">📊</span>
                    精选案例
                </h2>
                <router-link to="/essays" class="view-all-link">
                    查看全部
                    <span class="link-icon">→</span>
                </router-link>
            </div>
            <div class="cases-grid">
                <div class="case-card" v-for="(caseItem, index) in featuredCases" :key="index" data-aos="fade-up">
                    <div class="case-header">
                        <div class="case-category">{{ caseItem.category }}</div>
                    </div>
                    <h3 class="case-title">{{ caseItem.title }}</h3>
                    <p class="case-description">{{ caseItem.description }}</p>
                    <div class="case-tags">
                        <span class="case-tag" v-for="tag in caseItem.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <router-link :to="caseItem.link" class="case-link">
                        阅读更多
                        <span class="link-icon">→</span>
                    </router-link>
                </div>
            </div>
        </section>

        <!-- 贡献者展示 -->
        <section class="contributors-section">
            <h2 class="section-title">
                <span class="title-icon">👥</span>
                社区贡献者
            </h2>
            <div class="contributors-grid">
                <div class="contributor-card" v-for="(contributor, index) in contributors" :key="index"
                    data-aos="fade-up">
                    <div class="contributor-avatar">
                        <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="40" cy="40" r="38" fill="#FF7F50" stroke="white" stroke-width="3" />
                            <path
                                d="M25 50 C25 40 35 35 40 35 C45 35 55 40 55 50 C55 60 45 65 40 65 C35 65 25 60 25 50 Z"
                                fill="white" />
                            <path d="M32 45 C32 48 38 48 38 45 C38 42 32 42 32 45 Z" fill="#FF7F50" />
                            <path d="M42 45 C42 48 48 48 48 45 C48 42 42 42 42 45 Z" fill="#FF7F50" />
                            <path d="M32 58 L48 58" stroke="#FF7F50" stroke-width="3" stroke-linecap="round" />
                        </svg>
                    </div>
                    <h3 class="contributor-name">{{ contributor.name }}</h3>
                    <p class="contributor-role">{{ contributor.role }}</p>
                    <div class="contributor-stats">
                        <span class="stat-item">{{ contributor.articles }}篇文章</span>
                        <span class="stat-item">{{ contributor.contributions }}次贡献</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- 行动召唤 -->
        <section class="cta-section">
            <div class="cta-content">
                <h2 class="cta-title">准备好加入我们了吗？</h2>
                <p class="cta-description">成为知识创作平台的一员，分享你的知识和经验</p>
                <div class="cta-actions">
                    <router-link to="/login" class="primary-btn">
                        注册账号
                        <span class="btn-icon">→</span>
                    </router-link>
                    <router-link to="/profile" class="secondary-btn">
                        了解更多
                        <span class="btn-icon">ℹ️</span>
                    </router-link>
                </div>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
// 示例数据
const featuredCases = [
    {
        title: "Vue3 性能优化实战",
        category: "前端开发",
        description: "深入探讨Vue3中的性能优化技术，包括虚拟列表、按需加载等",
        tags: ["Vue3", "性能优化", "实战"],
        link: "/essays/vue3-performance"
    },
    {
        title: "CSS 动画性能优化指南",
        category: "UI/UX",
        description: "学习如何创建高性能的CSS动画，提升用户体验",
        tags: ["CSS", "动画", "性能"],
        link: "/essays/css-animation-optimization"
    },
    {
        title: "虚拟列表实现原理",
        category: "性能优化",
        description: "详细解析虚拟列表的实现原理和优化策略",
        tags: ["虚拟列表", "性能", "实现原理"],
        link: "/essays/virtual-list-implementation"
    }
];

const contributors = [
    {
        name: "Lin",
        role: "前端开发工程师",
        articles: 24,
        contributions: 150
    },
    {
        name: "Zhang",
        role: "UI/UX设计师",
        articles: 18,
        contributions: 120
    },
    {
        name: "Wang",
        role: "全栈开发者",
        articles: 32,
        contributions: 200
    },
    {
        name: "Li",
        role: "性能优化专家",
        articles: 28,
        contributions: 180
    }
];
</script>

<style scoped>
.home-container {
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: linear-gradient(135deg, #fff 0%, #fff8f5 100%);
}

/* 英雄区域 */
.hero-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4rem 1rem;
    max-width: 100%;
    margin: 0 auto;
    gap: 2rem;
    min-height: 85vh;
    position: relative;
    overflow: hidden;
    width: 100%;
    box-sizing: border-box;
}

.hero-visual svg {
    max-width: 100%;
    height: auto;
    box-sizing: border-box;
}

/* 添加背景装饰 */
.hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 50%;
    height: 100%;
    background: radial-gradient(circle at 100% 50%, rgba(255, 127, 80, 0.1) 0%, transparent 70%);
    z-index: -1;
    animation: pulse 4s ease-in-out infinite;
}

.hero-section::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 30%;
    height: 60%;
    background: radial-gradient(circle at 0% 100%, rgba(255, 127, 80, 0.05) 0%, transparent 60%);
    z-index: -1;
    animation: pulse 3s ease-in-out infinite reverse;
}

@keyframes pulse {

    0%,
    100% {
        opacity: 0.6;
        transform: scale(1);
    }

    50% {
        opacity: 1;
        transform: scale(1.1);
    }
}

.hero-content {
    flex: 1;
    animation: slideLeft 0.8s ease-out;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 1;
}

.hero-title {
    font-size: 4rem;
    font-weight: 700;
    color: #333;
    margin: 0 0 1.5rem;
    line-height: 1.1;
    background: linear-gradient(135deg, #333 0%, #FF7F50 50%, #333 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    background-size: 200% 100%;
    animation: gradientShift 3s ease-in-out infinite;
}

@keyframes gradientShift {

    0%,
    100% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }
}

.title-accent {
    color: #FF7F50;
    -webkit-text-fill-color: #FF7F50;
    display: inline-block;
    animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-10px);
    }
}

.hero-subtitle {
    font-size: 1.5rem;
    color: #666;
    margin: 0 0 2.5rem;
    font-weight: 400;
    animation: fadeInUp 0.8s ease-out 0.3s both;
}

.hero-actions {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    animation: fadeInUp 0.8s ease-out 0.6s both;
}

.primary-btn,
.secondary-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.primary-btn::before,
.secondary-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
}

.primary-btn:hover::before,
.secondary-btn:hover::before {
    left: 100%;
}

.primary-btn {
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    color: white;
    border: none;
    box-shadow: 0 4px 15px rgba(255, 127, 80, 0.3), 0 2px 5px rgba(255, 127, 80, 0.2);
}

.primary-btn:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 6px 20px rgba(255, 127, 80, 0.4), 0 4px 10px rgba(255, 127, 80, 0.3);
}

.secondary-btn {
    background: white;
    color: #FF7F50;
    border: 2px solid #FF7F50;
    box-shadow: 0 2px 10px rgba(255, 127, 80, 0.1);
}

.secondary-btn:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 4px 15px rgba(255, 127, 80, 0.2), 0 2px 5px rgba(255, 127, 80, 0.1);
    background: rgba(255, 127, 80, 0.05);
}

.btn-icon {
    font-size: 1.2rem;
    transition: transform 0.3s ease;
}

.primary-btn:hover .btn-icon,
.secondary-btn:hover .btn-icon {
    transform: translateX(5px) scale(1.2);
}

.hero-visual {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: slideRight 0.8s ease-out;
    position: relative;
}

.hero-visual svg {
    animation: float 6s ease-in-out infinite;
    filter: drop-shadow(0 10px 30px rgba(255, 127, 80, 0.2));
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0px) rotate(0deg);
    }

    33% {
        transform: translateY(-20px) rotate(5deg);
    }

    66% {
        transform: translateY(10px) rotate(-5deg);
    }
}

/* 平台特色 */
.features-section {
    padding: 4rem 2rem;
    background: white;
    text-align: center;
}

.section-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #333;
    margin: 0 0 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.title-icon {
    font-size: 2rem;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.feature-card {
    background: linear-gradient(135deg, #fff 0%, #fff8f5 100%);
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(255, 127, 80, 0.15);
    border-color: #FF7F50;
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 1.5rem;
}

.feature-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 1rem;
}

.feature-description {
    font-size: 1rem;
    color: #666;
    margin: 0;
    line-height: 1.6;
}

/* 案例预览 */
.cases-section {
    padding: 4rem 2rem;
    max-width: 1400px;
    margin: 0 auto;
    position: relative;
}

.cases-section::before {
    content: '';
    position: absolute;
    top: -50px;
    left: 50%;
    transform: translateX(-50%);
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(255, 127, 80, 0.1) 0%, transparent 70%);
    z-index: -1;
    animation: float 8s ease-in-out infinite reverse;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2.5rem;
    flex-wrap: wrap;
    gap: 1rem;
    animation: fadeInDown 0.8s ease-out;
}

.view-all-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #FF7F50;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    background: rgba(255, 127, 80, 0.05);
}

.view-all-link:hover {
    transform: translateY(-3px);
    background: rgba(255, 127, 80, 0.1);
    box-shadow: 0 4px 15px rgba(255, 127, 80, 0.15);
}

.view-all-link:hover .link-icon {
    transform: translateX(5px) scale(1.2);
}

.cases-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2rem;
}

.case-card {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-top: 4px solid #FF7F50;
    position: relative;
    overflow: hidden;
}

.case-card::before {
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

.case-card:hover::before {
    opacity: 1;
}

.case-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 35px rgba(255, 127, 80, 0.2);
}

.case-header {
    margin-bottom: 1rem;
    position: relative;
    z-index: 1;
}

.case-category {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: rgba(255, 127, 80, 0.1);
    color: #FF7F50;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.case-card:hover .case-category {
    background: rgba(255, 127, 80, 0.2);
    transform: translateX(5px);
}

.case-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 1rem;
    line-height: 1.4;
    position: relative;
    z-index: 1;
    transition: color 0.3s ease;
}

.case-card:hover .case-title {
    color: #FF7F50;
}

.case-description {
    font-size: 1rem;
    color: #666;
    margin: 0 0 1.5rem;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

.case-tags {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
    position: relative;
    z-index: 1;
}

.case-tag {
    padding: 0.3rem 0.8rem;
    background: rgba(255, 127, 80, 0.1);
    color: #FF7F50;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.case-card:hover .case-tag {
    background: rgba(255, 127, 80, 0.2);
    transform: translateY(-2px);
}

.case-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: #FF7F50;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    background: rgba(255, 127, 80, 0.05);
    position: relative;
    z-index: 1;
}

.case-link:hover {
    transform: translateX(5px);
    background: rgba(255, 127, 80, 0.1);
    box-shadow: 0 4px 15px rgba(255, 127, 80, 0.15);
}

.link-icon {
    font-size: 1rem;
    transition: transform 0.3s ease;
}

.case-link:hover .link-icon {
    transform: translateX(5px) scale(1.2);
}

/* 贡献者展示 */
.contributors-section {
    padding: 4rem 2rem;
    background: white;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.contributors-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, transparent 0%, rgba(255, 127, 80, 0.05) 50%, transparent 100%);
    z-index: -1;
}

.contributors-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

.contributor-card {
    background: linear-gradient(135deg, #fff 0%, #fff8f5 100%);
    padding: 2rem 1.5rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    border: 2px solid transparent;
    overflow: hidden;
}

.contributor-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(255, 127, 80, 0.1) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 0;
}

.contributor-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 35px rgba(255, 127, 80, 0.15);
    border-color: #FF7F50;
}

.contributor-card:hover::after {
    opacity: 1;
}

.contributor-avatar {
    margin-bottom: 1.5rem;
    position: relative;
    z-index: 1;
    transition: transform 0.3s ease;
}

.contributor-card:hover .contributor-avatar {
    transform: scale(1.1) rotate(5deg);
}

.contributor-avatar svg {
    filter: drop-shadow(0 4px 10px rgba(255, 127, 80, 0.2));
}

.contributor-name {
    font-size: 1.3rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 0.5rem;
    position: relative;
    z-index: 1;
    transition: color 0.3s ease;
}

.contributor-card:hover .contributor-name {
    color: #FF7F50;
}

.contributor-role {
    font-size: 0.95rem;
    color: #666;
    margin: 0 0 1rem;
    position: relative;
    z-index: 1;
}

.contributor-stats {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    font-size: 0.9rem;
    color: #999;
    position: relative;
    z-index: 1;
}

.contributor-card:hover .contributor-stats {
    color: #666;
}

.stat-item {
    transition: all 0.3s ease;
}

.contributor-card:hover .stat-item {
    transform: translateY(-2px);
}

/* 行动召唤 */
.cta-section {
    padding: 4rem 2rem;
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    text-align: center;
}

.cta-content {
    max-width: 800px;
    margin: 0 auto;
    color: white;
}

.cta-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0 0 1rem;
}

.cta-description {
    font-size: 1.2rem;
    margin: 0 0 2.5rem;
    opacity: 0.9;
}

.cta-actions {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.cta-actions .primary-btn {
    background: white;
    color: #FF7F50;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.cta-actions .primary-btn:hover {
    background: rgba(255, 255, 255, 0.95);
}

.cta-actions .secondary-btn {
    background: transparent;
    color: white;
    border-color: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.cta-actions .secondary-btn:hover {
    background: rgba(255, 255, 255, 0.1);
}

/* 动画效果 */
@keyframes slideLeft {
    from {
        opacity: 0;
        transform: translateX(-50px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideRight {
    from {
        opacity: 0;
        transform: translateX(50px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .hero-section {
        flex-direction: column;
        text-align: center;
        padding: 3rem 1.5rem;
    }

    .hero-title {
        font-size: 2.5rem;
    }

    .hero-subtitle {
        font-size: 1.2rem;
    }

    .hero-actions {
        justify-content: center;
    }

    .hero-visual {
        margin-top: 2rem;
    }

    .section-title {
        font-size: 2rem;
    }

    .section-header {
        flex-direction: column;
        align-items: center;
    }

    .cases-grid,
    .features-grid,
    .contributors-grid {
        grid-template-columns: 1fr;
    }

    .cta-title {
        font-size: 2rem;
    }

    .cta-description {
        font-size: 1.1rem;
    }
}

@media (max-width: 480px) {
    .hero-title {
        font-size: 2rem;
    }

    .section-title {
        font-size: 1.75rem;
        flex-direction: column;
        gap: 0.5rem;
    }

    .primary-btn,
    .secondary-btn {
        padding: 0.875rem 1.5rem;
        font-size: 1rem;
    }

    .features-grid,
    .cases-grid,
    .contributors-grid {
        gap: 1.5rem;
    }

    .feature-card,
    .case-card,
    .contributor-card {
        padding: 1.5rem 1rem;
    }
}
</style>