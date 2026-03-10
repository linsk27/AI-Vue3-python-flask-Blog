<template>
    <footer class="modern-footer">
        <div class="footer-content">
            <!-- 左侧功能图标区域 -->
            <div class="footer-features">
                <div class="feature-item" @click="changeBackground()">
                    <div class="feature-icon">
                        <IconPicture theme="outline" size="24" fill="#FF7F50" />
                    </div>
                    <span class="feature-text">更换背景</span>
                </div>
                <div class="feature-item" @click="changeStar()">
                    <div class="feature-icon">
                        <IconStar theme="outline" size="24" fill="#FF7F50" />
                    </div>
                    <span class="feature-text">星星特效</span>
                </div>
            </div>

            <!-- 中间文字内容区域 -->
            <div class="footer-text">
                <h3 class="footer-title">智汇博客</h3>
                <p class="copyright">© 2026 智汇博客. 保留所有权利.</p>
                <div class="footer-description">
                    <p>专注于性能优化、技术分享和创作交流的数字平台</p>
                </div>
            </div>

            <!-- 右侧链接区域 -->
            <div class="footer-links">
                <a href="https://lindablog.xyz" class="link-item" target="_blank" rel="noopener noreferrer">
                    <span class="link-icon">🌐</span>
                    <span>官方博客</span>
                </a>
                <a href="#" class="link-item">
                    <span class="link-icon">📧</span>
                    <span>联系我们</span>
                </a>
                <a href="#" class="link-item">
                    <span class="link-icon">📝</span>
                    <span>投稿指南</span>
                </a>
            </div>
        </div>
    </footer>
</template>

<script setup>
import { ref } from 'vue'
import { NewPicture as IconPicture, StarOne as IconStar } from '@icon-park/vue-next'
import { useImgStore } from '@/store/backgroundImg'
const imgStore = useImgStore()
const index = ref(0)

// 背景图片数据
const imgUrlData = ref([
    "https://s2.loli.net/2025/08/27/XkKHlSEcUIvafWd.jpg",
    "https://s2.loli.net/2025/08/27/ygncYMIGHK1NAaT.jpg",
    "https://s2.loli.net/2025/08/27/wUVaC94WNfsFrcP.jpg"
])

if (imgStore.url) {
    index.value = imgUrlData.value.findIndex(item => item === imgStore.url) + 1
}

// 更换背景图片
const changeBackground = async () => {
    if (index.value >= imgUrlData.value.length) index.value = 0

    // 预加载图片优化体验
    const img = new Image()
    img.src = imgUrlData.value[index.value]
    img.onload = () => {
        imgStore.changeUrl(img.src)
    }
    index.value++
}

// 切换星星状态
const changeStar = () => {
    imgStore.toggleStar()
}
</script>

<style scoped>
.modern-footer {
    background: linear-gradient(135deg, #fff 0%, #fff8f5 100%);
    box-shadow: 0 -4px 20px rgba(255, 127, 80, 0.15);
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    padding: 3rem 0 2rem;
    animation: fadeUp 0.8s ease-out;
}

@keyframes fadeUp {
    from {
        transform: translateY(30px);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.footer-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2.5rem;
    padding: 0 20px;
}

/* 功能图标区域 */
.footer-features {
    display: flex;
    gap: 3rem;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
}

.feature-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 1rem;
    border-radius: 12px;
    transition: all 0.3s ease;
    background-color: white;
    box-shadow: 0 2px 8px rgba(255, 127, 80, 0.1);

    &:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(255, 127, 80, 0.2);
        background-color: #fff;
    }
}

.feature-icon {
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(255, 127, 80, 0.1);
    border-radius: 50%;
    transition: all 0.3s ease;

    .feature-item:hover & {
        background-color: rgba(255, 127, 80, 0.2);
        transform: scale(1.1);
    }
}

.feature-text {
    color: #FF7F50;
    font-size: 14px;
    font-weight: 500;
    text-align: center;
}

/* 文字内容区域 */
.footer-text {
    text-align: center;
    max-width: 400px;
}

.footer-title {
    color: #FF7F50;
    font-size: 24px;
    font-weight: 700;
    margin: 0 0 0.5rem;
    letter-spacing: 1px;
}

.copyright {
    color: #666;
    font-size: 14px;
    margin: 0 0 1rem;
}

.footer-description p {
    color: #888;
    font-size: 13px;
    margin: 0;
    line-height: 1.5;
}

/* 链接区域 */
.footer-links {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    align-items: center;
}

.link-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #666;
    text-decoration: none;
    font-size: 14px;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
    background-color: white;
    box-shadow: 0 2px 8px rgba(255, 127, 80, 0.1);

    &:hover {
        color: #FF7F50;
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(255, 127, 80, 0.15);
        background-color: #fff;
    }
}

.link-icon {
    font-size: 16px;
}

/* 响应式设计 */
@media (min-width: 768px) {
    .footer-content {
        flex-direction: row;
        justify-content: space-between;
        align-items: flex-start;
        gap: 2rem;
    }

    .footer-text {
        text-align: center;
    }

    .footer-links {
        align-items: flex-start;
    }
}

@media (max-width: 767px) {
    .footer-features {
        gap: 1.5rem;
    }

    .feature-item {
        padding: 0.8rem;
    }

    .feature-icon {
        width: 40px;
        height: 40px;
    }

    .footer-title {
        font-size: 20px;
    }
}
</style>