export const ARTICLE_CREATE = '/articles'
export const ARTICLE_DETAIL = (id: number | string) => `/articles/${id}`
export const ARTICLE_UPDATE = (id: number | string) => `/articles/${id}`
export const ARTICLE_DELETE = (id: number | string) => `/articles/${id}`
export const ARTICLE_LIST = '/articles'
export const ARTICLE_TOGGLE_LIKE = (id: number | string) => `/articles/${id}/like`
export const ARTICLE_INCREMENT_VIEW = (id: number | string) => `/articles/${id}/view`
export const ARTICLE_MY_LIKES = '/articles/my-likes'
