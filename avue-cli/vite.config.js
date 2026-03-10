import { defineConfig, loadEnv } from 'vite'
const { resolve } = require('path')
import createVitePlugins from './vite/plugins'
// https://vitejs.dev/config/
export default ({ mode, command }) => {
    const env = loadEnv(mode, process.cwd())
    const { VITE_APP_BASE, VITE_APP_ENV } = env
    const isProd = VITE_APP_ENV === 'production'
    return defineConfig({
        base: VITE_APP_BASE,
        build: {
            target: 'esnext',
            minify: true,
            terserOptions: {
                compress: {
                    drop_console: true, // 删除 console
                    drop_debugger: true // 删除 debugger
                },
                format: {
                    comments: false // 删除所有注释
                }
            },
            rollupOptions: {
                output: {
                    manualChunks: {
                        'element-plus': ['element-plus'],
                        '@smallwei/avue': ['@smallwei/avue']
                    }
                }
            }
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
            port: 5001, // 更改端口为 5001
            proxy: {
                '/api': {
                    target: 'http://127.0.0.1:5000',
                    changeOrigin: true,
                    rewrite: path => path
                }
            }
        }
    })
}
