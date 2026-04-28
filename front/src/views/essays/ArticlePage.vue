<template>
    <div class="article-page">
        <div class="article-container">
            <div class="article-header">
                <button class="back-btn" @click="$router.back()">← 返回列表</button>
                <div v-if="article">
                    <h1 class="article-title">{{ article.title }}</h1>
                    <div class="article-meta">
                        <span class="article-date" v-if="article.created_at">发布于 {{ formatDate(article.created_at)
                            }}</span>
                        <span class="article-author" v-if="article.author_name"> · 作者: {{ article.author_name }}</span>
                        <span class="meta-item"> · {{ article.views }} 阅读</span>
                        <span class="meta-item like-btn" @click="toggleLike" :class="{ 'is-liked': article.is_liked }">
                            {{ article.is_liked ? '❤️' : '🤍' }} {{ article.likes }} 点赞
                        </span>
                    </div>
                    <div class="article-tags">
                        <span class="article-tag" v-for="tag in article.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <p class="article-summary">{{ article.summary }}</p>
                </div>
            </div>
            <div class="article-content-card">
                <div v-if="loading" class="loading">加载中...</div>

                <!-- 交互式组件渲染 -->
                <div v-else-if="activeComponent" class="interactive-component">
                    <component :is="activeComponent" />
                </div>

                <!-- 富文本内容渲染 -->
                <div v-else-if="article" class="article-html-content ql-editor" v-html="parsedContent"></div>

                <div v-else class="not-found">文章不存在</div>
            </div>

            <!-- 评论模块 -->
            <div class="comment-section" v-if="article">
                <div class="section-title">
                    <h3>全部评论 ({{ comments.length }})</h3>
                </div>

                <!-- 发表评论 -->
                <div class="comment-input-box">
                    <textarea v-model="commentContent" placeholder="写下你的评论..." class="comment-textarea"></textarea>
                    <div class="input-footer">
                        <button class="submit-comment-btn" @click="submitComment" :disabled="submittingComment">
                            {{ submittingComment ? '提交中...' : '发表评论' }}
                        </button>
                    </div>
                </div>

                <!-- 评论列表 -->
                <div class="comments-list">
                    <div v-if="comments.length === 0" class="no-comments">
                        暂无评论，快来抢沙发吧~
                    </div>
                    <div v-for="comment in comments" :key="comment.id" class="comment-item">
                        <div class="comment-user-avatar">
                            <img :src="comment.user_avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'"
                                alt="用户头像">
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
            </div>
        </div>

        <!-- AI 摘要悬浮按钮 -->
        <div class="ai-float-btn" @click="generateAiSummary" v-if="article && !loading" title="生成 AI 摘要">
            <span class="ai-icon">✨</span>
            <span class="ai-text">AI 摘要</span>
        </div>

        <!-- AI 摘要面板 -->
        <transition name="slide-fade">
            <div class="ai-summary-panel" v-if="showAiPanel" ref="aiPanelRef">
                <div class="panel-header">
                    <h3>✨ AI 智能摘要</h3>
                    <button class="close-btn" @click="showAiPanel = false">×</button>
                </div>
                <div class="panel-content">
                    <div v-if="isAiGenerating" class="ai-loading">
                        <div class="spinner"></div>
                        <p>AI 正在阅读并生成摘要...</p>
                    </div>
                    <div v-else class="ai-result">
                        <p>{{ aiSummary }}</p>
                    </div>
                </div>
            </div>
        </transition>
    </div>
</template>
<script setup lang="ts">
import { useRoute } from 'vue-router'
import { ref, onMounted, shallowRef, defineAsyncComponent, nextTick, computed } from 'vue'
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

const fetchComments = async () => {
    const id = route.params.id as string
    if (!id) return
    try {
        const res = await articleApi.getComments(id)
        comments.value = res.data || res
    } catch (error) {
        console.error('获取评论失败', error)
    }
}

const submitComment = async () => {
    if (!commentContent.value.trim()) {
        message.warning('请输入评论内容')
        return
    }

    const id = route.params.id as string
    submittingComment.value = true
    try {
        await articleApi.createComment(id, commentContent.value)
        message.success('评论发表成功')
        commentContent.value = ''
        await fetchComments() // 刷新评论列表
    } catch (error) {
        console.error('发表评论失败', error)
        message.error('发表评论失败，请先登录')
    } finally {
        submittingComment.value = false
    }
}

// AI 摘要相关状态
const showAiPanel = ref(false)
const aiSummary = ref('')
const isAiGenerating = ref(false)
const aiPanelRef = ref<HTMLElement | null>(null)

// 配置 marked
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

// 解析文章内容
const parsedContent = ref('')
const parseMarkdown = async () => {
    if (!article.value?.content) {
        parsedContent.value = ''
        return
    }
    // 异步解析 Markdown，防止阻塞主线程
    parsedContent.value = await marked.parse(article.value.content)
}

const formatDate = (dateStr: string) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleDateString()
}

// 点赞文章
const toggleLike = async () => {
    if (!article.value) return
    try {
        const res = await articleApi.toggleLike(article.value.id)
        if (article.value) {
            article.value.is_liked = res.liked
            article.value.likes = res.likes
        }
    } catch (error) {
        console.error('点赞失败', error)
        message.error('操作失败，请先登录')
    }
}

// 增加阅读量
const incrementView = async () => {
    if (!article.value) return
    try {
        await articleApi.incrementView(article.value.id)
        if (article.value) {
            article.value.views++
        }
    } catch (error) {
        console.error('增加阅读量失败', error)
    }
}

// 提取纯文本内容
const extractTextContent = (html: string) => {
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = html
    return tempDiv.textContent || tempDiv.innerText || ''
}

// 生成 AI 摘要
const generateAiSummary = async () => {
    if (!article.value) return

    // 如果已经有摘要了，直接显示面板
    if (aiSummary.value) {
        showAiPanel.value = true
        return
    }

    showAiPanel.value = true
    isAiGenerating.value = true

    try {
        // 获取文章内容（优先使用 content，如果是交互式组件则尝试获取描述）
        let contentToSummarize = ''
        if (article.value.content) {
            contentToSummarize = extractTextContent(article.value.content)
        } else {
            contentToSummarize = article.value.summary || article.value.title
        }

        if (!contentToSummarize || contentToSummarize.length < 50) {
            aiSummary.value = '文章内容过短，无法生成摘要。'
            return
        }

        const res = await aiSummaryService.generateSummary({
            content: contentToSummarize,
            length: 200, // 侧边栏展示，200字左右比较合适
        }) as any

        const summaryText = res?.reply || res?.data?.reply || res?.summary || res?.data?.summary

        if (summaryText) {
            aiSummary.value = summaryText
        } else {
            throw new Error('未获取到有效摘要')
        }
    } catch (error) {
        console.error('AI summary generation failed:', error)
        message.error('摘要生成失败，请稍后重试')
        showAiPanel.value = false
    } finally {
        isAiGenerating.value = false
    }
}

onMounted(async () => {
    window.scrollTo(0, 0)
    const id = route.params.id as string
    if (id) {
        const localArticle = localArticles.find(a => a.id === id)
        if (localArticle) {
            article.value = {
                ...localArticle,
                tags: [...(localArticle.tags || []), '可交互文章'],
                created_at: new Date().toISOString(),
                author_name: '智汇编辑部',
                content: ''
            }

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
            if (typeof article.value.views !== 'number') {
                article.value.views = 0
            }
            article.value.is_liked = !!article.value.is_liked
            await parseMarkdown()
            await fetchComments()
            loading.value = false

            try {
                await articleApi.incrementView(id)
                if (article.value) {
                    article.value.views++
                    cacheStore.setArticleDetail(id, article.value)
                }
            } catch (e) {
                console.error('更新阅读量失败', e)
            }
            return
        }

        try {
            await articleApi.incrementView(id)
        } catch (e) {
            console.error('更新阅读量失败', e)
        }

        loading.value = true

        try {
            const res = await articleApi.getDetail(id)
            article.value = res.data || res

            if (article.value) {
                if (typeof article.value.views !== 'number') {
                    article.value.views = 0
                }
                article.value.is_liked = !!article.value.is_liked

                cacheStore.setArticleDetail(id, article.value)

                await parseMarkdown()
                await fetchComments()
            }
        } catch (error) {
            console.error('Failed to load article:', error)
            message.error('加载文章失败')
        } finally {
            loading.value = false
        }
    }
})
</script>

<style scoped lang="scss">
.article-page {
    min-height: calc(100vh - 140px);
    padding: 64px 0 88px;
    color: var(--text-primary);
    background: transparent;
}

.article-container {
    width: min(920px, var(--page-width));
    margin: 0 auto;
    padding: 0;
}

.article-header {
    margin-bottom: 28px;
}

.back-btn {
    height: 36px;
    display: inline-flex;
    align-items: center;
    border: 0;
    border-radius: 10px;
    color: var(--text-secondary);
    background: var(--surface);
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    padding: 0 12px;
    margin-bottom: 28px;
    box-shadow: var(--ring);
    transition: background 180ms ease, color 180ms ease;

    &:hover {
        color: var(--text-primary);
        background: var(--surface-hover);
    }
}

.article-title {
    color: var(--text-primary);
    margin: 0 0 18px;
    font-family: var(--font-serif);
    font-size: clamp(42px, 7vw, 72px);
    font-weight: 600;
    line-height: 1.04;
    letter-spacing: 0;
}

.article-meta {
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}

.meta-item {
    &.like-btn {
        cursor: pointer;
        min-height: 28px;
        display: inline-flex;
        align-items: center;
        padding: 0 10px;
        border-radius: 9999px;
        color: var(--text-secondary);
        background: var(--surface-subtle);
        box-shadow: var(--ring);
        transition: background 180ms ease, color 180ms ease;
        user-select: none;

        &:hover {
            color: var(--text-primary);
            background: var(--surface-hover);
        }

        &.is-liked {
            color: var(--button-fg);
            background: var(--button-bg);
        }
    }
}

.article-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 22px;
}

.article-tag {
    min-height: 26px;
    display: inline-flex;
    align-items: center;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    padding: 0 10px;
    border-radius: 9999px;
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 500;
    box-shadow: var(--ring);
}

.article-summary {
    margin: 0;
    padding: 18px 20px;
    border-radius: 12px;
    color: var(--text-secondary);
    background: var(--surface);
    box-shadow: inset 3px 0 0 var(--terracotta), var(--card-shadow);
    line-height: 1.75;
}

.article-html-content {
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
        font-weight: 600;
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
        color: var(--terracotta);
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
        border-left: 3px solid var(--terracotta);
        padding: 0.75rem 1rem;
        background: var(--surface-subtle);
        color: var(--text-secondary);
        margin: 1.5rem 0;
        border-radius: 0 10px 10px 0;
    }

    :deep(img) {
        max-width: 100%;
        border-radius: 10px;
        box-shadow: var(--ring);
        margin: 1.5rem 0;
    }
}

.article-content-card {
    background: var(--surface);
    padding: 3rem;
    border-radius: 12px;
    box-shadow: var(--card-shadow);
    min-height: 400px;
    margin-bottom: 2rem;
}

/* 评论模块样式 */
.comment-section {
    background: var(--surface);
    padding: 2.5rem 3rem;
    border-radius: 12px;
    box-shadow: var(--card-shadow);
}

.section-title {
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--line);
    padding-bottom: 1rem;

    h3 {
        font-size: 1.4rem;
        color: var(--text-primary);
        margin: 0;
    }
}

.comment-input-box {
    margin-bottom: 3rem;
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
    font-weight: 500;
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
    gap: 2rem;
}

.no-comments {
    text-align: center;
    color: var(--text-muted);
    padding: 3rem 0;
    font-style: italic;
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

.comment-user-avatar {
    img {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
    }
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
    font-weight: 600;
    color: var(--text-primary);
    font-size: 1.05rem;
}

.comment-time {
    font-size: 0.85rem;
    color: var(--text-muted);
}

.comment-text {
    line-height: 1.6;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-all;
}

.not-found {
    color: var(--terracotta);
    font-size: 1.2rem;
    text-align: center;
    padding: 40px 0;
}

.loading {
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
}

/* 复用 Quill 编辑器的样式来渲染内容 */
.article-html-content {
    line-height: 1.8;
    color: var(--text-primary);
}

.article-html-content :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 10px;
    margin: 10px 0;
}

.article-html-content :deep(pre) {
    background-color: var(--anthropic-black);
    padding: 16px;
    border-radius: 10px;
    overflow-x: auto;
}

@media (max-width: 700px) {
    .article-content-card {
        padding: 16px 12px;
    }

    .article-title {
        font-size: 34px;
        line-height: 1.08;
    }

    .ai-float-btn {
        bottom: 20px;
        right: 20px;
        top: auto;
    }

    .ai-summary-panel {
        width: 90%;
        right: 5%;
        top: 20%;
    }
}

/* AI 功能样式 */
.ai-float-btn {
    position: fixed;
    right: 40px;
    top: 150px;
    /* 位于文章内容右侧上方 */
    color: var(--button-fg);
    background: var(--button-bg);
    padding: 12px 20px;
    border-radius: 50px;
    box-shadow: var(--card-shadow);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: background 180ms ease, transform 180ms ease, box-shadow 180ms ease;
    border: 0;
    z-index: 100;
}

.ai-float-btn:hover {
    transform: translateY(-2px);
    box-shadow: rgba(20, 20, 19, 0.14) 0 8px 24px -14px;
    background: var(--button-hover);
}

.ai-icon {
    font-size: 1.2rem;
}

.ai-text {
    font-weight: 600;
    color: currentColor;
    font-size: 0.95rem;
}

/* 摘要面板 */
.ai-summary-panel {
    position: fixed;
    right: 40px;
    top: 220px;
    /* 按钮下方 */
    width: 320px;
    color: var(--text-primary);
    background: var(--surface);
    border-radius: 12px;
    box-shadow: var(--card-shadow);
    z-index: 99;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.panel-header {
    padding: 15px 20px;
    background: var(--surface-subtle);
    border-bottom: 1px solid var(--line);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.panel-header h3 {
    margin: 0;
    font-size: 1rem;
    color: var(--text-primary);
    font-weight: 600;
}

.close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: var(--text-muted);
    cursor: pointer;
    line-height: 1;
    padding: 0 5px;
}

.close-btn:hover {
    color: var(--text-primary);
}

.panel-content {
    padding: 20px;
    max-height: 400px;
    overflow-y: auto;
}

.ai-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px 0;
    color: var(--text-secondary);
    gap: 15px;
}

.spinner {
    width: 30px;
    height: 30px;
    border: 3px solid var(--surface-subtle);
    border-top: 3px solid var(--terracotta);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.ai-result {
    line-height: 1.6;
    color: var(--text-secondary);
    font-size: 0.95rem;
    text-align: justify;
}

/* 动画效果 */
.slide-fade-enter-active,
.slide-fade-leave-active {
    transition: all 0.3s ease-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
    transform: translateX(20px);
    opacity: 0;
}
</style>
