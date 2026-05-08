<template>
    <main class="admin-settings-page">
        <header class="settings-header">
            <div>
                <span class="eyebrow">Admin Settings</span>
                <h1>后台设置</h1>
                <p>系统自检、AI 配置和 RAG/Embedding 这类管理能力集中放在这里，前台只保留用户工作流。</p>
            </div>
            <button class="primary-action" type="button" :disabled="selfCheckState.running || !canObserveSystem" @click="handleSelfCheck">
                <RefreshRight class="button-icon" />
                <span>{{ selfCheckState.running ? '自检中...' : '手动自检' }}</span>
            </button>
        </header>

        <section class="overview-grid">
            <article class="overview-card">
                <span>系统状态</span>
                <strong>{{ latestReport?.score ?? '--' }}</strong>
                <small>{{ latestReport ? formatStatusLabel(latestReport.status) : '等待自检' }}</small>
            </article>
            <article class="overview-card">
                <span>Embedding</span>
                <strong>{{ embeddingConfig?.configured ? '已启用' : '未启用' }}</strong>
                <small>{{ embeddingConfig?.model || '关键词 RAG 可继续使用' }}</small>
            </article>
            <article class="overview-card">
                <span>边界</span>
                <strong>后台</strong>
                <small>权限、模型、自检从前台工作流中分离</small>
            </article>
        </section>

        <section class="settings-grid">
            <article class="settings-panel">
                <div class="panel-heading">
                    <div>
                        <span class="eyebrow">RAG Settings</span>
                        <h2>语义检索配置</h2>
                        <p>默认不产生费用；只有保存配置并手动生成语义索引时才会调用 embedding 接口。</p>
                    </div>
                    <el-switch v-model="embeddingForm.enabled" :disabled="!canManageAi || embeddingSaving" />
                </div>

                <div class="embedding-form">
                    <label>
                        <span>Provider</span>
                        <el-input v-model="embeddingForm.provider" :disabled="!canManageAi" placeholder="openai / volcano / custom" />
                    </label>
                    <label>
                        <span>Model</span>
                        <el-input v-model="embeddingForm.model" :disabled="!canManageAi" placeholder="例如 text-embedding-3-small" />
                    </label>
                    <label>
                        <span>Base URL</span>
                        <el-input v-model="embeddingForm.base_url" :disabled="!canManageAi" placeholder="可留空，或填写兼容 OpenAI 的地址" />
                    </label>
                    <label>
                        <span>API Key</span>
                        <el-input
                            v-model="embeddingForm.api_key"
                            :disabled="!canManageAi"
                            type="password"
                            show-password
                            :placeholder="embeddingConfig?.api_key_masked || '保存后不明文展示'"
                        />
                    </label>
                    <label class="wide-field">
                        <span>Notes</span>
                        <el-input v-model="embeddingForm.notes" :disabled="!canManageAi" type="textarea" :rows="2" placeholder="用途、费用归属或模型说明" />
                    </label>
                </div>

                <div class="panel-actions">
                    <small>{{ embeddingSummary }}</small>
                    <div class="button-row">
                        <button class="secondary-action" type="button" :disabled="!canManageAi || embeddingSaving || embeddingValidating" @click="validateEmbeddingConfig">
                            {{ embeddingValidating ? '校验中...' : '零成本校验' }}
                        </button>
                        <button class="primary-action compact" type="button" :disabled="!canManageAi || embeddingSaving || embeddingValidating" @click="saveEmbeddingConfig">
                            {{ embeddingSaving ? '保存中...' : '保存配置' }}
                        </button>
                    </div>
                </div>

                <div v-if="embeddingValidation" class="validation-box" :class="{ ok: embeddingValidation.ok }">
                    <strong>{{ embeddingValidation.ok ? '配置完整' : '配置未完成' }}</strong>
                    <span>未调用网络，也未消耗 token。</span>
                    <ul>
                        <li v-for="check in embeddingValidation.checks" :key="check.name" :class="{ ok: check.ok }">
                            {{ formatEmbeddingCheckName(check.name) }}：{{ check.detail }}
                        </li>
                    </ul>
                </div>
            </article>

            <article class="settings-panel">
                <div class="panel-heading">
                    <div>
                        <span class="eyebrow">System Check</span>
                        <h2>手动系统自检</h2>
                        <p>检查数据库、表结构、AI Key 和 Embedding 配置；不会后台循环运行。</p>
                    </div>
                </div>

                <div v-if="latestReport" class="check-list">
                    <div v-for="check in latestReport.checks" :key="check.name" class="check-item">
                        <span :class="{ ok: check.ok }"></span>
                        <div>
                            <strong>{{ formatCheckName(check.name) }}</strong>
                            <small>{{ check.detail }}</small>
                        </div>
                    </div>
                </div>
                <p v-else class="empty-text">还没有自检记录，点击右上角按钮生成第一份报告。</p>
            </article>
        </section>

        <section class="history-panel" v-if="selfCheckReports.length">
            <div class="panel-heading compact">
                <div>
                    <span class="eyebrow">Run History</span>
                    <h2>最近自检记录</h2>
                </div>
            </div>
            <div class="history-list">
                <article v-for="report in selfCheckReports" :key="report.checked_at" class="history-item">
                    <strong>{{ report.score }}%</strong>
                    <span :class="report.status">{{ formatStatusLabel(report.status) }}</span>
                    <small>{{ formatFullTime(report.checked_at) }} · {{ report.ok_count }}/{{ report.total }} 通过</small>
                </article>
            </div>
        </section>
    </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import { useElMessage } from '@/hooks/useMessage'
import { usePermission } from '@/hooks/usePermission'
import { useSelfCheck } from '@/hooks/useSelfCheck'
import { aiOpsService } from '@/api/modules/ai'
import type { AIEmbeddingConfig, AIEmbeddingValidation } from '@/api/modules/ai/interface'
import type { SystemSelfCheckReport } from '@/api/modules/system'

const { message } = useElMessage()
const { hasPermission } = usePermission()
const {
    state: selfCheckState,
    latestReport,
    runManualSelfCheck
} = useSelfCheck()

const canManageAi = computed(() => hasPermission('ai:manage'))
const canObserveSystem = computed(() => hasPermission('system:observe'))
const embeddingConfig = ref<AIEmbeddingConfig | null>(null)
const embeddingValidation = ref<AIEmbeddingValidation | null>(null)
const embeddingSaving = ref(false)
const embeddingValidating = ref(false)
const embeddingForm = reactive({
    enabled: false,
    provider: 'openai',
    model: '',
    base_url: '',
    api_key: '',
    notes: ''
})

const selfCheckReports = computed(() => selfCheckState.reports.slice(0, 6))
const embeddingSummary = computed(() => {
    if (!embeddingConfig.value) return '配置尚未读取'
    if (embeddingConfig.value.configured) return `当前模型：${embeddingConfig.value.model}`
    return '未配置时系统继续使用关键词 RAG，不会自动产生费用'
})

function syncEmbeddingForm(config: AIEmbeddingConfig) {
    embeddingForm.enabled = config.enabled
    embeddingForm.provider = config.provider || 'openai'
    embeddingForm.model = config.model || ''
    embeddingForm.base_url = config.base_url || ''
    embeddingForm.api_key = ''
    embeddingForm.notes = config.notes || ''
}

function buildEmbeddingPayload() {
    const payload: Partial<AIEmbeddingConfig> = {
        enabled: embeddingForm.enabled,
        provider: embeddingForm.provider.trim(),
        model: embeddingForm.model.trim(),
        base_url: embeddingForm.base_url.trim(),
        notes: embeddingForm.notes.trim()
    }
    if (embeddingForm.api_key.trim()) {
        payload.api_key = embeddingForm.api_key.trim()
    }
    return payload
}

async function loadEmbeddingConfig() {
    if (!canManageAi.value) return
    try {
        const config = await aiOpsService.getEmbeddingConfig()
        embeddingConfig.value = config
        syncEmbeddingForm(config)
        embeddingValidation.value = null
    } catch (error) {
        console.error('Load embedding config failed:', error)
    }
}

async function validateEmbeddingConfig() {
    if (!canManageAi.value || embeddingValidating.value) return

    embeddingValidating.value = true
    try {
        const result = await aiOpsService.validateEmbeddingConfig(buildEmbeddingPayload())
        embeddingValidation.value = result
        if (result.ok) {
            message.success('Embedding 配置完整，校验未调用网络')
        } else {
            message.warning('Embedding 配置还不完整，校验未调用网络')
        }
    } catch (error: any) {
        console.error('Validate embedding config failed:', error)
        message.error(error?.msg || 'Embedding 配置校验失败')
    } finally {
        embeddingValidating.value = false
    }
}

async function saveEmbeddingConfig() {
    if (!canManageAi.value || embeddingSaving.value) return

    embeddingSaving.value = true
    try {
        const config = await aiOpsService.saveEmbeddingConfig(buildEmbeddingPayload())
        embeddingConfig.value = config
        syncEmbeddingForm(config)
        embeddingValidation.value = null
        message.success('Embedding 配置已保存')
    } catch (error: any) {
        console.error('Save embedding config failed:', error)
        message.error(error?.msg || 'Embedding 配置保存失败')
    } finally {
        embeddingSaving.value = false
    }
}

async function handleSelfCheck() {
    if (!canObserveSystem.value) {
        message.warning('当前账号没有系统自检权限')
        return
    }
    const report = await runManualSelfCheck()
    if (report) {
        message.success('系统自检完成')
    }
}

function formatCheckName(name: string) {
    const labels: Record<string, string> = {
        database_connection: '数据库连接',
        schema_integrity: '数据表结构',
        ai_config: 'AI 配置',
        ai_key: 'AI Key',
        embedding_config: 'Embedding'
    }
    return labels[name] || name
}

function formatEmbeddingCheckName(name: string) {
    const labels: Record<string, string> = {
        enabled: '启用状态',
        provider: '服务商',
        model: '向量模型',
        api_key: 'API Key',
        base_url: 'Base URL'
    }
    return labels[name] || name
}

function formatStatusLabel(status: SystemSelfCheckReport['status']) {
    const labels = {
        healthy: '健康',
        attention: '关注',
        critical: '风险'
    }
    return labels[status]
}

function formatFullTime(value: string) {
    return new Date(value).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

onMounted(loadEmbeddingConfig)
</script>

<style scoped>
.admin-settings-page {
    width: var(--page-width);
    min-height: calc(100vh - 160px);
    margin: 0 auto;
    padding: 44px 0 76px;
    color: var(--text-primary);
}

.settings-header,
.panel-heading,
.panel-actions {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 18px;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--badge-bg);
    color: var(--badge-fg);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
}

.settings-header h1,
.panel-heading h2 {
    margin: 14px 0 8px;
    font-size: clamp(34px, 5vw, 56px);
    line-height: 1.04;
}

.panel-heading h2 {
    font-size: 28px;
}

.settings-header p,
.panel-heading p,
.overview-card small,
.panel-actions small,
.check-item small,
.empty-text {
    color: var(--text-secondary);
}

.primary-action,
.secondary-action {
    min-height: 38px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: 0;
    border-radius: 8px;
    padding: 0 14px;
    font: inherit;
    font-weight: 700;
    cursor: pointer;
}

.primary-action {
    color: var(--button-fg);
    background: var(--button-bg);
}

.primary-action.compact,
.secondary-action {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.primary-action:disabled,
.secondary-action:disabled {
    cursor: not-allowed;
    opacity: 0.58;
}

.button-icon {
    width: 16px;
    height: 16px;
}

.overview-grid,
.settings-grid,
.history-list {
    display: grid;
    gap: 12px;
}

.overview-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    margin-top: 24px;
}

.overview-card,
.settings-panel,
.history-panel {
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.overview-card {
    min-height: 116px;
    padding: 18px;
    display: grid;
    gap: 8px;
}

.overview-card span {
    color: var(--text-secondary);
    font-weight: 700;
}

.overview-card strong {
    font-size: 30px;
    line-height: 1;
}

.settings-grid {
    grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.75fr);
    margin-top: 12px;
}

.settings-panel,
.history-panel {
    padding: 20px;
}

.embedding-form {
    margin-top: 18px;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.embedding-form label {
    display: grid;
    gap: 8px;
    color: var(--text-secondary);
    font-size: 13px;
    font-weight: 700;
}

.wide-field {
    grid-column: 1 / -1;
}

.panel-actions {
    align-items: center;
    margin-top: 16px;
}

.button-row {
    display: inline-flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 8px;
}

.validation-box {
    margin-top: 14px;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid rgba(180, 35, 24, 0.24);
    background: rgba(180, 35, 24, 0.08);
}

.validation-box.ok {
    border-color: rgba(12, 122, 67, 0.24);
    background: rgba(12, 122, 67, 0.08);
}

.validation-box span,
.validation-box li,
.history-item small {
    color: var(--text-secondary);
    font-size: 13px;
}

.validation-box ul {
    margin: 10px 0 0;
    padding: 0;
    list-style: none;
    display: grid;
    gap: 6px;
}

.validation-box li {
    color: #b42318;
}

.validation-box li.ok {
    color: #0c7a43;
}

.check-list {
    margin-top: 18px;
    display: grid;
    gap: 12px;
}

.check-item {
    display: grid;
    grid-template-columns: 10px minmax(0, 1fr);
    gap: 10px;
}

.check-item > span {
    width: 8px;
    height: 8px;
    margin-top: 6px;
    border-radius: 999px;
    background: #b42318;
}

.check-item > span.ok {
    background: #0c7a43;
}

.check-item strong,
.check-item small {
    display: block;
}

.history-panel {
    margin-top: 12px;
}

.history-list {
    grid-template-columns: repeat(6, minmax(0, 1fr));
    margin-top: 14px;
}

.history-item {
    padding: 14px;
    border-radius: 8px;
    background: var(--surface-subtle);
}

.history-item strong,
.history-item span,
.history-item small {
    display: block;
}

.history-item strong {
    font-size: 26px;
}

.history-item span {
    margin: 4px 0;
    color: #9a5a00;
    font-size: 13px;
    font-weight: 700;
}

.history-item span.healthy {
    color: #0c7a43;
}

.history-item span.critical {
    color: #b42318;
}

@media (max-width: 1120px) {
    .settings-grid,
    .overview-grid,
    .history-list {
        grid-template-columns: 1fr;
    }

    .settings-header,
    .panel-heading,
    .panel-actions {
        align-items: flex-start;
        flex-direction: column;
    }
}

@media (max-width: 640px) {
    .embedding-form {
        grid-template-columns: 1fr;
    }
}
</style>
