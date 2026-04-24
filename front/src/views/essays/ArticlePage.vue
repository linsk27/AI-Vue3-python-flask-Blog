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
    background: #f5f7fa;
    min-height: 100vh;
    padding: 2rem 0;
}

.article-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 20px;
}

.article-header {
    margin-bottom: 2rem;
}

.back-btn {
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    font-size: 1rem;
    padding: 0;
    margin-bottom: 1.5rem;
    transition: color 0.3s;

    &:hover {
        color: #ff7f50;
    }
}

.article-title {
    font-size: 2.5rem;
    color: #333;
    margin: 0 0 1rem;
    line-height: 1.3;
}

.article-meta {
    color: #666;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 10px;
}

.meta-item {
    &.like-btn {
        cursor: pointer;
        padding: 4px 10px;
        border-radius: 15px;
        background: rgba(0, 0, 0, 0.05);
        transition: all 0.3s;
        user-select: none;

        &:hover {
            background: rgba(255, 127, 80, 0.1);
        }

        &.is-liked {
            color: #ff4757;
            background: rgba(255, 71, 87, 0.1);
        }
    }
}

.article-tags {
    margin-bottom: 1.5rem;
}

.article-tag {
    display: inline-block;
    background: #fff;
    color: #ff7f50;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    margin-right: 0.8rem;
    box-shadow: 0 2px 8px rgba(255, 127, 80, 0.1);
}

.article-summary {
    background: rgba(255, 255, 255, 0.8);
    padding: 1.5rem;
    border-radius: 12px;
    color: #555;
    line-height: 1.6;
    border-left: 4px solid #ff7f50;
    font-style: italic;
}

.article-html-content {
    line-height: 1.8;
    color: #2c3e50;
    font-size: 1.1rem;

    :deep(h1),
    :deep(h2),
    :deep(h3),
    :deep(h4) {
        color: #1a1a1a;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    :deep(h1) {
        font-size: 2rem;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.5rem;
    }

    :deep(h2) {
        font-size: 1.6rem;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.3rem;
    }

    :deep(h3) {
        font-size: 1.3rem;
    }

    :deep(p) {
        margin-bottom: 1.2rem;
    }

    :deep(pre) {
        background: #282c34;
        padding: 1.2rem;
        border-radius: 8px;
        overflow-x: auto;
        margin: 1.5rem 0;

        code {
            background: transparent;
            color: #abb2bf;
            padding: 0;
            font-family: 'Fira Code', 'Consolas', monospace;
        }
    }

    :deep(code) {
        background: rgba(255, 127, 80, 0.1);
        color: #ff7f50;
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
        border-left: 4px solid #ff7f50;
        padding: 0.5rem 1rem;
        background: #fafafa;
        color: #666;
        margin: 1.5rem 0;
    }

    :deep(img) {
        max-width: 100%;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
    }
}

.article-content-card {
    background: #fff;
    padding: 3rem;
    border-radius: 16px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
    min-height: 400px;
    margin-bottom: 2rem;
}

/* 评论模块样式 */
.comment-section {
    background: #fff;
    padding: 2.5rem 3rem;
    border-radius: 16px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
}

.section-title {
    margin-bottom: 2rem;
    border-bottom: 2px solid #f5f7fa;
    padding-bottom: 1rem;

    h3 {
        font-size: 1.4rem;
        color: #333;
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
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    resize: vertical;
    transition: all 0.3s;
    background: #f9f9f9;

    &:focus {
        outline: none;
        border-color: #ff7f50;
        background: #fff;
        box-shadow: 0 0 0 3px rgba(255, 127, 80, 0.1);
    }
}

.input-footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 1rem;
}

.submit-comment-btn {
    background: #ff7f50;
    color: #fff;
    border: none;
    padding: 0.8rem 2rem;
    border-radius: 25px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;

    &:hover:not(:disabled) {
        background: #ff6a33;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 127, 80, 0.3);
    }

    &:disabled {
        background: #ccc;
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
    color: #999;
    padding: 3rem 0;
    font-style: italic;
}

.comment-item {
    display: flex;
    gap: 1.2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #f0f0f0;

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
    color: #333;
    font-size: 1.05rem;
}

.comment-time {
    font-size: 0.85rem;
    color: #999;
}

.comment-text {
    line-height: 1.6;
    color: #444;
    white-space: pre-wrap;
    word-break: break-all;
}

.not-found {
    color: #d32f2f;
    font-size: 1.2rem;
    text-align: center;
    padding: 40px 0;
}

.loading {
    text-align: center;
    padding: 40px;
    color: #666;
}

/* 复用 Quill 编辑器的样式来渲染内容 */
.article-html-content {
    line-height: 1.8;
    color: #333;
}

.article-html-content :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 10px 0;
}

.article-html-content :deep(pre) {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}

@media (max-width: 700px) {
    .article-content-card {
        padding: 16px 12px;
    }

    .article-title {
        font-size: 1.3rem;
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
    background: white;
    padding: 12px 20px;
    border-radius: 50px;
    box-shadow: 0 4px 15px rgba(255, 127, 80, 0.25);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    border: 1px solid rgba(255, 127, 80, 0.1);
    z-index: 100;
}

.ai-float-btn:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 8px 25px rgba(255, 127, 80, 0.35);
    background: linear-gradient(135deg, #fff 0%, #fff5f0 100%);
}

.ai-icon {
    font-size: 1.2rem;
}

.ai-text {
    font-weight: 600;
    color: #ff7f50;
    font-size: 0.95rem;
}

/* 摘要面板 */
.ai-summary-panel {
    position: fixed;
    right: 40px;
    top: 220px;
    /* 按钮下方 */
    width: 320px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    z-index: 99;
    border: 1px solid rgba(255, 127, 80, 0.1);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.panel-header {
    padding: 15px 20px;
    background: linear-gradient(135deg, #fff5f0 0%, #fff 100%);
    border-bottom: 1px solid rgba(255, 127, 80, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.panel-header h3 {
    margin: 0;
    font-size: 1rem;
    color: #ff7f50;
    font-weight: 700;
}

.close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #999;
    cursor: pointer;
    line-height: 1;
    padding: 0 5px;
}

.close-btn:hover {
    color: #666;
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
    color: #666;
    gap: 15px;
}

.spinner {
    width: 30px;
    height: 30px;
    border: 3px solid #ffece5;
    border-top: 3px solid #ff7f50;
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
    color: #333;
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
