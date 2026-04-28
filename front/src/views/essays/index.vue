<template>
    <div class="knowledge-page">
        <section class="library-hero">
            <div>
                <span class="eyebrow">Knowledge Base</span>
                <h1>Documents that can become AI context.</h1>
                <p>
                    Collect technical notes, project records, papers, tutorials, and source materials. Search them,
                    filter them, and turn the right set into context packs when you need deeper AI help.
                </p>
            </div>
            <div class="hero-actions">
                <div class="layout-switch" aria-label="Switch layout">
                    <button
                        class="layout-btn"
                        :class="{ active: layoutMode === 'grid' }"
                        type="button"
                        title="Grid view"
                        @click="layoutMode = 'grid'"
                    >
                        <Grid class="icon" />
                    </button>
                    <button
                        class="layout-btn"
                        :class="{ active: layoutMode === 'list' }"
                        type="button"
                        title="List view"
                        @click="layoutMode = 'list'"
                    >
                        <List class="icon" />
                    </button>
                </div>
                <button class="write-btn" type="button" @click="goToWrite">
                    <EditPen class="icon" />
                    <span>New Document</span>
                </button>
            </div>
        </section>

        <section class="search-panel">
            <Search class="search-icon" />
            <input v-model="search" class="knowledge-search" type="search" placeholder="Search title, summary, or tags..." />
            <span class="search-count">{{ filteredArticles.length }} docs</span>
        </section>

        <section class="filter-panel">
            <div class="filter-group">
                <span>Type</span>
                <div class="filter-options">
                    <button
                        v-for="type in documentTypes"
                        :key="type.value"
                        class="filter-chip"
                        :class="{ active: selectedType === type.value }"
                        type="button"
                        @click="selectedType = type.value"
                    >
                        {{ type.label }}
                    </button>
                </div>
            </div>
            <div class="filter-group">
                <span>Status</span>
                <div class="filter-options">
                    <button
                        v-for="statusItem in documentStatuses"
                        :key="statusItem.value"
                        class="filter-chip"
                        :class="{ active: selectedStatus === statusItem.value }"
                        type="button"
                        @click="selectedStatus = statusItem.value"
                    >
                        {{ statusItem.label }}
                    </button>
                </div>
            </div>
        </section>

        <section class="tags-section" v-if="allTags.length > 0">
            <div class="tags-header">
                <span>Knowledge Tags</span>
                <button v-if="selectedTags.length > 0" type="button" @click="clearSelectedTags">Clear tags</button>
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
            class="document-results"
            :class="layoutMode === 'grid' ? 'knowledge-grid' : 'knowledge-list'"
        >
            <article
                v-for="article in filteredArticles"
                :key="article.id"
                class="document-card"
                tabindex="0"
                role="button"
                @click="goToArticle(article.id)"
                @keydown.enter="goToArticle(article.id)"
            >
                <div class="card-main">
                    <div class="card-kicker">
                        <span>{{ getDocumentTypeLabel(article) }}</span>
                        <span>{{ getDocumentStatusLabel(article) }}</span>
                    </div>
                    <h2>{{ article.title }}</h2>
                    <p>{{ article.summary || 'A knowledge document ready to be summarized, reused, and packed into context.' }}</p>
                </div>
                <div class="card-footer">
                    <div class="card-tags">
                        <span v-for="tag in article.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <div class="card-meta">
                        <span v-if="article.author_name">{{ article.author_name }}</span>
                        <span>{{ formatDate(article.updated_at || article.created_at) }}</span>
                        <span>{{ article.views || 0 }} views</span>
                        <span>{{ article.likes || 0 }} favorites</span>
                    </div>
                </div>
            </article>
        </section>

        <section class="no-results" v-else>
            <Search class="empty-icon" />
            <h2>No documents found</h2>
            <p>Try a different keyword, clear filters, or create a new document.</p>
            <button class="write-btn" type="button" @click="goToWrite">
                <EditPen class="icon" />
                <span>New Document</span>
            </button>
        </section>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { EditPen, Grid, List, Search } from '@element-plus/icons-vue'
import articleApi from '@/api/modules/article'
import { IArticle } from '@/api/modules/article/interface'
import { articles as localArticles } from './articles/index'
import { useCacheStore } from '@/store/cache'

const router = useRouter()
const cacheStore = useCacheStore()

const search = ref('')
const selectedTags = ref<string[]>([])
const selectedType = ref('all')
const selectedStatus = ref('all')
const articles = ref<IArticle[]>([])
const loading = ref(false)
const layoutMode = ref<'grid' | 'list'>('list')

const documentTypes = [
    { value: 'all', label: 'All' },
    { value: 'note', label: 'Note' },
    { value: 'technical-doc', label: 'Technical Doc' },
    { value: 'tutorial', label: 'Tutorial' },
    { value: 'project-record', label: 'Project Record' },
    { value: 'paper', label: 'Paper' },
    { value: 'idea', label: 'Idea' }
]

const documentStatuses = [
    { value: 'all', label: 'All' },
    { value: 'published', label: 'Published' },
    { value: 'draft', label: 'Draft' },
    { value: 'organized', label: 'Organized' },
    { value: 'reviewing', label: 'Reviewing' },
    { value: 'archived', label: 'Archived' }
]

const formatDate = (dateStr: string) => {
    if (!dateStr) return 'Recently updated'
    const date = new Date(dateStr)
    if (Number.isNaN(date.getTime())) return 'Recently updated'
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit'
    })
}

const slugifyType = (value?: string) => {
    if (!value) return 'note'
    const normalized = value.toLowerCase().replace(/_/g, '-').replace(/\s+/g, '-')
    const categoryMap: Record<string, string> = {
        frontend: 'technical-doc',
        backend: 'technical-doc',
        database: 'technical-doc',
        algorithm: 'technical-doc',
        devops: 'technical-doc',
        architecture: 'project-record',
        ai: 'technical-doc',
        other: 'note'
    }
    return categoryMap[normalized] || normalized
}

const getDocumentType = (article: IArticle) => slugifyType(article.resource_type || article.category)
const getDocumentStatus = (article: IArticle) => article.document_status || article.status || 'published'

const getDocumentTypeLabel = (article: IArticle) => {
    const type = getDocumentType(article)
    return documentTypes.find(item => item.value === type)?.label || 'Document'
}

const getDocumentStatusLabel = (article: IArticle) => {
    const status = getDocumentStatus(article)
    return documentStatuses.find(item => item.value === status)?.label || status
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
    tags: [...(article.tags || []), 'example'],
    resource_type: 'technical-doc',
    document_status: 'organized',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    author_name: 'ContextForge Team',
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
        console.error('Failed to fetch documents:', error)
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
        const status = getDocumentStatus(article)
        const isVisible = status !== 'archived' || selectedStatus.value === 'archived'
        const matchesType = selectedType.value === 'all' || getDocumentType(article) === selectedType.value
        const matchesStatus = selectedStatus.value === 'all' || status === selectedStatus.value
        const matchesTags =
            selectedTags.value.length === 0 ||
            (article.tags && selectedTags.value.every(tag => article.tags?.includes(tag)))
        return isVisible && matchesType && matchesStatus && matchesTags
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
.knowledge-page {
    width: var(--page-width);
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
    min-height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--badge-bg);
    color: var(--badge-fg);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
}

.library-hero h1 {
    max-width: 880px;
    margin: 16px 0 12px;
    font-size: clamp(44px, 7vw, 72px);
    font-weight: 650;
    line-height: 0.98;
    letter-spacing: 0;
}

.library-hero p {
    max-width: 720px;
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
    border-radius: 12px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.layout-btn,
.write-btn,
.filter-tag,
.filter-chip,
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
    border-radius: 10px;
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
    min-height: 42px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 0 14px;
    border-radius: 10px;
    color: var(--button-fg);
    background: var(--button-bg);
    font-size: 14px;
    font-weight: 600;
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
    min-height: 58px;
    display: grid;
    grid-template-columns: 20px 1fr auto;
    align-items: center;
    gap: 12px;
    padding: 0 16px;
    border-radius: 12px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.search-icon {
    width: 18px;
    height: 18px;
    color: var(--text-muted);
}

.knowledge-search {
    width: 100%;
    border: 0;
    outline: 0;
    background: transparent;
    color: var(--text-primary);
    font: inherit;
    font-size: 16px;
}

.knowledge-search::placeholder {
    color: var(--text-muted);
}

.search-count {
    color: var(--text-secondary);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 600;
}

.filter-panel,
.tags-section {
    margin: 20px 0 0;
    padding: 18px;
    border-radius: 12px;
    background: var(--surface);
    box-shadow: var(--ring);
}

.filter-panel {
    display: grid;
    gap: 16px;
}

.filter-group {
    display: grid;
    gap: 10px;
}

.filter-group > span,
.tags-header {
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 700;
}

.filter-options,
.tags-list,
.card-tags,
.card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.filter-chip,
.filter-tag,
.card-tags span {
    min-height: 28px;
    display: inline-flex;
    align-items: center;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 600;
    transition: background 180ms ease, color 180ms ease;
}

.filter-chip:hover,
.filter-chip.active,
.filter-tag:hover,
.filter-tag.active {
    color: var(--badge-fg);
    background: var(--badge-bg);
}

.tags-section {
    margin-bottom: 32px;
}

.tags-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 12px;
}

.tags-header button {
    padding: 0;
    color: var(--badge-fg);
    background: transparent;
    font-size: 14px;
    font-weight: 600;
}

.knowledge-list {
    display: grid;
    gap: 12px;
}

.document-results {
    width: 100%;
    min-height: max(560px, calc(100vh - 420px));
    align-content: start;
    overflow-anchor: none;
}

.knowledge-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.document-card {
    min-height: 240px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    border-radius: 12px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
    cursor: pointer;
    transition: transform 180ms ease, box-shadow 180ms ease;
}

.knowledge-list .document-card {
    min-height: 180px;
}

.document-card:hover,
.document-card:focus-visible {
    transform: translateY(-2px);
    box-shadow: rgba(0, 0, 0, 0.12) 0 0 0 1px,
        rgba(0, 0, 0, 0.06) 0 8px 18px -12px;
}

.card-kicker {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.document-card h2 {
    margin: 18px 0 10px;
    color: var(--text-primary);
    font-size: 24px;
    font-weight: 650;
    line-height: 1.25;
    letter-spacing: 0;
}

.document-card p {
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
    gap: 12px;
    text-align: center;
    border-radius: 12px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.empty-icon {
    width: 32px;
    height: 32px;
    color: var(--text-muted);
}

.no-results h2 {
    margin: 0;
    font-size: 24px;
    font-weight: 650;
    letter-spacing: 0;
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

    .knowledge-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 640px) {
    .knowledge-page {
        padding: 48px 0 64px;
    }

    .hero-actions {
        width: 100%;
        justify-content: space-between;
    }

    .knowledge-grid {
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
