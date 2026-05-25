const { chromium } = require('playwright')
const fs = require('fs')
const path = require('path')

const baseUrl = process.env.BASE_URL || 'http://127.0.0.1:8080'
const outDir = path.resolve(__dirname, '..', '..', '.codex-logs')

const routes = [
    ['home', '/'],
    ['summary', '/ai-center/summary'],
    ['write', '/essays/write'],
    ['chat', '/ai-center/chat']
]

async function checkViewport(browser, viewportName, viewport) {
    const page = await browser.newPage({ viewport, isMobile: viewport.width < 600 })
    const consoleMessages = []
    const httpErrors = []
    const results = []

    page.on('console', (message) => {
        if (['error', 'warning'].includes(message.type())) {
            consoleMessages.push(`${message.type()}: ${message.text()}`)
        }
    })
    page.on('response', (response) => {
        if (response.status() >= 400) {
            httpErrors.push({ status: response.status(), url: response.url() })
        }
    })
    page.on('pageerror', (error) => {
        consoleMessages.push(`pageerror: ${error.message}`)
    })

    for (const [name, route] of routes) {
        await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle', timeout: 30000 })
        await page.screenshot({
            path: path.join(outDir, `${name}-${viewportName}.png`),
            fullPage: true
        })

        const horizontalOverflow = await page.evaluate(() => {
            return document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
        })

        results.push({
            name,
            requestedUrl: `${baseUrl}${route}`,
            finalUrl: page.url(),
            horizontalOverflow
        })
    }

    await page.close()
    return { viewport: viewportName, results, consoleMessages, httpErrors }
}

async function main() {
    fs.mkdirSync(outDir, { recursive: true })
    const browser = await chromium.launch({ headless: true })

    const reports = [
        await checkViewport(browser, 'desktop', { width: 1280, height: 900 }),
        await checkViewport(browser, 'mobile', { width: 390, height: 844 })
    ]

    await browser.close()

    const hasOverflow = reports.some((report) => {
        return report.results.some((result) => result.horizontalOverflow)
    })

    console.log(JSON.stringify({ baseUrl, outDir, reports }, null, 2))

    if (hasOverflow) {
        process.exitCode = 1
    }
}

main().catch((error) => {
    console.error(error)
    process.exit(1)
})
