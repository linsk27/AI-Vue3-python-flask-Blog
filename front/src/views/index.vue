<template>
    <main class="home-page">
        <section class="hero-section" aria-labelledby="home-title">
            <div class="hero-copy">
                <span class="eyebrow">知镜 AI 知识写作</span>
                <h1 id="home-title">资料变成可引用的初稿。</h1>
                <p>
                    收集网页、笔记、论文和项目材料，让 AI 只基于命中的资料起草内容。
                    来源保留，结构可改，写作过程更稳。
                </p>

                <div class="hero-actions">
                    <router-link to="/context-packs" class="primary-action">
                        <CollectionTag class="button-icon" />
                        <span>进入上下文包</span>
                    </router-link>
                    <router-link to="/ai-center" class="secondary-action">
                        <DataAnalysis class="button-icon" />
                        <span>打开 AI 工作台</span>
                    </router-link>
                </div>
            </div>

            <aside class="hero-panel" aria-label="工作流概览">
                <div class="panel-header">
                    <span>工作流</span>
                    <strong>先找依据</strong>
                </div>
                <div class="panel-flow">
                    <span>资料</span>
                    <i></i>
                    <span>依据</span>
                    <i></i>
                    <span>初稿</span>
                </div>
                <p>每一次生成都先回到资料来源，而不是直接让模型自由发挥。</p>
            </aside>
        </section>

        <section v-if="hasWorkspaceData" class="metric-section" aria-label="工作区数据">
            <article v-for="metric in metrics" :key="metric.label" class="metric-item">
                <strong>{{ metric.value }}</strong>
                <span>{{ metric.label }}</span>
            </article>
        </section>

        <section class="section-block" aria-labelledby="flow-title">
            <div class="section-heading">
                <h2 id="flow-title">三个步骤，不打扰写作。</h2>
            </div>

            <div class="flow-grid">
                <article v-for="(step, index) in productSteps" :key="step.title" class="flow-item">
                    <span class="step-index">0{{ index + 1 }}</span>
                    <component :is="step.icon" class="item-icon" />
                    <h3>{{ step.title }}</h3>
                    <p>{{ step.description }}</p>
                </article>
            </div>
        </section>

        <section class="section-block two-column" aria-labelledby="value-title">
            <div class="section-heading">
                <h2 id="value-title">让 AI 有依据，也有边界。</h2>
            </div>

            <div class="value-list">
                <article v-for="item in values" :key="item.title" class="value-item">
                    <h3>{{ item.title }}</h3>
                    <p>{{ item.description }}</p>
                </article>
            </div>
        </section>

        <section class="section-block handoff-section" aria-labelledby="handoff-title">
            <div>
                <h2 id="handoff-title">生成后继续编辑，而不是结束。</h2>
                <p>
                    AI 起草只是第一步。你可以继续调整标题、补充证据、重排结构，
                    把初稿整理成文章、报告、学习笔记或发布内容。
                </p>
            </div>
            <router-link to="/essays/write" class="text-action">
                <EditPen class="button-icon" />
                <span>进入写作编辑器</span>
            </router-link>
        </section>
    </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
    CollectionTag,
    DataAnalysis,
    EditPen,
    Files,
    Notebook,
    Search
} from '@element-plus/icons-vue'
import articleApi from '@/api/modules/article'
import type { IArticle } from '@/api/modules/article/interface'
import contextPackApi, { type ContextPack, type ContextPackStats } from '@/api/modules/contextPacks'

const articles = ref<IArticle[]>([])
const packs = ref<ContextPack[]>([])
const stats = ref<ContextPackStats | null>(null)

const sourceCount = computed(() => packs.value.reduce((total, pack) => total + (pack.sources?.length ?? 0), 0))
const metrics = computed(() => [
    { value: articles.value.length, label: '知识文档' },
    { value: stats.value?.packs ?? packs.value.length, label: '上下文包' },
    { value: stats.value?.sources ?? sourceCount.value, label: '资料来源' }
])
const hasWorkspaceData = computed(() => metrics.value.some(metric => Number(metric.value) > 0))

const productSteps = [
    {
        title: '整理资料',
        description: '把网页、笔记、论文摘录和项目记录放进同一个资料包。',
        icon: Files
    },
    {
        title: '查找依据',
        description: '提问前先从资料里找相关片段，减少凭空回答。',
        icon: Search
    },
    {
        title: '生成初稿',
        description: '把依据交给 AI 起草，再进入编辑器继续修改。',
        icon: Notebook
    }
]

const values = [
    {
        title: '资料先行',
        description: '写作不从空白开始，先把可引用的材料沉淀下来。'
    },
    {
        title: '来源可追溯',
        description: '重要结论能够回到原始资料，便于复核和补充。'
    },
    {
        title: '前台专注创作',
        description: '页面只保留资料、检索、起草和编辑，少跳转，少解释。'
    },
    {
        title: '持续沉淀',
        description: '每次写作都会留下资料和草稿，下次还能继续复用。'
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
    } catch {
        articles.value = []
        packs.value = []
        stats.value = null
    }
})
</script>

<style scoped>
/* Hallmark · macrostructure: product workspace · tone: warm white minimal · anchor hue: champagne */
.home-page {
    --home-bg: var(--page-bg);
    --home-surface: var(--surface);
    --home-surface-soft: var(--surface-subtle);
    --home-line: var(--line);
    --home-line-strong: color-mix(in oklch, var(--color-rule-strong) 74%, transparent);
    --home-text: var(--text-primary);
    --home-muted: color-mix(in oklch, var(--text-secondary) 82%, transparent);
    --home-faint: color-mix(in oklch, var(--text-secondary) 48%, transparent);
    --home-accent: var(--color-accent);
    --home-ink: var(--text-inverse);

    min-height: 100vh;
    color: var(--home-text);
    background: transparent;
    overflow-x: clip;
}

.hero-section,
.metric-section,
.section-block {
    width: var(--page-width);
    margin: 0 auto;
}

.hero-section {
    min-height: calc(100svh - 80px);
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(360px, 0.72fr);
    align-items: center;
    gap: clamp(42px, 7vw, 92px);
    padding: 86px 0 96px;
}

.hero-copy {
    max-width: 820px;
}

.eyebrow {
    width: fit-content;
    min-height: 28px;
    display: inline-flex;
    align-items: center;
    border: 1px solid var(--home-line);
    border-radius: 999px;
    padding: 0 11px;
    color: var(--home-accent);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

h1,
h2,
h3,
p {
    margin: 0;
}

.hero-copy h1 {
    max-width: 800px;
    margin-top: 22px;
    font-family: var(--font-serif);
    font-size: clamp(54px, 7.2vw, 96px);
    font-weight: 600;
    line-height: 1.02;
    letter-spacing: 0;
    text-wrap: balance;
}

.hero-copy p {
    max-width: 600px;
    margin-top: 28px;
    color: var(--home-muted);
    font-size: 18px;
    line-height: 1.86;
}

.hero-actions {
    margin-top: 38px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.primary-action,
.secondary-action,
.text-action {
    min-height: 48px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border-radius: 12px;
    padding: 0 18px;
    font-weight: 800;
}

.primary-action {
    color: var(--home-ink);
    background: var(--home-text);
    box-shadow: color-mix(in oklch, var(--home-text) 16%, transparent) 0 18px 38px -28px;
}

.secondary-action,
.text-action {
    color: var(--home-text);
    border: 1px solid var(--home-line-strong);
    background: color-mix(in oklch, var(--home-surface) 72%, transparent);
}

.button-icon,
.item-icon {
    width: 18px;
    height: 18px;
}

.hero-panel {
    min-height: 420px;
    display: grid;
    align-content: space-between;
    border: 1px solid var(--home-line);
    border-radius: 28px;
    padding: 26px;
    background: var(--home-surface);
    box-shadow: color-mix(in oklch, var(--home-text) 9%, transparent) 0 24px 70px -42px;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    color: var(--home-faint);
    font-family: var(--font-mono);
    font-size: 12px;
    text-transform: uppercase;
}

.panel-header strong {
    color: var(--home-accent);
}

.panel-flow {
    display: grid;
    gap: 14px;
    padding: 42px 0;
}

.panel-flow span {
    min-height: 58px;
    display: flex;
    align-items: center;
    border: 1px solid var(--home-line);
    border-radius: 18px;
    padding: 0 18px;
    color: var(--home-text);
    background: var(--home-surface-soft);
    font-size: 22px;
    font-weight: 700;
}

.panel-flow i {
    width: 1px;
    height: 28px;
    margin-left: 28px;
    background: var(--home-line-strong);
}

.hero-panel p {
    color: var(--home-muted);
    line-height: 1.76;
}

.metric-section {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    border-top: 1px solid var(--home-line);
    border-bottom: 1px solid var(--home-line);
    background: color-mix(in oklch, var(--home-surface) 62%, transparent);
}

.metric-item {
    min-height: 140px;
    display: grid;
    align-content: center;
    gap: 10px;
    padding: 24px;
}

.metric-item + .metric-item {
    border-left: 1px solid var(--home-line);
}

.metric-item strong {
    font-size: 42px;
    line-height: 1;
}

.metric-item span {
    color: var(--home-muted);
}

.section-block {
    padding: 110px 0;
    border-bottom: 1px solid var(--home-line);
}

.section-heading {
    display: grid;
    gap: 18px;
}

.section-heading h2,
.handoff-section h2 {
    max-width: 760px;
    font-family: var(--font-serif);
    font-size: clamp(42px, 5.6vw, 76px);
    font-weight: 600;
    line-height: 1;
    letter-spacing: 0;
    text-wrap: balance;
}

.flow-grid {
    margin-top: 44px;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1px;
    background: var(--home-line);
    border: 1px solid var(--home-line);
    border-radius: 24px;
    overflow: hidden;
    box-shadow: color-mix(in oklch, var(--home-text) 8%, transparent) 0 20px 56px -38px;
}

.flow-item {
    min-height: 300px;
    display: grid;
    align-content: start;
    gap: 18px;
    padding: 28px;
    background: var(--home-surface);
}

.step-index {
    color: var(--home-faint);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 800;
}

.item-icon {
    width: 36px;
    height: 36px;
    color: var(--home-accent);
}

.flow-item h3,
.value-item h3 {
    font-size: 28px;
    line-height: 1.12;
}

.flow-item p,
.value-item p,
.handoff-section p {
    color: var(--home-muted);
    line-height: 1.78;
}

.two-column {
    display: grid;
    grid-template-columns: minmax(0, 0.86fr) minmax(0, 1.14fr);
    gap: clamp(42px, 7vw, 92px);
}

.value-list {
    display: grid;
    gap: 1px;
    background: var(--home-line);
    border: 1px solid var(--home-line);
    border-radius: 24px;
    overflow: hidden;
    box-shadow: color-mix(in oklch, var(--home-text) 8%, transparent) 0 20px 56px -38px;
}

.value-item {
    display: grid;
    gap: 10px;
    padding: 26px;
    background: var(--home-surface);
}

.handoff-section {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 28px;
    padding-bottom: 130px;
}

.handoff-section p {
    max-width: 620px;
    margin-top: 22px;
    font-size: 17px;
}

.text-action {
    flex: 0 0 auto;
}

@media (max-width: 980px) {
    .hero-section,
    .two-column,
    .handoff-section {
        grid-template-columns: 1fr;
    }

    .handoff-section {
        display: grid;
        align-items: start;
    }
}

@media (max-width: 720px) {
    .hero-section {
        min-height: auto;
        padding: 68px 0 76px;
    }

    .hero-copy h1 {
        font-size: clamp(46px, 13vw, 62px);
    }

    .hero-copy p {
        font-size: 16px;
        line-height: 1.74;
    }

    .hero-actions {
        display: grid;
    }

    .primary-action,
    .secondary-action,
    .text-action {
        width: 100%;
    }

    .hero-panel {
        min-height: 360px;
    }

    .metric-section,
    .flow-grid {
        grid-template-columns: 1fr;
    }

    .metric-item + .metric-item {
        border-left: 0;
        border-top: 1px solid var(--home-line);
    }

    .section-block {
        padding: 74px 0;
    }

    .section-heading h2,
    .handoff-section h2 {
        font-size: clamp(36px, 11vw, 52px);
    }

    .flow-item {
        min-height: 220px;
    }
}
</style>
