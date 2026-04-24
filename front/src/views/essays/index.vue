<template>
    <div class="essays-page">
        <section class="library-hero">
            <div>
                <span class="eyebrow">Knowledge library</span>
                <h1>文章库</h1>
                <p>探索精选技术文章、AI 创作实践与工程经验沉淀，快速找到值得深入阅读的内容。</p>
            </div>
            <div class="hero-actions">
                <div class="layout-switch" aria-label="切换布局">
                    <button
                        class="layout-btn"
                        :class="{ active: layoutMode === 'grid' }"
                        type="button"
                        title="网格视图"
                        @click="layoutMode = 'grid'"
                    >
                        <Grid class="icon" />
                    </button>
                    <button
                        class="layout-btn"
                        :class="{ active: layoutMode === 'list' }"
                        type="button"
                        title="列表视图"
                        @click="layoutMode = 'list'"
                    >
                        <List class="icon" />
                    </button>
                </div>
                <button class="write-btn" type="button" @click="goToWrite">
                    <EditPen class="icon" />
                    <span>写文章</span>
                </button>
            </div>
        </section>

        <section class="search-panel">
            <Search class="search-icon" />
            <input v-model="search" class="essay-search" type="search" placeholder="搜索标题、摘要或标签..." />
            <span class="search-count">{{ filteredArticles.length }} 篇</span>
        </section>

        <section class="tags-section" v-if="allTags.length > 0">
            <div class="tags-header">
                <span>热门标签</span>
                <button v-if="selectedTags.length > 0" type="button" @click="clearSelectedTags">清除筛选</button>
            </div>
            <div class="tags-list">
                <button
                    v-for="tag in allTags"
                    :key="tag"
                    class="filter-tag"
                    :class="{ active: selectedTags.includes(tag) }"
                    type="button"
                    @click="toggleTag(tag)"
                >
                    {{ tag }}
                </button>
            </div>
        </section>

        <section
            v-if="filteredArticles.length > 0"
            class="article-results"
            :class="layoutMode === 'grid' ? 'essays-grid' : 'essays-list'"
        >
            <article
                v-for="article in filteredArticles"
                :key="article.id"
                class="essay-card"
                tabindex="0"
                role="button"
                @click="goToArticle(article.id)"
                @keydown.enter="goToArticle(article.id)"
            >
                <div class="card-main">
                    <div class="card-kicker">
                        <span>{{ article.category || 'Article' }}</span>
                        <span>{{ formatDate(article.created_at) }}</span>
                    </div>
                    <h2>{{ article.title }}</h2>
                    <p>{{ article.summary || '精选技术内容，适合继续深入阅读。' }}</p>
                </div>
                <div class="card-footer">
                    <div class="card-tags">
                        <span v-for="tag in article.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <div class="card-meta">
                        <span v-if="article.author_name">{{ article.author_name }}</span>
                        <span>{{ article.views || 0 }} views</span>
                        <span>{{ article.likes || 0 }} likes</span>
                    </div>
                </div>
            </article>
        </section>

        <section class="no-results" v-else>
            <Search class="empty-icon" />
            <h2>没有找到相关文章</h2>
            <p>换一个关键词，或者清除标签筛选后再试。</p>
        </section>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { EditPen, Grid, List, Search } from '@element-plus/icons-vue'
import articleApi from '@/api/modules/article'
import { IArticle } from '@/api/modules/article/interface'
import { useElMessage } from '@/hooks/useMessage'
import { articles as localArticles } from './articles/index'
import { useCacheStore } from '@/store/cache'

const router = useRouter()
const { message } = useElMessage()
const cacheStore = useCacheStore()

const search = ref('')
const selectedTags = ref<string[]>([])
const articles = ref<IArticle[]>([])
const loading = ref(false)
const layoutMode = ref<'grid' | 'list'>('list')

const formatDate = (dateStr: string) => {
    if (!dateStr) return '精选文章'
    const date = new Date(dateStr)
    if (Number.isNaN(date.getTime())) return '精选文章'
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    })
}

const allTags = computed(() => {
    const tagsSet = new Set<string>()
    articles.value.forEach(article => {
        article.tags?.forEach(tag => tagsSet.add(tag))
    })
    return Array.from(tagsSet).slice(0, 18)
})

const processedLocalArticles = localArticles.map(article => ({
    ...article,
    id: article.id,
    tags: [...(article.tags || []), '精选'],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    author_name: '智汇编辑部',
    views: 0,
    likes: 0,
    content: ''
}))

const fetchArticles = async (forceRefresh = false) => {
    if (!forceRefresh && !search.value) {
        const cachedArticles = cacheStore.getCache<IArticle[]>('articles')
        if (cachedArticles) {
            articles.value = [...processedLocalArticles, ...cachedArticles]
            return
        }
    }

    loading.value = true
    try {
        const params: any = {}
        if (search.value) params.search = search.value

        const res = await articleApi.getList(params)
        const backendArticles = Array.isArray(res) ? res : (res as any).data || []

        let filteredLocal = processedLocalArticles
        if (search.value) {
            const lowerSearch = search.value.toLowerCase()
            filteredLocal = processedLocalArticles.filter(a =>
                a.title.toLowerCase().includes(lowerSearch) ||
                a.summary.toLowerCase().includes(lowerSearch) ||
                a.tags.some(t => t.toLowerCase().includes(lowerSearch))
            )
        }

        articles.value = [...filteredLocal, ...backendArticles].map(a => ({
            ...a,
            views: a.views || 0,
            likes: a.likes || 0
        }))

        if (!search.value) {
            cacheStore.setCache('articles', backendArticles)
        }
    } catch (error) {
        console.error('Failed to fetch articles:', error)
        articles.value = processedLocalArticles
    } finally {
        loading.value = false
    }
}

let searchTimer: number | undefined
watch(search, () => {
    if (searchTimer) window.clearTimeout(searchTimer)
    searchTimer = window.setTimeout(() => {
        fetchArticles()
    }, 400)
})

onMounted(() => {
    fetchArticles()
})

const filteredArticles = computed(() => {
    return articles.value.filter(article => {
        const isPublished = !article.status || article.status === 'published'
        const matchesTags =
            selectedTags.value.length === 0 ||
            (article.tags && selectedTags.value.every(tag => article.tags?.includes(tag)))
        return isPublished && matchesTags
    })
})

function goToArticle(id: string | number) {
    router.push(`/essays/${id}`)
}

function goToWrite() {
    router.push('/essays/write')
}

function toggleTag(tag: string) {
    const index = selectedTags.value.indexOf(tag)
    if (index > -1) {
        selectedTags.value.splice(index, 1)
    } else {
        selectedTags.value.push(tag)
    }
}

function clearSelectedTags() {
    selectedTags.value = []
}
</script>

<style scoped>
.essays-page {
    width: min(1200px, calc(100vw - 32px));
    min-height: calc(100vh - 160px);
    margin: 0 auto;
    padding: 72px 0 80px;
    color: var(--text-primary);
}

.library-hero {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 32px;
    margin-bottom: 28px;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--badge-bg);
    color: var(--badge-fg);
    font-family: "Geist Mono", ui-monospace, monospace;
    font-size: 12px;
    font-weight: 500;
}

.library-hero h1 {
    margin: 16px 0 12px;
    font-size: clamp(44px, 7vw, 72px);
    font-weight: 600;
    line-height: 0.96;
    letter-spacing: -2.4px;
}

.library-hero p {
    max-width: 620px;
    margin: 0;
    color: var(--text-secondary);
    font-size: 18px;
    line-height: 1.75;
}

.hero-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.layout-switch {
    display: flex;
    gap: 4px;
    padding: 4px;
    border-radius: 8px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.layout-btn,
.write-btn,
.filter-tag,
.tags-header button {
    border: 0;
    font: inherit;
    cursor: pointer;
}

.layout-btn {
    width: 34px;
    height: 34px;
    display: grid;
    place-items: center;
    border-radius: 6px;
    color: var(--text-secondary);
    background: transparent;
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease;
}

.layout-btn:hover,
.layout-btn.active {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.write-btn {
    height: 42px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0 14px;
    border-radius: 6px;
    color: var(--button-fg);
    background: var(--button-bg);
    font-size: 14px;
    font-weight: 500;
    box-shadow: var(--ring);
    transition: background 180ms ease;
}

.write-btn:hover {
    background: var(--button-hover);
}

.icon {
    width: 16px;
    height: 16px;
}

.search-panel {
    height: 58px;
    display: grid;
    grid-template-columns: 20px 1fr auto;
    align-items: center;
    gap: 12px;
    padding: 0 16px;
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.search-icon {
    width: 18px;
    height: 18px;
    color: var(--text-muted);
}

.essay-search {
    width: 100%;
    border: 0;
    outline: 0;
    background: transparent;
    color: var(--text-primary);
    font: inherit;
    font-size: 16px;
}

.essay-search::placeholder {
    color: var(--text-muted);
}

.search-count {
    color: var(--text-secondary);
    font-family: "Geist Mono", ui-monospace, monospace;
    font-size: 12px;
    font-weight: 500;
}

.tags-section {
    margin: 20px 0 32px;
    padding: 18px;
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--ring);
}

.tags-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 12px;
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 600;
}

.tags-header button {
    padding: 0;
    color: var(--badge-fg);
    background: transparent;
    font-size: 14px;
}

.tags-list,
.card-tags,
.card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.filter-tag,
.card-tags span {
    height: 26px;
    display: inline-flex;
    align-items: center;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 500;
    transition: background 180ms ease, color 180ms ease;
}

.filter-tag:hover,
.filter-tag.active {
    color: var(--badge-fg);
    background: var(--badge-bg);
}

.essays-list {
    display: grid;
    gap: 12px;
}

.article-results {
    width: 100%;
    min-height: max(560px, calc(100vh - 360px));
    align-content: start;
    overflow-anchor: none;
}

.essays-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.essay-card {
    min-height: 240px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
    cursor: pointer;
    transition: transform 180ms ease, box-shadow 180ms ease;
}

.essays-list .essay-card {
    min-height: 180px;
}

.essay-card:hover,
.essay-card:focus-visible {
    transform: translateY(-2px);
    box-shadow: rgba(0, 0, 0, 0.12) 0 0 0 1px,
        rgba(0, 0, 0, 0.06) 0 8px 18px -12px;
}

.card-kicker {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    color: var(--text-muted);
    font-family: "Geist Mono", ui-monospace, monospace;
    font-size: 12px;
    font-weight: 500;
}

.essay-card h2 {
    margin: 18px 0 10px;
    color: var(--text-primary);
    font-size: 24px;
    font-weight: 600;
    line-height: 1.25;
    letter-spacing: -0.96px;
}

.essay-card p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 15px;
    line-height: 1.7;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.card-footer {
    margin-top: 24px;
    display: grid;
    gap: 14px;
}

.card-meta {
    color: var(--text-muted);
    font-size: 12px;
}

.no-results {
    margin-top: 32px;
    min-height: 320px;
    display: grid;
    place-items: center;
    text-align: center;
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.empty-icon {
    width: 32px;
    height: 32px;
    color: var(--text-muted);
}

.no-results h2 {
    margin: 14px 0 8px;
    font-size: 24px;
    font-weight: 600;
    letter-spacing: -0.96px;
}

.no-results p {
    margin: 0;
    color: var(--text-secondary);
}

@media (max-width: 960px) {
    .library-hero {
        align-items: flex-start;
        flex-direction: column;
    }

    .essays-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 640px) {
    .essays-page {
        width: calc(100vw - 24px);
        padding: 48px 0 64px;
    }

    .hero-actions {
        width: 100%;
        justify-content: space-between;
    }

    .essays-grid {
        grid-template-columns: 1fr;
    }

    .search-panel {
        grid-template-columns: 20px 1fr;
    }

    .search-count {
        display: none;
    }
}
</style>
