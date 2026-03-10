<template>
    <!-- 星星特效 -->
    <StarBackground v-if="imgStore.ifShowStar" />
    <!-- 背景图片 -->
    <transition name="fade" mode="out-in">
        <img class="img-base" :key="imgStore.url ?? ''" :src="imgStore?.url || defaultBg" alt="背景图片" />
    </transition>
    <!-- 登录页 -->
    <div v-if="route.path === '/login'" class="login-container">
        <router-view></router-view>
    </div>
    <!-- 内容 -->
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
import defaultBg from "@/assets/images/backImg.jpg"
import { useRoute } from 'vue-router';
import { onMounted } from 'vue';
import authApi from '@/api/modules/auth';
import { useGlobalStore } from '@/store';

const route = useRoute();
const globalStore = useGlobalStore();
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
import StarBackground from './components/StarBackground.vue';
import { useImgStore } from './store/backgroundImg';
import TextSelectAi from './components/TextSelectAi/index.vue';
// 背景图片状态管理
const imgStore = useImgStore()

// 初始化时获取用户信息，确保权限是最新的
onMounted(async () => {
    if (globalStore.token) {
        try {
            const userInfo = await authApi.getUserInfo();
            if (userInfo) {
                // 保持原有的 token
                globalStore.setLoginInfo(globalStore.token, {
                    ...userInfo,
                    token: globalStore.token
                });
            }
        } catch (error) {
            console.error('获取用户信息失败:', error);
            // 如果获取失败且是 401，清除登录信息
            if ((error as any).response?.status === 401) {
                globalStore.clearLoginInfo();
            }
        }
    }
})

</script>

<style>
/* 全局重置 - 不使用scoped，确保应用到整个文档 */
html,
body {
    margin: 0;
    padding: 0;
    width: 100%;
    overflow-x: hidden;
    box-sizing: border-box;
}

* {
    box-sizing: inherit;
    margin: 0;
    padding: 0;
}

/* 确保所有容器都不会导致横向滚动 */
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
.container {
    height: 100vh;
    display: flex;
    flex-direction: column;
}

.img-base {
    position: fixed;
    height: 100vh;
    top: 0;
    width: 100%;
    overflow: hidden;
    left: 0;
    object-fit: cover;
    z-index: -10;
}

.fade-enter-active {
    transition: opacity 0.5s ease;
}


.fade-enter-from {
    opacity: 0.5;
}

.fade-enter-to,
.fade-leave-from {
    opacity: 1;
}

.fade-leave-to {
    opacity: 1;
    /* 不让旧图淡出 */
}

/* 登录页容器 */
.login-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* 主应用容器 */
.app-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

/* 主内容区域 */
.app-container main {
    flex: 1;
}

/* 确保footer固定在底部 */
.app-container footer {
    margin-top: auto;
}
</style>
