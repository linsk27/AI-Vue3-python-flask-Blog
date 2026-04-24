<template>
    <footer class="site-footer">
        <div class="footer-shell">
            <div class="footer-brand">
                <span class="footer-mark" aria-hidden="true"></span>
                <div>
                    <h2>智汇博客</h2>
                    <p>面向开发者的 AI 知识创作与阅读工作台。</p>
                </div>
            </div>

            <div class="footer-actions" aria-label="显示设置">
                <button class="footer-button" type="button" @click="changeBackground">
                    <Picture class="footer-icon" />
                    <span>切换背景</span>
                </button>
                <button class="footer-button" type="button" @click="changeStar">
                    <MagicStick class="footer-icon" />
                    <span>星空效果</span>
                </button>
            </div>

            <div class="footer-links">
                <a href="https://lindablog.xyz" target="_blank" rel="noopener noreferrer">线上站点</a>
                <router-link to="/essays">文章库</router-link>
                <router-link to="/ai-center">AI 中心</router-link>
            </div>
        </div>
        <div class="footer-bottom">
            <span>© 2026 智汇博客</span>
            <span class="mono">VUE3 / FLASK / AI</span>
        </div>
    </footer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { MagicStick, Picture } from '@element-plus/icons-vue'
import { useImgStore } from '@/store/backgroundImg'

const imgStore = useImgStore()
const index = ref(0)

const imgUrlData = ref([
    'https://s2.loli.net/2025/08/27/XkKHlSEcUIvafWd.jpg',
    'https://s2.loli.net/2025/08/27/ygncYMIGHK1NAaT.jpg',
    'https://s2.loli.net/2025/08/27/wUVaC94WNfsFrcP.jpg'
])

if (imgStore.url) {
    index.value = imgUrlData.value.findIndex(item => item === imgStore.url) + 1
}

const changeBackground = () => {
    if (index.value >= imgUrlData.value.length) index.value = 0
    const img = new Image()
    img.src = imgUrlData.value[index.value]
    img.onload = () => {
        imgStore.changeUrl(img.src)
    }
    index.value++
}

const changeStar = () => {
    imgStore.toggleStar()
}
</script>

<style scoped>
.site-footer {
    background: var(--surface);
    box-shadow: rgba(0, 0, 0, 0.08) 0 -1px 0 0;
}

.footer-shell {
    max-width: 1200px;
    margin: 0 auto;
    padding: 32px 16px;
    display: grid;
    grid-template-columns: 1.2fr auto auto;
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
    border-radius: 50%;
    background: linear-gradient(135deg, var(--button-bg) 0%, var(--text-secondary) 100%);
    box-shadow: var(--ring);
}

.footer-brand h2 {
    margin: 0;
    color: var(--text-primary);
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.32px;
}

.footer-brand p {
    margin: 4px 0 0;
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.5;
}

.footer-actions,
.footer-links {
    display: flex;
    align-items: center;
    gap: 8px;
}

.footer-button,
.footer-links a {
    height: 34px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0 12px;
    border: 0;
    border-radius: 6px;
    background: var(--surface);
    color: var(--text-secondary);
    box-shadow: var(--ring);
    cursor: pointer;
    font: inherit;
    font-size: 14px;
    font-weight: 500;
    transition: color 180ms ease, background 180ms ease;
}

.footer-button:hover,
.footer-links a:hover {
    color: var(--text-primary);
    background: var(--surface-hover);
}

.footer-icon {
    width: 16px;
    height: 16px;
}

.footer-bottom {
    max-width: 1200px;
    margin: 0 auto;
    padding: 14px 16px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: var(--text-muted);
    font-size: 12px;
}

.mono {
    font-family: "Geist Mono", ui-monospace, monospace;
    font-weight: 500;
    letter-spacing: 0;
}

@media (max-width: 900px) {
    .footer-shell {
        grid-template-columns: 1fr;
        align-items: flex-start;
        gap: 20px;
    }

    .footer-actions,
    .footer-links {
        flex-wrap: wrap;
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
