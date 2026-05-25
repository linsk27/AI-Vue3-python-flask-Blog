import { defineConfig, loadEnv } from 'vite'
const { resolve } = require('path')
import createVitePlugins from './vite/plugins'

// https://vitejs.dev/config/
export default ({ mode, command }) => {
    const env = loadEnv(mode, process.cwd())
    const { VITE_APP_BASE, VITE_APP_ENV, VITE_API_TARGET } = env
    const isProd = VITE_APP_ENV === 'production'
    return defineConfig({
        base: VITE_APP_BASE,
        build: {
            target: 'esnext',
            minify: 'esbuild',
            chunkSizeWarningLimit: 2500,
            rollupOptions: {
                output: {
                    manualChunks: {
                        'vendor-vue': ['vue', 'vue-router', 'vuex', 'vue-i18n'],
                        'vendor-element': ['element-plus', '@element-plus/icons-vue'],
                        'vendor-avue': ['@smallwei/avue'],
                        'vendor-utils': ['axios', 'dayjs', 'js-cookie', 'nprogress', 'crypto-js']
                    }
                }
            }
        },
        esbuild: {
            drop: isProd ? ['console', 'debugger'] : []
        },
        optimizeDeps: {
            esbuildOptions: {
                target: 'esnext'
            }
        },
        resolve: {
            alias: {
                '~': resolve(__dirname, './'),
                '@': resolve(__dirname, './src'),
                components: resolve(__dirname, './src/components'),
                styles: resolve(__dirname, './src/styles'),
                utils: resolve(__dirname, './src/utils')
            }
        },
        plugins: createVitePlugins(env, command === 'build'),
        server: {
            port: 5001,
            proxy: {
                '/api': {
                    target: VITE_API_TARGET || 'http://127.0.0.1:5100',
                    changeOrigin: true,
                    rewrite: path => path
                }
            }
        }
    })
}
