<template>
    <div class="document-editor-page">
        <section class="editor-header">
            <div>
                <span class="eyebrow">文档工作室</span>
                <h1>{{ pageTitle }}</h1>
                <p>把标题、来源、标签和正文整理完整，之后可以加入资料包，继续用于问答和起草。</p>
            </div>
            <el-button class="ai-help-btn" native-type="button" :disabled="aiGenerating" @click.stop="openAiDialog">
                <Grid />
                <span>AI 起草</span>
            </el-button>
        </section>

        <section v-if="aiDialogVisible" class="ai-draft-panel">
            <div class="ai-draft-header">
                <span class="ai-dialog-mark">AI</span>
                <div>
                    <span class="ai-dialog-eyebrow">从资料起草</span>
                    <h2>先检索依据，再写入编辑器</h2>
                </div>
                <el-button class="dialog-cancel" native-type="button" @click="aiDialogVisible = false">收起</el-button>
            </div>

            <p class="ai-tip">写下主题、读者和结构要求。选择资料包后，会先预览可引用片段，再把草稿填入下方正文。</p>
            <div class="ai-dialog-tags">
                <span>结构</span>
                <span>来源</span>
                <span>标签</span>
                <span>引用</span>
            </div>
            <div class="ai-context-controls">
                <div>
                    <label class="ai-input-label">可选上下文包</label>
                    <el-select
                        v-model="aiDraftContextPackId"
                        clearable
                        filterable
                        :loading="aiDraftPacksLoading"
                        placeholder="选择后，AI 会先检索相关片段再起草"
                        class="ai-context-select"
                    >
                        <el-option
                            v-for="pack in aiDraftPacks"
                            :key="pack.id"
                            :label="`${pack.name} · ${pack.sources.length} 份资料`"
                            :value="pack.id"
                        />
                    </el-select>
                </div>
                <label class="ai-rag-toggle" :class="{ disabled: !selectedAiDraftPack }">
                    <input v-model="aiDraftAllowEmbedding" type="checkbox" :disabled="!selectedAiDraftPack" />
                    <span>优先语义匹配</span>
                    <small>{{ aiDraftRagHint }}</small>
                </label>
            </div>
            <label class="ai-input-label">起草要求</label>
            <el-input
                v-model="aiTopic"
                type="textarea"
                :rows="6"
                placeholder="例如：面向初学者写一篇 Vue 3 组合式 API 笔记，包含概念、示例和常见问题。"
                class="ai-input"
            />
            <div v-if="aiDraftRetrieval" class="ai-rag-result">
                <strong>{{ getDraftRetrievalLabel(aiDraftRetrieval) }}</strong>
                <span>命中 {{ aiDraftRetrieval.snippets.length }} 段 · 约 {{ aiDraftRetrieval.used_tokens_estimate }} tokens</span>
                <small v-if="aiDraftRetrieval.semantic_requested && aiDraftRetrieval.mode !== 'semantic'">
                    语义匹配已回退：{{ aiDraftRetrieval.semantic_unavailable_reason || '条件不足' }}
                </small>
            </div>
            <div class="ai-draft-actions">
                <el-button class="dialog-cancel" native-type="button" @click="aiTopic = buildAiDraftSeed()">使用当前内容填充</el-button>
                <el-button
                    class="dialog-cancel"
                    native-type="button"
                    :disabled="!selectedAiDraftPack || !aiTopic.trim() || aiDraftRetrievalLoading"
                    :loading="aiDraftRetrievalLoading"
                    @click="previewAiDraftRetrieval"
                >
                    预览引用
                </el-button>
                <el-button class="dialog-generate" type="primary" native-type="button" @click="handleAiGenerate" :loading="aiGenerating">
                    {{ aiGenerating ? '生成中...' : '生成草稿' }}
                </el-button>
            </div>
        </section>

        <section class="editor-content">
            <div class="form-section title-section">
                <label class="field-label">标题</label>
                <el-input
                    v-model="article.title"
                    placeholder="给这份文档起个名字"
                    class="title-input"
                    :prefix-icon="Document"
                />
            </div>

            <div class="form-row four-cols">
                <div class="form-section">
                    <label class="field-label">类型</label>
                    <el-select v-model="article.resource_type" placeholder="选择类型" class="meta-select" :prefix-icon="Grid">
                        <el-option v-for="type in documentTypes" :key="type.value" :label="type.label" :value="type.value" />
                    </el-select>
                </div>
                <div class="form-section">
                    <label class="field-label">状态</label>
                    <el-select v-model="article.document_status" placeholder="选择状态" class="meta-select" :prefix-icon="Flag">
                        <el-option v-for="status in documentStatuses" :key="status.value" :label="status.label" :value="status.value" />
                    </el-select>
                </div>
                <div class="form-section">
                    <label class="field-label">可见性</label>
                    <el-select v-model="article.visibility" placeholder="选择可见性" class="meta-select" :prefix-icon="View">
                        <el-option label="私有" value="private" />
                        <el-option label="公开" value="public" />
                        <el-option label="团队" value="team" />
                    </el-select>
                </div>
                <div class="form-section">
                    <label class="field-label">兼容分类</label>
                    <el-select v-model="article.category" placeholder="兼容旧文章分类" class="meta-select" :prefix-icon="Collection">
                        <el-option v-for="category in categories" :key="category.value" :label="category.label" :value="category.value" />
                    </el-select>
                </div>
            </div>

            <div class="form-section">
                <label class="field-label">来源链接</label>
                <el-input
                    v-model="article.source_url"
                    placeholder="可选：网页、仓库、论文或资料来源链接"
                    class="source-input"
                    :prefix-icon="Link"
                />
            </div>

            <div class="form-section">
                <label class="field-label">标签</label>
                <el-input v-model="newTag" placeholder="输入标签后按 Enter" class="tag-input" @keyup.enter="addTag" clearable />
            </div>

            <div v-if="article.tags.length" class="tags-display-section">
                <el-tag v-for="(tag, index) in article.tags" :key="index" closable @close="removeTag(index)" class="article-tag">
                    {{ tag }}
                </el-tag>
            </div>

            <div class="form-section editor-section">
                <div class="editor-toolbar-row">
                    <div>
                        <label class="field-label">正文</label>
                        <h2>文档内容</h2>
                    </div>
                    <div class="editor-tools">
                        <span class="content-stats">{{ contentStats.words }} 词 / {{ contentStats.paragraphs }} 段</span>
                        <el-button size="small" @click="handleClearContent" class="clear-button">清空</el-button>
                    </div>
                </div>
                <div class="editor-wrapper">
                    <div ref="editorRef" class="quill-editor"></div>
                </div>
            </div>

            <div class="form-section">
                <label class="field-label">摘要</label>
                <el-input
                    v-model="article.summary"
                    type="textarea"
                    placeholder="写一段简洁摘要。留空时会根据正文自动截取。"
                    :rows="3"
                    class="summary-input"
                    :prefix-icon="CopyDocument"
                />
            </div>

            <div class="action-section">
                <el-button @click="handleCancel" class="cancel-button">
                    <ArrowLeft />
                    <span>取消</span>
                </el-button>
                <el-button type="primary" @click="handleSave" :loading="saving" class="save-button">
                    <Upload />
                    <span>{{ isEditing ? '保存修改' : '发布文档' }}</span>
                </el-button>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useElMessage } from '@/hooks/useMessage'
import { usePermission } from '@/hooks/usePermission'
import {
    ArrowLeft,
    Collection,
    CopyDocument,
    Document,
    Flag,
    Grid,
    Link,
    Upload,
    View
} from '@element-plus/icons-vue'
import articleApi from '@/api/modules/article'
import { aiArticleService, aiOpsService } from '@/api/modules/ai'
import type { AIRetrievalMeta } from '@/api/modules/ai/interface'
import contextPackApi, { type ContextPack } from '@/api/modules/contextPacks'
import { getApiUrl } from '@/api/config'
import { useGlobalStore } from '@/store'
import { marked } from 'marked'

// @ts-ignore
import Quill from 'quill'
import 'quill/dist/quill.snow.css'

import { getHighlight } from '@/utils/highlight'
import 'highlight.js/styles/github.css'

const router = useRouter()
const route = useRoute()
const { message } = useElMessage()
const { hasPermission } = usePermission()
const globalStore = useGlobalStore()
const hljs = getHighlight()
const AppId = import.meta.env.VITE_APP_ID

const aiDialogVisible = ref(false)
const aiTopic = ref('')
const aiGenerating = ref(false)
const aiDraftPacks = ref<ContextPack[]>([])
const aiDraftPacksLoading = ref(false)
const aiDraftContextPackId = ref<number | null>(null)
const aiDraftAllowEmbedding = ref(false)
const aiDraftRetrieval = ref<AIRetrievalMeta | null>(null)
const aiDraftRetrievalLoading = ref(false)

const editorRef = ref<HTMLElement | null>(null)
let quillEditor: Quill | null = null

const documentTypes = [
    { value: 'note', label: '笔记' },
    { value: 'technical-doc', label: '技术文档' },
    { value: 'tutorial', label: '教程' },
    { value: 'project-record', label: '项目记录' },
    { value: 'paper', label: '论文' },
    { value: 'idea', label: '灵感' },
    { value: 'qa-record', label: '问答记录' },
    { value: 'other', label: '其他' }
]

const documentStatuses = [
    { value: 'published', label: '已发布' },
    { value: 'draft', label: '草稿' },
    { value: 'organized', label: '已整理' },
    { value: 'reviewing', label: '待复习' },
    { value: 'archived', label: '已归档' }
]

const categories = [
    { value: 'frontend', label: '前端' },
    { value: 'backend', label: '后端' },
    { value: 'database', label: '数据库' },
    { value: 'algorithm', label: '算法' },
    { value: 'devops', label: 'DevOps' },
    { value: 'architecture', label: '架构' },
    { value: 'ai', label: 'AI' },
    { value: 'other', label: '其他' }
]

const articleId = computed(() => route.params.id as string)
const isEditing = computed(() => !!articleId.value)
const pageTitle = computed(() => isEditing.value ? '编辑文档' : '新建文档')
const canUseAiDraft = computed(() => hasPermission('ai:access') || hasPermission('ai:manage'))
const selectedAiDraftPack = computed(() => {
    return aiDraftPacks.value.find(pack => pack.id === aiDraftContextPackId.value) || null
})
const aiDraftRagHint = computed(() => {
    if (!selectedAiDraftPack.value) return '不选择上下文包时不会检索资料'
    return aiDraftAllowEmbedding.value
        ? '仅在已配置向量并建好索引时调用 embedding'
        : '默认使用关键词检索，不产生 embedding 成本'
})

const article = reactive({
    id: '',
    title: '',
    category: 'other',
    resource_type: 'note',
    document_status: 'published',
    visibility: 'private',
    source_url: '',
    tags: [] as string[],
    content: '',
    summary: '',
    createTime: ''
})

const newTag = ref('')
const contentStats = reactive({
    words: 0,
    paragraphs: 0
})
const saving = ref(false)

const stripHtmlToText = (value = '') => {
    return value.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
}

const buildAiDraftSeed = () => {
    const pieces = []
    if (article.title.trim()) pieces.push(`标题：${article.title.trim()}`)
    if (article.summary.trim()) pieces.push(`摘要：${article.summary.trim()}`)
    if (article.tags.length) pieces.push(`标签：${article.tags.join('、')}`)

    const currentText = stripHtmlToText(article.content).slice(0, 500)
    if (currentText) pieces.push(`已有内容：${currentText}`)

    return pieces.join('\n')
}

const loadAiDraftPacks = async () => {
    if (!globalStore.token || aiDraftPacksLoading.value || aiDraftPacks.value.length) return

    aiDraftPacksLoading.value = true
    try {
        aiDraftPacks.value = await contextPackApi.getList()
    } catch (error) {
        console.error('Load AI draft context packs failed:', error)
        aiDraftPacks.value = []
    } finally {
        aiDraftPacksLoading.value = false
    }
}

const getDraftRetrievalLabel = (retrieval: AIRetrievalMeta | null) => {
    if (!retrieval) return '未检索上下文'
    if (retrieval.mode === 'semantic') return '已按语义匹配资料'
    if (retrieval.semantic_requested && retrieval.mode !== 'semantic') return '语义匹配不可用，已按关键词匹配'
    return '已按关键词匹配资料'
}

const resolveAiErrorMessage = (error: any) => {
    return error?.response?.data?.msg
        || error?.response?.data?.message
        || error?.msg
        || error?.message
        || 'AI 起草失败，请检查 AI 配置或稍后重试'
}

const extractJsonText = (value: string) => {
    const trimmed = value.trim()
    const fenced = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i)
    const candidate = fenced?.[1]?.trim() || trimmed
    if (candidate.startsWith('{') && candidate.endsWith('}')) return candidate
    const match = candidate.match(/\{[\s\S]*\}/)
    return match?.[0] || ''
}

const decodeJsonishStringValue = (value: string) => {
    try {
        return JSON.parse(`"${value}"`)
    } catch {
        return value
            .replace(/\\r\\n/g, '\n')
            .replace(/\\n/g, '\n')
            .replace(/\\r/g, '\n')
            .replace(/\\t/g, '\t')
            .replace(/\\"/g, '"')
            .replace(/\\\\/g, '\\')
    }
}

const readJsonishStringField = (source: string, field: string) => {
    const keys = [`"${field}"`, `'${field}'`]

    for (const key of keys) {
        const keyIndex = source.indexOf(key)
        if (keyIndex < 0) continue

        const colonIndex = source.indexOf(':', keyIndex + key.length)
        if (colonIndex < 0) continue

        let cursor = colonIndex + 1
        while (cursor < source.length && /\s/.test(source[cursor])) cursor++

        const quote = source[cursor]
        if (quote !== '"' && quote !== "'") continue

        cursor++
        let value = ''
        let escaped = false

        while (cursor < source.length) {
            const char = source[cursor]

            if (escaped) {
                value += `\\${char}`
                escaped = false
                cursor++
                continue
            }

            if (char === '\\') {
                escaped = true
                cursor++
                continue
            }

            if (char === quote) {
                const rest = source.slice(cursor + 1)
                if (/^\s*(,|\})/.test(rest)) {
                    return decodeJsonishStringValue(value).trim()
                }
            }

            value += char
            cursor++
        }
    }

    return ''
}

const readJsonishTags = (source: string) => {
    const match = source.match(/["']tags["']\s*:\s*\[([\s\S]*?)\]/)
    if (!match) return []

    try {
        const parsed = JSON.parse(`[${match[1]}]`)
        return Array.isArray(parsed) ? parsed.map((tag: unknown) => String(tag).trim()).filter(Boolean) : []
    } catch {
        return Array.from(match[1].matchAll(/["']([^"']+)["']/g))
            .map(item => item[1].trim())
            .filter(Boolean)
    }
}

const repairJsonishDraft = (value: unknown) => {
    if (typeof value !== 'string') return null

    const candidate = extractJsonText(value) || value.trim()
    if (!candidate || !/["'](?:title|content|summary|category|tags)["']\s*:/.test(candidate)) return null

    const content = readJsonishStringField(candidate, 'content')
    if (!content) return null

    return {
        title: readJsonishStringField(candidate, 'title'),
        content,
        summary: readJsonishStringField(candidate, 'summary'),
        category: readJsonishStringField(candidate, 'category'),
        tags: readJsonishTags(candidate)
    }
}

const looksLikeDraftEnvelope = (value: string) => {
    const trimmed = value.trim()
    return trimmed.startsWith('{') && /["']content["']\s*:/.test(trimmed)
}

const parseJsonDraft = (value: unknown): any | null => {
    if (!value) return null
    if (typeof value === 'object') return value
    if (typeof value !== 'string') return null

    const jsonText = extractJsonText(value)
    if (!jsonText) return null

    try {
        return JSON.parse(jsonText)
    } catch {
        return null
    }
}

const normalizeAiDraft = (raw: any, fallbackTitle: string) => {
    let payload = raw?.data || raw
    const parsedPayload = parseJsonDraft(payload)
    if (parsedPayload) {
        payload = parsedPayload
    } else {
        const repairedPayload = repairJsonishDraft(payload)
        if (repairedPayload) payload = repairedPayload
    }

    if (!payload || typeof payload !== 'object') {
        throw new Error('AI 返回格式不正确')
    }

    let nestedContent = payload.content
    const parsedContent = parseJsonDraft(nestedContent)
    if (parsedContent && typeof parsedContent === 'object' && (parsedContent.content || parsedContent.title)) {
        payload = { ...payload, ...parsedContent }
        nestedContent = parsedContent.content
    } else {
        const repairedContent = repairJsonishDraft(nestedContent)
        if (repairedContent) {
            payload = { ...payload, ...repairedContent }
            nestedContent = repairedContent.content
        }
    }

    if (typeof nestedContent !== 'string') {
        throw new Error('AI 返回的正文不是可编辑文本')
    }

    let content = decodeJsonishStringValue(nestedContent).trim()
    const repairedEnvelope = repairJsonishDraft(content)
    if (repairedEnvelope) {
        payload = { ...payload, ...repairedEnvelope }
        content = repairedEnvelope.content
    }

    if (!content) {
        throw new Error('AI 没有返回正文内容')
    }
    if (looksLikeDraftEnvelope(content)) {
        throw new Error('AI 返回仍是 JSON 外壳，已阻止写入编辑器，请重新生成')
    }

    return {
        title: typeof payload.title === 'string' ? payload.title.trim() : fallbackTitle.slice(0, 28),
        content,
        summary: typeof payload.summary === 'string' ? payload.summary.trim() : '',
        category: typeof payload.category === 'string' ? payload.category : '',
        tags: Array.isArray(payload.tags)
            ? payload.tags.map((tag: unknown) => String(tag).trim()).filter(Boolean)
            : []
    }
}

const openAiDialog = () => {
    if (!globalStore.token) {
        message.warning('请先登录后再使用 AI 起草')
        return
    }
    if (!canUseAiDraft.value) {
        message.warning('当前账号没有 AI 起草权限')
        return
    }

    if (!aiTopic.value.trim()) {
        aiTopic.value = buildAiDraftSeed()
    }

    aiDialogVisible.value = true
    void loadAiDraftPacks()
    message.info('已打开 AI 起草面板')
}

const previewAiDraftRetrieval = async () => {
    if (!selectedAiDraftPack.value) {
        message.warning('请先选择上下文包')
        return
    }

    const query = aiTopic.value.trim()
    if (!query) {
        message.warning('请先填写起草要求')
        return
    }

    aiDraftRetrievalLoading.value = true
    try {
        const result = await aiOpsService.previewContextPackRetrieval(selectedAiDraftPack.value.id, {
            query,
            context_token_budget: 2600,
            allow_embedding: Boolean(aiDraftAllowEmbedding.value)
        })
        aiDraftRetrieval.value = result.retrieval
        const hitCount = result.retrieval?.snippets.length ?? 0
        message.success(`${getDraftRetrievalLabel(result.retrieval)}预览完成，命中 ${hitCount} 段`)
    } catch (error: any) {
        console.error('Preview AI draft retrieval failed:', error)
        message.error(error?.msg || error?.response?.data?.msg || '预览引用失败')
    } finally {
        aiDraftRetrievalLoading.value = false
    }
}

const handleAiGenerate = async () => {
    if (!globalStore.token) {
        message.warning('请先登录后再使用 AI 起草')
        return
    }
    if (!canUseAiDraft.value) {
        message.warning('当前账号没有 AI 起草权限')
        return
    }

    const topic = aiTopic.value.trim()
    if (!topic) {
        message.warning('请输入主题或文档概要')
        return
    }
    if (aiGenerating.value) return

    aiGenerating.value = true
    aiDraftRetrieval.value = null
    try {
        message.info('正在调用 AI 起草，请稍候')
        const res = await aiArticleService.generateArticle({
            topic,
            context_pack_id: aiDraftContextPackId.value || undefined,
            context_token_budget: 2600,
            allow_embedding: Boolean(aiDraftContextPackId.value && aiDraftAllowEmbedding.value)
        })
        const data = normalizeAiDraft(res, topic)
        aiDraftRetrieval.value = res.retrieval || null

        article.title = data.title || article.title
        article.summary = data.summary || article.summary
        if (data.category) article.category = data.category
        if (data.tags.length) article.tags = data.tags

        const htmlContent = await marked.parse(data.content)
        if (quillEditor) {
            quillEditor.setText('')
            quillEditor.clipboard.dangerouslyPasteHTML(0, htmlContent)
            article.content = quillEditor.root.innerHTML
            updateStatsFromEditor()
            highlightEditorCode()
        } else {
            article.content = htmlContent
        }

        if (!article.title.trim() && !stripHtmlToText(article.content)) {
            throw new Error('AI 没有返回可用草稿')
        }

        const retrievalText = aiDraftRetrieval.value
            ? `，${getDraftRetrievalLabel(aiDraftRetrieval.value)}命中 ${aiDraftRetrieval.value.snippets.length} 段`
            : ''
        message.success(`AI 草稿已生成${retrievalText}`)
        aiDialogVisible.value = false
    } catch (error: any) {
        console.error('AI generation failed', error)
        message.error(resolveAiErrorMessage(error))
    } finally {
        aiGenerating.value = false
    }
}

const addTag = () => {
    const tag = newTag.value.trim()
    if (tag && !article.tags.includes(tag)) {
        article.tags.push(tag)
        newTag.value = ''
    }
}

const removeTag = (index: number) => {
    article.tags.splice(index, 1)
}

const handleImageUpload = async (file: File): Promise<string> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(getApiUrl('/upload'), {
        method: 'POST',
        credentials: 'include',
        headers: {
            Authorization: globalStore.token || '',
            'APP-ID': AppId || ''
        },
        body: formData
    })

    const payload = await response.json()
    if (!response.ok || payload.status !== 0) {
        throw new Error(payload.msg || '图片上传失败')
    }

    const uploadedUrl = payload.data?.url
    if (!uploadedUrl) throw new Error('后端未返回图片地址')

    const apiPath = uploadedUrl.startsWith('/api/') ? uploadedUrl.slice(4) : uploadedUrl
    return getApiUrl(apiPath)
}

const highlightEditorCode = () => {
    const codeBlocks = quillEditor?.root.querySelectorAll('pre.ql-code-block code')
    codeBlocks?.forEach((block: any) => {
        hljs.highlightElement(block)
    })
}

const updateStatsFromEditor = () => {
    if (!quillEditor) return

    const text = quillEditor.getText()
    const words = text.trim().replace(/\s+/g, ' ').split(' ').filter((word: string) => word.length > 0)
    contentStats.words = text.trim() ? words.length : 0
    contentStats.paragraphs = text.trim()
        ? text.trim().split(/\n+/).filter((paragraph: string) => paragraph.length > 0).length
        : 0
}

const initEditor = () => {
    if (!editorRef.value) return

    const toolbarOptions = [
        ['bold', 'italic', 'underline', 'strike'],
        ['blockquote', 'code-block'],
        [{ header: 1 }, { header: 2 }],
        [{ list: 'ordered' }, { list: 'bullet' }],
        [{ indent: '-1' }, { indent: '+1' }],
        [{ size: ['small', false, 'large', 'huge'] }],
        [{ header: [1, 2, 3, 4, 5, 6, false] }],
        [{ color: [] }, { background: [] }],
        [{ align: [] }],
        ['clean'],
        ['link', 'image', 'video']
    ]

    const toolbarHandlers = {
        image: function () {
            const input = document.createElement('input')
            input.type = 'file'
            input.accept = 'image/*'
            input.onchange = async (event) => {
                const target = event.target as HTMLInputElement
                if (!target.files || !target.files[0]) return

                const file = target.files[0]
                try {
                    message.info('正在插入图片...')
                    const imageUrl = await handleImageUpload(file)
                    message.success('图片已插入')

                    const selection = quillEditor?.getSelection()
                    quillEditor?.insertEmbed(selection?.index ?? quillEditor.getLength(), 'image', imageUrl)
                } catch (error) {
                    message.error('图片插入失败')
                    console.error('Image upload error:', error)
                }
            }
            input.click()
        },
        clean: function () {
            if (confirm('确定清空全部文档内容吗？')) {
                quillEditor?.setText('')
                message.success('内容已清空')
            }
        }
    }

    quillEditor = new Quill(editorRef.value, {
        theme: 'snow',
        modules: {
            toolbar: {
                container: toolbarOptions,
                handlers: toolbarHandlers
            }
        },
        placeholder: '开始编写一份可复用的知识文档...',
        scrollingContainer: '.quill-editor'
    })

    quillEditor.on('text-change', () => {
        article.content = quillEditor?.root.innerHTML || ''
        setTimeout(highlightEditorCode, 0)
        updateStatsFromEditor()
    })

    if (article.content) quillEditor.root.innerHTML = article.content
    setTimeout(() => {
        highlightEditorCode()
        updateStatsFromEditor()
    }, 100)
}

const loadArticle = async () => {
    if (!isEditing.value) return

    try {
        const data: any = await articleApi.getDetail(articleId.value)
        if (!data) return

        article.id = String(data.id)
        article.title = data.title
        article.content = data.content
        article.summary = data.summary || ''
        article.category = data.category || 'other'
        article.resource_type = data.resource_type || 'note'
        article.document_status = data.document_status || data.status || 'published'
        article.visibility = data.visibility || 'private'
        article.source_url = data.source_url || ''
        article.tags = data.tags || []
        article.createTime = data.created_at

        if (quillEditor) {
            quillEditor.root.innerHTML = article.content
            setTimeout(() => {
                highlightEditorCode()
                updateStatsFromEditor()
            }, 100)
        }
    } catch (err) {
        console.error('Failed to load document:', err)
        message.error('文档加载失败')
    }
}

onMounted(async () => {
    if (!globalStore.token) {
        message.warning('请先登录后再写文档')
        router.push({ path: '/login', query: { redirect: route.fullPath } })
        return
    }

    await loadArticle()
    nextTick(() => {
        initEditor()
    })
})

const handleSave = async () => {
    if (!article.title.trim()) {
        message.warning('请输入标题')
        return
    }

    if (!article.content.trim()) {
        message.warning('请输入文档内容')
        return
    }

    if (!article.summary.trim()) {
        article.summary = article.content.replace(/<[^>]*>/g, '').substring(0, 180) + '...'
    }

    saving.value = true

    try {
        const params = {
            title: article.title,
            content: article.content,
            summary: article.summary,
            category: article.category,
            resource_type: article.resource_type,
            document_status: article.document_status,
            visibility: article.visibility,
            source_url: article.source_url,
            status: article.document_status,
            tags: article.tags
        }

        if (isEditing.value) {
            await articleApi.update(article.id, params)
            message.success('文档已更新')
        } else {
            const res = await articleApi.create(params)
            article.id = String(res.id)
            message.success('文档已发布')
        }

        router.push('/essays')
    } catch (error) {
        message.error('保存失败，请稍后重试')
        console.error('Save error:', error)
    } finally {
        saving.value = false
    }
}

const handleClearContent = () => {
    if (confirm('确定清空全部文档内容吗？')) {
        quillEditor?.setText('')
        article.content = ''
        contentStats.words = 0
        contentStats.paragraphs = 0
        message.success('内容已清空')
    }
}

const handleCancel = () => {
    if (article.title || article.content) {
        if (confirm('确定放弃当前编辑吗？')) {
            router.push('/essays')
        }
    } else {
        router.push('/essays')
    }
}
</script>

<style scoped>
/* Hallmark · macrostructure: document workbench · theme: white minimal · enrichment: none */
.document-editor-page {
    width: 100%;
    min-height: calc(100vh - 140px);
    padding: 56px 0 80px;
    background: transparent;
    color: var(--text-primary);
}

.editor-header,
.editor-content {
    width: var(--page-width);
    margin: 0 auto;
}

.editor-header {
    padding: 32px 0 28px;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
}

.eyebrow,
.field-label,
.content-stats,
.ai-dialog-eyebrow,
.ai-input-label,
.ai-dialog-tags span {
    font-family: var(--font-mono);
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 700;
}

.editor-header h1 {
    margin: 18px 0 0;
    color: var(--text-primary);
    font-size: clamp(40px, 6vw, 64px);
    font-weight: 650;
    line-height: 1;
    letter-spacing: 0;
}

.editor-header p {
    max-width: 720px;
    margin: 16px 0 0;
    color: var(--text-secondary);
    font-size: 18px;
    line-height: 1.7;
}

.ai-help-btn,
.cancel-button,
.save-button,
.clear-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: 0;
    border-radius: 10px;
    font-weight: 600;
}

.ai-help-btn,
.save-button {
    min-height: 40px;
    padding: 0 16px;
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.ai-draft-panel {
    width: var(--page-width);
    margin: 0 auto 18px;
    padding: 22px;
    border-radius: 12px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.ai-draft-header {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    gap: 16px;
    align-items: center;
}

.ai-draft-header h2 {
    margin: 6px 0 0;
    color: var(--text-primary);
    font-size: 28px;
    line-height: 1.15;
}

.ai-draft-actions {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 12px;
}

.editor-content {
    padding: 32px;
    background: var(--surface);
    border-radius: 12px;
    box-shadow: var(--card-shadow);
}

.form-section {
    margin-bottom: 24px;
}

.title-section {
    margin-bottom: 28px;
}

.field-label {
    display: block;
    margin-bottom: 10px;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.form-row {
    display: grid;
    gap: 16px;
}

.four-cols {
    grid-template-columns: repeat(4, minmax(0, 1fr));
}

.title-input,
.meta-select,
.tag-input,
.source-input,
.summary-input {
    width: 100%;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner),
:deep(.el-select__wrapper) {
    min-height: 42px;
    border-radius: 10px;
    background: var(--surface);
    box-shadow: var(--ring);
}

.title-input :deep(.el-input__wrapper) {
    min-height: 56px;
}

.title-input :deep(.el-input__inner) {
    font-size: 24px;
    font-weight: 650;
}

.tags-display-section {
    margin: -8px 0 28px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.article-tag {
    min-height: 28px;
    padding: 0 10px;
    border: 0;
    border-radius: 9999px;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    box-shadow: var(--ring);
    font-weight: 600;
}

.editor-toolbar-row {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 14px;
}

.editor-toolbar-row h2 {
    margin: 0;
    color: var(--text-primary);
    font-size: 24px;
    font-weight: 650;
    line-height: 1.25;
}

.editor-tools {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.content-stats {
    display: inline-flex;
    align-items: center;
    min-height: 30px;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 700;
}

.clear-button,
.cancel-button {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.editor-wrapper {
    min-height: 620px;
    overflow: hidden;
    border-radius: 12px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.quill-editor {
    min-height: 620px;
    max-height: 760px;
    overflow-y: auto;
}

:deep(.ql-toolbar.ql-snow) {
    position: sticky;
    top: 0;
    z-index: 2;
    border: 0;
    background: var(--surface);
    box-shadow: var(--ring);
}

:deep(.ql-container.ql-snow) {
    border: 0;
    color: var(--text-primary);
    font-family: inherit;
    font-size: 16px;
    line-height: 1.75;
}

:deep(.ql-editor) {
    min-height: 560px;
    padding: 28px;
}

.summary-input :deep(.el-textarea__inner) {
    min-height: 112px;
    padding: 12px 14px;
    line-height: 1.7;
    resize: vertical;
}

.action-section {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 32px;
    padding-top: 24px;
    box-shadow: inset 0 1px 0 color-mix(in oklch, var(--text-primary) 8%, transparent);
}

.cancel-button,
.save-button {
    min-height: 40px;
    padding: 0 16px;
}

:global(.ai-dialog) {
    overflow: hidden;
    border-radius: 10px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

:global(.ai-dialog .el-dialog__header) {
    padding: 0;
    margin: 0;
}

:global(.ai-dialog .el-dialog__body) {
    padding: 0 28px 8px;
}

:global(.ai-dialog .el-dialog__footer) {
    padding: 18px 28px 28px;
    box-shadow: inset 0 1px 0 color-mix(in oklch, var(--text-primary) 8%, transparent);
}

.ai-dialog-header {
    min-height: 112px;
    padding: 28px 64px 22px 28px;
    display: flex;
    align-items: center;
    gap: 16px;
    background: var(--surface);
    box-shadow: inset 0 -1px 0 color-mix(in oklch, var(--text-primary) 8%, transparent);
}

.ai-dialog-mark {
    width: 46px;
    height: 46px;
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    color: var(--button-fg);
    background: var(--button-bg);
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 700;
    box-shadow: var(--ring);
}

.ai-dialog-eyebrow,
.ai-input-label {
    display: block;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.ai-dialog-header h2 {
    margin: 6px 0 0;
    color: var(--text-primary);
    font-size: 28px;
    font-weight: 650;
    line-height: 1.15;
}

.ai-tip {
    margin: 22px 0 14px;
    color: var(--text-secondary);
    line-height: 1.7;
}

.ai-dialog-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 22px;
}

.ai-dialog-tags span {
    display: inline-flex;
    align-items: center;
    min-height: 26px;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 700;
}

.ai-input-label {
    margin-bottom: 10px;
}

.ai-context-controls {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(220px, 320px);
    gap: 14px;
    align-items: end;
    margin-bottom: 18px;
}

.ai-context-select {
    width: 100%;
}

.ai-rag-toggle {
    min-height: 42px;
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    gap: 4px 8px;
    align-items: center;
    padding: 8px 10px;
    border-radius: 10px;
    color: var(--text-primary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    cursor: pointer;
}

.ai-rag-toggle input {
    width: 16px;
    height: 16px;
    grid-row: span 2;
    accent-color: var(--button-bg);
}

.ai-rag-toggle span {
    font-size: 13px;
    font-weight: 700;
}

.ai-rag-toggle small {
    min-width: 0;
    color: var(--text-muted);
    font-size: 12px;
    line-height: 1.35;
}

.ai-rag-toggle.disabled {
    cursor: not-allowed;
    opacity: 0.68;
}

.ai-rag-result {
    margin-top: 12px;
    padding: 12px 14px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px 12px;
    align-items: center;
    border-radius: 10px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.ai-rag-result strong {
    color: var(--text-primary);
}

.ai-rag-result small {
    color: var(--text-muted);
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.dialog-cancel,
.dialog-generate {
    min-height: 40px;
    padding: 0 16px;
    border: 0;
    border-radius: 10px;
    font-weight: 600;
}

.dialog-cancel {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.dialog-generate {
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

@media (max-width: 1100px) {
    .four-cols {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 760px) {
    .editor-header,
    .editor-toolbar-row,
    .ai-draft-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .four-cols {
        grid-template-columns: 1fr;
    }

    .ai-draft-header {
        display: flex;
    }

    .ai-draft-actions {
        justify-content: flex-start;
    }

    .ai-context-controls {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 640px) {
    .document-editor-page {
        padding: 32px 0 56px;
    }

    .editor-content {
        padding: 20px;
    }

    .editor-wrapper,
    .quill-editor {
        min-height: 500px;
    }

    :deep(.ql-editor) {
        min-height: 440px;
        padding: 20px;
    }

    .action-section {
        flex-direction: column-reverse;
    }

    .cancel-button,
    .save-button {
        width: 100%;
    }
}
</style>
