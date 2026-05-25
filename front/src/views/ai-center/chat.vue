<template>
    <div class="ai-chat-container">
        <header class="chat-header">
            <div class="header-info">
                <span class="eyebrow">资料问答</span>
                <h1 class="chat-title">先找依据，再回答。</h1>
                <p class="chat-subtitle">选择资料包后提问，系统会先检索相关片段，再把来源和回答放在同一个对话里。</p>
            </div>
            <div class="header-actions">
                <el-select
                    v-model="selectedContextPackId"
                    class="context-select"
                    clearable
                    filterable
                    :loading="loadingContextPacks"
                    :disabled="isLoading || !isLoggedIn"
                    placeholder="选择上下文包"
                >
                    <el-option
                        v-for="pack in contextPacks"
                        :key="pack.id"
                        :label="`${pack.name} · ${pack.sources.length} 份资料`"
                        :value="pack.id"
                    />
                </el-select>
                <button class="control-btn" type="button" @click="resetContext" :disabled="isLoading || !isLoggedIn">重置上下文</button>
                <button class="control-btn" type="button" @click="clearChat" :disabled="isLoading">清空对话</button>
            </div>
        </header>

        <main class="chat-panel">
            <section class="chat-messages" ref="messagesRef">
                <div v-if="messages.length === 0" class="welcome-message">
                    <span class="welcome-mark">问</span>
                    <h2>从资料里问出答案</h2>
                    <p>先选一个上下文包，再提出写作或梳理问题。命中的片段会随回答保留下来，方便复核。</p>
                    <div class="welcome-badges">
                        <span>引用来源</span>
                        <span>控制预算</span>
                        <span>连续追问</span>
                    </div>
                    <div class="welcome-suggestions">
                        <button type="button" :disabled="!isLoggedIn || isLoading" @click="sendSuggestion('根据当前资料包，帮我梳理核心结论')">梳理核心结论</button>
                        <button type="button" :disabled="!isLoggedIn || isLoading" @click="sendSuggestion('这份资料还缺哪些证据？')">检查缺失证据</button>
                        <button type="button" :disabled="!isLoggedIn || isLoading" @click="sendSuggestion('把命中片段整理成一段文章开头')">生成文章开头</button>
                    </div>
                </div>

                <article v-for="(item, index) in messages" :key="index" class="chat-message" :class="item.role">
                    <div class="message-avatar">{{ item.role === 'user' ? '我' : '答' }}</div>
                    <div class="message-content">
                        <div class="message-meta">
                            <span>{{ item.role === 'user' ? '我' : '资料回答' }}</span>
                            <time>{{ formatTime(item.timestamp) }}</time>
                        </div>
                        <div class="message-bubble">
                            <div v-if="item.role === 'user'" class="message-text">{{ item.content }}</div>
                            <div v-else-if="!item.content && isLoading && index === messages.length - 1"
                                class="typing-bubble inline-typing">
                                <span></span><span></span><span></span>
                            </div>
                            <div v-else class="message-text markdown-content" v-html="renderMarkdown(item.content)"></div>
                            <div v-if="item.role === 'ai' && item.retrieval" class="retrieval-card">
                                <div class="retrieval-header">
                                    <span>本次引用</span>
                                    <small>
                                        {{ item.retrieval.mode === 'semantic' ? '语义检索' : '关键词检索' }} · 命中 {{ item.retrieval.snippets.length }} 段 · 约 {{ item.retrieval.used_tokens_estimate }} tokens
                                    </small>
                                </div>
                                <div v-if="item.retrieval.snippets.length" class="retrieval-list">
                                    <span v-for="snippet in item.retrieval.snippets" :key="snippet.id" :title="snippet.content_preview">
                                        {{ snippet.id }} {{ snippet.title }}
                                    </span>
                                </div>
                                <div v-else class="retrieval-empty">没有命中足够相关的上下文片段</div>
                            </div>
                            <button v-if="item.content" class="copy-btn" type="button" @click="copyMessage(item.content)">复制</button>
                        </div>
                    </div>
                </article>
            </section>

            <footer class="chat-input-area">
                <div class="context-strip" v-if="selectedContextPack">
                    <span>当前资料包</span>
                    <strong>{{ selectedContextPack.name }}</strong>
                    <small>{{ selectedContextPack.sources.length }} 份资料，会按问题检索可引用片段</small>
                </div>
                <div class="rag-budget-strip" v-if="selectedContextPack">
                    <span>引用范围</span>
                    <button
                        v-for="option in ragBudgetOptions"
                        :key="option.value"
                        type="button"
                        :class="{ active: selectedRagBudget === option.value }"
                        :disabled="isLoading"
                        @click="selectedRagBudget = option.value"
                    >
                        <strong>{{ option.label }}</strong>
                        <small>{{ option.detail }}</small>
                    </button>
                </div>
                <textarea v-model="inputMessage" :placeholder="isLoggedIn ? '输入问题，例如：这份资料能支持什么观点？' : '登录后可以使用资料问答'" rows="2"
                    @keydown.enter.prevent="sendMessage" @keydown.enter.shift.exact="inputMessage += '\n'"
                    :disabled="isLoading || !isLoggedIn" class="message-input"></textarea>
                <div class="input-actions">
                    <button class="control-btn" type="button" @click="inputMessage = ''" v-if="inputMessage.trim()" :disabled="isLoading">清空输入</button>
                    <button class="send-btn" type="button" @click="sendMessage" :disabled="!inputMessage.trim() || isLoading || !isLoggedIn">
                        {{ isLoading ? '...' : '发送' }}
                    </button>
                </div>
            </footer>
        </main>
    </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useElMessage } from '@/hooks/useMessage'
import { useGlobalStore } from '@/store'
import { aiChatService } from '@/api/modules/ai'
import { type AIRetrievalMeta } from '@/api/modules/ai/interface'
import contextPackApi, { type ContextPack } from '@/api/modules/contextPacks'
import { marked } from 'marked'

const { message } = useElMessage()
const route = useRoute()
const globalStore = useGlobalStore()

function renderMarkdown(content: string): string {
    marked.setOptions({ breaks: true, gfm: true })
    return marked.parse(content) as string
}

interface Message {
    role: 'user' | 'ai'
    content: string
    timestamp: Date
    retrieval?: AIRetrievalMeta | null
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
const contextPacks = ref<ContextPack[]>([])
const selectedContextPackId = ref<number | null>(null)
const loadingContextPacks = ref(false)
const selectedRagBudget = ref(2600)

const ragBudgetOptions = [
    { label: '精简', value: 1200, detail: '低消耗' },
    { label: '标准', value: 2600, detail: '日常问答' },
    { label: '深度', value: 4800, detail: '复杂梳理' }
]

const selectedContextPack = computed(() => {
    return contextPacks.value.find(pack => pack.id === selectedContextPackId.value) || null
})

const isLoggedIn = computed(() => Boolean(globalStore.token && globalStore.userInfo?.id))

const currentUserId = computed(() => {
    return globalStore.userInfo?.id ? String(globalStore.userInfo.id) : 'guest'
})

function ensureCanUseAI() {
    if (isLoggedIn.value) return true
    message.warning('请先登录后再使用 AI 对话')
    return false
}

async function sendMessage() {
    if (!ensureCanUseAI()) return

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
        await aiChatService.sendMessageStream({
            message: content,
            user_id: currentUserId.value,
            context_pack_id: selectedContextPackId.value || undefined,
            context_token_budget: selectedRagBudget.value
        }, {
            onStart: (payload) => {
                messages.value[aiMessageIndex].retrieval = payload.retrieval || null
                saveMessagesToStorage(messages.value)
            },
            onDelta: async (delta) => {
                messages.value[aiMessageIndex].content += delta
                saveMessagesToStorage(messages.value)
                await nextTick(scrollToBottom)
            },
            onDone: (payload) => {
                messages.value[aiMessageIndex].retrieval = payload.retrieval || messages.value[aiMessageIndex].retrieval || null
                saveMessagesToStorage(messages.value)
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
        const errorMessage = error?.message || 'AI 服务暂时不可用，请稍后重试'
        messages.value[aiMessageIndex].content = errorMessage
        message.error(errorMessage)
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
    if (!ensureCanUseAI()) return

    try {
        await aiChatService.sendMessage({
            user_id: currentUserId.value,
            reset_context: true,
            context_pack_id: selectedContextPackId.value || undefined,
            context_token_budget: selectedRagBudget.value
        })
        messages.value = []
        saveMessagesToStorage(messages.value)
        message.success('上下文已重置')
    } catch (error) {
        console.error('Reset context failed:', error)
        message.error('重置上下文失败，请稍后重试')
    }
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

async function clearChatForContextSwitch() {
    if (messages.value.length) {
        messages.value = []
        localStorage.removeItem(STORAGE_KEY)
        message.info('上下文包已切换，对话已清空')
    }

    if (!isLoggedIn.value) return

    try {
        await aiChatService.sendMessage({
            user_id: currentUserId.value,
            reset_context: true,
            context_pack_id: selectedContextPackId.value || undefined,
            context_token_budget: selectedRagBudget.value
        })
    } catch (error) {
        console.error('Reset context after pack switch failed:', error)
    }
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

async function loadContextPacks() {
    if (!isLoggedIn.value) {
        contextPacks.value = []
        selectedContextPackId.value = null
        return
    }

    loadingContextPacks.value = true
    try {
        contextPacks.value = await contextPackApi.getList()
        const queryPackId = Number(route.query.pack)
        if (Number.isFinite(queryPackId) && contextPacks.value.some(pack => pack.id === queryPackId)) {
            selectedContextPackId.value = queryPackId
        }
    } catch (error) {
        console.error('Load context packs failed:', error)
        contextPacks.value = []
    } finally {
        loadingContextPacks.value = false
    }
}

onMounted(async () => {
    messages.value = loadMessagesFromStorage()
    await loadContextPacks()
})

watch(selectedContextPackId, (newValue, oldValue) => {
    if (newValue === oldValue) return
    clearChatForContextSwitch()
})
</script>

<style scoped>
/* Hallmark · macrostructure: conversation workbench · theme: white minimal · enrichment: none */
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

.context-select {
    width: min(320px, 100%);
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

.control-btn:disabled,
.send-btn:disabled,
.copy-btn:disabled,
.welcome-suggestions button:disabled {
    cursor: not-allowed;
    opacity: 0.55;
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
    background: color-mix(in oklch, var(--button-fg) 16%, transparent);
}

.retrieval-card {
    margin-top: 14px;
    padding: 12px;
    border-radius: 10px;
    background: var(--surface);
    box-shadow: var(--ring);
}

.retrieval-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 10px;
    color: var(--text-primary);
    font-size: 13px;
    font-weight: 600;
}

.retrieval-header small,
.retrieval-empty {
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 400;
}

.retrieval-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.retrieval-list span {
    max-width: 100%;
    padding: 4px 8px;
    border-radius: 999px;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
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
    box-shadow: inset 0 1px 0 color-mix(in oklch, var(--text-primary) 8%, transparent);
}

.context-strip {
    grid-column: 1 / -1;
    min-height: 34px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 10px;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    font-size: 13px;
}

.context-strip strong {
    color: var(--text-primary);
}

.context-strip small {
    color: var(--text-muted);
}

.rag-budget-strip {
    grid-column: 1 / -1;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
}

.rag-budget-strip > span {
    color: var(--text-muted);
    font-size: 13px;
}

.rag-budget-strip button {
    min-height: 38px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 0;
    border-radius: 10px;
    padding: 0 10px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    cursor: pointer;
}

.rag-budget-strip button.active {
    color: var(--button-fg);
    background: var(--button-bg);
}

.rag-budget-strip button:disabled {
    cursor: not-allowed;
    opacity: 0.55;
}

.rag-budget-strip strong,
.rag-budget-strip small {
    line-height: 1;
}

.rag-budget-strip small {
    color: inherit;
    opacity: 0.72;
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
    box-shadow: var(--ring), 0 0 0 3px color-mix(in oklch, var(--focus-blue) 18%, transparent);
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
