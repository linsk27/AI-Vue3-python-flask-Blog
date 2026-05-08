<template>
    <div class="ai-center-page">
        <router-view v-if="$route.path !== '/ai-center'" />
        <main v-else>
            <section class="ai-hero">
                <span class="eyebrow">AI Workspace</span>
                <h1>AI 工作台</h1>
                <p>
                    面向写作者和知识整理者的 AI 入口：聊天、摘要、上下文包和起草都从这里开始。
                    管理配置由管理员统一维护，普通使用路径保持清爽。
                </p>
                <div class="hero-actions">
                    <button class="primary-action" type="button" @click="goToChat">
                        开始对话
                    </button>
                    <button class="secondary-action" type="button" @click="goToWrite">
                        AI 起草
                    </button>
                </div>
            </section>

            <section class="agent-grid">
                <article
                    v-for="agent in agents"
                    :key="agent.title"
                    class="agent-card"
                    tabindex="0"
                    role="button"
                    @click="agent.action"
                    @keydown.enter="agent.action"
                >
                    <div class="agent-top">
                        <component :is="agent.icon" class="agent-icon" />
                        <span>{{ agent.mode }}</span>
                    </div>
                    <h2>{{ agent.title }}</h2>
                    <p>{{ agent.description }}</p>
                    <strong>{{ agent.cta }}</strong>
                </article>
            </section>
        </main>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ChatDotRound, DocumentChecked, MagicStick, Share } from '@element-plus/icons-vue'
import { useElMessage } from '@/hooks/useMessage'
import { usePermission } from '@/hooks/usePermission'

const router = useRouter()
const { message } = useElMessage()
const { hasPermission } = usePermission()

const agents = [
    {
        mode: 'Context',
        title: '上下文对话',
        description: '围绕上下文包、项目资料和正在写的内容持续追问。',
        cta: '进入聊天',
        icon: ChatDotRound,
        action: goToChat
    },
    {
        mode: 'Digest',
        title: '长文摘要',
        description: '把文章、会议记录和说明文档压缩成摘要与要点。',
        cta: '生成摘要',
        icon: DocumentChecked,
        action: goToSummary
    },
    {
        mode: 'Forge',
        title: '上下文包',
        description: '把真实资料组织成可检索、可导出、可提问的知识资产。',
        cta: '构建资产',
        icon: Share,
        action: goToPacks
    },
    {
        mode: 'Draft',
        title: 'AI 起草',
        description: '根据主题生成标题、摘要、标签和正文分离的文档草稿。',
        cta: '新建文档',
        icon: MagicStick,
        action: goToWrite
    }
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

function goToPacks() {
    router.push('/context-packs')
}

function goToWrite() {
    router.push('/essays/write')
}
</script>

<style scoped>
.ai-center-page {
    width: var(--page-width);
    min-height: calc(100vh - 160px);
    margin: 0 auto;
    padding: 44px 0 72px;
    color: var(--text-primary);
}

.ai-hero {
    padding: 28px;
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.eyebrow,
.agent-top span {
    font-family: var(--font-mono);
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--badge-bg);
    color: var(--badge-fg);
    font-size: 12px;
    font-weight: 700;
}

.ai-hero h1 {
    max-width: 900px;
    margin: 18px 0 14px;
    font-size: clamp(42px, 5vw, 64px);
    font-weight: 700;
    line-height: 1.02;
}

.ai-hero p {
    max-width: 760px;
    margin: 0;
    color: var(--text-secondary);
    font-size: 17px;
    line-height: 1.7;
}

.hero-actions {
    margin-top: 24px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.primary-action,
.secondary-action {
    min-height: 40px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 0;
    border-radius: 8px;
    padding: 0 16px;
    font: inherit;
    font-weight: 700;
    cursor: pointer;
    transition: background 180ms ease, color 180ms ease, transform 180ms ease;
}

.primary-action {
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.secondary-action {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.primary-action:hover,
.secondary-action:hover {
    transform: translateY(-1px);
}

.agent-grid {
    margin-top: 18px;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
}

.agent-card {
    min-height: 210px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
    cursor: pointer;
    transition: transform 180ms ease, box-shadow 180ms ease;
}

.agent-card:hover,
.agent-card:focus-visible {
    transform: translateY(-2px);
    box-shadow: var(--card-shadow), 0 14px 30px rgba(0, 0, 0, 0.08);
}

.agent-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.agent-icon {
    width: 24px;
    height: 24px;
    color: var(--accent-blue);
}

.agent-top span {
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.agent-card h2 {
    margin: 22px 0 10px;
    font-size: 21px;
    line-height: 1.2;
}

.agent-card p {
    color: var(--text-secondary);
    line-height: 1.65;
}

.agent-card strong {
    margin-top: auto;
    font-size: 14px;
}

@media (max-width: 1180px) {
    .agent-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 640px) {
    .ai-center-page {
        padding-top: 32px;
    }

    .agent-grid {
        grid-template-columns: 1fr;
    }
}
</style>
