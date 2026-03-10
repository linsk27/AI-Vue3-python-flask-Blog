<template>
    <div class="ai-summary-container">
        <!-- 页面头部 -->
        <header class="summary-header">
            <div class="header-left">
                <div class="header-icon">📝</div>
                <div class="header-info">
                    <h1 class="summary-title">AI智能摘要</h1>
                    <p class="summary-subtitle">一键生成文章摘要，快速掌握核心内容</p>
                </div>
            </div>
            <div class="header-right">
                <button class="control-btn" @click="clearContent" title="清空内容">
                    <span>清空</span>
                </button>
            </div>
        </header>

        <!-- 主要内容区域 -->
        <main class="summary-content">
            <!-- 输入区域 -->
            <section class="input-section">
                <div class="section-header">
                    <h2 class="section-title">输入文章内容</h2>
                    <div class="section-actions">
                        <input ref="fileUploadRef" type="file" accept=".txt,.md,.doc,.docx" style="display: none;"
                            @change="handleFileUpload">
                        <button class="action-btn" @click="fileUploadRef?.click()">
                            <span>上传文件</span>
                        </button>
                        <button class="action-btn" @click="pasteContent">
                            <span>粘贴内容</span>
                        </button>
                    </div>
                </div>
                <div class="input-wrapper">
                    <textarea v-model="originalContent" placeholder="请在此粘贴或上传您需要生成摘要的文章内容..." rows="15"
                        :disabled="isGenerating"></textarea>
                </div>
                <div class="input-stats">
                    <span>{{ originalContent.length }} 字符</span>
                    <span>{{originalContent.split(/\s+/).filter(word => word).length}} 单词</span>
                </div>
            </section>

            <!-- 操作区域 -->
            <section class="action-section">
                <div class="action-controls">
                    <div class="summary-settings">
                        <label class="setting-label">摘要长度：</label>
                        <div class="setting-control">
                            <el-slider v-model="summaryLength" :min="100" :max="1000" :step="50"
                                :disabled="isGenerating" />
                            <span class="setting-value">{{ summaryLength }} 字符</span>
                        </div>
                    </div>
                    <button class="generate-btn" @click="generateSummary"
                        :disabled="!originalContent.trim() || isGenerating">
                        <span v-if="isGenerating">
                            <span class="loading-spinner"></span>
                            生成中...
                        </span>
                        <span v-else>生成摘要</span>
                    </button>
                </div>
            </section>

            <!-- 结果区域 -->
            <section class="result-section" v-if="generatedSummary">
                <div class="section-header">
                    <h2 class="section-title">生成的摘要</h2>
                    <div class="section-actions">
                        <button class="action-btn" @click="copySummary" title="复制摘要">
                            <span>复制摘要</span>
                        </button>
                        <button class="action-btn" @click="regenerateSummary" title="重新生成">
                            <span>重新生成</span>
                        </button>
                    </div>
                </div>
                <div class="result-wrapper">
                    <div class="generated-summary-content">
                        <p>{{ generatedSummary }}</p>
                    </div>
                </div>
                <div class="result-stats">
                    <span>{{ generatedSummary.length }} 字符</span>
                    <span>{{generatedSummary.split(/\s+/).filter(word => word).length}} 单词</span>
                    <span class="summary-quality">摘要质量：<span class="quality-indicator"></span> 良好</span>
                </div>
            </section>

            <!-- 提示信息 -->
            <section class="tips-section">
                <h3 class="tips-title">使用提示</h3>
                <ul class="tips-list">
                    <li>建议输入500字以上的文章，以获得更准确的摘要</li>
                    <li>可以调整摘要长度，生成适合您需求的内容</li>
                    <li>支持TXT、MD、DOC、DOCX等格式的文件上传</li>
                    <li>生成的摘要可以直接复制使用，也可以根据需要手动修改</li>
                </ul>
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

// 状态管理
const originalContent = ref('')
const generatedSummary = ref('')
const isGenerating = ref(false)
const summaryLength = ref(300) // 默认摘要长度
const fileUploadRef = ref<HTMLInputElement | null>(null)

// 生成摘要
async function generateSummary() {
    if (!originalContent.value.trim() || isGenerating.value) return

    isGenerating.value = true

    try {
        // 调用真实 AI 摘要接口
        const res = await aiSummaryService.generateSummary({
            content: originalContent.value,
            length: summaryLength.value,
            // user_id: 'current_user_id' // 如果有用户系统，在此传入
        }) as any

        // 处理拦截器处理后的响应
        // 这里的 res 实际上是 AIChatResponseData，包含 reply 字段
        // 为了兼容性，我们同时检查 summary (旧定义) 和 reply (Chat接口)
        const summaryText = res?.reply || res?.data?.reply || res?.summary || res?.data?.summary

        if (summaryText) {
            generatedSummary.value = summaryText
            message.success('摘要生成成功')
        } else {
            // 处理后端返回的错误信息
            const errorMsg = res?.error || res?.msg || '摘要生成失败'
            throw new Error(errorMsg)
        }
    } catch (error: any) {
        // 如果拦截器 reject 了（例如 status !== 0），会走到这里
        const errorMsg = error.msg || error.message || '摘要生成失败，请稍后再试'
        message.error(errorMsg)
        console.error('摘要生成错误:', error)
    } finally {
        isGenerating.value = false
    }
}

// 重新生成摘要
function regenerateSummary() {
    generateSummary()
}

// 清空内容
function clearContent() {
    originalContent.value = ''
    generatedSummary.value = ''
    message.success('内容已清空')
}

// 粘贴内容
async function pasteContent() {
    try {
        const text = await navigator.clipboard.readText()
        originalContent.value = text
        message.success('内容已粘贴')
    } catch (error) {
        message.error('粘贴失败，请手动粘贴')
        console.error('粘贴错误:', error)
    }
}

// 复制摘要
async function copySummary() {
    if (!generatedSummary.value) return

    try {
        await navigator.clipboard.writeText(generatedSummary.value)
        message.success('摘要已复制到剪贴板')
    } catch (error) {
        message.error('复制失败，请手动复制')
        console.error('复制错误:', error)
    }
}

// 处理文件上传
function handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement
    if (!input.files || input.files.length === 0) return

    const file = input.files[0]

    // 处理 docx 文件
    if (file.name.endsWith('.docx')) {
        const reader = new FileReader()
        reader.onload = (e) => {
            const arrayBuffer = e.target?.result as ArrayBuffer
            mammoth.extractRawText({ arrayBuffer: arrayBuffer })
                .then((result) => {
                    originalContent.value = result.value
                    message.success(`已上传 Word 文档：${file.name}`)
                })
                .catch((err) => {
                    console.error('Word 解析错误:', err)
                    message.error('Word 文档解析失败')
                })
        }
        reader.onerror = () => {
            message.error('文件读取失败')
        }
        reader.readAsArrayBuffer(file)

        // 清空文件输入
        input.value = ''
        return
    }

    // 处理文本文件
    const reader = new FileReader()

    reader.onload = (e) => {
        const content = e.target?.result as string
        originalContent.value = content
        message.success(`已上传文件：${file.name}`)
    }

    reader.onerror = () => {
        message.error('文件读取失败')
    }

    // 只处理文本文件，对于其他格式需要额外的解析库
    if (file.type.includes('text') || file.name.endsWith('.md')) {
        reader.readAsText(file)
    } else {
        message.warning('暂不支持该文件格式，请上传文本文件或 Word 文档(.docx)')
    }

    // 清空文件输入，以便下次可以上传同一个文件
    input.value = ''
}
</script>

<style scoped>
/* 定义局部变量以确保主题一致性 */
.ai-summary-container {
    --primary: #FF7F50;
    --primary-dark: #FF6347;
    --primary-light: rgba(255, 127, 80, 0.1);
    --primary-lighter: rgba(255, 127, 80, 0.05);
    --text-main: #2c3e50;
    --text-regular: #606266;
    --text-secondary: #909399;
    --bg-white: #ffffff;
    --bg-light: #fffaf8;
    --border-color: #ffd8c6;
    --border-radius: 16px;
    --shadow-soft: 0 10px 30px rgba(255, 127, 80, 0.08);
    --shadow-strong: 0 15px 40px rgba(255, 127, 80, 0.12);
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: linear-gradient(135deg, #ffffff 0%, #fff5f0 100%);
    min-height: 100vh;
    color: var(--text-main);
}

/* 页面头部 */
.summary-header {
    background: var(--bg-white);
    padding: 1.5rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    box-shadow: 0 2px 12px rgba(255, 127, 80, 0.05);
}

.header-left {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.header-icon {
    font-size: 2.25rem;
    filter: drop-shadow(0 4px 6px rgba(255, 127, 80, 0.2));
}

.header-info {
    display: flex;
    flex-direction: column;
}

.summary-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--primary);
    margin: 0;
    letter-spacing: -0.5px;
    background: linear-gradient(120deg, var(--primary), var(--primary-dark));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.summary-subtitle {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin: 0.25rem 0 0;
}

.control-btn {
    background: var(--bg-white);
    color: var(--primary);
    border: 1.5px solid var(--primary);
    padding: 0.6rem 1.5rem;
    border-radius: 10px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition);
}

.control-btn:hover {
    background: var(--primary);
    color: white;
    box-shadow: 0 4px 12px rgba(255, 127, 80, 0.2);
}

/* 主要内容区域 */
.summary-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2.5rem 2rem;
}

/* 通用区块样式 */
.input-section,
.action-section,
.result-section,
.tips-section {
    background: var(--bg-white);
    padding: 2rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-soft);
    margin-bottom: 2rem;
    border: 1px solid var(--border-color);
    transition: var(--transition);
}

.input-section:hover,
.action-section:hover,
.result-section:hover {
    box-shadow: var(--shadow-strong);
    border-color: var(--primary);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-title::before {
    content: '';
    width: 4px;
    height: 18px;
    background: var(--primary);
    border-radius: 2px;
}

.section-actions {
    display: flex;
    gap: 0.75rem;
}

.action-btn {
    background: var(--primary-light);
    color: var(--primary);
    border: none;
    padding: 0.5rem 1.25rem;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition);
}

.action-btn:hover {
    background: var(--primary);
    color: white;
}

/* 输入框样式 */
.input-wrapper {
    margin-bottom: 1rem;
}

.input-wrapper textarea {
    width: 100%;
    padding: 1.25rem;
    border: 1.5px solid #eee;
    border-radius: 12px;
    font-size: 1rem;
    color: var(--text-main);
    background: var(--bg-light);
    resize: vertical;
    min-height: 300px;
    line-height: 1.6;
    transition: var(--transition);
}

.input-wrapper textarea:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--bg-white);
    box-shadow: 0 0 0 4px rgba(255, 127, 80, 0.1);
}

.input-wrapper textarea::placeholder {
    color: var(--text-secondary);
}

.input-stats {
    display: flex;
    justify-content: flex-end;
    gap: 1.5rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

/* 设置区域 */
.action-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
}

.summary-settings {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex: 1;
}

.setting-label {
    font-weight: 600;
    color: var(--text-main);
    white-space: nowrap;
}

.setting-control {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    flex: 1;
}

/* 自定义 el-slider 颜色 */
:deep(.el-slider__bar) {
    background-color: var(--primary);
}

:deep(.el-slider__button) {
    border-color: var(--primary);
}

.setting-value {
    font-size: 0.9rem;
    color: var(--primary);
    font-weight: 700;
    min-width: 80px;
}

.generate-btn {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    border: none;
    padding: 1rem 2.5rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: var(--transition);
    display: flex;
    align-items: center;
    gap: 0.75rem;
    box-shadow: 0 8px 20px rgba(255, 127, 80, 0.3);
}

.generate-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 12px 25px rgba(255, 127, 80, 0.4);
    filter: brightness(1.1);
}

.generate-btn:disabled {
    background: #e0e0e0;
    color: #999;
    cursor: not-allowed;
    box-shadow: none;
}

/* 结果展示区 */
.result-section {
    border-left: 6px solid var(--primary);
    animation: fadeIn 0.5s ease-out;
}

.generated-summary-content {
    background: #fffcfb;
    padding: 1.75rem;
    border-radius: 12px;
    border: 1px dashed var(--border-color);
    line-height: 1.8;
    font-size: 1.05rem;
    color: var(--text-main);
    white-space: pre-wrap;
}

.result-stats {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 1.5rem;
    margin-top: 1rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.summary-quality {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #67c23a;
    font-weight: 600;
}

.quality-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #67c23a;
}

/* 提示区 */
.tips-section {
    background: var(--primary-lighter);
    border: 1px dashed var(--border-color);
}

.tips-title {
    font-size: 1.1rem;
    color: var(--primary-dark);
    margin-bottom: 1rem;
}

.tips-list li {
    font-size: 0.95rem;
    color: var(--text-regular);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
}

.tips-list li::before {
    content: '💡';
    font-size: 1rem;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 768px) {
    .summary-header {
        padding: 1rem 1.5rem;
    }

    .action-controls {
        flex-direction: column;
        align-items: stretch;
    }

    .generate-btn {
        width: 100%;
        justify-content: center;
    }
}
</style>