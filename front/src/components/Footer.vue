<template>
    <footer class="site-footer">
        <div class="footer-shell">
            <div class="footer-brand">
                <span class="footer-mark" aria-hidden="true"></span>
                <div>
                    <h2>ContextForge</h2>
                    <p>开源 AI 上下文工作台，用文档、上下文包、提示词和知识复用组织你的思考材料。</p>
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
            <span>Copyright 2026 ContextForge / 语境工坊</span>
            <span class="mono">VUE3 / FLASK / AI</span>
        </div>
    </footer>
</template>

<script setup lang="ts">
</script>

<style scoped>
.site-footer {
    background: var(--surface);
    box-shadow: rgba(0, 0, 0, 0.08) 0 -1px 0 0;
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
    transition: color 180ms ease, background 180ms ease;
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
