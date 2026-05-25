<template>
    <footer class="site-footer" :class="{ 'site-footer--home': isHomeRoute }">
        <div class="footer-shell">
            <div class="footer-brand">
                <span class="footer-mark" aria-hidden="true"></span>
                <div>
                    <h2>知镜</h2>
                    <p>把资料整理成可追问、可引用、可写作的个人知识库。</p>
                </div>
            </div>

            <div class="footer-links">
                <router-link to="/">工作台</router-link>
                <router-link to="/essays">知识库</router-link>
                <router-link to="/context-packs">上下文包</router-link>
                <router-link to="/ai-center">AI 工作台</router-link>
            </div>
        </div>
        <div class="footer-bottom">
            <span>Copyright 2026 知镜</span>
            <span class="mono">资料可追溯 · 写作有依据</span>
        </div>
    </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isHomeRoute = computed(() => route.path === '/')
</script>

<style scoped>
.site-footer {
    background: var(--surface);
    box-shadow: color-mix(in oklch, var(--text-primary) 10%, transparent) 0 -1px 0 0;
}

.site-footer--home {
    background: var(--page-bg);
    box-shadow: color-mix(in oklch, var(--text-primary) 10%, transparent) 0 -1px 0 0;
}

.site-footer--home .footer-brand h2 {
    color: var(--text-primary);
}

.site-footer--home .footer-brand p,
.site-footer--home .footer-bottom {
    color: var(--text-muted);
}

.site-footer--home .footer-mark {
    background: var(--button-bg);
}

.site-footer--home .footer-links a {
    color: var(--text-secondary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.site-footer--home .footer-links a:hover {
    color: var(--text-primary);
    background: var(--surface-hover);
}

.footer-shell {
    width: var(--page-width);
    margin: 0 auto;
    padding: 32px 0;
    display: grid;
    grid-template-columns: 1.2fr auto;
    align-items: center;
    gap: 32px;
}

.footer-brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.footer-mark {
    width: 32px;
    height: 32px;
    flex: 0 0 auto;
    border-radius: 8px;
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.footer-brand h2 {
    margin: 0;
    color: var(--text-primary);
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0;
}

.footer-brand p {
    max-width: 560px;
    margin: 4px 0 0;
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.5;
}

.footer-links {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 8px;
}

.footer-links a {
    min-height: 34px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0 12px;
    border: 0;
    border-radius: 10px;
    background: var(--surface);
    color: var(--text-secondary);
    box-shadow: var(--ring);
    cursor: pointer;
    font: inherit;
    font-size: 14px;
    font-weight: 500;
}

.footer-links a:hover {
    color: var(--text-primary);
    background: var(--surface-hover);
}

.footer-bottom {
    width: var(--page-width);
    margin: 0 auto;
    padding: 14px 0 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: var(--text-muted);
    font-size: 12px;
}

.mono {
    font-family: var(--font-mono);
    font-weight: 500;
    letter-spacing: 0;
}

@media (max-width: 900px) {
    .footer-shell {
        grid-template-columns: 1fr;
        align-items: flex-start;
        gap: 20px;
    }

    .footer-links {
        justify-content: flex-start;
    }
}

@media (max-width: 520px) {
    .footer-bottom {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }
}
</style>
