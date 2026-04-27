<template>
    <main class="auth-page">
        <section class="auth-intro" aria-label="产品介绍">
            <button class="brand" type="button" @click="goHome" aria-label="返回首页">
                <span class="brand-mark" aria-hidden="true"></span>
                <span>智汇博客</span>
            </button>

            <div class="intro-copy">
                <span class="eyebrow">AI Knowledge Lab</span>
                <h1>{{ isLoginMode ? '欢迎回来' : '创建账号' }}</h1>
                <p>
                    登录后继续管理你的文章、AI 摘要和知识工作流。也可以先以访客身份浏览精选内容。
                </p>
            </div>

            <div class="workflow-card" aria-hidden="true">
                <div class="workflow-row">
                    <span class="dot develop"></span>
                    <span>Develop</span>
                    <strong>整理想法</strong>
                </div>
                <div class="workflow-row">
                    <span class="dot preview"></span>
                    <span>Preview</span>
                    <strong>AI 辅助</strong>
                </div>
                <div class="workflow-row">
                    <span class="dot ship"></span>
                    <span>Ship</span>
                    <strong>发布沉淀</strong>
                </div>
            </div>
        </section>

        <section class="auth-card" aria-label="账号表单">
            <div class="auth-header">
                <span class="card-kicker">{{ isLoginMode ? 'Sign in' : 'Sign up' }}</span>
                <h2>{{ isLoginMode ? '登录账号' : '注册账号' }}</h2>
                <p>{{ isLoginMode ? '使用用户名和密码进入工作台。' : '创建一个新账号，开始写作与收藏。' }}</p>
            </div>

            <form class="auth-form" autocomplete="off" @submit.prevent="handleSubmit">
                <label class="field" for="username">
                    <span>用户名</span>
                    <div class="input-shell">
                        <User class="field-icon" />
                        <input id="username" v-model="formData.username" type="text" placeholder="请输入用户名" required />
                    </div>
                </label>

                <label class="field" for="password">
                    <span>密码</span>
                    <div class="input-shell">
                        <Lock class="field-icon" />
                        <input
                            id="password"
                            v-model="formData.password"
                            type="password"
                            placeholder="请输入密码"
                            required
                            minlength="6"
                        />
                    </div>
                </label>

                <label v-if="!isLoginMode" class="field" for="email">
                    <span>邮箱</span>
                    <div class="input-shell">
                        <Message class="field-icon" />
                        <input id="email" v-model="formData.email" type="email" placeholder="请输入邮箱" />
                    </div>
                </label>

                <label v-if="!isLoginMode" class="field" for="confirmPassword">
                    <span>确认密码</span>
                    <div class="input-shell">
                        <Key class="field-icon" />
                        <input
                            id="confirmPassword"
                            v-model="formData.confirmPassword"
                            type="password"
                            placeholder="请再次输入密码"
                            required
                            minlength="6"
                        />
                    </div>
                </label>

                <button class="submit-btn" type="submit">
                    <span>{{ isLoginMode ? '登录' : '注册' }}</span>
                    <ArrowRight class="button-icon" />
                </button>
            </form>

            <div class="auth-footer">
                <button class="text-button" type="button" @click="toggleMode">
                    {{ isLoginMode ? '没有账号？去注册' : '已有账号？去登录' }}
                </button>
                <button class="guest-btn" type="button" @click="guestLogin">
                    <View class="button-icon" />
                    <span>访客体验</span>
                </button>
            </div>
        </section>
    </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Key, Lock, Message, User, View } from '@element-plus/icons-vue'
import { useElMessage } from '@/hooks/useMessage'
import authApi from '@/api/modules/auth'
import { useGlobalStore } from '@/store'
import { IUserInfo } from '@/api/modules/auth/interface'

const router = useRouter()
const { message } = useElMessage()
const global = useGlobalStore()
const isLoginMode = ref(true)

const formData = ref({
    username: '',
    password: '',
    confirmPassword: '',
    email: ''
})

const goHome = () => {
    router.push('/')
}

const toggleMode = () => {
    isLoginMode.value = !isLoginMode.value
    formData.value = { username: '', password: '', confirmPassword: '', email: '' }
}

const login = async () => {
    try {
        const data: IUserInfo = await authApi.login({
            username: formData.value.username,
            password: formData.value.password
        })
        if (data) {
            global.setLoginInfo(data.token, data)
            message.success('登录成功')
            router.push('/')
        }
    } catch (error: any) {
        const msg = error.response?.data?.msg || error.message || '登录失败'
        message.error(msg)
    }
}

const register = async () => {
    try {
        if (formData.value.password !== formData.value.confirmPassword) {
            message.warning('两次输入的密码不一致，请检查后重试')
            return
        }
        const data = (await authApi.register({
            username: formData.value.username,
            password: formData.value.password,
            email: formData.value.email
        })) as { success: boolean }
        if (data.success) {
            toggleMode()
            message.success('注册成功，请重新登录')
        }
    } catch (error: any) {
        const msg = error.response?.data?.msg || error.message || '注册失败'
        message.error(msg)
    }
}

const handleSubmit = async () => {
    if (isLoginMode.value) {
        await login()
    } else {
        await register()
    }
}

const guestLogin = () => {
    router.push('/')
    message.success('已进入访客模式')
}
</script>

<style scoped>
.auth-page {
    min-height: 100vh;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(360px, 480px);
    gap: 48px;
    align-items: center;
    width: var(--page-width);
    max-width: var(--page-max);
    margin: 0 auto;
    padding: 48px 0;
    color: var(--text-primary);
    background: transparent;
}

.auth-intro {
    min-height: 620px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 32px 0;
}

.brand {
    width: fit-content;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    border: 0;
    background: transparent;
    color: var(--text-primary);
    cursor: pointer;
    padding: 6px;
    border-radius: 10px;
    font: inherit;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0;
}

.brand:hover {
    background: var(--surface-hover);
}

.brand-mark {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--button-bg);
    box-shadow: var(--ring);
    position: relative;
}

.brand-mark::after {
    content: '';
    position: absolute;
    width: 11px;
    height: 11px;
    top: 8.5px;
    left: 8.5px;
    background: var(--button-fg);
    transform: rotate(45deg);
}

.eyebrow,
.card-kicker {
    display: inline-flex;
    align-items: center;
    height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--badge-bg);
    color: var(--badge-fg);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 500;
}

.intro-copy {
    max-width: 680px;
}

.intro-copy h1 {
    margin: 18px 0 20px;
    color: var(--text-primary);
    font-size: clamp(52px, 8vw, 86px);
    font-weight: 600;
    line-height: 0.96;
    letter-spacing: 0;
}

.intro-copy p,
.auth-header p,
.workflow-row strong {
    margin: 0;
    color: var(--text-secondary);
    font-size: 18px;
    line-height: 1.75;
}

.workflow-card,
.auth-card {
    background: var(--surface);
    border-radius: 12px;
    box-shadow: var(--card-shadow);
}

.workflow-card {
    max-width: 560px;
    padding: 12px;
    display: grid;
    gap: 8px;
}

.workflow-row {
    min-height: 58px;
    display: grid;
    grid-template-columns: 10px 96px 1fr;
    align-items: center;
    gap: 12px;
    padding: 0 14px;
    border-radius: 10px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.workflow-row span:not(.dot) {
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

.workflow-row strong {
    color: var(--text-primary);
    font-size: 15px;
    font-weight: 600;
    line-height: 1.4;
}

.dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.develop {
    background: #0a72ef;
}

.preview {
    background: #de1d8d;
}

.ship {
    background: #ff5b4f;
}

.auth-card {
    width: 100%;
    padding: 32px;
}

.auth-header {
    margin-bottom: 28px;
}

.auth-header h2 {
    margin: 16px 0 8px;
    color: var(--text-primary);
    font-size: 32px;
    font-weight: 600;
    line-height: 1.15;
    letter-spacing: 0;
}

.auth-header p {
    font-size: 15px;
    line-height: 1.6;
}

.auth-form {
    display: grid;
    gap: 16px;
}

.field {
    display: grid;
    gap: 8px;
}

.field > span {
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 500;
}

.input-shell {
    height: 46px;
    display: grid;
    grid-template-columns: 18px 1fr;
    align-items: center;
    gap: 10px;
    padding: 0 12px;
    border-radius: 10px;
    background: var(--surface);
    box-shadow: var(--ring);
    transition: box-shadow 180ms ease;
}

.input-shell:focus-within {
    box-shadow: var(--ring), 0 0 0 3px rgba(0, 114, 245, 0.14);
}

.field-icon {
    width: 16px;
    height: 16px;
    color: var(--text-muted);
}

.input-shell input {
    width: 100%;
    min-width: 0;
    border: 0;
    outline: 0;
    background: transparent;
    color: var(--text-primary);
    font: inherit;
    font-size: 15px;
}

.input-shell input::placeholder {
    color: var(--text-muted);
}

.submit-btn,
.guest-btn,
.text-button {
    border: 0;
    font: inherit;
    cursor: pointer;
}

.submit-btn,
.guest-btn {
    height: 42px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
}

.submit-btn {
    margin-top: 8px;
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
    transition: background 180ms ease;
}

.submit-btn:hover {
    background: var(--button-hover);
}

.button-icon {
    width: 16px;
    height: 16px;
}

.auth-footer {
    margin-top: 24px;
    display: grid;
    gap: 10px;
    text-align: center;
}

.text-button {
    padding: 8px;
    color: var(--badge-fg);
    background: transparent;
    font-size: 14px;
    font-weight: 500;
    border-radius: 10px;
}

.text-button:hover {
    background: var(--badge-bg);
}

.guest-btn {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.guest-btn:hover {
    background: var(--surface-hover);
}

@media (max-width: 920px) {
    .auth-page {
        grid-template-columns: 1fr;
        max-width: 560px;
        gap: 24px;
    }

    .auth-intro {
        min-height: auto;
        gap: 40px;
        padding: 0;
    }

    .workflow-card {
        display: none;
    }
}

@media (max-width: 520px) {
    .auth-page {
        padding: 28px 0;
    }

    .auth-card {
        padding: 24px 18px;
    }

    .intro-copy h1 {
        letter-spacing: 0;
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
