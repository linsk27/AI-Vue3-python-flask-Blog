import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
    // 关键步骤：加载环境变量
    const env = loadEnv(mode, process.cwd(), 'VITE_') // 第三个参数过滤前缀

    // 获取环境变量
    const baseUrl = env.VITE_API_BASE_URL
    const target = env.VITE_PROXY_TARGET

    return {
        base: './', // 设置基础路径
        plugins: [vue()],
        resolve: {
            alias: {
                '@': path.resolve(__dirname, 'src')
            }
        },
        build: {
            outDir: 'dist', // 输出目录
            target: 'esnext' // 支持最新ES特性，包括顶级await
        },
        server: {
            port: 8080, // 指定端口
            proxy: {
                '/api': {
                    target: 'http://127.0.0.1:5000',
                    changeOrigin: true,
                    rewrite: (path) => path
                }
            }
        }
    }
})
