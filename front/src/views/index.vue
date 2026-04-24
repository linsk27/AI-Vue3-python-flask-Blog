<template>
    <div class="home-page">
        <section class="hero-section">
            <div class="hero-copy">
                <span class="eyebrow">AI-native developer blog</span>
                <h1>智汇博客</h1>
                <p>
                    一个面向开发者的知识创作空间。把文章、AI 摘要、阅读上下文和个人作品管理放在同一个干净工作台里。
                </p>
                <div class="hero-actions">
                    <router-link to="/essays" class="primary-action">浏览文章</router-link>
                    <router-link to="/ai-center" class="secondary-action">打开 AI 中心</router-link>
                </div>
            </div>

            <div class="console-card" aria-label="平台预览">
                <div class="console-topbar">
                    <span></span>
                    <span></span>
                    <span></span>
                    <strong>knowledge.run</strong>
                </div>
                <div class="console-body">
                    <div class="pipeline">
                        <div v-for="step in workflow" :key="step.name" class="pipeline-step">
                            <span class="step-dot" :style="{ background: step.color }"></span>
                            <span class="step-label" :style="{ color: step.color }">{{ step.name }}</span>
                            <strong>{{ step.title }}</strong>
                        </div>
                    </div>
                    <div class="terminal">
                        <p><span>$</span> summarize latest/vue-performance.md</p>
                        <p class="muted">AI context loaded · 18 notes indexed</p>
                        <p><span>→</span> Ship a sharper article in 42s</p>
                    </div>
                </div>
            </div>
        </section>

        <section class="metrics-row" aria-label="平台能力">
            <article v-for="metric in metrics" :key="metric.label" class="metric-card">
                <strong>{{ metric.value }}</strong>
                <span>{{ metric.label }}</span>
            </article>
        </section>

        <section class="section-block">
            <div class="section-heading">
                <span class="eyebrow">Workflow</span>
                <h2>从阅读到创作，保持同一种节奏。</h2>
            </div>
            <div class="feature-grid">
                <article v-for="feature in features" :key="feature.title" class="feature-card">
                    <span class="feature-index">{{ feature.index }}</span>
                    <h3>{{ feature.title }}</h3>
                    <p>{{ feature.description }}</p>
                </article>
            </div>
        </section>

        <section class="section-block">
            <div class="section-heading inline">
                <div>
                    <span class="eyebrow">Selected writing</span>
                    <h2>精选内容</h2>
                </div>
                <router-link to="/essays" class="text-link">查看全部</router-link>
            </div>
            <div class="case-grid">
                <article v-for="caseItem in featuredCases" :key="caseItem.title" class="case-card">
                    <span class="case-category">{{ caseItem.category }}</span>
                    <h3>{{ caseItem.title }}</h3>
                    <p>{{ caseItem.description }}</p>
                    <div class="case-tags">
                        <span v-for="tag in caseItem.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <router-link :to="caseItem.link" class="card-link">阅读全文</router-link>
                </article>
            </div>
        </section>

        <section class="cta-section">
            <span class="eyebrow">Start writing</span>
            <h2>把零散想法变成可沉淀的技术资产。</h2>
            <router-link to="/essays/write" class="primary-action">写一篇文章</router-link>
        </section>
    </div>
</template>

<script setup lang="ts">
const workflow = [
    { name: 'Develop', title: '整理上下文', color: '#0a72ef' },
    { name: 'Preview', title: 'AI 生成摘要', color: '#de1d8d' },
    { name: 'Ship', title: '发布文章', color: '#ff5b4f' }
]

const metrics = [
    { value: 'Vue 3', label: '前端体验' },
    { value: 'Flask', label: '内容接口' },
    { value: 'AI', label: '阅读与创作辅助' }
]

const features = [
    {
        index: '01',
        title: '文章库',
        description: '用清晰的标签、列表和搜索组织技术内容，减少读者在信息之间来回切换的成本。'
    },
    {
        index: '02',
        title: 'AI 中心',
        description: '面向摘要、问答和上下文解释的智能入口，让阅读不只停留在浏览。'
    },
    {
        index: '03',
        title: '创作工作台',
        description: '保留写作、作品、喜欢和个人数据入口，让知识生产有完整闭环。'
    }
]

const featuredCases = [
    {
        title: 'Vue3 性能优化实战',
        category: 'Frontend',
        description: '从虚拟列表、组件缓存到按需加载，梳理大型前端页面的性能优化路径。',
        tags: ['Vue3', 'Performance', 'Practice'],
        link: '/essays/vue2-vs-vue3'
    },
    {
        title: 'CSS 伪元素高级用法',
        category: 'UI Engineering',
        description: '用更少 DOM 构建状态、装饰和交互细节，让页面保持轻盈。',
        tags: ['CSS', 'UI', 'Detail'],
        link: '/essays/pseudo-elements'
    },
    {
        title: '虚拟列表实现原理',
        category: 'Architecture',
        description: '解析长列表渲染的窗口化策略，找到体验和性能之间的平衡点。',
        tags: ['Virtual List', 'Render', 'UX'],
        link: '/performance'
    }
]
</script>

<style scoped>
.home-page {
    width: 100%;
    background: var(--page-bg);
    color: var(--text-primary);
}

.hero-section {
    max-width: 1200px;
    min-height: calc(100vh - 96px);
    margin: 0 auto;
    padding: 96px 16px 56px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(360px, 520px);
    align-items: center;
    gap: 48px;
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

.hero-copy h1 {
    margin: 18px 0 20px;
    color: var(--text-primary);
    font-size: clamp(48px, 8vw, 88px);
    font-weight: 600;
    line-height: 0.96;
    letter-spacing: -2.4px;
}

.hero-copy p {
    max-width: 620px;
    margin: 0;
    color: var(--text-secondary);
    font-size: 20px;
    line-height: 1.8;
}

.hero-actions {
    margin-top: 32px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.primary-action,
.secondary-action,
.text-link,
.card-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 40px;
    padding: 0 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
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
.text-link,
.card-link {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.secondary-action:hover,
.text-link:hover,
.card-link:hover {
    background: var(--surface-hover);
}

.console-card {
    border-radius: 12px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
    overflow: hidden;
}

.console-topbar {
    height: 42px;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 14px;
    box-shadow: var(--ring);
}

.console-topbar span {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #ebebeb;
}

.console-topbar strong {
    margin-left: auto;
    color: var(--text-muted);
    font-family: "Geist Mono", ui-monospace, monospace;
    font-size: 12px;
    font-weight: 500;
}

.console-body {
    padding: 24px;
}

.pipeline {
    display: grid;
    gap: 12px;
}

.pipeline-step {
    min-height: 72px;
    display: grid;
    grid-template-columns: 12px 92px 1fr;
    align-items: center;
    gap: 14px;
    padding: 0 14px;
    border-radius: 8px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.step-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.step-label {
    font-family: "Geist Mono", ui-monospace, monospace;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

.pipeline-step strong {
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.32px;
}

.terminal {
    margin-top: 16px;
    padding: 18px;
    border-radius: 8px;
    color: var(--button-fg);
    background: var(--button-bg);
    font-family: "Geist Mono", ui-monospace, monospace;
    font-size: 13px;
    line-height: 1.65;
}

.terminal p {
    margin: 0;
}

.terminal span {
    color: #0a72ef;
}

.terminal .muted {
    color: #a3a3a3;
}

.metrics-row,
.section-block {
    max-width: 1200px;
    margin: 0 auto;
    padding: 56px 16px;
}

.metrics-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    padding-top: 0;
}

.metric-card,
.feature-card,
.case-card,
.cta-section {
    background: var(--surface);
    border-radius: 8px;
    box-shadow: var(--card-shadow);
}

.metric-card {
    min-height: 128px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.metric-card strong {
    font-size: 40px;
    font-weight: 600;
    line-height: 1;
    letter-spacing: -2.4px;
}

.metric-card span {
    color: var(--text-secondary);
    font-size: 14px;
}

.section-heading {
    max-width: 760px;
    margin-bottom: 32px;
}

.section-heading.inline {
    max-width: none;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
}

.section-heading h2,
.cta-section h2 {
    margin: 14px 0 0;
    color: var(--text-primary);
    font-size: clamp(32px, 5vw, 48px);
    font-weight: 600;
    line-height: 1.08;
    letter-spacing: -2.4px;
}

.feature-grid,
.case-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.feature-card,
.case-card {
    padding: 24px;
}

.feature-index {
    font-family: "Geist Mono", ui-monospace, monospace;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 500;
}

.feature-card h3,
.case-card h3 {
    margin: 18px 0 10px;
    color: var(--text-primary);
    font-size: 24px;
    font-weight: 600;
    line-height: 1.25;
    letter-spacing: -0.96px;
}

.feature-card p,
.case-card p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 15px;
    line-height: 1.7;
}

.case-category,
.case-tags span {
    display: inline-flex;
    align-items: center;
    height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 500;
}

.case-tags {
    margin: 18px 0;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.card-link {
    width: fit-content;
}

.cta-section {
    max-width: 1200px;
    margin: 56px auto 80px;
    padding: 48px 16px;
    text-align: center;
}

.cta-section h2 {
    max-width: 720px;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 28px;
}

@media (max-width: 980px) {
    .hero-section {
        grid-template-columns: 1fr;
        min-height: auto;
        padding-top: 72px;
    }

    .console-card {
        max-width: 640px;
    }

    .feature-grid,
    .case-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 680px) {
    .hero-section,
    .metrics-row,
    .section-block {
        padding-left: 12px;
        padding-right: 12px;
    }

    .metrics-row {
        grid-template-columns: 1fr;
    }

    .section-heading.inline {
        align-items: flex-start;
        flex-direction: column;
    }

    .hero-copy h1 {
        letter-spacing: -1.6px;
    }

    .hero-copy p {
        font-size: 17px;
        line-height: 1.7;
    }

    .pipeline-step {
        grid-template-columns: 12px 1fr;
    }

    .pipeline-step strong {
        grid-column: 2;
    }
}
</style>
