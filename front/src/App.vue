<template>
    <div v-if="route.path === '/login'" class="login-container">
        <router-view></router-view>
    </div>
    <div v-else class="app-container">
        <Header />
        <main>
            <TextSelectAi>
                <router-view></router-view>
            </TextSelectAi>
        </main>
        <Footer />
    </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { nextTick, onBeforeUnmount, onMounted, watch } from 'vue'
import authApi from '@/api/modules/auth'
import { useGlobalStore } from '@/store'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import TextSelectAi from './components/TextSelectAi/index.vue'

const route = useRoute()
const globalStore = useGlobalStore()
let overlayCleanupTimer: number | undefined
let overlayObserver: MutationObserver | null = null

function cleanupOrphanOverlays() {
    const overlays = Array.from(document.querySelectorAll<HTMLElement>('.el-overlay'))
    overlays.forEach(overlay => {
        const hasVisibleDialog = Boolean(overlay.querySelector('.el-dialog, .el-drawer, .el-message-box'))
        if (!hasVisibleDialog) {
            overlay.remove()
        }
    })

    if (!document.querySelector('.el-overlay')) {
        document.body.classList.remove('el-popup-parent--hidden')
        document.body.style.removeProperty('overflow')
        document.body.style.removeProperty('padding-right')
    }
}

function scheduleOverlayCleanup() {
    window.clearTimeout(overlayCleanupTimer)
    overlayCleanupTimer = window.setTimeout(cleanupOrphanOverlays, 160)
}

onMounted(async () => {
    if (globalStore.token) {
        try {
            const userInfo = await authApi.getUserInfo()
            if (userInfo) {
                globalStore.setLoginInfo(globalStore.token, {
                    ...userInfo,
                    token: globalStore.token
                })
            }
        } catch (error) {
            console.error('Get user info failed:', error)
            if ((error as any).response?.status === 401) {
                globalStore.clearLoginInfo()
            }
        }
    }

    scheduleOverlayCleanup()
    overlayObserver = new MutationObserver(scheduleOverlayCleanup)
    overlayObserver.observe(document.body, { childList: true, subtree: true })
})

onBeforeUnmount(() => {
    window.clearTimeout(overlayCleanupTimer)
    overlayObserver?.disconnect()
    overlayObserver = null
})

watch(
    () => route.fullPath,
    async () => {
        await nextTick()
        scheduleOverlayCleanup()
    }
)
</script>

<style>
html,
body {
    margin: 0;
    padding: 0;
    width: 100%;
    min-height: 100%;
    overflow-x: hidden;
    box-sizing: border-box;
}

#app {
    min-height: 100vh;
    background: transparent;
}

* {
    box-sizing: inherit;
    margin: 0;
    padding: 0;
}

.container,
.login-container,
.app-container,
.app-container main,
.app-container footer {
    width: 100%;
    overflow-x: hidden;
}
</style>

<style scoped>
.login-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.app-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background: transparent;
}

.app-container main {
    flex: 1;
    background: transparent;
}

.app-container footer {
    margin-top: auto;
}
</style>
