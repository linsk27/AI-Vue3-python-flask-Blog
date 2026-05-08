// AI 聊天消息接口
export interface ChatMessage {
    role: 'user' | 'assistant' | 'system'
    content: string
}

export interface AIRetrievalSnippet {
    id: string
    source_id?: number
    source_ref_type?: string
    source_ref_id?: number
    title: string
    type?: string
    score: number
    retrieval_mode?: 'keyword' | 'semantic'
    tokens_estimate: number
    content_preview?: string
}

export interface AIRetrievalMeta {
    mode: 'keyword' | 'semantic'
    embedding_used?: boolean
    semantic_requested?: boolean
    semantic_available?: boolean
    semantic_unavailable_reason?: string
    embedding_configured?: boolean
    embedding_model?: string
    embedded_chunks?: number
    current_model_embedded_chunks?: number
    token_budget: number
    used_tokens_estimate: number
    indexed_chunks?: number
    snippets: AIRetrievalSnippet[]
    query_terms?: string[]
    truncated?: boolean
}

export interface AIRetrievalPreviewRequest {
    query: string
    context_token_budget?: number
    allow_embedding?: boolean
}

export interface AIRetrievalPreview {
    pack?: {
        id: number
        name: string
    } | null
    retrieval: AIRetrievalMeta | null
    prompt_tokens_estimate: number
}

// AI 聊天请求参数接口
export interface AIChatRequest {
    message?: string
    user_id?: string
    reset_context?: boolean
    context_pack_id?: number | string
    context_token_budget?: number
    system_prompt?: string
    max_tokens?: number
    temperature?: number
    model_provider?: string
    model_name?: string
}

// AI 聊天响应数据接口
export interface AIChatResponseData {
    reply: string
    context_length: number
    full_response: string
    retrieval?: AIRetrievalMeta | null
    context_pack?: {
        id: number
        name: string
    } | null
}

// AI 聊天响应接口
export interface AIChatResponse {
    status: number
    reply?: string
    msg: string
    data?: AIChatResponseData
    error?: string
}

export interface AIStreamPayload {
    type: 'start' | 'delta' | 'done' | 'error'
    content?: string
    message?: string
    context_length?: number
    model_used?: string
    provider_used?: string
    context_pack?: {
        id: number
        name: string
    } | null
    retrieval?: AIRetrievalMeta | null
}

export interface AIStreamHandlers {
    onStart?: (payload: AIStreamPayload) => void
    onDelta?: (content: string, payload: AIStreamPayload) => void
    onDone?: (payload: AIStreamPayload) => void
    onError?: (message: string, payload?: AIStreamPayload) => void
}

export interface AIEmbeddingConfig {
    id?: number
    enabled: boolean
    configured: boolean
    provider: string
    model: string
    base_url?: string
    api_key?: string
    api_key_masked?: string
    notes?: string
    source?: 'database' | 'environment'
    updated_at?: string
}

export interface AIEmbeddingValidationCheck {
    name: string
    ok: boolean
    detail: string
}

export interface AIEmbeddingValidation {
    ok: boolean
    network_call: boolean
    token_cost: boolean
    embedding_configured: boolean
    source: 'database' | 'environment'
    model: string
    checks: AIEmbeddingValidationCheck[]
    next_action: string
}

// AI 上下文响应数据接口
export interface AIContextResponseData {
    context: ChatMessage[]
    length: number
}

// AI 上下文响应接口
export interface AIContextResponse {
    status: number
    msg?: string
    data: AIContextResponseData
}

// 聊天历史记录项接口
export interface ChatHistoryItem {
    id: string
    message: string
    response: string
    timestamp: string
}

// 聊天历史响应数据接口
export interface ChatHistoryResponseData {
    history: ChatHistoryItem[]
}

// 聊天历史响应接口
export interface ChatHistoryResponse {
    status: number
    msg: string
    data: ChatHistoryResponseData
}

// AI 摘要请求参数接口
export interface AISummaryRequest {
    content: string
    length?: number
    user_id?: string
}

// AI 摘要响应数据接口
export interface AISummaryResponseData {
    summary: string
    usage: Record<string, any>
}

// AI 摘要响应接口
export interface AISummaryResponse {
    status: number
    msg: string
    data?: AISummaryResponseData
    error?: string
}
