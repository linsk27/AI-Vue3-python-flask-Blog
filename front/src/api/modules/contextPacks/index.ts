import http from '@/api'

export interface ContextPackSource {
    id?: number
    title: string
    type: string
    ref_type?: string
    ref_id?: number
    content?: string
    weight: string
    status: string
    created_at?: string
}

export interface ContextPack {
    id: number
    user_id?: number | null
    name: string
    type: string
    stage: string
    description: string
    intent: string
    summary: string
    nextAction: string
    keyPoints: string[]
    sources: ContextPackSource[]
    documents?: string[]
    tags: string[]
    quality: number
    tokenBudget: string
    freshness: string
    visibility?: 'public' | 'private'
    canManage?: boolean
    canUseRag?: boolean
    created_at?: string
    updated_at?: string
}

export interface ContextPackCreateParams {
    name: string
    type?: string
    stage?: string
    description?: string
    intent?: string
    tags?: string[]
    article_ids?: number[]
    sources?: Partial<ContextPackSource>[]
}

export interface ContextPackExport {
    markdown: string
    prompt: string
}

export interface ContextPackStats {
    packs: number
    sources: number
    articles: number
    latest_updated_at: string
}

export interface ContextPackRagIndex {
    sources: number
    indexed_sources?: number
    chunks: number
    embedded_chunks?: number
    current_model_embedded_chunks?: number
    stale_embedding_chunks?: number
    pending_embedding_chunks?: number
    embedding_configured?: boolean
    embedding_model?: string
    generated_embeddings?: number
    skipped_embeddings?: number
    failed_embeddings?: number
    planned_embeddings?: number
    planned_embedding_tokens_estimate?: number
    tokens_estimate?: number
    pending_embedding_tokens_estimate?: number
    embedding_target_chunks?: number
    embedding_target_tokens_estimate?: number
    embedding_skip_current_model_chunks?: number
    pending_sources?: number
    latest_updated_at?: string
    dry_run?: boolean
    force?: boolean
}

export interface ContextPackRagIndexResult {
    pack: ContextPack
    index: ContextPackRagIndex
}

const contextPackApi = {
    getList: (params?: { type?: string; search?: string }) => {
        return http.get<ContextPack[]>('/context-packs', params)
    },
    getStats: () => {
        return http.get<ContextPackStats>('/context-packs/stats')
    },
    create: (params: ContextPackCreateParams) => {
        return http.post<ContextPack>('/context-packs', params)
    },
    update: (id: number | string, params: Partial<ContextPackCreateParams>) => {
        return http.put<ContextPack>(`/context-packs/${id}`, params)
    },
    delete: (id: number | string) => {
        return http.delete(`/context-packs/${id}`)
    },
    addSources: (id: number | string, params: { article_ids?: number[]; sources?: Partial<ContextPackSource>[] }) => {
        return http.post<ContextPack>(`/context-packs/${id}/sources`, params)
    },
    addSourcesCompat: (id: number | string, params: { article_ids?: number[]; sources?: Partial<ContextPackSource>[] }) => {
        return http.post<ContextPack>('/context-pack-sources', { pack_id: id, ...params })
    },
    deleteSource: (packId: number | string, sourceId: number | string) => {
        return http.delete<ContextPack>(`/context-packs/${packId}/sources/${sourceId}`)
    },
    getRagIndex: (id: number | string) => {
        return http.get<ContextPackRagIndex>(`/context-packs/${id}/rag-index`)
    },
    rebuildRagIndex: (id: number | string) => {
        return http.post<ContextPackRagIndexResult>(`/context-packs/${id}/rag-index/rebuild`)
    },
    buildEmbeddings: (id: number | string, params?: { force?: boolean; dry_run?: boolean }) => {
        return http.post<ContextPackRagIndexResult>(`/context-packs/${id}/rag-index/embeddings`, params || {})
    },
    exportMarkdown: (id: number | string) => {
        return http.get<ContextPackExport>(`/context-packs/${id}/markdown`)
    }
}

export default contextPackApi
