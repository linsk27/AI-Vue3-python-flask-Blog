import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAiChatStore = defineStore('aiChat', () => {
  // 聊天框显示状态
  const showChat = ref(false)
  
  // 聊天框位置
  const chatPosition = ref({ x: 0, y: 0 })
  
  // 是否首次显示
  const isFirstShow = ref(true)
  
  // 右键菜单位置（用于首次定位）
  const menuPosition = ref({ x: 0, y: 0 })
  
  // 设置菜单位置
  function setMenuPosition(x: number, y: number) {
    menuPosition.value = { x, y }
  }
  
  // 显示聊天框
  function showChatBox() {
    // 如果是首次显示，定位到菜单附近
    if (isFirstShow.value) {
      chatPosition.value = {
        x: menuPosition.value.x - 200, // 在菜单左侧显示
        y: menuPosition.value.y - 50
      }
      isFirstShow.value = false
    }
    showChat.value = true
  }
  
  // 隐藏聊天框
  function hideChatBox() {
    showChat.value = false
  }
  
  // 更新聊天框位置
  function updateChatPosition(x: number, y: number) {
    chatPosition.value = { x, y }
  }
  
  // 重置状态（用于重新开始）
  function reset() {
    showChat.value = false
    isFirstShow.value = true
    chatPosition.value = { x: 0, y: 0 }
    menuPosition.value = { x: 0, y: 0 }
  }
  
  return {
    showChat,
    chatPosition,
    isFirstShow,
    menuPosition,
    setMenuPosition,
    showChatBox,
    hideChatBox,
    updateChatPosition,
    reset
  }
})
