export interface IArticleParams {
    title: string
    content: string
    summary?: string
    category?: string
    tags?: string[]
    cover_image?: string
    status?: string
}

export interface IArticle {
    id: number
    title: string
    content: string
    summary: string
    category: string
    tags: string[]
    cover_image: string
    author_id: number
    views: number
    likes: number
    status: string
    created_at: string
    updated_at: string
    author_name?: string
    author_avatar?: string
    is_liked?: boolean
}
