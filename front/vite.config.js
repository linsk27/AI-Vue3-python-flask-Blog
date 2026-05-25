import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

const normalizeId = (id) => id.replace(/\\/g, '/')
const normalizeProxyTarget = (target) => (target || 'http://127.0.0.1:5000').replace(/\/api\/?$/, '')

const vendorChunks = [
    {
        name: 'vendor-vue',
        packages: ['/node_modules/@vue/', '/node_modules/vue/', '/node_modules/vue-router/', '/node_modules/pinia/']
    },
    {
        name: 'vendor-icons',
        packages: ['/node_modules/@element-plus/icons-vue/']
    },
    {
        name: 'vendor-element',
        packages: [
            '/node_modules/element-plus/',
            '/node_modules/@element-plus/',
            '/node_modules/@floating-ui/',
            '/node_modules/@popperjs/',
            '/node_modules/async-validator/'
        ]
    },
    {
        name: 'vendor-editor',
        packages: ['/node_modules/quill/', '/node_modules/parchment/', '/node_modules/quill-delta/']
    },
    {
        name: 'vendor-markdown',
        packages: ['/node_modules/marked/', '/node_modules/highlight.js/']
    },
    {
        name: 'vendor-docx',
        packages: [
            '/node_modules/mammoth/',
            '/node_modules/@xmldom/',
            '/node_modules/argparse/',
            '/node_modules/base64-js/',
            '/node_modules/bluebird/',
            '/node_modules/dingbat-to-unicode/',
            '/node_modules/lop/',
            '/node_modules/path-is-absolute/',
            '/node_modules/underscore/',
            '/node_modules/xmlbuilder/'
        ]
    },
    {
        name: 'vendor-zip',
        packages: [
            '/node_modules/jszip/',
            '/node_modules/pako/',
            '/node_modules/lie/',
            '/node_modules/setimmediate/',
            '/node_modules/readable-stream/',
            '/node_modules/inherits/',
            '/node_modules/process-nextick-args/',
            '/node_modules/safe-buffer/',
            '/node_modules/core-util-is/',
            '/node_modules/isarray/',
            '/node_modules/string_decoder/',
            '/node_modules/util-deprecate/'
        ]
    },
    {
        name: 'vendor-request',
        packages: ['/node_modules/axios/', '/node_modules/nprogress/']
    }
]

function manualChunks(id) {
    const normalized = normalizeId(id)
    if (normalized.includes('commonjsHelpers')) return 'vendor-commonjs'
    if (!normalized.includes('/node_modules/')) return

    const matched = vendorChunks.find(chunk => chunk.packages.some(pkg => normalized.includes(pkg)))
    return matched?.name
}

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), 'VITE_')
    const proxyTarget = normalizeProxyTarget(env.VITE_PROXY_TARGET)

    return {
        base: './',
        plugins: [vue()],
        resolve: {
            alias: {
                '@': path.resolve(__dirname, 'src')
            }
        },
        build: {
            outDir: 'dist',
            target: 'esnext',
            chunkSizeWarningLimit: 650,
            rollupOptions: {
                output: {
                    manualChunks
                }
            }
        },
        server: {
            port: 8080,
            proxy: {
                '/api': {
                    target: proxyTarget,
                    changeOrigin: true,
                    rewrite: requestPath => requestPath
                }
            }
        }
    }
})
