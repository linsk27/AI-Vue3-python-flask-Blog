<template>
    <header class="site-header">
        <nav class="nav-shell" aria-label="主导航">
            <button class="brand" type="button" aria-label="回到首页" @click="goToHome">
                <span class="brand-mark" aria-hidden="true">
                    <span class="brand-mark-inner"></span>
                </span>
                <span class="brand-copy">
                    <span class="brand-name">智汇博客</span>
                    <span class="brand-subtitle">AI Knowledge Lab</span>
                </span>
            </button>

            <ul class="nav-menu">
                <li v-for="item in navItems" :key="item.path">
                    <router-link :to="item.path" class="nav-link">
                        {{ item.label }}
                    </router-link>
                </li>
            </ul>

            <div class="nav-actions">
                <button class="theme-toggle" type="button" :aria-label="themeLabel" @click="toggleTheme">
                    <Sunny v-if="theme === 'dark'" class="action-icon" />
                    <Moon v-else class="action-icon" />
                </button>
                <router-link to="/essays/write" class="write-link">
                    <EditPen class="action-icon" />
                    <span>写作</span>
                </router-link>
                <el-dropdown trigger="hover" @command="handleCommand" placement="bottom-end">
                    <button class="user-profile" type="button" aria-label="打开用户菜单">
                        <el-avatar :size="28" :src="userAvatar" class="avatar" />
                        <span class="username">{{ userName }}</span>
                        <ArrowDown class="chevron" />
                    </button>
                    <template #dropdown>
                        <el-dropdown-menu class="profile-menu">
                            <el-dropdown-item command="profile">
                                <User class="menu-icon" />
                                <span>个人中心</span>
                            </el-dropdown-item>
                            <el-dropdown-item command="my-works">
                                <Document class="menu-icon" />
                                <span>我的作品</span>
                            </el-dropdown-item>
                            <el-dropdown-item command="my-likes">
                                <Star class="menu-icon" />
                                <span>我的喜欢</span>
                            </el-dropdown-item>
                            <el-dropdown-item divided command="logout" v-if="globalStore.token">
                                <SwitchButton class="menu-icon" />
                                <span>退出登录</span>
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </div>
        </nav>
    </header>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown, Document, EditPen, Moon, Star, Sunny, SwitchButton, User } from '@element-plus/icons-vue'
import { useElMessage } from '@/hooks/useMessage'
import { useGlobalStore } from '@/store'

const { message } = useElMessage()
const router = useRouter()
const globalStore = useGlobalStore()

const userName = computed(() => globalStore.userInfo?.username || '访客')
const userAvatar = ref('https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png')

const theme = ref(document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light')
const themeLabel = computed(() => theme.value === 'dark' ? '切换到白色主题' : '切换到黑色主题')

const navItems = [
    { path: '/', label: '首页' },
    { path: '/essays', label: '文章' },
    { path: '/ai-center', label: 'AI 中心' }
]

const goToHome = () => {
    router.push('/')
}

const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    document.documentElement.dataset.theme = theme.value
    localStorage.setItem('theme', theme.value)
}

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
        case 'logout':
            globalStore.clearLoginInfo()
            message.success('已退出登录')
            router.push('/login')
            break
    }
}
</script>

<style scoped lang="scss">
.site-header {
    position: sticky;
    top: 0;
    z-index: 1000;
    width: 100%;
    padding: 12px 16px;
    background: var(--header-bg);
    backdrop-filter: blur(18px);
}

.nav-shell {
    max-width: 1200px;
    height: 56px;
    margin: 0 auto;
    padding: 0 8px 0 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--ring), rgba(0, 0, 0, 0.04) 0 2px 2px;
}

.brand {
    min-width: 0;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    border: 0;
    background: transparent;
    color: var(--text-primary);
    cursor: pointer;
    padding: 6px;
    border-radius: 6px;
    transition: background 180ms ease;

    &:hover {
        background: var(--surface-hover);
    }
}

.brand-mark {
    width: 28px;
    height: 28px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: var(--button-bg);
}

.brand-mark-inner {
    width: 11px;
    height: 11px;
    display: block;
    background: var(--button-fg);
    transform: rotate(45deg);
}

.brand-copy {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    line-height: 1.05;
}

.brand-name {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: -0.32px;
}

.brand-subtitle {
    margin-top: 3px;
    font-family: "Geist Mono", ui-monospace, monospace;
    font-size: 10px;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
}

.nav-menu {
    display: flex;
    align-items: center;
    gap: 4px;
    list-style: none;
    margin: 0;
    padding: 0;
}

.nav-link {
    display: inline-flex;
    align-items: center;
    height: 34px;
    padding: 0 12px;
    border-radius: 6px;
    color: var(--text-secondary);
    font-size: 14px;
    font-weight: 500;
    transition: color 180ms ease, background 180ms ease, box-shadow 180ms ease;

    &:hover,
    &.router-link-active {
        color: var(--text-primary);
        background: var(--surface-hover);
        box-shadow: var(--ring);
    }
}

.nav-actions {
    display: flex;
    align-items: center;
    gap: 8px;
}

.theme-toggle,
.write-link,
.user-profile {
    height: 36px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease;
}

.write-link {
    padding: 0 12px;
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);

    &:hover {
        background: var(--button-hover);
    }
}

.theme-toggle {
    width: 36px;
    justify-content: center;
    padding: 0;
    color: var(--text-primary);
    background: var(--surface);
    border: 0;
    box-shadow: var(--ring);

    &:hover {
        background: var(--surface-hover);
    }
}

.user-profile {
    max-width: 180px;
    padding: 0 10px 0 6px;
    color: var(--text-primary);
    background: var(--surface);
    border: 0;
    box-shadow: var(--ring);

    &:hover {
        background: var(--surface-hover);
    }
}

.avatar {
    box-shadow: var(--ring);
}

.username {
    max-width: 84px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.action-icon,
.chevron,
.menu-icon {
    width: 16px;
    height: 16px;
}

.chevron {
    color: var(--text-muted);
}

.profile-menu :deep(.el-dropdown-menu__item) {
    gap: 8px;
    font-size: 14px;
}

@media (max-width: 760px) {
    .site-header {
        padding: 8px;
    }

    .nav-shell {
        height: 54px;
    }

    .brand-subtitle,
    .nav-menu,
    .write-link span,
    .username {
        display: none;
    }

    .write-link,
    .user-profile {
        width: 36px;
        justify-content: center;
        padding: 0;
    }
}
</style>
