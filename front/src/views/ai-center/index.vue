<template>
    <div class="ai-center-page">
        <router-view v-if="$route.path !== '/ai-center'" />
        <main v-else>
            <section class="ai-hero">
                <div class="hero-copy">
                    <span class="eyebrow">知镜 AI</span>
                    <h1>先找资料，再问 AI。</h1>
                    <p>
                        选择资料包、追问依据、生成摘要或起草文档。AI 会尽量回到你沉淀的来源，
                        而不是从空白里自由发挥。
                    </p>
                    <div class="hero-actions">
                        <button class="primary-action" type="button" @click="goToChat">
                            开始对话
                        </button>
                        <button class="secondary-action" type="button" @click="goToPacks">
                            整理资料
                        </button>
                    </div>
                </div>

                <div class="hero-flow" aria-label="AI 工作流">
                    <div v-for="step in flowSteps" :key="step" class="flow-step">
                        {{ step }}
                    </div>
                </div>
            </section>

            <section class="agent-grid" aria-label="AI 能力入口">
                <article
                    v-for="agent in agents"
                    :key="agent.title"
                    class="agent-card"
                    tabindex="0"
                    role="button"
                    @click="agent.action"
                    @keydown.enter="agent.action"
                    @keydown.space.prevent="agent.action"
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

const flowSteps = ['资料包', '命中片段', 'AI 回答', '继续编辑']

const agents = [
    {
        mode: '问资料',
        title: '上下文对话',
        description: '选择资料包后提问，回答会带着本轮命中的来源片段。',
        cta: '进入聊天',
        icon: ChatDotRound,
        action: goToChat
    },
    {
        mode: '压缩',
        title: '长文摘要',
        description: '把文章、会议记录和资料说明压缩成摘要与要点。',
        cta: '生成摘要',
        icon: DocumentChecked,
        action: goToSummary
    },
    {
        mode: '沉淀',
        title: '上下文包',
        description: '把网页、笔记、论文和文章整理成可复用资料包。',
        cta: '整理资料',
        icon: Share,
        action: goToPacks
    },
    {
        mode: '写作',
        title: 'AI 起草',
        description: '输入主题或选中资料包，生成可继续修改的文档草稿。',
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
/* Hallmark · macrostructure: split workspace launcher · tone: white minimal · anchor hue: warm brass */
.ai-center-page {
    width: var(--page-width);
    min-height: calc(100vh - 160px);
    margin: 0 auto;
    padding: 44px 0 72px;
    color: var(--text-primary);
}

.ai-hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(320px, 0.62fr);
    gap: clamp(28px, 5vw, 72px);
    align-items: end;
    padding: clamp(28px, 5vw, 56px);
    border: 1px solid var(--line);
    border-radius: var(--radius-xl);
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
    border-radius: var(--radius-pill);
    background: var(--badge-bg);
    color: var(--badge-fg);
    font-size: 12px;
    font-weight: 700;
}

.ai-hero h1 {
    max-width: 760px;
    margin: 18px 0 16px;
    font-family: var(--font-serif);
    font-size: var(--text-display-s);
    font-weight: 600;
    line-height: 1.02;
    letter-spacing: 0;
    text-wrap: balance;
}

.ai-hero p {
    max-width: 640px;
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
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 0;
    border-radius: var(--radius-md);
    padding: 0 18px;
    font: inherit;
    font-weight: 700;
    cursor: pointer;
    transition:
        background var(--dur-med) var(--ease-out),
        color var(--dur-med) var(--ease-out),
        transform var(--dur-med) var(--ease-out);
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

.hero-flow {
    display: grid;
    gap: var(--space-sm);
}

.flow-step {
    min-height: 58px;
    display: flex;
    align-items: center;
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);
    padding: 0 var(--space-lg);
    color: var(--text-primary);
    background: var(--surface-subtle);
    font-size: var(--text-xl);
    font-weight: 700;
}

.agent-grid {
    margin-top: var(--space-md);
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
}

.agent-card {
    min-height: 210px;
    padding: var(--space-lg);
    display: flex;
    flex-direction: column;
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);
    background: var(--surface);
    box-shadow: var(--card-shadow);
    cursor: pointer;
    transition:
        transform var(--dur-med) var(--ease-out),
        box-shadow var(--dur-med) var(--ease-out),
        background var(--dur-med) var(--ease-out);
}

.agent-card:hover,
.agent-card:focus-visible {
    transform: translateY(-2px);
    background: color-mix(in oklch, var(--surface) 86%, var(--surface-subtle));
    box-shadow: var(--card-shadow), var(--color-overlay-soft) 0 14px 30px;
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
    color: var(--color-accent);
}

.agent-top span {
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 700;
}

.agent-card h2 {
    margin: 22px 0 10px;
    font-family: var(--font-serif);
    font-size: 21px;
    font-weight: 600;
    line-height: 1.2;
}

.agent-card p {
    color: var(--text-secondary);
    line-height: 1.65;
}

.agent-card strong {
    margin-top: auto;
    font-size: 14px;
    color: var(--color-accent-strong);
}

@media (max-width: 1180px) {
    .ai-hero {
        grid-template-columns: 1fr;
    }

    .agent-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 640px) {
    .ai-center-page {
        padding-top: 32px;
    }

    .ai-hero {
        padding: var(--space-lg);
        border-radius: var(--radius-lg);
    }

    .ai-hero h1 {
        font-size: clamp(38px, 12vw, 54px);
    }

    .hero-actions {
        display: grid;
    }

    .primary-action,
    .secondary-action {
        width: 100%;
    }

    .flow-step {
        min-height: 52px;
        font-size: var(--text-lg);
    }

    .agent-grid {
        grid-template-columns: 1fr;
    }
}
</style>
