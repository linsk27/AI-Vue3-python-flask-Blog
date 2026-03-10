import request from '@/api'
import { AI_CHAT_API, AI_CONTEXT_API, AI_SUMMARY_API } from './url.const'
import type { AIChatRequest, AIChatResponse, AISummaryRequest, AISummaryResponse, AIContextResponse } from './interface'

/**
 * AI 聊天服务
 */
export const aiChatService = {
    /**
     * 发送聊天消息
     * @param params 聊天请求参数
     * @returns 聊天响应
     */
    sendMessage: (params: AIChatRequest) => {
        return request.post<AIChatResponse>(AI_CHAT_API, params)
    },

    /**
     * 获取上下文
     * @param user_id 用户ID
     * @returns 上下文响应
     */
    getContext: (user_id: string) => {
        return request.get<AIContextResponse>(AI_CONTEXT_API, { user_id })
    },

    /**
     * 清除上下文
     * @param user_id 用户ID
     * @returns 清除响应
     */
    clearContext: (user_id: string) => {
        return request.delete<AIContextResponse>(AI_CONTEXT_API, { user_id })
    }
}

/**
 * AI 摘要服务
 */
export const aiArticleService = {
    /**
     * 生成文章
     * @param topic 文章主题或概要
     * @returns 文章内容
     */
    generateArticle: (topic: string) => {
        return request.post<{
            title: string
            content: string
            summary: string
            category: string
            tags: string[]
        }>('/ai/generate-article', { topic })
    }
}

export const aiSummaryService = {
    /**
     * 生成内容摘要
     * @param params 摘要请求参数
     * @returns 摘要响应
     */
    generateSummary: (params: AISummaryRequest) => {
        // 复用 Chat 接口生成摘要
        const length = params.length || 300
        const lengthPrompt = `，字数严格控制在${length}字左右，绝对不能超过${Math.ceil(length * 1.1)}字`

        // 更加严格地计算 max_tokens
        // 1个汉字 ≈ 2 tokens (DeepSeek/Doubao 常见的比例)
        // 限制回复的 token 数，从物理上防止 AI 话多
        const maxTokens = Math.ceil(length * 2.5) + 100

        return request.post<AIChatResponse>(AI_CHAT_API, {
            // 在消息中再次强调任务，防止 AI 被原文内容带偏
            message: `请为以下内容生成一份摘要（要求字数：${length}字左右）：\n\n${params.content}`,
            system_prompt: `你是一个专业的文章摘要助手。你必须严格遵守字数限制。
你的任务是：仅根据用户提供的文本生成一份简洁的摘要。

严格遵守以下输出规则：
1. 摘要字数限制：${lengthPrompt}。这是最高优先级要求。
2. 直接输出摘要内容，禁止任何开场白（如"好的"、"摘要如下"、"这篇文章讲述了"）。
3. 禁止输出任何建议、评价或后续引导。
4. 仅提取核心观点和关键信息，不要对原文进行不必要的润色或扩充。
5. 保持客观、中立的语气。
6. 如果内容过短，请按比例缩减摘要长度，不要强行凑字数。`,
            reset_context: true,
            user_id: params.user_id,
            max_tokens: maxTokens,
            temperature: 0.3 // 降低随机性，使输出更稳定
        })
    }
}
