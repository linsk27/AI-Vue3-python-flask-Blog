// AI 聊天消息接口
export interface ChatMessage {
    role: 'user' | 'assistant' | 'system'
    content: string
}

// AI 聊天请求参数接口
export interface AIChatRequest {
    message?: string
    user_id?: string
    reset_context?: boolean
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
}

// AI 聊天响应接口
export interface AIChatResponse {
    status: number
    reply?: string
    msg: string
    data?: AIChatResponseData
    error?: string
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
