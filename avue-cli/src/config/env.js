const API_BASE_URL = (import.meta.env.VITE_APP_API || '').replace(/\/+$/, '')

const getApiUrl = url => {
  if (!url || /^https?:\/\//.test(url)) return url
  if (!url.startsWith('/api')) return url
  return API_BASE_URL ? `${API_BASE_URL}${url}` : url
}

let baseUrl = ''
export { API_BASE_URL, baseUrl, getApiUrl }
