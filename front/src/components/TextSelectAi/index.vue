<template>
    <div @mouseup="handleSelection" @contextmenu="handleContextMenu" @selectstart="handleSelection" class="text-select-wrapper">
        <slot></slot>

        <!-- 自定义右键菜单 -->
        <div 
            v-if="menuVisible" 
            class="context-menu" 
            :style="{ top: menuY + 'px', left: menuX + 'px' }" 
            @click.stop
            role="menu"
            aria-label="文本操作菜单"
        >
            <div 
                class="menu-item" 
                @click.stop="askAi"
                role="menuitem"
                tabindex="0"
                @keydown.enter="askAi"
                @keydown.space.prevent="askAi"
            >
                💬 使用 AI 询问
            </div>
        </div>

        <!-- 浮动聊天框 -->
        <transition name="slide-fade">
            <div 
                v-if="aiChatStore.showChat" 
                class="chat-float"
                :style="{ 
                    left: aiChatStore.chatPosition.x + 'px', 
                    top: aiChatStore.chatPosition.y + 'px' 
                }"
            >
                <AiChatBox />
            </div>
        </transition>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue";
import AiChatBox from "./AiChatBox.vue";
import { useAiChatStore } from "@/store/aiChat";
import { usePermission } from "@/hooks/usePermission";

const selectedText = ref(""); // 缓存选中的文本
const menuVisible = ref(false);
const menuX = ref(0);
const menuY = ref(0);

// 使用store管理聊天框状态
const aiChatStore = useAiChatStore();
const { hasPermission } = usePermission();

// ✅ 选中文本时缓存下来
function handleSelection() {
    // 延迟处理，确保选择完成
    setTimeout(() => {
        // 如果菜单正在显示，不要清空缓存
        if (menuVisible.value) {
            return;
        }
        
        const selection = window.getSelection();
        const text = selection?.toString().trim();
        
        // 验证选择是否有效
        if (text && text.length >= 2 && text.length <= 1000) {
            // 检查是否在可选择的元素内
            const range = selection?.getRangeAt(0);
            if (range && isValidSelection(range)) {
                selectedText.value = text;
            } else {
                selectedText.value = "";
            }
        } else {
            selectedText.value = "";
        }
    }, 50);
}

// 验证选择是否在允许的区域内
function isValidSelection(range: Range): boolean {
    const container = range.commonAncestorContainer;
    // 排除不可选择的元素（如按钮、输入框等）
    const excludedTags = ['INPUT', 'TEXTAREA', 'BUTTON', 'SELECT'];
    let element = container.nodeType === Node.TEXT_NODE ? container.parentElement : container as Element;
    
    while (element && element !== document.body) {
        if (excludedTags.includes(element.tagName)) {
            return false;
        }
        element = element.parentElement;
    }
    return true;
}

// ✅ 打开右键菜单时仅显示，不再更新选中内容
function handleContextMenu(e: MouseEvent) {
    // 检查权限，如果没有AI聊天权限，不拦截右键菜单，直接返回
    if (!hasPermission('ai:access')) {
        return;
    }

    e.preventDefault();
    
    // 记录菜单位置到store
    aiChatStore.setMenuPosition(e.clientX, e.clientY);
    
    // 在右键时重新获取选中的文本，确保是最新的
    const selection = window.getSelection();
    const text = selection?.toString().trim();
    
    if (text && text.length >= 2 && text.length <= 1000) {
        // 检查是否在可选择的元素内
        const range = selection?.getRangeAt(0);
        if (range && isValidSelection(range)) {
            selectedText.value = text;
            menuVisible.value = true;
        } else {
            menuVisible.value = false;
        }
    } else {
        menuVisible.value = false;
    }
    
    // 智能定位菜单，避免超出屏幕边界
    const menuWidth = 150; // 预估菜单宽度
    const menuHeight = 40; // 预估菜单高度
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    let x = e.clientX;
    let y = e.clientY;
    
    // 水平方向调整
    if (x + menuWidth > viewportWidth) {
        x = viewportWidth - menuWidth - 10;
    }
    
    // 垂直方向调整
    if (y + menuHeight > viewportHeight) {
        y = y - menuHeight - 5; // 显示在鼠标上方
    }
    
    menuX.value = Math.max(10, x);
    menuY.value = Math.max(10, y);
}

// ✅ 点击AI按钮时使用缓存内容
async function askAi() {
    // 在函数开始时立即保存文本，防止被其他地方清空
    const text = selectedText.value.trim();
    
    if (!text) {
        return;
    }
    
    // 使用store显示聊天框
    aiChatStore.showChatBox();
    
    await nextTick(); // 等待聊天框渲染
    window.dispatchEvent(new CustomEvent("ai-query", { detail: text }));
    menuVisible.value = false;
    // 延迟清空缓存，让事件处理完成
    setTimeout(() => {
        selectedText.value = "";
    }, 200);
}

// 点击空白关闭菜单
function handleClickOutside(e: MouseEvent) {
    // 延迟处理，确保菜单项的点击事件先执行
    setTimeout(() => {
        const target = e.target as Element;
        if (!target.closest('.context-menu') && !target.closest('.chat-float')) {
            menuVisible.value = false;
        }
    }, 100);
}

// 键盘快捷键支持
function handleKeydown(e: KeyboardEvent) {
    // Ctrl/Cmd + K 快速打开AI聊天
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (selectedText.value) {
            askAi();
        }
    }
    
    // ESC 关闭菜单
    if (e.key === 'Escape') {
        menuVisible.value = false;
        aiChatStore.hideChatBox();
    }
}

// 处理关闭聊天框事件
function handleCloseChat() {
    aiChatStore.hideChatBox();
}

onMounted(() => {
    window.addEventListener("click", handleClickOutside);
    window.addEventListener("keydown", handleKeydown);
    window.addEventListener("close-ai-chat", handleCloseChat);
    // 监听选择变化事件，更可靠地捕获文本选择
    document.addEventListener("selectionchange", handleSelection);
});
onBeforeUnmount(() => {
    window.removeEventListener("click", handleClickOutside);
    window.removeEventListener("keydown", handleKeydown);
    window.removeEventListener("close-ai-chat", handleCloseChat);
    document.removeEventListener("selectionchange", handleSelection);
});
</script>

<style scoped>
.text-select-wrapper {
    position: relative;
    user-select: text;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    min-height: 100%;
}

.context-menu {
    position: fixed;
    background: #fff;
    border: 1px solid #ccc;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    border-radius: 8px;
    z-index: 2000;
    font-size: 14px;
}

.menu-item {
    padding: 8px 12px;
    cursor: pointer;
}

.menu-item:hover {
    background: #f0f0f0;
}

.chat-float {
    position: fixed;
    z-index: 2100;
    cursor: move;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity .3s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

.slide-fade-enter-active {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.slide-fade-leave-active {
    transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
}

.slide-fade-leave-to {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
}
</style>
