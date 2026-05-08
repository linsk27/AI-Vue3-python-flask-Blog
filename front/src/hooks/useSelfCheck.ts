import { computed, reactive } from 'vue'
import { systemService, type SystemSelfCheckReport } from '@/api/modules/system'

const STORAGE_KEY = 'contextforge.selfCheck.reports'

interface LocalReport extends SystemSelfCheckReport {
    source: 'backend' | 'local'
}

interface SelfCheckState {
    running: boolean
    lastError: string
    reports: LocalReport[]
}

const state = reactive<SelfCheckState>({
    running: false,
    lastError: '',
    reports: loadReports()
})

function loadReports(): LocalReport[] {
    try {
        const rawReports = localStorage.getItem(STORAGE_KEY)
        if (!rawReports) return []
        return JSON.parse(rawReports)
    } catch (error) {
        console.error('Load self-check reports failed:', error)
        return []
    }
}

function persistReports() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state.reports.slice(0, 12)))
}

async function runManualSelfCheck() {
    if (state.running) return state.reports[0]

    state.running = true
    state.lastError = ''

    try {
        const report = await systemService.selfCheck()
        const normalizedReport = {
            ...report,
            source: 'backend' as const
        }
        state.reports.unshift(normalizedReport)
        state.reports = state.reports.slice(0, 12)
        persistReports()
        return normalizedReport
    } catch (error: any) {
        const fallbackReport = buildLocalReport(error?.message || '后端自检接口暂时不可用')
        state.lastError = fallbackReport.checks.find(item => !item.ok)?.detail || ''
        state.reports.unshift(fallbackReport)
        state.reports = state.reports.slice(0, 12)
        persistReports()
        return fallbackReport
    } finally {
        state.running = false
    }
}

function buildLocalReport(errorMessage: string): LocalReport {
    const online = window.navigator.onLine
    const storageOk = canUseLocalStorage()
    const checks = [
        {
            name: 'browser_network',
            ok: online,
            detail: online ? '浏览器网络在线' : '浏览器处于离线状态',
            severity: online ? 'normal' : 'high'
        },
        {
            name: 'local_storage',
            ok: storageOk,
            detail: storageOk ? '本地缓存可写' : '本地缓存不可写',
            severity: storageOk ? 'normal' : 'medium'
        },
        {
            name: 'backend_self_check',
            ok: false,
            detail: errorMessage,
            severity: 'high'
        }
    ] as LocalReport['checks']

    const okCount = checks.filter(item => item.ok).length
    const score = Math.round((okCount / checks.length) * 100)

    return {
        source: 'local',
        status: score >= 90 ? 'healthy' : score >= 60 ? 'attention' : 'critical',
        score,
        ok_count: okCount,
        total: checks.length,
        checks,
        checked_at: new Date().toISOString(),
        duration_ms: 0
    }
}

function canUseLocalStorage() {
    try {
        const key = 'contextforge.selfCheck.storageProbe'
        localStorage.setItem(key, String(Date.now()))
        localStorage.removeItem(key)
        return true
    } catch {
        return false
    }
}

export function useSelfCheck() {
    const latestReport = computed(() => state.reports[0])

    return {
        state,
        latestReport,
        runManualSelfCheck
    }
}
