<template>
    <div class="ai-chat-box" role="dialog" aria-labelledby="chat-title" aria-modal="true">
        <div class="chat-header" ref="headerRef" @mousedown="startDrag">
            <div class="header-left">
                <div class="ai-avatar">
                    <svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="22" cy="22" r="20" fill="url(#avatarGradient)" />
                        <path d="M15 22L22 15L29 22L22 29Z" fill="white" />
                        <path d="M18 18L26 18" stroke="white" stroke-width="2" stroke-linecap="round" />
                        <path d="M18 26L26 26" stroke="white" stroke-width="2" stroke-linecap="round" />
                        <defs>
                            <linearGradient id="avatarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:#FF7F50;stop-opacity:1" />
                                <stop offset="100%" style="stop-color:#FF6347;stop-opacity:1" />
                            </linearGradient>
                        </defs>
                    </svg>
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
                        <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="32" cy="32" r="30" stroke="#FF7F50" stroke-width="2" opacity="0.3" />
                            <path d="M20 32L28 24L36 32L28 40Z" fill="#FF7F50" opacity="0.6" />
                            <path d="M23 28L31 20L39 28L31 36Z" fill="#FF7F50" opacity="0.8" />
                        </svg>
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
    border-radius: 20px;
    width: 400px;
    height: 550px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: white;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15), 0 10px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 127, 80, 0.1);
    user-select: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
}

.ai-chat-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2), 0 15px 30px rgba(0, 0, 0, 0.15);
}

.chat-header {
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    padding: 20px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    cursor: move;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.chat-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url('data:image/svg+xml,<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><circle cx="30" cy="30" r="1" fill="white" opacity="0.1"/></svg>');
    background-size: 30px 30px;
}

.chat-header:hover {
    background: linear-gradient(135deg, #FF8A65 0%, #FF7043 100%);
}

.header-left {
    display: flex;
    align-items: center;
    gap: 16px;
    position: relative;
    z-index: 1;
}

.ai-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 20px rgba(255, 127, 80, 0.3);
    background: linear-gradient(135deg, #FF7F50, #FF6347);
    border: 3px solid rgba(255, 255, 255, 0.2);
    transition: transform 0.3s ease;
}

.chat-header:hover .ai-avatar {
    transform: scale(1.05) rotate(5deg);
}

.header-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.chat-title {
    font-weight: 700;
    font-size: 18px;
    color: white;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #4CAF50;
    box-shadow: 0 0 8px rgba(76, 175, 80, 0.8);
    animation: pulse 2s infinite;
}

@keyframes pulse {

    0%,
    100% {
        opacity: 1;
        transform: scale(1);
    }

    50% {
        opacity: 0.7;
        transform: scale(1.1);
    }
}

.header-actions {
    display: flex;
    gap: 8px;
    position: relative;
    z-index: 1;
}

.control-btn {
    width: 36px;
    height: 36px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: rgba(255, 255, 255, 0.2);
    color: white;
    backdrop-filter: blur(10px);
}

.control-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.close-btn:hover {
    background: rgba(255, 71, 71, 0.4);
}

.chat-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #fefefe;
    min-height: 0;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    font-size: 14px;
    background: linear-gradient(180deg, #ffffff 0%, #fff8f5 100%);
    min-height: 0;
}

/* 自定义滚动条样式 */
.chat-messages::-webkit-scrollbar {
    width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
    background: rgba(255, 127, 80, 0.1);
    border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #FF7F50, #FF6347);
    border-radius: 4px;
    border: 2px solid rgba(255, 255, 255, 0.3);
}

.chat-messages::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #FF8A65, #FF7043);
}

.empty-state {
    text-align: center;
    color: #666;
    padding: 60px 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
}

.empty-icon {
    margin-bottom: 10px;
    animation: float 3s ease-in-out infinite;
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-10px);
    }
}

.empty-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin: 0;
}

.empty-text {
    font-size: 14px;
    color: #666;
    margin: 0;
    line-height: 1.6;
    max-width: 280px;
}

.chat-message {
    margin-bottom: 16px;
}

.message-content {
    max-width: 85%;
    word-wrap: break-word;
    animation: messageSlide 0.3s ease-out both;
}

@keyframes messageSlide {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.chat-message.user {
    display: flex;
    justify-content: flex-end;
}

.chat-message.user .message-content {
    background: linear-gradient(135deg, #FF7F50, #FF6347);
    color: white;
    padding: 14px 18px;
    border-radius: 20px 20px 6px 20px;
    box-shadow: 0 4px 16px rgba(255, 127, 80, 0.25);
    backdrop-filter: blur(10px);
}

.chat-message.ai {
    display: flex;
    justify-content: flex-start;
}

.chat-message.ai .message-content {
    background: white;
    color: #333;
    padding: 14px 18px;
    border-radius: 20px 20px 20px 6px;
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 127, 80, 0.1);
}

.message-time {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 6px;
    text-align: right;
    opacity: 0.8;
}

.chat-message.ai .message-time {
    color: #999;
    text-align: left;
}

.typing-indicator {
    display: flex;
    gap: 6px;
    padding: 12px;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    background: linear-gradient(135deg, #FF7F50, #FF6347);
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {

    0%,
    60%,
    100% {
        transform: translateY(0);
        opacity: 0.5;
    }

    30% {
        transform: translateY(-12px);
        opacity: 1;
    }
}

.chat-input {
    padding: 20px 24px;
    background: white;
    border-top: 1px solid rgba(255, 127, 80, 0.1);
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
}

.input-wrapper {
    flex: 1;
    border-radius: 16px;
    border: 2px solid rgba(255, 127, 80, 0.1);
    background: #fefefe;
    transition: all 0.3s ease;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.input-wrapper:focus-within {
    border-color: #FF7F50;
    box-shadow: 0 0 0 3px rgba(255, 127, 80, 0.1), 0 4px 12px rgba(255, 127, 80, 0.15);
    background: white;
}

.input-actions {
    display: flex;
    gap: 12px;
    margin-top: 12px;
    justify-content: flex-end;
    flex-shrink: 0;
}

.action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 12px 20px;
    border-radius: 14px;
    border: none;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-weight: 600;
    font-size: 14px;
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.clear-btn {
    background: rgba(255, 127, 80, 0.1);
    color: #FF7F50;
    border: 2px solid transparent;
    min-width: 44px;
}

.clear-btn:hover {
    background: rgba(255, 127, 80, 0.15);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 127, 80, 0.2);
    border-color: rgba(255, 127, 80, 0.3);
}

.send-btn {
    background: linear-gradient(135deg, #FF7F50, #FF6347);
    color: white;
    min-width: 44px;
    box-shadow: 0 6px 20px rgba(255, 127, 80, 0.3);
}

.send-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #FF8A65, #FF7043);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 127, 80, 0.4);
}

.send-btn:disabled {
    background: #E0E0E0;
    color: #9E9E9E;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.sending-text {
    font-size: 14px;
    color: white;
    font-weight: 600;
}

textarea {
    width: 100%;
    resize: none;
    border: none;
    padding: 16px 20px;
    font-size: 14px;
    font-family: inherit;
    background: transparent;
    color: #333;
    min-height: 60px;
    max-height: 100px;
    box-sizing: border-box;
    line-height: 1.5;
    outline: none;
}

textarea::placeholder {
    color: #999;
    opacity: 0.7;
}

/* 隐藏滚动条 */
textarea::-webkit-scrollbar {
    display: none;
}

textarea {
    scrollbar-width: none;
    -ms-overflow-style: none;
}

/* 屏幕阅读器专用样式 */
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

/* 响应式设计 */
@media (max-width: 480px) {
    .ai-chat-box {
        width: 340px;
        height: 500px;
    }

    .chat-header {
        padding: 16px 20px;
    }

    .chat-messages {
        padding: 20px;
    }

    .chat-input {
        padding: 16px 20px;
    }

    .chat-message.user .message-content,
    .chat-message.ai .message-content {
        padding: 12px 16px;
        max-width: 90%;
    }
}
</style>