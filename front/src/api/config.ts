const DEFAULT_API_BASE_URL = '/api'

function trimTrailingSlash(value: string) {
    return value.replace(/\/+$/, '')
}

export function getApiBaseUrl() {
    const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL
    const normalizedBaseUrl = trimTrailingSlash(rawBaseUrl)

    if (!normalizedBaseUrl) return DEFAULT_API_BASE_URL
    if (normalizedBaseUrl.endsWith('/api')) return normalizedBaseUrl

    return `${normalizedBaseUrl}/api`
}

export function getApiUrl(path: string) {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`
    return `${getApiBaseUrl()}${normalizedPath}`
}
