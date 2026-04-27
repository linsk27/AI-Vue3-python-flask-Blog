<template>
    <div class="ai-summary-container">
        <header class="summary-header">
            <div class="header-info">
                <span class="eyebrow">AI Summary</span>
                <h1 class="summary-title">AI 智能摘要</h1>
                <p class="summary-subtitle">将长文、文档或草稿压缩为可阅读、可复用的核心要点。</p>
            </div>
            <button class="control-btn" type="button" @click="clearContent">清空</button>
        </header>

        <main class="summary-content">
            <section class="input-section panel-card">
                <div class="section-header">
                    <h2 class="section-title">输入内容</h2>
                    <div class="section-actions">
                        <input ref="fileUploadRef" type="file" accept=".txt,.md,.doc,.docx" hidden @change="handleFileUpload">
                        <button class="control-btn" type="button" @click="fileUploadRef?.click()">上传文件</button>
                        <button class="control-btn" type="button" @click="pasteContent">粘贴内容</button>
                    </div>
                </div>

                <textarea v-model="originalContent" class="content-input" :placeholder="'在这里粘贴需要生成摘要的文章、文档或会议记录...'" rows="16"
                    :disabled="isGenerating"></textarea>

                <div class="input-stats">
                    <span>{{ originalContent.length }} 字符</span>
                    <span>{{ wordCount(originalContent) }} 单词</span>
                </div>
            </section>

            <aside class="side-panel">
                <section class="panel-card action-card">
                    <label class="setting-label">摘要长度</label>
                    <div class="setting-control">
                        <el-slider v-model="summaryLength" :min="100" :max="1000" :step="50" :disabled="isGenerating" />
                        <span class="setting-value">{{ summaryLength }} 字符</span>
                    </div>
                    <button class="generate-btn" type="button" @click="generateSummary"
                        :disabled="!originalContent.trim() || isGenerating">
                        {{ isGenerating ? '生成中...' : '生成摘要' }}
                    </button>
                </section>

                <section class="panel-card tips-section">
                    <h3 class="tips-title">使用建议</h3>
                    <ul class="tips-list">
                        <li>建议输入 500 字以上的文章，结果会更稳定。</li>
                        <li>摘要长度可以按阅读场景调整。</li>
                        <li>支持 TXT、MD 和 DOCX 文件。</li>
                        <li>生成后可复制到文章摘要或知识卡片中继续使用。</li>
                    </ul>
                </section>
            </aside>

            <section class="result-section panel-card">
                <div class="section-header">
                    <h2 class="section-title">生成结果</h2>
                    <div v-if="generatedSummary" class="section-actions">
                        <button class="control-btn" type="button" @click="copySummary">复制摘要</button>
                        <button class="control-btn" type="button" @click="regenerateSummary">重新生成</button>
                    </div>
                </div>

                <div v-if="generatedSummary" class="generated-summary-content">
                    <p>{{ generatedSummary }}</p>
                </div>
                <div v-else class="empty-result">
                    <strong>等待生成摘要</strong>
                    <span>输入内容并点击生成后，结果会显示在这里。</span>
                </div>

                <div v-if="generatedSummary" class="result-stats">
                    <span>{{ generatedSummary.length }} 字符</span>
                    <span>{{ wordCount(generatedSummary) }} 单词</span>
                    <span>摘要状态：已生成</span>
                </div>
            </section>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useElMessage } from '@/hooks/useMessage'
import { aiSummaryService } from '@/api/modules/ai'
import mammoth from 'mammoth'

const { message } = useElMessage()

const originalContent = ref('')
const generatedSummary = ref('')
const isGenerating = ref(false)
const summaryLength = ref(300)
const fileUploadRef = ref<HTMLInputElement | null>(null)

const wordCount = (value: string) => value.split(/\s+/).filter(Boolean).length

async function generateSummary() {
    if (!originalContent.value.trim() || isGenerating.value) return

    isGenerating.value = true
    try {
        const res = await aiSummaryService.generateSummary({
            content: originalContent.value,
            length: summaryLength.value,
        }) as any

        const summaryText = res?.reply || res?.data?.reply || res?.summary || res?.data?.summary
        if (!summaryText) {
            throw new Error(res?.error || res?.msg || '摘要生成失败')
        }

        generatedSummary.value = summaryText
        message.success('摘要生成成功')
    } catch (error: any) {
        const errorMsg = error.msg || error.message || '摘要生成失败，请稍后再试'
        message.error(errorMsg)
        console.error('Summary generation failed:', error)
    } finally {
        isGenerating.value = false
    }
}

function regenerateSummary() {
    generateSummary()
}

function clearContent() {
    originalContent.value = ''
    generatedSummary.value = ''
    message.success('内容已清空')
}

async function pasteContent() {
    try {
        originalContent.value = await navigator.clipboard.readText()
        message.success('内容已粘贴')
    } catch (error) {
        message.error('粘贴失败，请手动粘贴')
        console.error('Paste failed:', error)
    }
}

async function copySummary() {
    if (!generatedSummary.value) return

    try {
        await navigator.clipboard.writeText(generatedSummary.value)
        message.success('摘要已复制到剪贴板')
    } catch (error) {
        message.error('复制失败，请手动复制')
        console.error('Copy failed:', error)
    }
}

function handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement
    if (!input.files || input.files.length === 0) return

    const file = input.files[0]

    if (file.name.endsWith('.docx')) {
        const reader = new FileReader()
        reader.onload = (e) => {
            const arrayBuffer = e.target?.result as ArrayBuffer
            mammoth.extractRawText({ arrayBuffer })
                .then((result) => {
                    originalContent.value = result.value
                    message.success(`已上传 Word 文档：${file.name}`)
                })
                .catch((err) => {
                    console.error('Word parse failed:', err)
                    message.error('Word 文档解析失败')
                })
        }
        reader.onerror = () => message.error('文件读取失败')
        reader.readAsArrayBuffer(file)
        input.value = ''
        return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
        originalContent.value = e.target?.result as string
        message.success(`已上传文件：${file.name}`)
    }
    reader.onerror = () => message.error('文件读取失败')

    if (file.type.includes('text') || file.name.endsWith('.md')) {
        reader.readAsText(file)
    } else {
        message.warning('暂不支持该文件格式，请上传文本文件或 Word 文档（.docx）')
    }

    input.value = ''
}
</script>

<style scoped>
.ai-summary-container {
    width: var(--page-width);
    min-height: calc(100vh - 140px);
    margin: 0 auto;
    padding: 56px 0 80px;
    color: var(--text-primary);
}

.summary-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 24px;
}

.eyebrow,
.setting-label,
.setting-value,
.input-stats,
.result-stats {
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

.summary-title {
    margin: 18px 0 0;
    font-size: clamp(40px, 6vw, 64px);
    font-weight: 600;
    line-height: 1;
    letter-spacing: 0;
}

.summary-subtitle {
    max-width: 720px;
    margin: 16px 0 0;
    color: var(--text-secondary);
    font-size: 18px;
    line-height: 1.7;
}

.summary-content {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 320px;
    grid-template-areas:
        "input side"
        "result side";
    gap: 16px;
}

.input-section { grid-area: input; }
.side-panel { grid-area: side; display: flex; flex-direction: column; gap: 16px; }
.result-section { grid-area: result; }

.panel-card {
    border-radius: 12px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
    padding: 24px;
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 16px;
}

.section-title,
.tips-title {
    margin: 0;
    color: var(--text-primary);
    font-size: 24px;
    font-weight: 600;
    letter-spacing: 0;
}

.section-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.control-btn,
.generate-btn {
    border: 0;
    border-radius: 10px;
    font-weight: 500;
    cursor: pointer;
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease;
}

.control-btn {
    height: 36px;
    padding: 0 12px;
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.control-btn:hover {
    background: var(--surface-hover);
}

.content-input {
    width: 100%;
    min-height: 430px;
    resize: vertical;
    border: 0;
    border-radius: 10px;
    padding: 16px;
    color: var(--text-primary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font: inherit;
    line-height: 1.75;
    outline: none;
}

.content-input:focus {
    box-shadow: var(--ring), 0 0 0 3px rgba(10, 114, 239, 0.16);
}

.input-stats,
.result-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 12px;
    color: var(--text-muted);
    font-size: 12px;
}

.setting-label {
    display: block;
    margin-bottom: 12px;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
}

.setting-value {
    display: inline-flex;
    align-items: center;
    height: 28px;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
}

.generate-btn {
    width: 100%;
    height: 42px;
    margin-top: 18px;
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.generate-btn:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}

.generated-summary-content {
    min-height: 180px;
    padding: 18px;
    border-radius: 10px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    color: var(--text-primary);
    line-height: 1.85;
}

.generated-summary-content p {
    margin: 0;
    white-space: pre-wrap;
}

.empty-result {
    min-height: 180px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 8px;
    border-radius: 10px;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    box-shadow: var(--ring);
}

.empty-result strong {
    color: var(--text-primary);
    font-size: 18px;
    font-weight: 600;
}

.tips-list {
    margin: 14px 0 0;
    padding-left: 18px;
    color: var(--text-secondary);
    line-height: 1.75;
}

@media (max-width: 980px) {
    .summary-content {
        grid-template-columns: 1fr;
        grid-template-areas:
            "input"
            "side"
            "result";
    }

    .side-panel {
        display: grid;
        grid-template-columns: 1fr 1fr;
    }
}

@media (max-width: 680px) {
    .ai-summary-container {
        padding: 32px 0 56px;
    }

    .summary-header,
    .section-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .side-panel {
        grid-template-columns: 1fr;
    }

    .panel-card {
        padding: 18px;
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
