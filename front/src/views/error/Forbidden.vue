<template>
    <main class="forbidden-page">
        <section class="forbidden-panel">
            <span class="eyebrow">Access Control</span>
            <h1>当前账号无权访问这个页面</h1>
            <p>如果你需要后台、AI 配置或系统自检能力，请使用管理员账号登录，或让管理员给当前角色分配对应权限。</p>
            <div class="actions">
                <button type="button" class="primary-button" @click="goHome">返回工作台</button>
                <button type="button" class="secondary-button" @click="goProfile">查看我的权限</button>
            </div>
        </section>
    </main>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
    router.push('/')
}

function goProfile() {
    router.push('/profile')
}
</script>

<style scoped>
.forbidden-page {
    min-height: calc(100vh - 180px);
    width: var(--page-width);
    margin: 0 auto;
    display: grid;
    place-items: center;
    padding: 48px 0;
    color: var(--text-primary);
}

.forbidden-panel {
    width: min(640px, 100%);
    padding: 32px;
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--badge-bg);
    color: var(--badge-fg);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
}

h1 {
    margin: 18px 0 12px;
    font-size: 34px;
    line-height: 1.15;
}

p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 15px;
    line-height: 1.7;
}

.actions {
    margin-top: 24px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.primary-button,
.secondary-button {
    min-height: 40px;
    padding: 0 16px;
    border: 0;
    border-radius: 8px;
    font: inherit;
    font-weight: 700;
    cursor: pointer;
    box-shadow: var(--ring);
}

.primary-button {
    color: var(--button-fg);
    background: var(--button-bg);
}

.secondary-button {
    color: var(--text-primary);
    background: var(--surface);
}
</style>
