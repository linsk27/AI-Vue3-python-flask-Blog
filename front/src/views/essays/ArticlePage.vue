<template>
    <div class="document-page">
        <div class="document-layout">
            <main class="document-main">
                <button class="back-btn" @click="$router.back()">返回知识库</button>

                <header class="document-header" v-if="article">
                    <div class="document-kicker">
                        <span>{{ getDocumentTypeLabel(article) }}</span>
                        <span>{{ getDocumentStatusLabel(article) }}</span>
                    </div>
                    <h1 class="document-title">{{ article.title }}</h1>
                    <div class="document-meta">
                        <span v-if="article.created_at">创建于 {{ formatDate(article.created_at) }}</span>
                        <span v-if="article.author_name">作者 {{ article.author_name }}</span>
                        <span>{{ article.views || 0 }} 次浏览</span>
                        <button class="favorite-btn" type="button" @click="toggleLike" :class="{ 'is-liked': article.is_liked }">
                            <Star class="meta-icon" />
                            <span>{{ article.likes || 0 }} 次收藏</span>
                        </button>
                    </div>
                    <div class="document-tags">
                        <span v-for="tag in article.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <p v-if="article.summary" class="document-summary">{{ article.summary }}</p>
                </header>

                <section class="document-content-card">
                    <div v-if="loading" class="loading">Loading document...</div>
                    <div v-else-if="activeComponent" class="interactive-component">
                        <component :is="activeComponent" />
                    </div>
                    <div v-else-if="article" class="document-html-content ql-editor" v-html="parsedContent"></div>
                    <div v-else class="not-found">文档不存在。</div>
                </section>

                <section class="discussion-section" v-if="article">
                    <div class="section-title">
                        <h2>讨论 ({{ comments.length }})</h2>
                    </div>

                    <div class="comment-input-box">
                        <textarea v-model="commentContent" placeholder="写下问题、补充说明或讨论内容..." class="comment-textarea"></textarea>
                        <div class="input-footer">
                            <button class="submit-comment-btn" @click="submitComment" :disabled="submittingComment">
                                {{ submittingComment ? '提交中...' : '发布讨论' }}
                            </button>
                        </div>
                    </div>

                    <div class="comments-list">
                        <div v-if="comments.length === 0" class="no-comments">
                            暂无讨论。写下第一条上下文备注吧。
                        </div>
                        <div v-for="comment in comments" :key="comment.id" class="comment-item">
                            <div class="comment-user-avatar">
                                <img :src="comment.user_avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'"
                                    alt="User avatar">
                            </div>
                            <div class="comment-content-main">
                                <div class="comment-user-info">
                                    <span class="comment-user-name">{{ comment.user_name }}</span>
                                    <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                                </div>
                                <div class="comment-text">
                                    {{ comment.content }}
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </main>

            <aside class="ai-insight-panel" v-if="article && !loading">
                <div class="insight-header">
                    <span class="eyebrow">AI 洞察</span>
                    <h2>阅读助手</h2>
                    <p>从当前文档生成可复用的理解、摘要和问题。</p>
                </div>

                <div class="insight-actions">
                    <button type="button" @click="generateAiSummary" :disabled="isAiGenerating">
                        <DocumentChecked class="action-icon" />
                        <span>{{ isAiGenerating ? '摘要生成中...' : '生成摘要' }}</span>
                    </button>
                    <button type="button" @click="generateLocalKeywords">
                        <PriceTag class="action-icon" />
                        <span>提取关键词</span>
                    </button>
                    <button type="button" @click="generateLocalQuestions">
                        <QuestionFilled class="action-icon" />
                        <span>生成复习问题</span>
                    </button>
                    <router-link class="panel-link" to="/context-packs">
                        <FolderAdd class="action-icon" />
                        <span>加入上下文包</span>
                    </router-link>
                    <router-link class="panel-link" to="/ai-center/chat">
                        <ChatDotRound class="action-icon" />
                        <span>进入上下文对话</span>
                    </router-link>
                </div>

                <div class="insight-block">
                    <h3>摘要</h3>
                    <div v-if="isAiGenerating" class="ai-loading">
                        <div class="spinner"></div>
                        <p>AI 正在阅读这份文档...</p>
                    </div>
                    <p v-else>{{ aiSummary || article.summary || '生成摘要后，这里会形成一段紧凑的上下文备注。' }}</p>
                </div>

                <div class="insight-block">
                    <h3>关键词</h3>
                    <div class="keyword-list">
                        <span v-for="keyword in insightKeywords" :key="keyword">{{ keyword }}</span>
                    </div>
                </div>

                <div class="insight-block">
                    <h3>复习问题</h3>
                    <ol class="question-list">
                        <li v-for="question in insightQuestions" :key="question">{{ question }}</li>
                    </ol>
                </div>
            </aside>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { ref, onMounted, shallowRef } from 'vue'
import { ChatDotRound, DocumentChecked, FolderAdd, PriceTag, QuestionFilled, Star } from '@element-plus/icons-vue'
import articleApi, { IComment } from '@/api/modules/article'
import { aiSummaryService } from '@/api/modules/ai'
import { IArticle } from '@/api/modules/article/interface'
import { useElMessage } from '@/hooks/useMessage'
import { useCacheStore } from '@/store/cache'
import 'quill/dist/quill.snow.css'
import { articles as localArticles } from './articles/index'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

const route = useRoute()
const { message } = useElMessage()
const cacheStore = useCacheStore()
const article = ref<IArticle | null>(null)
const loading = ref(false)
const activeComponent = shallowRef<any>(null)

const comments = ref<IComment[]>([])
const commentContent = ref('')
const submittingComment = ref(false)

const aiSummary = ref('')
const isAiGenerating = ref(false)
const insightKeywords = ref<string[]>([])
const insightQuestions = ref<string[]>([
    '这份文档主要解决什么问题？',
    '哪些部分最适合加入上下文包？',
    '读完这份文档后下一步应该做什么？'
])

marked.setOptions({
    highlight: function (code: string, lang: string) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value
        }
        return hljs.highlightAuto(code).value
    },
    breaks: true,
    gfm: true
})

const parsedContent = ref('')
const parseMarkdown = async () => {
    if (!article.value?.content) {
        parsedContent.value = ''
        return
    }
    parsedContent.value = await marked.parse(article.value.content)
}

const formatDate = (dateStr: string) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    if (Number.isNaN(date.getTime())) return ''
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

const typeLabels: Record<string, string> = {
    note: '笔记',
    'technical-doc': '技术文档',
    tutorial: '教程',
    'project-record': '项目记录',
    paper: '论文',
    idea: '灵感'
}

const statusLabels: Record<string, string> = {
    published: '已发布',
    draft: '草稿',
    organized: '已整理',
    reviewing: '待复习',
    archived: '已归档'
}

const getDocumentTypeLabel = (item: IArticle) => typeLabels[slugifyType(item.resource_type || item.category)] || '文档'
const getDocumentStatusLabel = (item: IArticle) => statusLabels[item.document_status || item.status || 'published'] || '已发布'

const fetchComments = async () => {
    const id = route.params.id as string
    if (!id) return
    try {
        const res = await articleApi.getComments(id)
        comments.value = (res as any).data || res
    } catch (error) {
        console.error('Failed to fetch discussion:', error)
    }
}

const submitComment = async () => {
    if (!commentContent.value.trim()) {
        message.warning('请输入讨论内容')
        return
    }

    const id = route.params.id as string
    submittingComment.value = true
    try {
        await articleApi.createComment(id, commentContent.value)
        message.success('讨论已发布')
        commentContent.value = ''
        await fetchComments()
    } catch (error) {
        console.error('Failed to post discussion:', error)
        message.error('发布失败，请先登录')
    } finally {
        submittingComment.value = false
    }
}

const toggleLike = async () => {
    if (!article.value) return
    try {
        const res = await articleApi.toggleLike(article.value.id)
        if (article.value) {
            article.value.is_liked = res.liked
            article.value.likes = res.likes
        }
    } catch (error) {
        console.error('Favorite failed:', error)
        message.error('操作失败，请先登录')
    }
}

const extractTextContent = (html: string) => {
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = html
    return tempDiv.textContent || tempDiv.innerText || ''
}

const getReadableText = () => {
    if (!article.value) return ''
    if (article.value.content) return extractTextContent(article.value.content)
    return `${article.value.title}\n${article.value.summary || ''}`
}

const generateAiSummary = async () => {
    if (!article.value) return
    if (aiSummary.value) return

    isAiGenerating.value = true

    try {
        const contentToSummarize = getReadableText()

        if (!contentToSummarize || contentToSummarize.length < 50) {
            aiSummary.value = '这份文档内容较短，暂时无法生成有效摘要。'
            return
        }

        const res = await aiSummaryService.generateSummary({
            content: contentToSummarize,
            length: 220
        }) as any

        const summaryText = res?.reply || res?.data?.reply || res?.summary || res?.data?.summary

        if (summaryText) {
            aiSummary.value = summaryText
        } else {
            throw new Error('No summary returned')
        }
    } catch (error) {
        console.error('AI summary generation failed:', error)
        message.error('摘要生成失败，请稍后重试')
    } finally {
        isAiGenerating.value = false
    }
}

const generateLocalKeywords = () => {
    if (!article.value) return
    const tags = article.value.tags || []
    const titleWords = article.value.title
        .split(/[\s:：,，.。/\\-]+/)
        .map(word => word.trim())
        .filter(word => word.length > 2)
        .slice(0, 6)

    insightKeywords.value = Array.from(new Set([...tags, ...titleWords])).slice(0, 10)
}

const generateLocalQuestions = () => {
    if (!article.value) return
    insightQuestions.value = [
        `《${article.value.title}》提供了哪些可复用上下文？`,
        '哪些部分应该和相关文档一起打包？',
        '这份文档中有什么决策、解释或流程值得提取？'
    ]
}

onMounted(async () => {
    window.scrollTo(0, 0)
    const id = route.params.id as string
    if (!id) return

    const localArticle = localArticles.find(a => a.id === id)
    if (localArticle) {
        article.value = {
            ...localArticle,
            tags: [...(localArticle.tags || []), 'example'],
            resource_type: 'technical-doc',
            document_status: 'organized',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            author_name: '语境工坊团队',
            views: 0,
            likes: 0,
            content: ''
        }

        generateLocalKeywords()

        if (localArticle.component) {
            try {
                const compModule = await localArticle.component()
                activeComponent.value = compModule.default || compModule
            } catch (err) {
                console.error('Failed to load component:', err)
                message.error('组件加载失败')
            }
        }
        loading.value = false
        return
    }

    const cachedArticle = cacheStore.getArticleDetail(id)
    if (cachedArticle) {
        article.value = cachedArticle
        if (typeof article.value.views !== 'number') article.value.views = 0
        article.value.is_liked = !!article.value.is_liked
        await parseMarkdown()
        generateLocalKeywords()
        await fetchComments()
        loading.value = false

        try {
            await articleApi.incrementView(id)
            if (article.value) {
                article.value.views++
                cacheStore.setArticleDetail(id, article.value)
            }
        } catch (e) {
            console.error('Failed to update view count:', e)
        }
        return
    }

    try {
        await articleApi.incrementView(id)
    } catch (e) {
        console.error('Failed to update view count:', e)
    }

    loading.value = true

    try {
        const res = await articleApi.getDetail(id)
        article.value = (res as any).data || res

        if (article.value) {
            if (typeof article.value.views !== 'number') article.value.views = 0
            article.value.is_liked = !!article.value.is_liked

            cacheStore.setArticleDetail(id, article.value)

            await parseMarkdown()
            generateLocalKeywords()
            await fetchComments()
        }
    } catch (error) {
        console.error('Failed to load document:', error)
        message.error('文档加载失败')
    } finally {
        loading.value = false
    }
})
</script>

<style scoped lang="scss">
.document-page {
    min-height: calc(100vh - 140px);
    padding: 56px 0 88px;
    color: var(--text-primary);
    background: transparent;
}

.document-layout {
    width: var(--page-width);
    margin: 0 auto;
    display: grid;
    grid-template-columns: minmax(0, 1fr) 340px;
    align-items: start;
    gap: 18px;
}

.document-main {
    min-width: 0;
}

.back-btn {
    min-height: 36px;
    display: inline-flex;
    align-items: center;
    border: 0;
    border-radius: 10px;
    color: var(--text-secondary);
    background: var(--surface);
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    padding: 0 12px;
    margin-bottom: 28px;
    box-shadow: var(--ring);
    transition: background 180ms ease, color 180ms ease;

    &:hover {
        color: var(--text-primary);
        background: var(--surface-hover);
    }
}

.document-header {
    margin-bottom: 24px;
}

.document-kicker {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;

    span {
        min-height: 26px;
        display: inline-flex;
        align-items: center;
        padding: 0 10px;
        border-radius: 9999px;
        color: var(--text-secondary);
        background: var(--surface-subtle);
        box-shadow: var(--ring);
        font-family: var(--font-mono);
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
    }
}

.document-title {
    color: var(--text-primary);
    margin: 0 0 18px;
    font-family: var(--font-serif);
    font-size: clamp(42px, 7vw, 72px);
    font-weight: 650;
    line-height: 1.04;
    letter-spacing: 0;
}

.document-meta {
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}

.favorite-btn {
    min-height: 28px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0 10px;
    border: 0;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    cursor: pointer;
    font: inherit;
    transition: background 180ms ease, color 180ms ease;

    &:hover {
        color: var(--text-primary);
        background: var(--surface-hover);
    }

    &.is-liked {
        color: var(--button-fg);
        background: var(--button-bg);
    }
}

.meta-icon {
    width: 14px;
    height: 14px;
}

.document-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 22px;

    span {
        min-height: 26px;
        display: inline-flex;
        align-items: center;
        color: var(--text-secondary);
        background: var(--surface-subtle);
        padding: 0 10px;
        border-radius: 9999px;
        font-family: var(--font-mono);
        font-size: 12px;
        font-weight: 600;
        box-shadow: var(--ring);
    }
}

.document-summary {
    margin: 0;
    padding: 18px 20px;
    border-radius: 12px;
    color: var(--text-secondary);
    background: var(--surface);
    box-shadow: inset 3px 0 0 var(--button-bg), var(--card-shadow);
    line-height: 1.75;
}

.document-content-card,
.discussion-section,
.ai-insight-panel {
    background: var(--surface);
    border-radius: 12px;
    box-shadow: var(--card-shadow);
}

.document-content-card {
    padding: 3rem;
    min-height: 400px;
    margin-bottom: 18px;
}

.document-html-content {
    line-height: 1.8;
    color: var(--text-primary);
    font-size: 17px;

    :deep(h1),
    :deep(h2),
    :deep(h3),
    :deep(h4) {
        color: var(--text-primary);
        margin-top: 2.2rem;
        margin-bottom: 1rem;
        font-family: var(--font-serif);
        font-weight: 650;
        letter-spacing: 0;
    }

    :deep(h1) {
        font-size: 2rem;
        border-bottom: 1px solid var(--line);
        padding-bottom: 0.5rem;
    }

    :deep(h2) {
        font-size: 1.6rem;
        border-bottom: 1px solid var(--line);
        padding-bottom: 0.3rem;
    }

    :deep(h3) {
        font-size: 1.3rem;
    }

    :deep(p) {
        margin-bottom: 1.2rem;
    }

    :deep(pre) {
        background: var(--anthropic-black);
        padding: 1.2rem;
        border-radius: 10px;
        overflow-x: auto;
        margin: 1.5rem 0;
        box-shadow: var(--ring);

        code {
            background: transparent;
            color: #abb2bf;
            padding: 0;
            font-family: 'Fira Code', 'Consolas', monospace;
        }
    }

    :deep(code) {
        background: var(--surface-subtle);
        color: var(--button-bg);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
    }

    :deep(ul),
    :deep(ol) {
        padding-left: 1.5rem;
        margin-bottom: 1.2rem;

        li {
            margin-bottom: 0.5rem;
        }
    }

    :deep(blockquote) {
        border-left: 3px solid var(--button-bg);
        padding: 0.75rem 1rem;
        background: var(--surface-subtle);
        color: var(--text-secondary);
        margin: 1.5rem 0;
        border-radius: 0 10px 10px 0;
    }

    :deep(img) {
        max-width: 100%;
        height: auto;
        border-radius: 10px;
        box-shadow: var(--ring);
        margin: 1.5rem 0;
    }
}

.discussion-section {
    padding: 2rem;
}

.section-title {
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--line);
    padding-bottom: 1rem;

    h2 {
        font-size: 1.3rem;
        color: var(--text-primary);
        margin: 0;
    }
}

.comment-input-box {
    margin-bottom: 2rem;
}

.comment-textarea {
    width: 100%;
    min-height: 120px;
    padding: 1rem;
    border: 0;
    border-radius: 10px;
    font-size: 1rem;
    resize: vertical;
    color: var(--text-primary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    transition: box-shadow 180ms ease, background 180ms ease;

    &:focus {
        outline: none;
        background: var(--surface);
        box-shadow: var(--ring), 0 0 0 3px rgba(56, 152, 236, 0.16);
    }
}

.input-footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 1rem;
}

.submit-comment-btn {
    background: var(--button-bg);
    color: var(--button-fg);
    border: none;
    min-height: 40px;
    padding: 0 18px;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: var(--ring);
    transition: background 180ms ease, transform 180ms ease;

    &:hover:not(:disabled) {
        background: var(--button-hover);
        transform: translateY(-1px);
    }

    &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
}

.comments-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.no-comments {
    text-align: center;
    color: var(--text-muted);
    padding: 2.5rem 0;
}

.comment-item {
    display: flex;
    gap: 1.2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--line);

    &:last-child {
        border-bottom: none;
    }
}

.comment-user-avatar img {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    object-fit: cover;
}

.comment-content-main {
    flex: 1;
}

.comment-user-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}

.comment-user-name {
    font-weight: 700;
    color: var(--text-primary);
    font-size: 1rem;
}

.comment-time {
    font-size: 0.85rem;
    color: var(--text-muted);
}

.comment-text {
    line-height: 1.6;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
}

.not-found,
.loading {
    text-align: center;
    padding: 40px;
}

.not-found {
    color: var(--button-bg);
    font-size: 1.2rem;
}

.loading {
    color: var(--text-muted);
}

.ai-insight-panel {
    position: sticky;
    top: 104px;
    padding: 20px;
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

.insight-header h2 {
    margin: 14px 0 8px;
    font-size: 26px;
    font-weight: 650;
    line-height: 1.1;
}

.insight-header p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.6;
}

.insight-actions {
    display: grid;
    gap: 8px;
    margin: 20px 0;
}

.insight-actions button,
.panel-link {
    min-height: 38px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0 12px;
    border: 0;
    border-radius: 10px;
    color: var(--text-primary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font: inherit;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background 180ms ease, color 180ms ease;
}

.insight-actions button:hover,
.panel-link:hover {
    background: var(--surface-hover);
}

.insight-actions button:disabled {
    cursor: not-allowed;
    opacity: 0.6;
}

.action-icon {
    width: 16px;
    height: 16px;
}

.insight-block {
    padding: 16px;
    border-radius: 12px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    margin-bottom: 12px;

    h3 {
        margin: 0 0 10px;
        color: var(--text-primary);
        font-size: 15px;
        font-weight: 700;
    }

    p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 14px;
        line-height: 1.65;
    }
}

.keyword-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    span {
        min-height: 24px;
        display: inline-flex;
        align-items: center;
        padding: 0 8px;
        border-radius: 9999px;
        background: var(--surface);
        color: var(--text-secondary);
        box-shadow: var(--ring);
        font-size: 12px;
        font-weight: 600;
    }
}

.question-list {
    margin: 0;
    padding-left: 18px;
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.6;

    li + li {
        margin-top: 8px;
    }
}

.ai-loading {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--text-secondary);
}

.spinner {
    width: 18px;
    height: 18px;
    border: 2px solid var(--surface);
    border-top: 2px solid var(--button-bg);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    flex: 0 0 auto;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@media (max-width: 1040px) {
    .document-layout {
        grid-template-columns: 1fr;
    }

    .ai-insight-panel {
        position: static;
        order: -1;
    }
}

@media (max-width: 700px) {
    .document-page {
        padding-top: 36px;
    }

    .document-content-card,
    .discussion-section {
        padding: 18px;
    }

    .document-title {
        font-size: 34px;
        line-height: 1.08;
    }
}
</style>
