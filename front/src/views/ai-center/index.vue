<template>
    <div class="ai-center-page">
        <router-view v-if="$route.path !== '/ai-center'" />
        <div v-else>
            <section class="ai-hero">
                <div>
                    <span class="eyebrow">AI workspace</span>
                    <h1>AI 中心</h1>
                    <p>把聊天、摘要和选中文本解释集中到一个轻量入口，减少创作时的上下文切换。</p>
                </div>
                <div class="status-card">
                    <span class="mono">ACTIVE MODEL</span>
                    <strong>Context Assistant</strong>
                    <p>用于阅读理解、文章摘要和创作辅助。</p>
                </div>
            </section>

            <section class="ai-features">
                <article class="ai-feature-card" tabindex="0" role="button" @click="goToChat" @keydown.enter="goToChat">
                    <div class="feature-top">
                        <ChatDotRound class="feature-icon develop" />
                        <span>Develop</span>
                    </div>
                    <h2>全局 AI 聊天</h2>
                    <p>和 AI 助手进行连续对话，快速获得技术解释、思路拆解和方案建议。</p>
                    <strong>开始聊天</strong>
                </article>

                <article class="ai-feature-card" tabindex="0" role="button" @click="goToSummary" @keydown.enter="goToSummary">
                    <div class="feature-top">
                        <DocumentChecked class="feature-icon preview" />
                        <span>Preview</span>
                    </div>
                    <h2>智能摘要</h2>
                    <p>对文章生成短摘要和重点提炼，帮助读者更快判断内容价值。</p>
                    <strong>生成摘要</strong>
                </article>

                <article class="ai-feature-card" tabindex="0" role="button" @click="showContextMenuInfo" @keydown.enter="showContextMenuInfo">
                    <div class="feature-top">
                        <MagicStick class="feature-icon ship" />
                        <span>Ship</span>
                    </div>
                    <h2>情景式助手</h2>
                    <p>阅读时选中文本并唤起 AI，围绕当前片段解释概念、改写或扩展。</p>
                    <strong>了解更多</strong>
                </article>
            </section>

            <section class="guide-panel">
                <div class="section-heading">
                    <span class="eyebrow">How it works</span>
                    <h2>三步进入 AI 辅助流。</h2>
                </div>
                <div class="guide-steps">
                    <div v-for="step in steps" :key="step.title" class="guide-step">
                        <span>{{ step.index }}</span>
                        <div>
                            <h3>{{ step.title }}</h3>
                            <p>{{ step.description }}</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ChatDotRound, DocumentChecked, MagicStick } from '@element-plus/icons-vue'
import { useElMessage } from '@/hooks/useMessage'
import { usePermission } from '@/hooks/usePermission'

const router = useRouter()
const { message } = useElMessage()
const { hasPermission } = usePermission()

const steps = [
    { index: '01', title: '打开聊天', description: '进入全局 AI 聊天，围绕技术问题持续追问。' },
    { index: '02', title: '生成摘要', description: '选择文章或输入内容，让 AI 输出短摘要和重点。' },
    { index: '03', title: '选中文本', description: '在阅读场景中选中片段，直接唤起上下文助手。' }
]

function ensureAccess() {
    if (!hasPermission('ai:access')) {
        message.warning('当前账号没有 AI 功能权限')
        return false
    }
    return true
}

function goToChat() {
    if (ensureAccess()) router.push('/ai-center/chat')
}

function goToSummary() {
    if (ensureAccess()) router.push('/ai-center/summary')
}

function showContextMenuInfo() {
    if (!ensureAccess()) return
    message.info('阅读文章时选中文本并右键，选择“使用 AI 询问”即可唤起情景式助手')
}
</script>

<style scoped>
.ai-center-page {
    max-width: 1200px;
    min-height: calc(100vh - 160px);
    margin: 0 auto;
    padding: 72px 16px 80px;
    color: var(--text-primary);
}

.ai-hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 320px;
    align-items: end;
    gap: 32px;
    margin-bottom: 32px;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: #ebf5ff;
    color: #0068d6;
    font-family: "Geist Mono", ui-monospace, monospace;
    font-size: 12px;
    font-weight: 500;
}

.ai-hero h1,
.section-heading h2 {
    margin: 16px 0 12px;
    color: var(--text-primary);
    font-size: clamp(44px, 7vw, 72px);
    font-weight: 600;
    line-height: 0.96;
    letter-spacing: -2.4px;
}

.ai-hero p,
.status-card p,
.ai-feature-card p,
.guide-step p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 16px;
    line-height: 1.7;
}

.ai-hero > div:first-child > p {
    max-width: 660px;
    font-size: 18px;
    line-height: 1.75;
}

.status-card,
.ai-feature-card,
.guide-panel {
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.status-card {
    padding: 24px;
}

.mono,
.feature-top span {
    font-family: "Geist Mono", ui-monospace, monospace;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
}

.status-card strong {
    display: block;
    margin: 16px 0 8px;
    font-size: 24px;
    font-weight: 600;
    letter-spacing: -0.96px;
}

.ai-features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.ai-feature-card {
    min-height: 280px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    cursor: pointer;
    transition: transform 180ms ease, box-shadow 180ms ease;
}

.ai-feature-card:hover,
.ai-feature-card:focus-visible {
    transform: translateY(-2px);
    box-shadow: rgba(0, 0, 0, 0.12) 0 0 0 1px,
        rgba(0, 0, 0, 0.06) 0 8px 18px -12px;
}

.feature-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.feature-icon {
    width: 24px;
    height: 24px;
}

.develop {
    color: #0a72ef;
}

.preview {
    color: #de1d8d;
}

.ship {
    color: #ff5b4f;
}

.ai-feature-card h2 {
    margin: 28px 0 12px;
    color: var(--text-primary);
    font-size: 24px;
    font-weight: 600;
    line-height: 1.25;
    letter-spacing: -0.96px;
}

.ai-feature-card strong {
    margin-top: auto;
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 500;
}

.guide-panel {
    margin-top: 12px;
    padding: 32px;
}

.section-heading {
    max-width: 720px;
    margin-bottom: 28px;
}

.section-heading h2 {
    font-size: clamp(32px, 5vw, 48px);
}

.guide-steps {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.guide-step {
    display: flex;
    gap: 16px;
    padding: 18px;
    border-radius: 8px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.guide-step > span {
    font-family: "Geist Mono", ui-monospace, monospace;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 500;
}

.guide-step h3 {
    margin: 0 0 8px;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.32px;
}

@media (max-width: 980px) {
    .ai-hero,
    .ai-features,
    .guide-steps {
        grid-template-columns: 1fr;
    }

    .status-card {
        max-width: 480px;
    }
}

@media (max-width: 640px) {
    .ai-center-page {
        padding: 48px 12px 64px;
    }

    .guide-panel {
        padding: 20px;
    }
}
</style>
