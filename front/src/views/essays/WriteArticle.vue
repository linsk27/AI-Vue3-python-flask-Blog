<template>
    <div class="write-article-container">
        <section class="write-article-header">
            <div class="header-content">
                <span class="eyebrow">Article Studio</span>
                <div class="title-row">
                    <div>
                        <h1 class="write-title">{{ pageTitle }}</h1>
                        <p class="write-subtitle">{{ labels.subtitle }}</p>
                    </div>
                    <el-button class="ai-help-btn" @click="openAiDialog">
                        <Grid />
                        <span>{{ labels.aiAssist }}</span>
                    </el-button>
                </div>
            </div>
        </section>

        <el-dialog v-model="aiDialogVisible" width="640px" :close-on-click-modal="false" custom-class="ai-dialog">
            <template #header>
                <div class="ai-dialog-header">
                    <span class="ai-dialog-mark">AI</span>
                    <div>
                        <span class="ai-dialog-eyebrow">Draft Assistant</span>
                        <h2>{{ labels.aiDialogTitle }}</h2>
                    </div>
                </div>
            </template>
            <div class="ai-dialog-content">
                <p class="ai-tip">{{ labels.aiTip }}</p>
                <div class="ai-dialog-tags">
                    <span>结构草稿</span>
                    <span>标题摘要</span>
                    <span>分类标签</span>
                </div>
                <label class="ai-input-label">创作要求</label>
                <el-input v-model="aiTopic" type="textarea" :rows="6" :placeholder="labels.aiPlaceholder"
                    class="ai-input" />
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button class="dialog-cancel" @click="aiDialogVisible = false">{{ labels.cancel }}</el-button>
                    <el-button class="dialog-generate" type="primary" @click="handleAiGenerate" :loading="aiGenerating">
                        {{ aiGenerating ? labels.generating : labels.generate }}
                    </el-button>
                </span>
            </template>
        </el-dialog>

        <section class="write-article-content">
            <div class="form-section title-section">
                <label class="field-label">{{ labels.title }}</label>
                <el-input v-model="article.title" :placeholder="labels.titlePlaceholder" class="title-input"
                    :prefix-icon="Document" :class="{ 'title-input-focused': titleFocused }"
                    @focus="titleFocused = true" @blur="titleFocused = false" />
            </div>

            <div class="form-row">
                <div class="form-section half-width">
                    <label class="field-label">{{ labels.category }}</label>
                    <el-select v-model="article.category" :placeholder="labels.categoryPlaceholder" class="category-select"
                        :prefix-icon="Grid" :class="{ 'select-focused': categoryFocused }"
                        @focus="categoryFocused = true" @blur="categoryFocused = false">
                        <el-option v-for="category in categories" :key="category.value" :label="category.label"
                            :value="category.value" />
                    </el-select>
                </div>

                <div class="form-section half-width">
                    <label class="field-label">{{ labels.tags }}</label>
                    <el-input v-model="newTag" :placeholder="labels.tagPlaceholder" class="tag-input"
                        @keyup.enter="addTag" clearable :class="{ 'tag-input-focused': tagFocused }"
                        @focus="tagFocused = true" @blur="tagFocused = false" />
                </div>
            </div>

            <div v-if="article.tags.length" class="tags-display-section">
                <el-tag v-for="(tag, index) in article.tags" :key="index" closable @close="removeTag(index)"
                    class="article-tag">
                    {{ tag }}
                </el-tag>
            </div>

            <div class="form-section editor-section">
                <div class="editor-header">
                    <div>
                        <label class="field-label">{{ labels.body }}</label>
                        <h3 class="editor-title">{{ labels.content }}</h3>
                    </div>
                    <div class="editor-tools">
                        <span class="content-stats">{{ contentStats.words }} {{ labels.words }} · {{ contentStats.paragraphs }} {{ labels.paragraphs }}</span>
                        <el-button size="small" @click="handleClearContent" class="clear-button">{{ labels.clear }}</el-button>
                    </div>
                </div>
                <div class="editor-wrapper">
                    <div ref="editorRef" class="quill-editor"></div>
                </div>
            </div>

            <div class="form-section">
                <label class="field-label">{{ labels.summary }}</label>
                <el-input v-model="article.summary" type="textarea" :placeholder="labels.summaryPlaceholder" :rows="3"
                    class="summary-input" :prefix-icon="CopyDocument"
                    :class="{ 'summary-input-focused': summaryFocused }" @focus="summaryFocused = true"
                    @blur="summaryFocused = false" />
            </div>

            <div class="action-section">
                <el-button @click="handleCancel" class="cancel-button">
                    <ArrowLeft />
                    <span>{{ labels.cancel }}</span>
                </el-button>
                <el-button type="primary" @click="handleSave" :loading="saving" class="save-button">
                    <Upload />
                    <span>{{ isEditing ? labels.save : labels.publish }}</span>
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
import { Document, Grid, CopyDocument, ArrowLeft, Upload } from '@element-plus/icons-vue'
import articleApi from '@/api/modules/article'
import { aiArticleService } from '@/api/modules/ai'
import { marked } from 'marked'

// Import Quill rich text editor.
// @ts-ignore
import Quill from 'quill'
import 'quill/dist/quill.snow.css'

// Import code highlighting.
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

const router = useRouter()
const route = useRoute()
const { message } = useElMessage()
const { hasPermission } = usePermission()

const aiDialogVisible = ref(false)
const aiTopic = ref('')
const aiGenerating = ref(false)

const openAiDialog = () => {
    aiDialogVisible.value = true
}

const handleAiGenerate = async () => {
    if (!aiTopic.value.trim()) {
        message.warning('请输入文章主题或概要')
        return
    }

    aiGenerating.value = true
    try {
        const res = await aiArticleService.generateArticle(aiTopic.value)
        // @ts-ignore
        const data = res.data || res

        article.title = data.title || article.title
        article.summary = data.summary || article.summary

        if (data.category) article.category = data.category
        if (data.tags && Array.isArray(data.tags)) article.tags = data.tags

        if (quillEditor && data.content) {
            const htmlContent = await marked.parse(data.content)
            quillEditor.root.innerHTML = htmlContent
            article.content = quillEditor.root.innerHTML
            updateStatsFromEditor()
            highlightEditorCode()
        }

        message.success('AI 创作完成，已自动填充内容')
        aiDialogVisible.value = false
    } catch (error: any) {
        console.error('AI 生成失败', error)
        if (error.message && error.message.includes('timeout')) {
            message.error('AI 生成超时，请缩短主题描述后重试')
        } else {
            message.error('AI 生成失败，请检查 AI 配置后重试')
        }
    } finally {
        aiGenerating.value = false
    }
}

const editorRef = ref<HTMLElement | null>(null)
let quillEditor: Quill | null = null

const titleFocused = ref(false)
const categoryFocused = ref(false)
const tagFocused = ref(false)
const summaryFocused = ref(false)

const categories = [
    { value: 'frontend', label: '前端开发' },
    { value: 'backend', label: '后端开发' },
    { value: 'database', label: '数据库' },
    { value: 'algorithm', label: '算法' },
    { value: 'devops', label: 'DevOps' },
    { value: 'architecture', label: '架构设计' },
    { value: 'ai', label: '人工智能' },
    { value: 'other', label: '其他' }
]

const articleId = computed(() => route.params.id as string)
const isEditing = computed(() => !!articleId.value)
const pageTitle = computed(() => isEditing.value ? '编辑文章' : '创作新文章')

const labels = {
    subtitle: '整理观点、补齐结构，并发布为正式内容。',
    aiAssist: 'AI 帮写',
    aiDialogTitle: 'AI 智能创作助手',
    aiTip: '输入主题、大纲或核心观点，系统会生成可继续编辑的文章草稿。',
    aiPlaceholder: '例如：写一篇 Vue3 组合式 API 入门教程，包含响应式原理、生命周期和实战示例。',
    cancel: '取消',
    generate: '开始生成',
    generating: '正在生成',
    title: '标题',
    titlePlaceholder: '请输入文章标题',
    category: '分类',
    categoryPlaceholder: '请选择文章分类',
    tags: '标签',
    tagPlaceholder: '输入标签后按回车',
    body: '正文',
    content: '文章内容',
    words: '字',
    paragraphs: '段',
    clear: '清空',
    summary: '摘要',
    summaryPlaceholder: '请输入文章摘要。留空时可在发布流程中自动生成。',
    save: '保存修改',
    publish: '发布文章',
}

const article = reactive({
    id: '',
    title: '',
    category: '',
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

const handleImageUpload = (file: File): Promise<string> => {
    return new Promise((resolve) => {
        const formData = new FormData()
        formData.append('image', file)

        // Keep the previous mock upload behavior until a real upload API is connected.
        setTimeout(() => {
            const mockImageUrl = `https://picsum.photos/800/600?random=${Date.now()}`
            resolve(mockImageUrl)
        }, 1000)
    })
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
    let wordCount = 0
    if (text.trim()) {
        const englishWords = text.trim().replace(/\s+/g, ' ').split(' ').filter((word: string | any[]) => word.length > 0)
        const chineseChars = text.match(/[\u4e00-\u9fa5]/g) || []
        wordCount = englishWords.length + chineseChars.length
    }

    const paragraphCount = text.trim()
        ? text.trim().split(/\n+/).filter((paragraph: string | any[]) => paragraph.length > 0).length
        : 0

    contentStats.words = wordCount
    contentStats.paragraphs = text.trim() && paragraphCount === 0 ? 1 : paragraphCount
}

const initEditor = () => {
    if (!editorRef.value) return

    const toolbarOptions = [
        ['bold', 'italic', 'underline', 'strike'],
        ['blockquote', 'code-block'],
        [{ 'header': 1 }, { 'header': 2 }],
        [{ 'list': 'ordered' }, { 'list': 'bullet' }],
        [{ 'script': 'sub' }, { 'script': 'super' }],
        [{ 'indent': '-1' }, { 'indent': '+1' }],
        [{ 'direction': 'rtl' }],
        [{ 'size': ['small', false, 'large', 'huge'] }],
        [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
        [{ 'color': [] }, { 'background': [] }],
        [{ 'font': [] }],
        [{ 'align': [] }],
        ['clean'],
        ['link', 'image', 'video']
    ]

    const toolbarHandlers = {
        image: function () {
            const input = document.createElement('input')
            input.type = 'file'
            input.accept = 'image/*'
            input.onchange = async (e) => {
                const target = e.target as HTMLInputElement
                if (!target.files || !target.files[0]) return

                const file = target.files[0]
                try {
                    message.info('图片上传中...')
                    const imageUrl = await handleImageUpload(file)
                    message.success('图片上传成功')

                    const selection = quillEditor?.getSelection()
                    if (selection) {
                        quillEditor?.insertEmbed(selection.index, 'image', imageUrl)
                    } else {
                        quillEditor?.insertEmbed(quillEditor.getLength(), 'image', imageUrl)
                    }
                } catch (error) {
                    message.error('图片上传失败，请重试')
                    console.error('Image upload error:', error)
                }
            }
            input.click()
        },
        clean: function () {
            if (confirm('确定要清空所有内容吗？此操作不可撤销。')) {
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
        placeholder: '开始编写你的文章...',
        scrollingContainer: '.quill-editor'
    })

    quillEditor.on('text-change', () => {
        article.content = quillEditor?.root.innerHTML || ''
        setTimeout(highlightEditorCode, 0)
        updateStatsFromEditor()
    })

    quillEditor.on('selection-change', () => {
        setTimeout(highlightEditorCode, 0)
    })

    if (article.content) quillEditor.root.innerHTML = article.content

    setTimeout(() => {
        highlightEditorCode()
        updateStatsFromEditor()

        const cleanButton: HTMLElement | null = document.querySelector('.ql-toolbar.ql-snow button.ql-clean')
        if (cleanButton) {
            cleanButton.title = '清空内容'
            cleanButton.style.backgroundColor = '#fef2f2'
            cleanButton.style.borderColor = '#fecaca'
            cleanButton.style.color = '#dc2626'
            cleanButton.style.padding = '8px'
            cleanButton.style.borderRadius = '4px'
        }
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
        article.category = data.category || ''
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
        console.error('加载文章失败:', err)
        message.error('加载文章失败')
    }
}

onMounted(async () => {
    if (!hasPermission('article:create')) {
        message.warning('您没有权限创作文章，请联系管理员')
        router.push('/')
        return
    }

    await loadArticle()
    nextTick(() => {
        initEditor()
    })
})

const saving = ref(false)

const handleSave = async () => {
    if (!article.title.trim()) {
        message.warning('请输入文章标题')
        return
    }

    if (!article.content.trim()) {
        message.warning('请输入文章内容')
        return
    }

    if (!article.summary.trim()) {
        article.summary = article.content.replace(/<[^>]*>/g, '').substring(0, 150) + '...'
    }

    saving.value = true

    try {
        const params = {
            title: article.title,
            content: article.content,
            summary: article.summary,
            category: article.category,
            tags: article.tags
        }

        if (isEditing.value) {
            await articleApi.update(article.id, params)
            message.success('文章修改成功')
        } else {
            const res = await articleApi.create(params)
            article.id = String(res.id)
            message.success('文章发布成功')
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
    if (confirm('确定要清空所有内容吗？此操作不可撤销。')) {
        quillEditor?.setText('')
        article.content = ''
        contentStats.words = 0
        contentStats.paragraphs = 0
        message.success('内容已清空')
    }
}

const handleCancel = () => {
    if (article.title || article.content) {
        if (confirm('确定要放弃当前编辑内容吗？')) {
            router.push('/essays')
        }
    } else {
        router.push('/essays')
    }
}
</script>


<style scoped>
.write-article-container {
    width: 100%;
    min-height: calc(100vh - 140px);
    padding: 56px 0 80px;
    background: transparent;
    color: var(--text-primary);
}

.write-article-header,
.write-article-content {
    width: var(--page-width);
    margin: 0 auto;
}

.write-article-header {
    padding: 32px 0 28px;
}

.header-content {
    width: 100%;
}

.eyebrow,
.field-label,
.content-stats {
    font-family: var(--font-mono);
}

.eyebrow {
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

.title-row {
    margin-top: 18px;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
}

.write-title {
    margin: 0;
    color: var(--text-primary);
    font-size: clamp(40px, 6vw, 64px);
    font-weight: 600;
    line-height: 1;
    letter-spacing: 0;
}

.write-subtitle {
    max-width: 640px;
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
    font-weight: 500;
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}

.ai-help-btn,
.save-button {
    height: 40px;
    padding: 0 16px;
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.ai-help-btn:hover,
.save-button:hover:not(:disabled) {
    background: var(--button-hover);
}

.write-article-content {
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
    font-weight: 500;
    text-transform: uppercase;
}

.form-row {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.half-width {
    min-width: 0;
}

.title-input,
.category-select,
.tag-input,
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
    transition: box-shadow 180ms ease, background 180ms ease;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-select__wrapper.is-focused),
:deep(.el-textarea__inner:focus) {
    box-shadow: var(--ring), 0 0 0 3px rgba(10, 114, 239, 0.16);
}

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
    color: var(--text-primary);
    font-family: inherit;
}

:deep(.el-input__inner::placeholder),
:deep(.el-textarea__inner::placeholder) {
    color: var(--text-muted);
}

.title-input :deep(.el-input__wrapper) {
    min-height: 56px;
}

.title-input :deep(.el-input__inner) {
    font-size: 24px;
    font-weight: 600;
    letter-spacing: 0;
}

.tags-display-section {
    margin: -8px 0 28px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.article-tag {
    height: 28px;
    padding: 0 10px;
    border: 0;
    border-radius: 9999px;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    box-shadow: var(--ring);
    font-weight: 500;
}

.editor-section {
    margin-bottom: 28px;
}

.editor-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 14px;
}

.editor-title {
    margin: 0;
    color: var(--text-primary);
    font-size: 24px;
    font-weight: 600;
    line-height: 1.25;
    letter-spacing: 0;
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
    height: 30px;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
}

.clear-button,
.cancel-button {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.clear-button {
    height: 30px;
    padding: 0 12px;
}

.clear-button:hover,
.cancel-button:hover {
    background: var(--surface-hover);
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

:deep(.ql-editor.ql-blank::before) {
    color: var(--text-muted);
    font-style: normal;
}

:deep(.ql-editor h1),
:deep(.ql-editor h2),
:deep(.ql-editor h3) {
    color: var(--text-primary);
    font-weight: 600;
    letter-spacing: 0;
}

:deep(.ql-editor blockquote) {
    margin: 16px 0;
    padding: 8px 0 8px 16px;
    border-left: 3px solid #0a72ef;
    color: var(--text-secondary);
}

:deep(.ql-editor pre.ql-code-block),
:deep(.ql-editor pre) {
    margin: 16px 0;
    padding: 16px;
    border-radius: 10px;
    background: var(--surface-subtle);
    color: var(--text-primary);
    box-shadow: var(--ring);
    overflow-x: auto;
}

:deep(.ql-editor code) {
    border-radius: 4px;
    background: var(--surface-subtle);
    padding: 2px 5px;
    font-family: var(--font-mono);
    font-size: 0.9em;
}

:deep(.ql-editor img) {
    max-width: 100%;
    height: auto;
    border-radius: 12px;
    box-shadow: var(--ring);
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
    box-shadow: inset 0 1px 0 rgba(0, 0, 0, 0.08);
}

.cancel-button,
.save-button {
    height: 40px;
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

:global(.ai-dialog .el-dialog__headerbtn) {
    top: 18px;
    right: 18px;
    width: 32px;
    height: 32px;
    border-radius: 10px;
    transition: background 180ms ease;
}

:global(.ai-dialog .el-dialog__headerbtn:hover) {
    background: var(--surface-hover);
}

:global(.ai-dialog .el-dialog__body) {
    padding: 0 28px 8px;
}

:global(.ai-dialog .el-dialog__footer) {
    padding: 18px 28px 28px;
    box-shadow: inset 0 1px 0 rgba(0, 0, 0, 0.08);
}

.ai-dialog-header {
    min-height: 112px;
    padding: 28px 64px 22px 28px;
    display: flex;
    align-items: center;
    gap: 16px;
    background: var(--surface);
    box-shadow: inset 0 -1px 0 rgba(0, 0, 0, 0.08);
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
    font-weight: 600;
    box-shadow: var(--ring);
}

.ai-dialog-eyebrow,
.ai-input-label,
.ai-dialog-tags span {
    font-family: var(--font-mono);
}

.ai-dialog-eyebrow {
    display: block;
    margin-bottom: 6px;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
}

.ai-dialog-header h2 {
    margin: 0;
    color: var(--text-primary);
    font-size: 28px;
    font-weight: 600;
    line-height: 1.15;
    letter-spacing: 0;
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
    height: 26px;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 500;
}

.ai-input-label {
    display: block;
    margin-bottom: 10px;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
}

.ai-input :deep(.el-textarea__inner) {
    min-height: 172px !important;
    padding: 14px 16px;
    border-radius: 12px;
    color: var(--text-primary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-family: inherit;
    font-size: 15px;
    line-height: 1.75;
    resize: vertical;
}

.ai-input :deep(.el-textarea__inner:focus) {
    box-shadow: var(--ring), 0 0 0 3px rgba(10, 114, 239, 0.16);
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.dialog-cancel,
.dialog-generate {
    height: 40px;
    padding: 0 16px;
    border: 0;
    border-radius: 10px;
    font-weight: 500;
}

.dialog-cancel {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.dialog-cancel:hover {
    background: var(--surface-hover);
}

.dialog-generate {
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.dialog-generate:hover {
    background: var(--button-hover);
}

@media (max-width: 980px) {
    .title-row,
    .editor-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .ai-help-btn {
        align-self: flex-start;
    }

    .form-row {
        grid-template-columns: 1fr;
        gap: 0;
    }
}

@media (max-width: 640px) {
    .write-article-container {
        padding: 32px 0 56px;
    }

    .write-article-content {
        padding: 20px;
    }

    .write-title {
        letter-spacing: 0;
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

:where(h1, h2, h3) {
    font-family: var(--font-serif);
    font-weight: 500;
    letter-spacing: 0;
}

:where(p, li, small) {
    line-height: 1.6;
}

:where(button, .el-button, a) {
    letter-spacing: 0;
}

</style>
