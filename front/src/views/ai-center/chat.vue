<template>
    <div class="ai-chat-container">
        <header class="chat-header">
            <div class="header-info">
                <span class="eyebrow">AI Chat</span>
                <h1 class="chat-title">AI 对话中心</h1>
                <p class="chat-subtitle">围绕文章创作、技术问答和知识梳理进行连续对话。</p>
            </div>
            <div class="header-actions">
                <button class="control-btn" type="button" @click="resetContext">重置上下文</button>
                <button class="control-btn" type="button" @click="clearChat">清空对话</button>
            </div>
        </header>

        <main class="chat-panel">
            <section class="chat-messages" ref="messagesRef">
                <div v-if="messages.length === 0" class="welcome-message">
                    <span class="welcome-mark">AI</span>
                    <h2>开始一次清晰的 AI 协作</h2>
                    <p>你可以请它解释概念、起草段落、梳理文章结构，或者将阅读材料转成可发布内容。</p>
                    <div class="welcome-badges">
                        <span>连续问答</span>
                        <span>创作辅助</span>
                        <span>知识梳理</span>
                    </div>
                    <div class="welcome-suggestions">
                        <button type="button" @click="sendSuggestion('帮我生成一段博客文章的开头')">帮我生成一段博客文章的开头</button>
                        <button type="button" @click="sendSuggestion('AI 智能摘要适合哪些场景？')">AI 智能摘要适合哪些场景？</button>
                        <button type="button" @click="sendSuggestion('如何设计多维标签与分类体系？')">如何设计多维标签与分类体系？</button>
                    </div>
                </div>

                <article v-for="(item, index) in messages" :key="index" class="chat-message" :class="item.role">
                    <div class="message-avatar">{{ item.role === 'user' ? 'U' : 'AI' }}</div>
                    <div class="message-content">
                        <div class="message-meta">
                            <span>{{ item.role === 'user' ? '作者' : 'AI 助手' }}</span>
                            <time>{{ formatTime(item.timestamp) }}</time>
                        </div>
                        <div class="message-bubble">
                            <div v-if="item.role === 'user'" class="message-text">{{ item.content }}</div>
                            <div v-else-if="!item.content && isLoading && index === messages.length - 1"
                                class="typing-bubble inline-typing">
                                <span></span><span></span><span></span>
                            </div>
                            <div v-else class="message-text markdown-content" v-html="renderMarkdown(item.content)"></div>
                            <button v-if="item.content" class="copy-btn" type="button" @click="copyMessage(item.content)">复制</button>
                        </div>
                    </div>
                </article>
            </section>

            <footer class="chat-input-area">
                <textarea v-model="inputMessage" placeholder="输入你的问题或创作需求..." rows="2"
                    @keydown.enter.prevent="sendMessage" @keydown.enter.shift.exact="inputMessage += '\n'"
                    :disabled="isLoading" class="message-input"></textarea>
                <div class="input-actions">
                    <button class="control-btn" type="button" @click="inputMessage = ''" v-if="inputMessage.trim()">清空输入</button>
                    <button class="send-btn" type="button" @click="sendMessage" :disabled="!inputMessage.trim() || isLoading">
                        {{ isLoading ? '...' : '发送' }}
                    </button>
                </div>
            </footer>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { useElMessage } from '@/hooks/useMessage'
import { aiChatService } from '@/api/modules/ai'
import { marked } from 'marked'

const { message } = useElMessage()

function renderMarkdown(content: string): string {
    marked.setOptions({ breaks: true, gfm: true })
    return marked.parse(content) as string
}

interface Message {
    role: 'user' | 'ai'
    content: string
    timestamp: Date
}

const STORAGE_KEY = 'aiChatMessages'

const loadMessagesFromStorage = (): Message[] => {
    try {
        const storedMessages = localStorage.getItem(STORAGE_KEY)
        if (!storedMessages) return []
        return JSON.parse(storedMessages).map((item: any) => ({ ...item, timestamp: new Date(item.timestamp) }))
    } catch (error) {
        console.error('Load chat history failed:', error)
        return []
    }
}

const saveMessagesToStorage = (items: Message[]) => {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
    } catch (error) {
        console.error('Save chat history failed:', error)
    }
}

const messages = ref<Message[]>(loadMessagesFromStorage())
const inputMessage = ref('')
const isLoading = ref(false)
const messagesRef = ref<HTMLElement | null>(null)

async function sendMessage() {
    const content = inputMessage.value.trim()
    if (!content || isLoading.value) return

    messages.value.push({ role: 'user', content, timestamp: new Date() })
    saveMessagesToStorage(messages.value)
    inputMessage.value = ''
    await nextTick(scrollToBottom)
    isLoading.value = true
    const aiMessageIndex = messages.value.length
    messages.value.push({ role: 'ai', content: '', timestamp: new Date() })

    try {
        await aiChatService.sendMessageStream({ message: content, user_id: '123' }, {
            onDelta: async (delta) => {
                messages.value[aiMessageIndex].content += delta
                saveMessagesToStorage(messages.value)
                await nextTick(scrollToBottom)
            },
            onError: (errorMessage) => {
                if (!messages.value[aiMessageIndex].content) {
                    messages.value[aiMessageIndex].content = errorMessage
                }
                message.warning(errorMessage)
            }
        })
    } catch (error: any) {
        console.error('AI chat API failed:', error)
        messages.value[aiMessageIndex].content = await generateResponse(content)
        message.warning('AI 服务暂时不可用，已显示本地示例回复')
    } finally {
        if (!messages.value[aiMessageIndex].content) {
            messages.value[aiMessageIndex].content = 'AI 回复失败'
        }
        isLoading.value = false
        saveMessagesToStorage(messages.value)
        await nextTick(scrollToBottom)
    }
}
async function resetContext() {
    try {
        await aiChatService.sendMessage({ user_id: '123', reset_context: true })
        messages.value = []
        saveMessagesToStorage(messages.value)
        message.success('上下文已重置')
    } catch (error) {
        console.error('Reset context failed:', error)
        message.error('重置上下文失败，请稍后重试')
    }
}

function generateResponse(content: string): Promise<string> {
    const responses: Record<string, string> = {
        '帮我生成一段博客文章的开头': `可以从一个具体问题切入：

当我们讨论技术方案时，真正值得关注的往往不是某个工具本身，而是它如何改变我们组织信息、理解问题和交付结果的方式。`,
        'AI 智能摘要适合哪些场景？': 'AI 智能摘要适合长文阅读、会议纪要、技术文档、知识库检索和文章发布前的内容提炼。',
        '如何设计多维标签与分类体系？': '可以从三层来设计：一是固定分类，用于确定内容归属；二是主题标签，用于连接知识点；三是状态标签，用于表达精选、原创、系列等运营信息。'
    }
    return Promise.resolve(responses[content] || `我理解你想处理“${content}”。可以先把目标、读者和希望输出的格式告诉我，我会帮你整理成更清晰的 AI 回复。`)
}
function sendSuggestion(suggestion: string) {
    inputMessage.value = suggestion
    sendMessage()
}

function clearChat() {
    if (!messages.value.length) return
    messages.value = []
    localStorage.removeItem(STORAGE_KEY)
    message.success('对话已清空')
}

function scrollToBottom() {
    messagesRef.value?.scrollTo({ top: messagesRef.value.scrollHeight, behavior: 'smooth' })
}

function formatTime(date: Date): string {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function copyMessage(content: string) {
    navigator.clipboard.writeText(content).then(() => {
        message.success('文本已复制到剪贴板')
    }).catch((error) => {
        console.error('Copy failed:', error)
        message.error('复制失败，请手动复制')
    })
}

onMounted(() => {
    messages.value = loadMessagesFromStorage()
})
</script>

<style scoped>
.ai-chat-container {
    width: var(--page-width);
    min-height: calc(100vh - 140px);
    margin: 0 auto;
    padding: 56px 0 80px;
    color: var(--text-primary);
}

.chat-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 24px;
}

.eyebrow,
.welcome-mark,
.message-avatar,
.message-meta,
.welcome-badges span {
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

.chat-title {
    margin: 18px 0 0;
    font-size: clamp(40px, 6vw, 64px);
    font-weight: 600;
    line-height: 1;
    letter-spacing: 0;
}

.chat-subtitle {
    max-width: 680px;
    margin: 16px 0 0;
    color: var(--text-secondary);
    font-size: 18px;
    line-height: 1.7;
}

.header-actions,
.input-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.control-btn,
.send-btn,
.copy-btn,
.welcome-suggestions button {
    border: 0;
    border-radius: 10px;
    font-weight: 500;
    cursor: pointer;
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease;
}

.control-btn,
.copy-btn,
.welcome-suggestions button {
    height: 36px;
    padding: 0 12px;
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.control-btn:hover,
.copy-btn:hover,
.welcome-suggestions button:hover {
    background: var(--surface-hover);
}

.chat-panel {
    overflow: hidden;
    border-radius: 12px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.chat-messages {
    height: min(66vh, 720px);
    min-height: 520px;
    overflow-y: auto;
    padding: 24px;
    background: var(--surface);
}

.welcome-message {
    min-height: 420px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.welcome-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    color: var(--button-fg);
    background: var(--button-bg);
    font-size: 13px;
    font-weight: 600;
}

.welcome-message h2 {
    margin: 18px 0 10px;
    font-size: 32px;
    font-weight: 600;
    letter-spacing: 0;
}

.welcome-message p {
    max-width: 680px;
    margin: 0;
    color: var(--text-secondary);
    line-height: 1.8;
}

.welcome-badges,
.welcome-suggestions {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
}

.welcome-badges {
    margin-top: 18px;
}

.welcome-badges span {
    height: 26px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    box-shadow: var(--ring);
    font-size: 12px;
    display: inline-flex;
    align-items: center;
}

.welcome-suggestions {
    max-width: 760px;
    margin-top: 24px;
}

.chat-message {
    display: grid;
    grid-template-columns: 42px minmax(0, 1fr);
    gap: 12px;
    margin-bottom: 18px;
}

.chat-message.user {
    grid-template-columns: minmax(0, 1fr) 42px;
}

.chat-message.user .message-avatar {
    grid-column: 2;
    grid-row: 1;
}

.chat-message.user .message-content {
    grid-column: 1;
    grid-row: 1;
    align-items: flex-end;
}

.message-avatar {
    width: 42px;
    height: 42px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 600;
}

.message-content {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.message-meta {
    display: flex;
    gap: 10px;
    color: var(--text-muted);
    font-size: 12px;
}

.message-bubble {
    position: relative;
    max-width: min(760px, 100%);
    padding: 16px 58px 16px 22px;
    border-radius: 12px;
    background: var(--surface-subtle);
    color: var(--text-primary);
    box-shadow: var(--ring);
    line-height: 1.75;
}

.chat-message.user .message-bubble {
    color: var(--button-fg);
    background: var(--button-bg);
}

.copy-btn {
    position: absolute;
    right: 12px;
    top: 12px;
    height: 28px;
    padding: 0 8px;
    font-size: 12px;
}

.chat-message.user .copy-btn {
    color: var(--button-fg);
    background: rgba(255, 255, 255, 0.14);
}

.markdown-content :deep(p) {
    margin: 0 0 10px;
}

.markdown-content :deep(p:last-child) {
    margin-bottom: 0;
}

.markdown-content :deep(pre) {
    overflow-x: auto;
    margin: 12px 0;
    padding: 12px;
    border-radius: 10px;
    background: var(--surface);
    box-shadow: var(--ring);
}

.typing-bubble {
    width: 86px;
    padding: 14px 16px;
    display: flex;
    gap: 6px;
}

.typing-bubble span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-muted);
    animation: pulse 1.2s ease-in-out infinite;
}

.typing-bubble span:nth-child(2) { animation-delay: 0.15s; }
.typing-bubble span:nth-child(3) { animation-delay: 0.3s; }

.chat-input-area {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 12px;
    padding: 16px;
    background: var(--surface);
    box-shadow: inset 0 1px 0 rgba(0, 0, 0, 0.08);
}

.message-input {
    width: 100%;
    min-height: 58px;
    max-height: 160px;
    resize: vertical;
    border: 0;
    border-radius: 10px;
    padding: 12px 14px;
    color: var(--text-primary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font: inherit;
    line-height: 1.6;
    outline: none;
}

.message-input:focus {
    box-shadow: var(--ring), 0 0 0 3px rgba(10, 114, 239, 0.16);
}

.send-btn {
    height: 40px;
    padding: 0 18px;
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.send-btn:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}

@keyframes pulse {
    0%, 80%, 100% { opacity: 0.35; transform: translateY(0); }
    40% { opacity: 1; transform: translateY(-2px); }
}

@media (max-width: 760px) {
    .ai-chat-container {
        padding: 32px 0 56px;
    }

    .chat-header,
    .chat-input-area {
        grid-template-columns: 1fr;
        flex-direction: column;
        align-items: flex-start;
    }

    .header-actions,
    .input-actions {
        justify-content: flex-start;
    }

    .chat-messages {
        min-height: 460px;
        padding: 16px;
    }

    .chat-message,
    .chat-message.user {
        grid-template-columns: 34px minmax(0, 1fr);
    }

    .chat-message.user .message-avatar,
    .chat-message.user .message-content {
        grid-column: auto;
        grid-row: auto;
        align-items: flex-start;
    }

    .message-avatar {
        width: 34px;
        height: 34px;
    }

    .message-bubble {
        padding: 14px 50px 14px 18px;
    }

    .copy-btn {
        right: 10px;
        top: 10px;
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
