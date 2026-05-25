const fs = require('fs')
const path = require('path')
const { chromium } = require('playwright')

const backendUrl = (process.env.BACKEND_URL || 'http://127.0.0.1:5100').replace(/\/+$/, '')
const frontendUrl = (process.env.FRONTEND_URL || process.env.BASE_URL || 'http://127.0.0.1:8080').replace(/\/+$/, '')
const username = process.env.E2E_USERNAME || 'admin'
const password = process.env.E2E_PASSWORD || 'admin123'
const callAi = process.env.E2E_CALL_AI === '1'
const skipBrowser = process.env.E2E_SKIP_BROWSER === '1'
const outDir = path.resolve(__dirname, '..', '..', '.codex-logs')

const runId = new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)
const prefix = `__e2e_zhijing_${runId}`
const created = {
    articleId: null,
    packId: null
}

function stringify(value) {
    try {
        return JSON.stringify(value)
    } catch {
        return String(value)
    }
}

async function request(pathname, options = {}) {
    const headers = {
        Accept: 'application/json',
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(options.token ? { Authorization: options.token } : {})
    }

    const response = await fetch(`${backendUrl}${pathname}`, {
        method: options.method || 'GET',
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined
    })

    const text = await response.text()
    let payload
    try {
        payload = text ? JSON.parse(text) : {}
    } catch {
        payload = { raw: text }
    }

    if (!response.ok && !options.allowHttpError) {
        throw new Error(`${options.label || pathname} HTTP ${response.status}: ${stringify(payload)}`)
    }

    return { response, payload }
}

function expectOk(result, label) {
    if (!result.payload || result.payload.status !== 0) {
        throw new Error(`${label} failed: ${stringify(result.payload)}`)
    }
    return result.payload.data
}

async function cleanup(token) {
    const errors = []

    if (created.packId) {
        try {
            await request(`/api/context-packs/${created.packId}`, {
                method: 'DELETE',
                token,
                allowHttpError: true,
                label: 'cleanup context pack'
            })
        } catch (error) {
            errors.push(error.message)
        }
    }

    if (created.articleId) {
        try {
            await request(`/api/articles/${created.articleId}`, {
                method: 'DELETE',
                token,
                allowHttpError: true,
                label: 'cleanup article'
            })
        } catch (error) {
            errors.push(error.message)
        }
    }

    return errors
}

async function verifyBrowser(userInfo, token) {
    if (skipBrowser) {
        return { skipped: true, reason: 'E2E_SKIP_BROWSER=1' }
    }

    fs.mkdirSync(outDir, { recursive: true })
    const browser = await chromium.launch({ headless: true })
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } })
    const consoleErrors = []
    const httpErrors = []

    page.on('console', (message) => {
        if (message.type() === 'error') consoleErrors.push(message.text())
    })
    page.on('pageerror', (error) => consoleErrors.push(error.message))
    page.on('response', (response) => {
        if (response.status() >= 400) {
            httpErrors.push({ status: response.status(), url: response.url() })
        }
    })

    await page.goto(`${frontendUrl}/`, { waitUntil: 'domcontentloaded', timeout: 30000 })
    await page.evaluate(
        ({ storedUserInfo, storedToken }) => {
            window.localStorage.setItem(
                'GlobalStore',
                JSON.stringify({
                    token: storedToken,
                    userInfo: storedUserInfo,
                    themeConfig: {
                        breadcrumb: true,
                        tabs: true,
                        footer: true
                    }
                })
            )
        },
        { storedUserInfo: userInfo, storedToken: token }
    )

    await page.goto(`${frontendUrl}/essays/write`, { waitUntil: 'networkidle', timeout: 30000 })
    if (page.url().includes('/login')) {
        throw new Error('browser flow redirected to login after setting authenticated store')
    }

    await page.locator('.ai-help-btn').click({ timeout: 15000 })
    await page.locator('.ai-draft-panel').waitFor({ state: 'visible', timeout: 15000 })
    await page.screenshot({ path: path.join(outDir, 'e2e-ai-draft-panel.png'), fullPage: true })
    await browser.close()

    return {
        skipped: false,
        consoleErrors,
        httpErrors,
        screenshot: path.join(outDir, 'e2e-ai-draft-panel.png')
    }
}

async function main() {
    const health = await request('/api/health', { label: 'health' })
    expectOk(health, 'health')

    const login = await request('/api/login', {
        method: 'POST',
        body: { username, password },
        allowHttpError: true,
        label: 'login'
    })
    const loginData = expectOk(login, 'login')
    const token = loginData.token
    if (!token) throw new Error('login succeeded but no token was returned')

    try {
        const article = expectOk(
            await request('/api/articles', {
                method: 'POST',
                token,
                label: 'create article',
                body: {
                    title: `${prefix} source article`,
                    content: [
                        '# ContextForge RAG verification',
                        '',
                        'Context packs collect trustworthy source material before AI drafting.',
                        'RAG retrieval must return source snippets with traceable evidence.',
                        'The editor should receive normalized draft content, not a raw JSON envelope.'
                    ].join('\n'),
                    summary: 'Temporary E2E article for RAG retrieval verification.',
                    category: 'ai',
                    tags: ['e2e', 'rag'],
                    status: 'published',
                    document_status: 'published',
                    resource_type: 'note',
                    visibility: 'private',
                    source_url: 'https://example.com/zhijing-e2e'
                }
            }),
            'create article'
        )
        created.articleId = article.id

        const pack = expectOk(
            await request('/api/context-packs', {
                method: 'POST',
                token,
                label: 'create context pack',
                body: {
                    name: `${prefix} context pack`,
                    type: 'project',
                    stage: 'E2E',
                    description: 'Temporary pack created by the RAG E2E verifier.',
                    intent: 'Verify context pack indexing, retrieval and AI drafting entry behavior.',
                    summary: 'Contains one article source and one custom source.',
                    tags: ['e2e', 'rag']
                }
            }),
            'create context pack'
        )
        created.packId = pack.id

        expectOk(
            await request(`/api/context-packs/${created.packId}/sources`, {
                method: 'POST',
                token,
                label: 'add pack sources',
                body: {
                    article_ids: [created.articleId],
                    sources: [
                        {
                            title: `${prefix} custom retrieval note`,
                            type: 'manual-note',
                            content: [
                                'RAG preview should retrieve this custom note when the query asks about source traceability.',
                                'The answer must cite source snippets and avoid unsupported claims.',
                                'Embedding is optional; keyword retrieval is the expected fallback when no vector model is configured.'
                            ].join('\n'),
                            weight: 'high',
                            status: 'ready'
                        }
                    ]
                }
            }),
            'add pack sources'
        )

        const rebuild = expectOk(
            await request(`/api/context-packs/${created.packId}/rag-index/rebuild`, {
                method: 'POST',
                token,
                label: 'rebuild rag index'
            }),
            'rebuild rag index'
        )
        if (!rebuild.index || Number(rebuild.index.chunks || 0) < 1) {
            throw new Error(`RAG rebuild returned no chunks: ${stringify(rebuild)}`)
        }

        const index = expectOk(
            await request(`/api/context-packs/${created.packId}/rag-index`, {
                token,
                label: 'get rag index'
            }),
            'get rag index'
        )
        if (Number(index.chunks || 0) < 1) {
            throw new Error(`RAG index has no chunks: ${stringify(index)}`)
        }

        const retrieval = expectOk(
            await request(`/api/ai/context-packs/${created.packId}/retrieve`, {
                method: 'POST',
                token,
                label: 'preview rag retrieval',
                body: {
                    query: 'How does the context pack keep source traceability for RAG drafting?',
                    context_token_budget: 1200,
                    allow_embedding: false
                }
            }),
            'preview rag retrieval'
        )
        if (!retrieval.retrieval || !Array.isArray(retrieval.retrieval.snippets) || retrieval.retrieval.snippets.length < 1) {
            throw new Error(`RAG retrieval returned no snippets: ${stringify(retrieval)}`)
        }

        const configs = expectOk(
            await request('/api/ai/configs', {
                token,
                label: 'list ai configs'
            }),
            'list ai configs'
        )
        const hasActiveDbConfig = Array.isArray(configs) && configs.some((item) => item.is_active)
        const hasEnvKey = Boolean(process.env.ARK_API_KEY || process.env.OPENAI_API_KEY)
        let aiDraft = { skipped: true, reason: 'AI call skipped to avoid token spend' }

        if (callAi) {
            const generated = expectOk(
                await request('/api/ai/generate-article', {
                    method: 'POST',
                    token,
                    label: 'generate article',
                    body: {
                        topic: 'Draft a short note about RAG source traceability.',
                        context_pack_id: created.packId,
                        context_token_budget: 1200,
                        allow_embedding: false
                    }
                }),
                'generate article'
            )
            if (!generated.content || typeof generated.content !== 'string') {
                throw new Error(`AI draft content is not a string: ${stringify(generated)}`)
            }
            aiDraft = { skipped: false, title: generated.title, contentLength: generated.content.length }
        } else if (!hasActiveDbConfig && !hasEnvKey) {
            const generated = await request('/api/ai/generate-article', {
                method: 'POST',
                token,
                allowHttpError: true,
                label: 'generate article without config',
                body: {
                    topic: 'Draft a short note about RAG source traceability.',
                    context_pack_id: created.packId,
                    context_token_budget: 1200,
                    allow_embedding: false
                }
            })
            if (generated.payload.status !== 1) {
                throw new Error(`expected controlled AI config error, got: ${stringify(generated.payload)}`)
            }
            aiDraft = { skipped: false, expectedError: generated.payload.msg || 'missing AI config' }
        }

        const browser = await verifyBrowser(loginData, token)

        console.log(JSON.stringify({
            ok: true,
            backendUrl,
            frontendUrl,
            created,
            index,
            retrieval: retrieval.retrieval,
            aiDraft,
            browser
        }, null, 2))
    } finally {
        const cleanupErrors = await cleanup(token)
        if (cleanupErrors.length) {
            console.warn(JSON.stringify({ cleanupErrors }, null, 2))
        }
    }
}

main().catch((error) => {
    console.error(error)
    process.exit(1)
})
