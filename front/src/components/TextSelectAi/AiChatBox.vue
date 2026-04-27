<template>
    <div class="ai-chat-box" role="dialog" aria-labelledby="chat-title" aria-modal="true">
        <div class="chat-header" ref="headerRef" @mousedown="startDrag">
            <div class="header-left">
                <div class="ai-avatar">
                    <span>AI</span>
                </div>
                <div class="header-info">
                    <span id="chat-title" class="chat-title">知识创作助手</span>
                    <span class="status-indicator">
                        <span class="status-dot"></span>
                        在线
                    </span>
                </div>
            </div>
            <div class="header-actions">
                <button class="control-btn minimize-btn" @click="toggleMinimize" title="最小化" aria-label="最小化">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <line x1="4" y1="8" x2="12" y2="8" stroke="currentColor" stroke-width="2"
                            stroke-linecap="round" />
                    </svg>
                </button>
                <button class="control-btn close-btn" @click="closeChat" title="关闭聊天框" aria-label="关闭聊天框">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <line x1="4" y1="4" x2="12" y2="12" stroke="currentColor" stroke-width="2"
                            stroke-linecap="round" />
                        <line x1="12" y1="4" x2="4" y2="12" stroke="currentColor" stroke-width="2"
                            stroke-linecap="round" />
                    </svg>
                </button>
            </div>
        </div>

        <div v-if="!isMinimized" class="chat-content">
            <div class="chat-messages" ref="messagesRef">
                <div v-if="messages.length === 0" class="empty-state">
                    <div class="empty-icon">
                        <span>AI</span>
                    </div>
                    <h3 class="empty-title">欢迎使用知识创作助手</h3>
                    <p class="empty-text">选中文本后右键选择"使用 AI 询问"，或直接输入问题</p>
                </div>
                <div v-for="(msg, i) in messages" :key="i" class="chat-message" :class="msg.role"
                    :aria-label="`${msg.role === 'user' ? '用户' : 'AI'}消息`">
                    <div class="message-content">
                        <div v-if="msg.role === 'user'" class="message-text">{{ msg.content }}</div>
                        <div v-else class="message-text markdown-content" v-html="renderMarkdown(msg.content)"></div>
                        <div class="message-time" aria-label="发送时间">{{ formatTime(msg.timestamp) }}</div>
                    </div>
                </div>
                <div v-if="isLoading" class="chat-message ai">
                    <div class="message-content">
                        <div class="typing-indicator">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="chat-input">
                <div class="input-wrapper">
                    <textarea v-model="input" placeholder="输入您的问题..." rows="2" @keydown.enter.prevent="send"
                        @keydown.enter.shift.exact="input += '\n'" ref="inputRef" aria-label="输入消息"
                        :aria-describedby="isLoading ? 'loading-status' : undefined" />
                    <div v-if="isLoading" id="loading-status" class="sr-only">AI正在回复中...</div>
                </div>
                <div class="input-actions">
                    <button @click="clearChat" class="action-btn clear-btn" title="清空对话" aria-label="清空对话历史">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M15 4H13V3C13 1.89543 12.1046 1 11 1H7C5.89543 1 5 1.89543 5 3V4H3C2.44772 4 2 4.44772 2 5V6C2 6.55228 2.44772 7 3 7H4V15C4 16.1046 4.89543 17 6 17H12C13.1046 17 14 16.1046 14 15V7H15C15.5523 7 16 6.55228 16 6V5C16 4.44772 15.5523 4 15 4Z"
                                fill="currentColor" />
                            <path d="M7 9V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                            <path d="M11 9V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                        </svg>
                    </button>
                    <button @click="send" :disabled="!input.trim() || isLoading" class="action-btn send-btn"
                        aria-label="发送消息">
                        <span v-if="isLoading" class="sending-text">发送中...</span>
                        <svg v-else width="18" height="18" viewBox="0 0 18 18" fill="none"
                            xmlns="http://www.w3.org/2000/svg">
                            <path d="M16.5 2.5L2.5 9.5L16.5 16.5V2.5Z" fill="currentColor" />
                            <path d="M2.5 9.5L11.5 5.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onBeforeUnmount } from "vue";
import { useAiChatStore } from "@/store/aiChat";
import { useGlobalStore } from "@/store";
import { aiChatService } from "@/api/modules/ai";
import { marked } from 'marked';
import type { AIChatRequest } from "@/api/modules/ai/interface";

interface Message {
    role: "user" | "ai";
    content: string;
    timestamp: Date;
}

const input = ref("");
const messages = ref<Message[]>([]);
const messagesRef = ref<HTMLElement | null>(null);
const inputRef = ref<HTMLTextAreaElement | null>(null);
const isLoading = ref(false);
const isMinimized = ref(false);
const headerRef = ref<HTMLElement | null>(null);

// 渲染Markdown内容
function renderMarkdown(content: string): string {
    // 配置marked以正确处理代码块
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    // 自定义代码块渲染
    const renderer = new marked.Renderer();
    renderer.code = function ({ text, lang, escaped }: { text: string; lang?: string; escaped?: boolean }) {
        return `<pre style="background: #f5f5f5; padding: 1rem; border-radius: 8px; overflow-x: auto; margin: 1rem 0;"><code style="font-family: 'Courier New', Courier, monospace; font-size: 0.9rem; color: #333;">${text}</code></pre>`;
    };

    // 使用自定义渲染器解析Markdown
    return marked.parse(content, { renderer }) as string
}

// 拖拽相关
const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });

// 使用store
const aiChatStore = useAiChatStore();
const globalStore = useGlobalStore();

// 调用真实的AI接口
async function askAi(content: string): Promise<string> {
    try {
        const requestData: AIChatRequest = {
            message: content,
            user_id: globalStore.userInfo?.id?.toString() || "anonymous" // 从全局状态获取用户ID
        };

        const response = await aiChatService.sendMessage(requestData);

        // 检查是否有回复内容
        if (response.reply || response.data?.reply) {
            return response.reply || response.data?.reply || "AI 没有返回有效回复";
        } else {
            throw new Error(response.msg || "AI 服务请求失败");
        }
    } catch (error: any) {
        console.error("AI 接口调用失败:", error);

        // 处理具体的错误类型
        let errorMessage = 'AI服务暂时不可用，显示模拟回复';
        if (error.response) {
            // 服务器返回错误
            const errorData = error.response.data;
            if (errorData && errorData.msg) {
                errorMessage = errorData.msg;
            }

            // 处理特定的错误状态码
            switch (error.response.status) {
                case 429:
                    errorMessage = '请求频率过高，请稍后再试';
                    break;
                case 504:
                    errorMessage = '请求超时，请稍后再试';
                    break;
                case 401:
                    errorMessage = 'API密钥无效';
                    break;
                case 400:
                    errorMessage = '请求格式错误';
                    break;
            }
        }

        // 使用模拟响应作为fallback
        return generateResponse(content);
    }
}

// 生成模拟AI响应
function generateResponse(content: string): string {
    // 模拟不同类型问题的回复
    const responses: Record<string, string> = {
        '如何优化Vue3应用性能？': 'Vue3应用性能优化可以从以下几个方面入手：\n1. 使用Teleport优化DOM结构\n2. 合理使用KeepAlive缓存组件\n3. 使用虚拟列表处理大数据渲染\n4. 优化图片加载策略\n5. 合理使用计算属性和监听器\n6. 避免不必要的响应式数据',
        '介绍一下智能知识库平台的功能？': '智能知识库平台是一个集成了AI技术的现代化知识管理系统，主要功能包括：\n1. 富文本编辑与知识发布\n2. 多维分类与标签系统\n3. 智能AI助手（选中文本右键呼出）\n4. 全局AI聊天功能\n5. AI辅助摘要生成\n6. 数据可视化看板\n7. 基于角色的权限管理',
        '如何使用AI智能摘要功能？': '使用AI智能摘要功能非常简单：\n1. 进入智能AI中心的摘要页面\n2. 粘贴或上传您需要生成摘要的文章\n3. 点击"生成摘要"按钮\n4. 等待AI处理完成，即可获取结构清晰的摘要\n5. 您可以根据需要调整摘要内容或重新生成'
    };

    // 返回匹配的回复或默认回复
    return responses[content] || `这是AI对"${content}"的回复。在实际项目中，这里会调用真实的LLM API来获取智能回答。`;
}

async function send() {
    const content = input.value.trim();
    if (!content || isLoading.value) return;

    // 添加用户消息
    messages.value.push({ role: "user", content, timestamp: new Date() });
    input.value = "";

    // 滚动到底部
    await nextTick(() => {
        scrollToBottom();
    });

    // 显示加载状态
    isLoading.value = true;

    try {
        // AI 回复
        const reply = await askAi(content);
        messages.value.push({ role: "ai", content: reply, timestamp: new Date() });
    } catch (error) {
        messages.value.push({
            role: "ai",
            content: "抱歉，AI服务暂时不可用，请稍后重试。",
            timestamp: new Date()
        });
    } finally {
        isLoading.value = false;
        await nextTick(() => {
            scrollToBottom();
        });
    }
}

function scrollToBottom() {
    messagesRef.value?.scrollTo({
        top: messagesRef.value.scrollHeight,
        behavior: "smooth",
    });
}

function clearChat() {
    messages.value = [];
}

function closeChat() {
    // 发送关闭事件给父组件
    window.dispatchEvent(new CustomEvent("close-ai-chat"));
}

function toggleMinimize() {
    isMinimized.value = !isMinimized.value;
}

// 拖拽功能
function startDrag(e: MouseEvent) {
    // 只有点击头部区域才能拖拽
    if (e.target !== headerRef.value && !headerRef.value?.contains(e.target as Node)) {
        return;
    }

    isDragging.value = true;
    dragStart.value = { x: e.clientX, y: e.clientY };

    document.addEventListener('mousemove', handleDrag);
    document.addEventListener('mouseup', stopDrag);
    e.preventDefault();
}

function handleDrag(e: MouseEvent) {
    if (!isDragging.value) return;

    // 计算鼠标移动的距离
    const deltaX = e.clientX - dragStart.value.x;
    const deltaY = e.clientY - dragStart.value.y;

    // 更新store中的位置
    const newPosition = {
        x: aiChatStore.chatPosition.x + deltaX,
        y: aiChatStore.chatPosition.y + deltaY
    };

    aiChatStore.updateChatPosition(newPosition.x, newPosition.y);

    // 更新拖拽起始点
    dragStart.value = { x: e.clientX, y: e.clientY };
}

function stopDrag() {
    isDragging.value = false;
    document.removeEventListener('mousemove', handleDrag);
    document.removeEventListener('mouseup', stopDrag);
}

function formatTime(date: Date): string {
    return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 接收外部选中文本
function handleAiQuery(e: CustomEvent) {
    input.value = e.detail;
    // 自动发送消息
    if (e.detail && e.detail.trim()) {
        send();
    }
}

onMounted(() => {
    window.addEventListener("ai-query", handleAiQuery as EventListener);
});
onBeforeUnmount(() => {
    window.removeEventListener("ai-query", handleAiQuery as EventListener);
});
</script>

<style scoped>
.ai-chat-box {
    width: min(420px, calc(100vw - 24px));
    height: min(560px, calc(100vh - 32px));
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border-radius: 22px;
    color: var(--text-primary);
    background: color-mix(in srgb, var(--surface) 94%, transparent);
    border: 1px solid var(--line);
    box-shadow: var(--card-shadow), rgba(20, 20, 19, 0.12) 0 24px 70px -38px;
    user-select: none;
    backdrop-filter: blur(20px);
}

.chat-header {
    min-height: 82px;
    padding: 18px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    background: var(--surface);
    border-bottom: 1px solid var(--line);
    cursor: move;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
}

.ai-avatar,
.empty-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    color: var(--button-fg);
    background: var(--terracotta);
    box-shadow: var(--ring);
    font-family: var(--font-mono);
    font-weight: 700;
    letter-spacing: 0;
}

.ai-avatar {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    font-size: 13px;
}

.empty-icon {
    width: 58px;
    height: 58px;
    border-radius: 18px;
    margin-bottom: 4px;
    font-size: 15px;
}

.header-info {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.chat-title {
    color: var(--text-primary);
    font-family: var(--font-serif);
    font-size: 20px;
    font-weight: 500;
    line-height: 1.15;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 7px;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 500;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--terracotta);
    box-shadow: 0 0 0 4px color-mix(in srgb, var(--terracotta) 14%, transparent);
}

.header-actions {
    display: flex;
    gap: 8px;
}

.control-btn {
    width: 34px;
    height: 34px;
    border: 0;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    transition: background 180ms ease, color 180ms ease, transform 180ms ease;
}

.control-btn:hover {
    color: var(--text-primary);
    background: var(--surface-hover);
    transform: translateY(-1px);
}

.close-btn:hover {
    color: var(--button-fg);
    background: var(--terracotta);
}

.chat-content {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    background: var(--surface);
}

.chat-messages {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 20px;
    font-size: 14px;
    background: color-mix(in srgb, var(--surface-subtle) 46%, var(--surface));
}

.chat-messages::-webkit-scrollbar {
    width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
    background: var(--surface-subtle);
}

.chat-messages::-webkit-scrollbar-thumb {
    background: color-mix(in srgb, var(--text-muted) 45%, transparent);
    border: 2px solid var(--surface-subtle);
    border-radius: 999px;
}

.empty-state {
    min-height: 100%;
    padding: 40px 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: var(--text-secondary);
}

.empty-title {
    margin: 8px 0 0;
    color: var(--text-primary);
    font-family: var(--font-serif);
    font-size: 22px;
    font-weight: 500;
    line-height: 1.25;
}

.empty-text {
    max-width: 280px;
    margin: 10px 0 0;
    color: var(--text-muted);
    font-size: 14px;
    line-height: 1.7;
}

.chat-message {
    margin-bottom: 14px;
    display: flex;
}

.chat-message.user {
    justify-content: flex-end;
}

.chat-message.ai {
    justify-content: flex-start;
}

.message-content {
    max-width: 86%;
    padding: 13px 15px;
    border-radius: 16px;
    word-break: break-word;
    box-shadow: var(--ring);
}

.chat-message.user .message-content {
    color: var(--button-fg);
    background: var(--terracotta);
    border-bottom-right-radius: 6px;
}

.chat-message.ai .message-content {
    color: var(--text-primary);
    background: var(--surface);
    border-bottom-left-radius: 6px;
}

.message-text {
    line-height: 1.7;
}

.message-time {
    margin-top: 6px;
    color: color-mix(in srgb, currentColor 66%, transparent);
    font-family: var(--font-mono);
    font-size: 11px;
    line-height: 1;
}

.chat-message.ai .message-time {
    color: var(--text-muted);
}

.typing-indicator {
    display: flex;
    gap: 6px;
    padding: 4px 0;
}

.typing-indicator span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--terracotta);
    animation: typing 1.2s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.16s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.32s; }

@keyframes typing {
    0%, 70%, 100% { transform: translateY(0); opacity: 0.45; }
    35% { transform: translateY(-6px); opacity: 1; }
}

.chat-input {
    flex-shrink: 0;
    padding: 16px 18px 18px;
    background: var(--surface);
    border-top: 1px solid var(--line);
}

.input-wrapper {
    border-radius: 14px;
    border: 1px solid var(--line);
    background: var(--surface-subtle);
    overflow: hidden;
    transition: border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;
}

.input-wrapper:focus-within {
    border-color: var(--focus-blue);
    background: var(--surface);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--focus-blue) 18%, transparent);
}

textarea {
    width: 100%;
    min-height: 62px;
    max-height: 120px;
    resize: none;
    border: 0;
    outline: 0;
    padding: 13px 14px;
    color: var(--text-primary);
    background: transparent;
    font: inherit;
    font-size: 14px;
    line-height: 1.6;
    scrollbar-width: none;
}

textarea::placeholder {
    color: var(--text-muted);
}

textarea::-webkit-scrollbar {
    display: none;
}

.input-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 12px;
}

.action-btn {
    min-width: 40px;
    height: 38px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 0;
    border-radius: 12px;
    cursor: pointer;
    font-weight: 600;
    transition: background 180ms ease, color 180ms ease, transform 180ms ease, opacity 180ms ease;
}

.clear-btn {
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.clear-btn:hover {
    color: var(--text-primary);
    background: var(--surface-hover);
    transform: translateY(-1px);
}

.send-btn {
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.send-btn:hover:not(:disabled) {
    background: var(--button-hover);
    transform: translateY(-1px);
}

.send-btn:disabled {
    opacity: 0.48;
    cursor: not-allowed;
}

.sending-text {
    padding: 0 4px;
    color: currentColor;
    font-size: 13px;
}

.markdown-content :deep(p) {
    margin: 0 0 8px;
}

.markdown-content :deep(p:last-child) {
    margin-bottom: 0;
}

.markdown-content :deep(pre) {
    margin: 10px 0;
    padding: 12px;
    overflow-x: auto;
    border-radius: 12px;
    color: var(--text-primary);
    background: var(--surface-subtle) !important;
    box-shadow: var(--ring);
}

.markdown-content :deep(code) {
    color: var(--text-primary) !important;
    font-family: var(--font-mono) !important;
}

.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

@media (max-width: 480px) {
    .ai-chat-box {
        width: calc(100vw - 18px);
        height: min(520px, calc(100vh - 18px));
    }

    .chat-header {
        padding: 16px;
    }

    .chat-messages {
        padding: 16px;
    }

    .message-content {
        max-width: 90%;
    }
}
</style>
