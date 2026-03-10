<template>
    <div class="auth-container">
        <div class="auth-bg-shapes">
            <div class="shape shape-1"></div>
            <div class="shape shape-2"></div>
            <div class="shape shape-3"></div>
        </div>

        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-logo">
                    <svg width="60" height="60" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="20" cy="20" r="18" fill="#FF7F50" stroke="white" stroke-width="2" />
                        <path d="M12 20 L20 12 L28 20 L20 28 Z" fill="white" />
                    </svg>
                </div>
                <h2 class="auth-title">{{ isLoginMode ? "欢迎回来" : "创建账号" }}</h2>
                <p class="auth-subtitle">{{ isLoginMode ? "登录您的智汇博客账号" : "加入我们的创作社区" }}</p>
            </div>

            <form @submit.prevent="handleSubmit" class="auth-form" autocomplete="off">
                <!-- 用户名 -->
                <div class="form-group">
                    <label for="username" class="form-label">
                        <span class="label-icon">👤</span>
                        用户名
                    </label>
                    <div class="input-wrapper">
                        <input type="text" id="username" v-model="formData.username" placeholder="请输入用户名" required
                            class="form-input" />
                    </div>
                </div>

                <!-- 密码 -->
                <div class="form-group">
                    <label for="password" class="form-label">
                        <span class="label-icon">🔒</span>
                        密码
                    </label>
                    <div class="input-wrapper">
                        <input type="password" id="password" v-model="formData.password" placeholder="请输入密码" required
                            minlength="6" class="form-input" />
                    </div>
                </div>

                <!-- 注册时额外显示邮箱 -->
                <div class="form-group" v-if="!isLoginMode">
                    <label for="email" class="form-label">
                        <span class="label-icon">📧</span>
                        邮箱
                    </label>
                    <div class="input-wrapper">
                        <input type="email" id="email" v-model="formData.email" placeholder="请输入邮箱"
                            class="form-input" />
                    </div>
                </div>

                <!-- 注册时额外显示确认密码 -->
                <div class="form-group" v-if="!isLoginMode">
                    <label for="confirmPassword" class="form-label">
                        <span class="label-icon">🔄</span>
                        确认密码
                    </label>
                    <div class="input-wrapper">
                        <input type="password" id="confirmPassword" v-model="formData.confirmPassword"
                            placeholder="请再次输入密码" required minlength="6" class="form-input" />
                    </div>
                </div>

                <!-- 提交按钮 -->
                <button type="submit" class="submit-btn">
                    <span class="btn-text">{{ isLoginMode ? "登录" : "注册" }}</span>
                    <span class="btn-icon">{{ isLoginMode ? "→" : "➕" }}</span>
                </button>
            </form>

            <!-- 切换登录/注册 -->
            <div class="auth-footer">
                <p class="toggle-mode" @click="toggleMode">
                    {{ isLoginMode ? "没有账号？去注册" : "已有账号？去登录" }}
                </p>
                <button class="guest-btn" @click="guestLogin">
                    <span class="guest-icon">👁️</span>
                    游客登录
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useElMessage } from "@/hooks/useMessage";
import authApi from "@/api/modules/auth";
import { useGlobalStore } from "@/store";
import { IUserInfo } from "@/api/modules/auth/interface";
import { useRouter } from "vue-router";

const router = useRouter();
const { message } = useElMessage();

// 登录/注册模式切换
const isLoginMode = ref(true);
const global = useGlobalStore();

// 表单数据
const formData = ref({
    username: "",
    password: "",
    confirmPassword: "",
    email: "",
});

// 切换模式
const toggleMode = () => {
    isLoginMode.value = !isLoginMode.value;
    formData.value = { username: "", password: "", confirmPassword: "", email: "" }; // 清空表单
};

// 登录处理
const login = async () => {
    try {
        const data: IUserInfo = await authApi.login({
            username: formData.value.username,
            password: formData.value.password,
        });
        if (data) {
            global.setLoginInfo(data.token, data);
            message.success("登录成功！");
            router.push("/"); // 登录成功后跳转到首页
        }
    } catch (error: any) {
        // 优先显示后端返回的错误信息
        const msg = error.response?.data?.msg || error.message || '登录失败';
        message.error(msg);
    }
};

// 注册处理
const register = async () => {
    try {
        if (formData.value.password !== formData.value.confirmPassword) {
            message.warning("两次输入的密码不一致，请检查后重试！");
            return;
        }
        const data = await authApi.register({
            username: formData.value.username,
            password: formData.value.password,
            email: formData.value.email,
        }) as { success: boolean };
        if (data.success) {
            toggleMode();
            message.success("注册成功，请重新登录");
        }
    } catch (error: any) {
        // 优先显示后端返回的错误信息
        const msg = error.response?.data?.msg || error.message || '注册失败';
        message.error(msg);
    }
};

// 提交表单
const handleSubmit = async () => {
    try {
        if (isLoginMode.value) {
            await login();
        } else {
            await register();
        }
    } catch (error: any) {
        const msg = error.response?.data?.msg || error.message || '提交表单失败';
        message.error(msg);
    }
};

// 游客登录
const guestLogin = () => {
    router.push('/');
    message.success("游客登录成功，欢迎使用！");
};
</script>

<style scoped>
.auth-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #fff8f5 0%, #fff 100%);
    position: relative;
    overflow: hidden;
    padding: 20px;
}

/* 背景装饰形状 */
.auth-bg-shapes {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    pointer-events: none;
}

.shape {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 127, 80, 0.1);
    animation: float 6s ease-in-out infinite;
}

.shape-1 {
    width: 200px;
    height: 200px;
    top: -100px;
    left: -100px;
    animation-delay: 0s;
}

.shape-2 {
    width: 150px;
    height: 150px;
    bottom: -75px;
    right: -75px;
    animation-delay: 2s;
}

.shape-3 {
    width: 100px;
    height: 100px;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation-delay: 4s;
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0px) rotate(0deg);
    }

    50% {
        transform: translateY(-20px) rotate(180deg);
    }
}

/* 认证卡片 */
.auth-card {
    background: white;
    border-radius: 20px;
    padding: 2.5rem;
    width: 100%;
    max-width: 450px;
    box-shadow: 0 10px 40px rgba(255, 127, 80, 0.15);
    position: relative;
    z-index: 10;
    animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
    from {
        transform: translateY(50px);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

/* 认证头部 */
.auth-header {
    text-align: center;
    margin-bottom: 2rem;
}

.auth-logo {
    margin: 0 auto 1.5rem;
}

.auth-title {
    font-size: 28px;
    font-weight: 700;
    color: #FF7F50;
    margin: 0 0 0.5rem;
    font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.auth-subtitle {
    font-size: 14px;
    color: #666;
    margin: 0;
}

/* 表单样式 */
.auth-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.form-group {
    position: relative;
}

.form-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 14px;
    font-weight: 500;
    color: #333;
    margin-bottom: 0.75rem;
}

.label-icon {
    font-size: 16px;
}

.input-wrapper {
    position: relative;
    background: rgba(255, 127, 80, 0.05);
    border-radius: 12px;
    transition: all 0.3s ease;
    padding: 2px;
}

.input-wrapper:focus-within {
    background: rgba(255, 127, 80, 0.1);
    box-shadow: 0 0 0 3px rgba(255, 127, 80, 0.15);
}

.form-input {
    width: 100%;
    padding: 1rem 1.25rem;
    border: 2px solid transparent;
    border-radius: 10px;
    font-size: 16px;
    color: #333;
    background: white;
    outline: none;
    transition: all 0.3s ease;
    box-sizing: border-box;
    /* 确保padding不影响宽度 */

    &::placeholder {
        color: #999;
    }

    &:focus {
        border-color: #FF7F50;
        box-shadow: none;
    }
}

/* 提交按钮 */
.submit-btn {
    width: 100%;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, #FF7F50 0%, #FF6347 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    box-shadow: 0 4px 15px rgba(255, 127, 80, 0.3);
    margin-top: 1rem;

    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 127, 80, 0.4);
    }

    &:active {
        transform: translateY(0);
    }
}

.btn-icon {
    font-size: 18px;
    transition: transform 0.3s ease;
}

.submit-btn:hover .btn-icon {
    transform: translateX(5px);
}

/* 认证底部 */
.auth-footer {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 2rem;
    text-align: center;
}

.toggle-mode {
    color: #666;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    padding: 0.5rem;
    border-radius: 8px;

    &:hover {
        color: #FF7F50;
        background: rgba(255, 127, 80, 0.05);
    }
}

.guest-btn {
    padding: 0.75rem 1.5rem;
    background: rgba(255, 127, 80, 0.1);
    color: #FF7F50;
    border: 2px solid rgba(255, 127, 80, 0.2);
    border-radius: 12px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;

    &:hover {
        background: rgba(255, 127, 80, 0.15);
        border-color: #FF7F50;
        transform: translateY(-2px);
    }
}

.guest-icon {
    font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .auth-card {
        padding: 2rem 1.5rem;
    }

    .auth-title {
        font-size: 24px;
    }

    .form-input {
        padding: 0.875rem 1rem;
        font-size: 14px;
    }

    .submit-btn {
        padding: 0.875rem 1.25rem;
        font-size: 14px;
    }
}
</style>