<template>
    <nav class="elegant-header">
        <div class="container">
            <!-- 左侧Logo和公司名称 -->
            <div class="brand" @click="goToHome">
                <div class="logo">
                    <svg width="48" height="48" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="20" cy="20" r="18" fill="url(#headerGradient)" stroke="white" stroke-width="2" />
                        <path d="M12 20 L20 12 L28 20 L20 28 Z" fill="white" />
                        <defs>
                            <linearGradient id="headerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:#FF7F50;stop-opacity:1" />
                                <stop offset="100%" style="stop-color:#FF6347;stop-opacity:1" />
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <span class="company-name">智汇博客</span>
            </div>

            <!-- 主导航菜单 -->
            <ul class="nav-menu">
                <li class="nav-item" v-for="item in navItems" :key="item.path">
                    <router-link :to="item.path" class="nav-link">
                        <span class="link-text">{{ item.label }}</span>
                        <span class="link-underline"></span>
                    </router-link>
                </li>
            </ul>

            <!-- 右侧用户区域 -->
            <div class="user-area">
                <el-dropdown trigger="hover" @command="handleCommand" placement="bottom">
                    <div class="user-profile">
                        <el-avatar :size="40" :src="userAvatar" class="avatar" />
                        <span class="username">{{ userName }}</span>
                        <span class="dropdown-icon">▼</span>
                    </div>
                    <template #dropdown>
                        <el-dropdown-menu class="elegant-dropdown">
                            <el-dropdown-item command="profile" class="dropdown-item">
                                <span class="item-icon">👤</span>
                                <span>个人中心</span>
                            </el-dropdown-item>
                            <el-dropdown-item command="my-works" class="dropdown-item">
                                <span class="item-icon">📚</span>
                                <span>我的作品</span>
                            </el-dropdown-item>
                            <el-dropdown-item command="my-likes" class="dropdown-item">
                                <span class="item-icon">❤️</span>
                                <span>我的喜欢</span>
                            </el-dropdown-item>
                            <el-dropdown-item command="settings" class="dropdown-item">
                                <span class="item-icon">⚙️</span>
                                <span>账号设置</span>
                            </el-dropdown-item>
                            <el-dropdown-item divided command="logout" class="dropdown-item" v-if="globalStore.token">
                                <span class="item-icon">🚪</span>
                                <span>退出登录</span>
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </div>
        </div>
    </nav>
</template>

<script lang="ts" setup>

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useElMessage } from '@/hooks/useMessage'
import { useGlobalStore } from '@/store'

const { message } = useElMessage()
const router = useRouter()
const globalStore = useGlobalStore()

// 用户信息
const userName = globalStore.userInfo?.username || '游客'
const userAvatar = ref('https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png')

// 导航菜单
const navItems = [
    { path: '/', label: '首页' },
    { path: '/essays', label: '文章' },
    // { path: '/performance', label: '性能优化' },
    { path: '/ai-center', label: 'AI中心' },
    // { path: '/dashboard', label: '数据分析看板' }
]

// 跳转到首页
const goToHome = () => {
    router.push('/')
}

// 处理下拉菜单命令
const handleCommand = (command: string) => {
    switch (command) {
        case 'profile':
            router.push('/profile')
            break
        case 'my-works':
            router.push('/essays/my-works')
            break
        case 'my-likes':
            router.push('/essays/my-likes')
            break
        case 'settings':
            router.push('/settings')
            break
        case 'logout':
            logOut()
            break
    }
}

// 退出登录
const logOut = () => {
    globalStore.clearLoginInfo()
    message.success('退出登录成功')
    router.push('/login')
}
</script>

<style scoped lang="scss">
.elegant-header {
    width: 100%;
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    box-shadow: 0 8px 32px rgba(255, 127, 80, 0.25), 0 2px 8px rgba(255, 127, 80, 0.15);
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    position: relative;
    z-index: 1000;
    animation: headerSlideDown 0.8s cubic-bezier(0.4, 0, 0.2, 1) both;
    backdrop-filter: blur(10px);
    overflow-x: hidden;

    .container {
        max-width: 100%;
        margin: 0 auto;
        padding: 0 15px;
        display: flex;
        align-items: center;
        height: 80px;
        justify-content: space-between;
        box-sizing: border-box;
        overflow-x: hidden;
    }
}

@keyframes headerSlideDown {
    from {
        transform: translateY(-100%);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.brand {
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
        transform: translateY(-2px);
    }

    .logo {
        margin-right: 16px;
        transition: transform 0.3s ease;
    }

    &:hover .logo {
        transform: rotate(5deg) scale(1.05);
    }

    .company-name {
        font-size: 22px;
        font-weight: 700;
        color: white;
        letter-spacing: 1px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }
}

.nav-menu {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: 48px;
}

.nav-item {
    position: relative;
}

.nav-link {
    color: white;
    font-weight: 600;
    text-decoration: none;
    font-size: 16px;
    padding: 8px 0;
    transition: all 0.3s ease;
    position: relative;
    display: inline-block;
    cursor: pointer;

    .link-text {
        position: relative;
        z-index: 1;
    }

    .link-underline {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 0;
        height: 3px;
        background: white;
        border-radius: 2px;
        transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    &:hover {
        transform: translateY(-2px);
    }

    &:hover .link-underline,
    &.router-link-active .link-underline {
        width: 100%;
    }

    &.router-link-active {
        font-weight: 700;
    }
}

.user-area {
    display: flex;
    align-items: center;
}

.user-profile {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 8px 16px;
    border-radius: 24px;
    background-color: rgba(255, 255, 255, 0.15);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);

    &:hover {
        background-color: rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15), 0 2px 8px rgba(0, 0, 0, 0.08);
        border-color: rgba(255, 255, 255, 0.3);
    }
}

.avatar {
    border: 2px solid rgba(255, 255, 255, 0.3);
    transition: transform 0.3s ease;
}

.user-profile:hover .avatar {
    transform: scale(1.1);
}

.username {
    margin: 0 12px 0 16px;
    font-size: 15px;
    color: white;
    font-weight: 600;
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.dropdown-icon {
    color: white;
    font-size: 16px;
    transition: transform 0.3s ease;
}

.user-profile:hover .dropdown-icon {
    transform: rotate(180deg) scale(1.1);
}

.elegant-dropdown {
    border-radius: 12px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.08);
    border: none;
    padding: 8px 0;
    background: white;
    backdrop-filter: blur(10px);
}

.dropdown-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 20px;
    transition: all 0.2s ease;
    border-radius: 8px;
    margin: 2px 8px;

    &:hover {
        background: linear-gradient(135deg, rgba(255, 127, 80, 0.05), rgba(255, 99, 71, 0.05));
        color: #FF7F50;
    }

    .item-icon {
        font-size: 18px;
    }
}

// 响应式设计
@media (max-width: 1024px) {
    .nav-menu {
        gap: 32px;
    }

    .company-name {
        font-size: 20px;
    }
}

@media (max-width: 768px) {
    .nav-menu {
        display: none;
    }

    .elegant-header .container {
        padding: 0 15px;
        height: 70px;
        width: 100%;
        box-sizing: border-box;
    }

    .company-name {
        font-size: 18px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 150px;
    }

    .logo {
        margin-right: 10px;
    }

    .username {
        display: none;
    }

    .user-profile {
        padding: 6px 12px;
    }
}
</style>