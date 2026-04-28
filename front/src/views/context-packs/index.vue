<template>
    <div class="packs-page">
        <section class="packs-header">
            <div>
                <span class="eyebrow">Context Packs</span>
                <h1>Bundle knowledge into reusable AI context.</h1>
                <p>
                    Context packs group documents, links, notes, and AI conversations into one portable workspace for
                    research, handoff, writing, review, and project debriefs.
                </p>
            </div>
            <button class="primary-button" type="button">
                <Plus class="icon" />
                <span>New Pack</span>
            </button>
        </section>

        <section class="packs-layout">
            <aside class="pack-sidebar">
                <h2>Pack Types</h2>
                <button v-for="type in packTypes" :key="type" type="button" class="type-button">
                    {{ type }}
                </button>
            </aside>

            <main class="pack-grid">
                <article v-for="pack in packs" :key="pack.name" class="pack-card">
                    <div class="pack-card-header">
                        <span>{{ pack.type }}</span>
                        <strong>{{ pack.documents }} docs</strong>
                    </div>
                    <h2>{{ pack.name }}</h2>
                    <p>{{ pack.description }}</p>
                    <div class="pack-tags">
                        <span v-for="tag in pack.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <div class="pack-actions">
                        <button type="button">Ask AI</button>
                        <button type="button">Export</button>
                    </div>
                </article>
            </main>
        </section>

        <section class="roadmap-panel">
            <span class="eyebrow">MVP Roadmap</span>
            <h2>What this page will become next</h2>
            <div class="roadmap-grid">
                <article v-for="item in roadmap" :key="item.title">
                    <strong>{{ item.title }}</strong>
                    <p>{{ item.description }}</p>
                </article>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
import { Plus } from '@element-plus/icons-vue'

const packTypes = ['All Packs', 'Project', 'Research', 'Learning', 'Writing', 'Handoff']

const packs = [
    {
        name: 'Graduation Defense Pack',
        type: 'Project',
        documents: 12,
        description: 'Collect requirements, architecture notes, database design, screenshots, and defense talking points.',
        tags: ['defense', 'architecture', 'resume']
    },
    {
        name: 'Vue 3 Interview Pack',
        type: 'Learning',
        documents: 8,
        description: 'Bundle Composition API notes, reactivity explanations, router patterns, and interview questions.',
        tags: ['vue', 'frontend', 'interview']
    },
    {
        name: 'Flask Backend Refactor Pack',
        type: 'Project',
        documents: 6,
        description: 'Track API decisions, database migrations, auth risks, and AI service integration notes.',
        tags: ['flask', 'api', 'backend']
    }
]

const roadmap = [
    {
        title: 'Pack Builder',
        description: 'Create packs, attach documents, reorder sources, and write pack-level intent.'
    },
    {
        title: 'Pack Insight',
        description: 'Generate summaries, key points, review questions, and project debriefs from a pack.'
    },
    {
        title: 'Pack Chat',
        description: 'Ask AI using only the selected pack context, then save useful answers as documents.'
    }
]
</script>

<style scoped>
.packs-page {
    width: var(--page-width);
    min-height: calc(100vh - 160px);
    margin: 0 auto;
    padding: 72px 0 80px;
    color: var(--text-primary);
}

.packs-header {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: end;
    gap: 32px;
    margin-bottom: 28px;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--badge-bg);
    color: var(--badge-fg);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
}

.packs-header h1 {
    max-width: 900px;
    margin: 16px 0 14px;
    font-size: clamp(42px, 7vw, 76px);
    font-weight: 650;
    line-height: 0.98;
    letter-spacing: 0;
}

.packs-header p {
    max-width: 720px;
    margin: 0;
    color: var(--text-secondary);
    font-size: 18px;
    line-height: 1.75;
}

.primary-button,
.pack-actions button,
.type-button {
    border: 0;
    border-radius: 10px;
    font: inherit;
    font-weight: 600;
    cursor: pointer;
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease;
}

.primary-button {
    min-height: 42px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 0 16px;
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.primary-button:hover {
    background: var(--button-hover);
}

.icon {
    width: 16px;
    height: 16px;
}

.packs-layout {
    display: grid;
    grid-template-columns: 220px minmax(0, 1fr);
    gap: 12px;
}

.pack-sidebar,
.pack-card,
.roadmap-panel {
    background: var(--surface);
    border-radius: 12px;
    box-shadow: var(--card-shadow);
}

.pack-sidebar {
    align-self: start;
    padding: 18px;
    position: sticky;
    top: 104px;
}

.pack-sidebar h2 {
    margin: 0 0 12px;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.type-button {
    width: 100%;
    min-height: 36px;
    margin-bottom: 8px;
    padding: 0 10px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    text-align: left;
    box-shadow: var(--ring);
}

.type-button:hover {
    color: var(--text-primary);
    background: var(--surface-hover);
}

.pack-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.pack-card {
    min-height: 300px;
    padding: 22px;
    display: flex;
    flex-direction: column;
}

.pack-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
}

.pack-card h2 {
    margin: 18px 0 10px;
    font-size: 24px;
    font-weight: 650;
    line-height: 1.2;
}

.pack-card p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 15px;
    line-height: 1.7;
}

.pack-tags {
    margin-top: 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.pack-tags span {
    min-height: 26px;
    display: inline-flex;
    align-items: center;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 600;
}

.pack-actions {
    margin-top: auto;
    padding-top: 24px;
    display: flex;
    gap: 8px;
}

.pack-actions button {
    min-height: 34px;
    padding: 0 12px;
    color: var(--text-primary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.pack-actions button:hover {
    background: var(--surface-hover);
}

.roadmap-panel {
    margin-top: 56px;
    padding: 28px;
}

.roadmap-panel h2 {
    margin: 14px 0 22px;
    font-size: clamp(30px, 5vw, 44px);
    font-weight: 650;
    line-height: 1.08;
}

.roadmap-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.roadmap-grid article {
    padding: 18px;
    border-radius: 12px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.roadmap-grid strong {
    display: block;
    margin-bottom: 8px;
    font-size: 16px;
}

.roadmap-grid p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.6;
}

@media (max-width: 1100px) {
    .pack-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 820px) {
    .packs-header,
    .packs-layout,
    .roadmap-grid {
        grid-template-columns: 1fr;
    }

    .pack-sidebar {
        position: static;
    }
}

@media (max-width: 560px) {
    .pack-grid {
        grid-template-columns: 1fr;
    }
}
</style>
