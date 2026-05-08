<template>
    <div class="workspace-page">
        <section class="workspace-hero">
            <div class="hero-copy">
                <span class="eyebrow">AI 上下文工作台</span>
                <h1>把零散知识锻造成可复用的 AI 上下文。</h1>
                <p>
                    ContextForge / 语境工坊可以把文档、笔记、网页、代码仓库和 AI 对话整理成上下文包，
                    用于摘要、问答、复盘、写作和项目交接。
                </p>
                <div class="hero-actions">
                    <router-link to="/context-packs" class="primary-action">查看上下文包</router-link>
                    <router-link to="/essays/write" class="secondary-action">新建文档</router-link>
                </div>
            </div>

            <div class="command-panel" aria-label="ContextForge workflow preview">
                <div class="panel-topbar">
                    <span></span>
                    <span></span>
                    <span></span>
                    <strong>context.run</strong>
                </div>
                <div class="panel-body">
                    <div v-for="step in workflow" :key="step.title" class="workflow-step">
                        <span class="step-index">{{ step.index }}</span>
                        <div>
                            <strong>{{ step.title }}</strong>
                            <p>{{ step.description }}</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="metrics-row" aria-label="Workspace metrics">
            <article v-for="metric in metrics" :key="metric.label" class="metric-card">
                <strong>{{ metric.value }}</strong>
                <span>{{ metric.label }}</span>
            </article>
        </section>

        <section class="workspace-grid">
            <article class="feature-panel feature-panel-large">
                <span class="eyebrow">核心特色</span>
                <h2>上下文包是可复用的 AI 记忆容器。</h2>
                <p>
                    把文档、链接、笔记、仓库分析和 AI 对话组织到一个上下文包里，用于问答、项目交接、
                    复习备考、研究整理或内容创作。
                </p>
                <div class="pack-preview">
                    <div v-for="pack in contextPacks" :key="pack.name" class="pack-row">
                        <span>{{ pack.name }}</span>
                        <strong>{{ pack.count }}</strong>
                    </div>
                </div>
            </article>

            <article v-for="feature in features" :key="feature.title" class="feature-panel">
                <span class="feature-kicker">{{ feature.kicker }}</span>
                <h3>{{ feature.title }}</h3>
                <p>{{ feature.description }}</p>
            </article>
        </section>

        <section class="quick-actions">
            <div>
                <span class="eyebrow">下一步</span>
                <h2>先沉淀一份文档，再围绕它锻造上下文。</h2>
            </div>
            <div class="action-list">
                <router-link to="/essays" class="action-card">浏览知识库</router-link>
                <router-link to="/ai-center/chat" class="action-card">打开上下文对话</router-link>
                <router-link to="/context-packs" class="action-card">构建上下文包</router-link>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import articleApi from '@/api/modules/article'
import type { IArticle } from '@/api/modules/article/interface'
import contextPackApi, { type ContextPack, type ContextPackStats } from '@/api/modules/contextPacks'

const workflow = [
    {
        index: '01',
        title: '收集',
        description: '把文档、笔记、链接、项目记录和 AI 对话放进同一个工作台。'
    },
    {
        index: '02',
        title: '锻造',
        description: '把相关材料组合成上下文包，保留目标、来源、决策和关键线索。'
    },
    {
        index: '03',
        title: '复用',
        description: '随时用它问答、摘要、生成提示词、产出复盘，或导出给其他工具。'
    }
]

const articles = ref<IArticle[]>([])
const packs = ref<ContextPack[]>([])
const stats = ref<ContextPackStats | null>(null)

const metrics = computed(() => [
    { value: articles.value.length, label: '真实知识文档' },
    { value: stats.value?.packs ?? packs.value.length, label: '可复用上下文包' },
    { value: stats.value?.sources ?? packs.value.reduce((total, pack) => total + pack.sources.length, 0), label: '资料来源' }
])

const contextPacks = computed(() => {
    if (!packs.value.length) {
        return [{ name: '暂无真实上下文包', count: '0 份资料' }]
    }

    return packs.value.slice(0, 3).map(pack => ({
        name: pack.name,
        count: `${pack.sources.length} 份资料`
    }))
})

const features = [
    {
        kicker: 'AI 阅读',
        title: '围绕当前文档提问。',
        description: '把选中的内容转成解释、例子、复习问题和可复用的上下文片段。'
    },
    {
        kicker: '提示词工坊',
        title: '把知识转成提示词。',
        description: '从文档或上下文包生成摘要、教学、问答、代码审查和项目复盘提示词。'
    },
    {
        kicker: '项目复盘',
        title: '生成项目表达材料。',
        description: '辅助生成架构总结、功能模块、简历描述和软著说明草稿。'
    },
    {
        kicker: '导入管线',
        title: '接入网页和代码仓库。',
        description: '后续支持 URL、Markdown、Word 和 GitHub 仓库导入，让资料入口更完整。'
    }
]

onMounted(async () => {
    try {
        const [articleList, packList, workspaceStats] = await Promise.all([
            articleApi.getList(),
            contextPackApi.getList(),
            contextPackApi.getStats()
        ])
        articles.value = Array.isArray(articleList) ? articleList : []
        packs.value = Array.isArray(packList) ? packList : []
        stats.value = workspaceStats
    } catch (error) {
        console.error('Load real workspace metrics failed:', error)
        articles.value = []
        packs.value = []
        stats.value = null
    }
})
</script>

<style scoped>
.workspace-page {
    width: 100%;
    color: var(--text-primary);
}

.workspace-hero {
    width: var(--page-width);
    min-height: calc(100vh - 112px);
    margin: 0 auto;
    padding: 72px 0 48px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(360px, 520px);
    align-items: center;
    gap: 48px;
}

.eyebrow,
.feature-kicker,
.step-index {
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
    font-weight: 600;
}

.hero-copy h1 {
    margin: 18px 0 20px;
    color: var(--text-primary);
    font-size: clamp(44px, 7vw, 84px);
    font-weight: 650;
    line-height: 0.98;
    letter-spacing: 0;
}

.hero-copy p {
    max-width: 660px;
    margin: 0;
    color: var(--text-secondary);
    font-size: 19px;
    line-height: 1.75;
}

.hero-actions {
    margin-top: 32px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.primary-action,
.secondary-action,
.action-card {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 40px;
    padding: 0 16px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease;
}

.primary-action {
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.primary-action:hover {
    background: var(--button-hover);
}

.secondary-action,
.action-card {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.secondary-action:hover,
.action-card:hover {
    background: var(--surface-hover);
}

.command-panel,
.metric-card,
.feature-panel,
.quick-actions {
    background: var(--surface);
    border-radius: 12px;
    box-shadow: var(--card-shadow);
}

.command-panel {
    overflow: hidden;
}

.panel-topbar {
    min-height: 42px;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 14px;
    box-shadow: var(--ring);
}

.panel-topbar span {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--line);
}

.panel-topbar strong {
    margin-left: auto;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 500;
}

.panel-body {
    padding: 24px;
    display: grid;
    gap: 12px;
}

.workflow-step {
    display: grid;
    grid-template-columns: 44px minmax(0, 1fr);
    gap: 14px;
    padding: 16px;
    border-radius: 12px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.step-index {
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 700;
}

.workflow-step strong {
    display: block;
    font-size: 17px;
    font-weight: 700;
}

.workflow-step p {
    margin: 6px 0 0;
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.6;
}

.metrics-row,
.workspace-grid,
.quick-actions {
    width: var(--page-width);
    margin: 0 auto;
}

.metrics-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    padding-bottom: 56px;
}

.metric-card {
    min-height: 124px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.metric-card strong {
    font-size: 38px;
    font-weight: 700;
    line-height: 1;
}

.metric-card span {
    color: var(--text-secondary);
    font-size: 14px;
}

.workspace-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    padding-bottom: 56px;
}

.feature-panel {
    min-height: 260px;
    padding: 24px;
}

.feature-panel-large {
    grid-column: span 2;
    grid-row: span 2;
}

.feature-panel h2,
.quick-actions h2 {
    margin: 14px 0 14px;
    font-size: clamp(32px, 5vw, 50px);
    font-weight: 650;
    line-height: 1.05;
}

.feature-panel h3 {
    margin: 16px 0 10px;
    font-size: 24px;
    font-weight: 650;
    line-height: 1.2;
}

.feature-panel p,
.quick-actions p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 15px;
    line-height: 1.7;
}

.feature-kicker {
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.pack-preview {
    margin-top: 26px;
    display: grid;
    gap: 10px;
}

.pack-row {
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 0 14px;
    border-radius: 10px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.pack-row span {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.pack-row strong {
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
}

.quick-actions {
    margin-bottom: 80px;
    padding: 32px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: center;
    gap: 32px;
}

.quick-actions h2 {
    max-width: 720px;
    margin-bottom: 0;
}

.action-list {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 10px;
}

@media (max-width: 1100px) {
    .workspace-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 900px) {
    .workspace-hero,
    .quick-actions {
        grid-template-columns: 1fr;
    }

    .workspace-hero {
        min-height: auto;
        padding-top: 56px;
    }

    .action-list {
        justify-content: flex-start;
    }
}

@media (max-width: 640px) {
    .metrics-row,
    .workspace-grid {
        grid-template-columns: 1fr;
    }

    .feature-panel-large {
        grid-column: span 1;
    }

    .hero-copy h1 {
        font-size: clamp(38px, 14vw, 58px);
    }
}
</style>
