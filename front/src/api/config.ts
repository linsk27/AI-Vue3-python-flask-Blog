const FALLBACK_API_BASE_URL = 'https://ai-vue3-python-flask-blog-copy-production.up.railway.app/api'

const RETIRED_API_BASE_URLS = new Set([
    'https://ai-vue3-python-flask-blog-production.up.railway.app'
])

function trimTrailingSlash(value: string) {
    return value.replace(/\/+$/, '')
}

export function getApiBaseUrl() {
    const configuredBaseUrl = trimTrailingSlash(import.meta.env.VITE_API_BASE_URL || '')

    if (!configuredBaseUrl) return ''

    const activeBaseUrl = RETIRED_API_BASE_URLS.has(configuredBaseUrl)
        ? FALLBACK_API_BASE_URL
        : configuredBaseUrl

    return activeBaseUrl.endsWith('/api') ? activeBaseUrl : `${activeBaseUrl}/api`
}
