import request from '@/api'

export interface SystemCheckItem {
    name: string
    ok: boolean
    detail: string
    severity: 'normal' | 'medium' | 'high'
}

export interface SystemSelfCheckReport {
    status: 'healthy' | 'attention' | 'critical'
    score: number
    ok_count: number
    total: number
    checks: SystemCheckItem[]
    checked_at: string
    duration_ms: number
}

export interface SystemHealthReport {
    status: 'healthy' | 'critical'
    checked_at: string
}

export const systemService = {
    health: () => request.get<SystemHealthReport>('/health'),
    selfCheck: () => request.get<SystemSelfCheckReport>('/system/self-check'),
    selfCheckHistory: () => request.get<{ reports: SystemSelfCheckReport[] }>('/system/self-check/history')
}
