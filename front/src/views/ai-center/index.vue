<template>
    <div class="ai-center-container">
        <router-view v-if="$route.path !== '/ai-center'" />
        <div v-else>
            <!-- 页面头部 -->
            <section class="ai-header">
                <h1 class="ai-title">
                    <span class="title-icon">🤖</span>
                    智能AI中心
                </h1>
                <p class="ai-subtitle">探索AI驱动的知识管理与创作体验</p>
            </section>

            <!-- AI功能卡片 -->
            <section class="ai-features">
                <div class="ai-feature-card" @click="goToChat">
                    <div class="feature-icon">💬</div>
                    <h3 class="feature-title">全局AI聊天</h3>
                    <p class="feature-description">与AI助手进行对话，获取专业知识和建议</p>
                    <div class="feature-action">
                        <span>开始聊天</span>
                        <span class="action-icon">→</span>
                    </div>
                </div>

                <div class="ai-feature-card" @click="goToSummary">
                    <div class="feature-icon">📝</div>
                    <h3 class="feature-title">智能摘要</h3>
                    <p class="feature-description">一键生成文章摘要，快速掌握核心内容</p>
                    <div class="feature-action">
                        <span>生成摘要</span>
                        <span class="action-icon">→</span>
                    </div>
                </div>

                <div class="ai-feature-card" @click="showContextMenuInfo">
                    <div class="feature-icon">✏️</div>
                    <h3 class="feature-title">情景式AI助手</h3>
                    <p class="feature-description">阅读时选中文本，右键呼出AI助手浮窗</p>
                    <div class="feature-action">
                        <span>了解更多</span>
                        <span class="action-icon">→</span>
                    </div>
                </div>
            </section>

            <!-- 使用指南 -->
            <section class="ai-guide">
                <h2 class="guide-title">使用指南</h2>
                <div class="guide-steps">
                    <div class="guide-step">
                        <div class="step-number">1</div>
                        <div class="step-content">
                            <h3 class="step-title">全局AI聊天</h3>
                            <p class="step-description">点击左侧导航栏的"全局AI聊天"，与AI助手进行对话</p>
                        </div>
                    </div>
                    <div class="guide-step">
                        <div class="step-number">2</div>
                        <div class="step-content">
                            <h3 class="step-title">智能摘要</h3>
                            <p class="step-description">选择一篇文章，点击"生成摘要"按钮获取文章摘要</p>
                        </div>
                    </div>
                    <div class="guide-step">
                        <div class="step-number">3</div>
                        <div class="step-content">
                            <h3 class="step-title">情景式AI助手</h3>
                            <p class="step-description">在阅读文章时，选中文本并右键，选择"使用AI询问"</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useElMessage } from '@/hooks/useMessage'
import { usePermission } from '@/hooks/usePermission'

const router = useRouter()
const { message } = useElMessage()
const { hasPermission } = usePermission()

// 跳转到AI聊天页面
function goToChat() {
    if (!hasPermission('ai:access')) {
        message.warning('您没有权限使用AI聊天功能')
        return
    }
    router.push('/ai-center/chat')
}

// 跳转到智能摘要页面
function goToSummary() {
    if (!hasPermission('ai:access')) {
        message.warning('您没有权限使用AI功能')
        return
    }
    router.push('/ai-center/summary')
}

// 显示情景菜单信息
function showContextMenuInfo() {
    if (!hasPermission('ai:access')) {
        message.warning('您没有权限使用AI功能')
        return
    }
    message.info('在阅读文章时，选中文本并右键，选择"使用AI询问"即可呼出情景式AI助手')
}
</script>

<style scoped>
.ai-center-container {
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(255, 248, 245, 0.85) 100%);
    /* padding: 0 4rem 2rem; */
}

/* 页面头部 */
.ai-header {
    text-align: center;
    margin-bottom: 4rem;
    animation: fadeInDown 0.8s ease-out;
}

.ai-title {
    font-size: 3rem;
    font-weight: 700;
    color: #FF7F50;
    margin: 0 0 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.title-icon {
    font-size: 2.5rem;
}

.ai-subtitle {
    font-size: 1.2rem;
    color: #666;
    margin: 0;
    font-weight: 400;
}

/* AI功能卡片 */
.ai-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2rem;
    max-width: 1200px;
    margin: 0 auto 4rem;
}

.ai-feature-card {
    background: rgba(255, 255, 255, 0.9);
    padding: 2.5rem 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    border-top: 4px solid #FF7F50;
    position: relative;
    overflow: hidden;
}

.ai-feature-card::before {
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

.ai-feature-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 35px rgba(255, 127, 80, 0.15);
}

.ai-feature-card:hover::before {
    opacity: 1;
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
    position: relative;
    z-index: 1;
}

.feature-description {
    font-size: 1rem;
    color: #666;
    margin: 0 0 2rem;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

.feature-action {
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

.ai-feature-card:hover .action-icon {
    transform: translateX(5px);
}

/* 使用指南 */
.ai-guide {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    padding: 3rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(255, 127, 80, 0.1);
    margin-bottom: 2rem;
}

.guide-title {
    font-size: 2rem;
    font-weight: 700;
    color: #FF7F50;
    margin: 0 0 2rem;
    text-align: center;
}

.guide-steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.guide-step {
    display: flex;
    gap: 1.5rem;
    align-items: flex-start;
    padding: 1.5rem;
    background: rgba(255, 127, 80, 0.05);
    border-radius: 12px;
    transition: all 0.3s ease;
}

.guide-step:hover {
    background: rgba(255, 127, 80, 0.1);
    transform: translateY(-3px);
}

.step-number {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: 700;
    flex-shrink: 0;
}

.step-content {
    flex: 1;
}

.step-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 0.5rem;
}

.step-description {
    font-size: 1rem;
    color: #666;
    margin: 0;
    line-height: 1.6;
}

/* 动画效果 */
@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .ai-center-container {
        padding: 2rem 1rem;
    }

    .ai-title {
        font-size: 2.5rem;
    }

    .ai-features {
        grid-template-columns: 1fr;
    }

    .guide-steps {
        grid-template-columns: 1fr;
    }

    .ai-guide {
        padding: 2rem 1.5rem;
    }
}
</style>