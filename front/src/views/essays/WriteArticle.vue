<template>
    <div class="document-editor-page">
        <section class="editor-header">
            <div>
                <span class="eyebrow">Document Studio</span>
                <h1>{{ pageTitle }}</h1>
                <p>Capture source material, structure it clearly, and prepare it for context packs and AI reuse.</p>
            </div>
            <el-button class="ai-help-btn" @click="openAiDialog">
                <Grid />
                <span>AI Draft</span>
            </el-button>
        </section>

        <el-dialog v-model="aiDialogVisible" width="640px" :close-on-click-modal="false" custom-class="ai-dialog">
            <template #header>
                <div class="ai-dialog-header">
                    <span class="ai-dialog-mark">AI</span>
                    <div>
                        <span class="ai-dialog-eyebrow">Draft Assistant</span>
                        <h2>Generate a reusable knowledge document</h2>
                    </div>
                </div>
            </template>
            <div class="ai-dialog-content">
                <p class="ai-tip">
                    Describe the source, topic, or project context. AI will draft a document that you can edit, tag, and
                    add to a context pack later.
                </p>
                <div class="ai-dialog-tags">
                    <span>Structure</span>
                    <span>Summary</span>
                    <span>Tags</span>
                </div>
                <label class="ai-input-label">Draft request</label>
                <el-input
                    v-model="aiTopic"
                    type="textarea"
                    :rows="6"
                    placeholder="Example: Create a Vue 3 Composition API note with core concepts, examples, and interview questions."
                    class="ai-input"
                />
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button class="dialog-cancel" @click="aiDialogVisible = false">Cancel</el-button>
                    <el-button class="dialog-generate" type="primary" @click="handleAiGenerate" :loading="aiGenerating">
                        {{ aiGenerating ? 'Generating...' : 'Generate Draft' }}
                    </el-button>
                </span>
            </template>
        </el-dialog>

        <section class="editor-content">
            <div class="form-section title-section">
                <label class="field-label">Title</label>
                <el-input
                    v-model="article.title"
                    placeholder="Name this document"
                    class="title-input"
                    :prefix-icon="Document"
                />
            </div>

            <div class="form-row four-cols">
                <div class="form-section">
                    <label class="field-label">Type</label>
                    <el-select v-model="article.resource_type" placeholder="Select type" class="meta-select" :prefix-icon="Grid">
                        <el-option v-for="type in documentTypes" :key="type.value" :label="type.label" :value="type.value" />
                    </el-select>
                </div>
                <div class="form-section">
                    <label class="field-label">Status</label>
                    <el-select v-model="article.document_status" placeholder="Select status" class="meta-select" :prefix-icon="Flag">
                        <el-option v-for="status in documentStatuses" :key="status.value" :label="status.label" :value="status.value" />
                    </el-select>
                </div>
                <div class="form-section">
                    <label class="field-label">Visibility</label>
                    <el-select v-model="article.visibility" placeholder="Select visibility" class="meta-select" :prefix-icon="View">
                        <el-option label="Private" value="private" />
                        <el-option label="Public" value="public" />
                        <el-option label="Team" value="team" />
                    </el-select>
                </div>
                <div class="form-section">
                    <label class="field-label">Legacy Category</label>
                    <el-select v-model="article.category" placeholder="Compatibility" class="meta-select" :prefix-icon="Collection">
                        <el-option v-for="category in categories" :key="category.value" :label="category.label" :value="category.value" />
                    </el-select>
                </div>
            </div>

            <div class="form-section">
                <label class="field-label">Source URL</label>
                <el-input
                    v-model="article.source_url"
                    placeholder="Optional source link, repository, paper, or webpage URL"
                    class="source-input"
                    :prefix-icon="Link"
                />
            </div>

            <div class="form-section">
                <label class="field-label">Tags</label>
                <el-input v-model="newTag" placeholder="Type a tag and press Enter" class="tag-input" @keyup.enter="addTag" clearable />
            </div>

            <div v-if="article.tags.length" class="tags-display-section">
                <el-tag v-for="(tag, index) in article.tags" :key="index" closable @close="removeTag(index)" class="article-tag">
                    {{ tag }}
                </el-tag>
            </div>

            <div class="form-section editor-section">
                <div class="editor-toolbar-row">
                    <div>
                        <label class="field-label">Body</label>
                        <h2>Document Content</h2>
                    </div>
                    <div class="editor-tools">
                        <span class="content-stats">{{ contentStats.words }} words / {{ contentStats.paragraphs }} paragraphs</span>
                        <el-button size="small" @click="handleClearContent" class="clear-button">Clear</el-button>
                    </div>
                </div>
                <div class="editor-wrapper">
                    <div ref="editorRef" class="quill-editor"></div>
                </div>
            </div>

            <div class="form-section">
                <label class="field-label">Summary</label>
                <el-input
                    v-model="article.summary"
                    type="textarea"
                    placeholder="Write a compact summary. If left empty, a summary will be derived from the content."
                    :rows="3"
                    class="summary-input"
                    :prefix-icon="CopyDocument"
                />
            </div>

            <div class="action-section">
                <el-button @click="handleCancel" class="cancel-button">
                    <ArrowLeft />
                    <span>Cancel</span>
                </el-button>
                <el-button type="primary" @click="handleSave" :loading="saving" class="save-button">
                    <Upload />
                    <span>{{ isEditing ? 'Save Changes' : 'Publish Document' }}</span>
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
import { aiArticleService } from '@/api/modules/ai'
import { marked } from 'marked'

// @ts-ignore
import Quill from 'quill'
import 'quill/dist/quill.snow.css'

import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

const router = useRouter()
const route = useRoute()
const { message } = useElMessage()
const { hasPermission } = usePermission()

const aiDialogVisible = ref(false)
const aiTopic = ref('')
const aiGenerating = ref(false)

const editorRef = ref<HTMLElement | null>(null)
let quillEditor: Quill | null = null

const documentTypes = [
    { value: 'note', label: 'Note' },
    { value: 'technical-doc', label: 'Technical Doc' },
    { value: 'tutorial', label: 'Tutorial' },
    { value: 'project-record', label: 'Project Record' },
    { value: 'paper', label: 'Paper' },
    { value: 'idea', label: 'Idea' },
    { value: 'qa-record', label: 'Q&A Record' },
    { value: 'other', label: 'Other' }
]

const documentStatuses = [
    { value: 'published', label: 'Published' },
    { value: 'draft', label: 'Draft' },
    { value: 'organized', label: 'Organized' },
    { value: 'reviewing', label: 'Reviewing' },
    { value: 'archived', label: 'Archived' }
]

const categories = [
    { value: 'frontend', label: 'Frontend' },
    { value: 'backend', label: 'Backend' },
    { value: 'database', label: 'Database' },
    { value: 'algorithm', label: 'Algorithm' },
    { value: 'devops', label: 'DevOps' },
    { value: 'architecture', label: 'Architecture' },
    { value: 'ai', label: 'AI' },
    { value: 'other', label: 'Other' }
]

const articleId = computed(() => route.params.id as string)
const isEditing = computed(() => !!articleId.value)
const pageTitle = computed(() => isEditing.value ? 'Edit Document' : 'New Document')

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

const openAiDialog = () => {
    aiDialogVisible.value = true
}

const handleAiGenerate = async () => {
    if (!aiTopic.value.trim()) {
        message.warning('Please enter a topic or document brief')
        return
    }

    aiGenerating.value = true
    try {
        const res = await aiArticleService.generateArticle(aiTopic.value)
        const data = (res as any).data || res

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

        message.success('AI draft generated')
        aiDialogVisible.value = false
    } catch (error: any) {
        console.error('AI generation failed', error)
        message.error('AI generation failed. Please check AI configuration.')
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

const handleImageUpload = (file: File): Promise<string> => {
    return new Promise((resolve) => {
        const formData = new FormData()
        formData.append('image', file)
        setTimeout(() => {
            resolve(`https://picsum.photos/800/600?random=${Date.now()}`)
        }, 700)
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
                    message.info('Uploading image...')
                    const imageUrl = await handleImageUpload(file)
                    message.success('Image inserted')

                    const selection = quillEditor?.getSelection()
                    quillEditor?.insertEmbed(selection?.index ?? quillEditor.getLength(), 'image', imageUrl)
                } catch (error) {
                    message.error('Image upload failed')
                    console.error('Image upload error:', error)
                }
            }
            input.click()
        },
        clean: function () {
            if (confirm('Clear all document content?')) {
                quillEditor?.setText('')
                message.success('Content cleared')
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
        placeholder: 'Start writing a reusable knowledge document...',
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
        message.error('Failed to load document')
    }
}

onMounted(async () => {
    if (!hasPermission('article:create')) {
        message.warning('You do not have permission to create documents')
        router.push('/')
        return
    }

    await loadArticle()
    nextTick(() => {
        initEditor()
    })
})

const handleSave = async () => {
    if (!article.title.trim()) {
        message.warning('Please enter a title')
        return
    }

    if (!article.content.trim()) {
        message.warning('Please enter document content')
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
            message.success('Document updated')
        } else {
            const res = await articleApi.create(params)
            article.id = String(res.id)
            message.success('Document published')
        }

        router.push('/essays')
    } catch (error) {
        message.error('Save failed. Please try again later.')
        console.error('Save error:', error)
    } finally {
        saving.value = false
    }
}

const handleClearContent = () => {
    if (confirm('Clear all document content?')) {
        quillEditor?.setText('')
        article.content = ''
        contentStats.words = 0
        contentStats.paragraphs = 0
        message.success('Content cleared')
    }
}

const handleCancel = () => {
    if (article.title || article.content) {
        if (confirm('Discard current edits?')) {
            router.push('/essays')
        }
    } else {
        router.push('/essays')
    }
}
</script>

<style scoped>
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
    box-shadow: inset 0 1px 0 rgba(0, 0, 0, 0.08);
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
    .editor-toolbar-row {
        align-items: flex-start;
        flex-direction: column;
    }

    .four-cols {
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
