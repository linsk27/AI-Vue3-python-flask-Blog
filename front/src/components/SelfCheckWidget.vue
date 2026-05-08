<template>
    <el-popover placement="bottom-end" :width="360" trigger="click" popper-class="self-check-popover">
        <template #reference>
            <button class="self-check-trigger" type="button" :class="statusClass" aria-label="打开系统自检面板">
                <component :is="statusIcon" class="trigger-icon" />
                <span>{{ triggerLabel }}</span>
            </button>
        </template>

        <section class="self-check-panel">
            <header class="panel-header">
                <div>
                    <span class="panel-kicker">System Check</span>
                    <h2>系统自检</h2>
                </div>
                <button class="refresh-button" type="button" :disabled="state.running" @click="handleManualCheck">
                    <RefreshRight class="refresh-icon" />
                </button>
            </header>

            <div class="score-row">
                <strong>{{ latestReport?.score ?? '--' }}</strong>
                <div>
                    <span>{{ statusText }}</span>
                    <small>{{ latestTime }}</small>
                </div>
            </div>

            <ul class="check-list" v-if="latestReport">
                <li v-for="item in latestReport.checks" :key="item.name">
                    <span :class="{ ok: item.ok }"></span>
                    <div>
                        <strong>{{ formatCheckName(item.name) }}</strong>
                        <small>{{ item.detail }}</small>
                    </div>
                </li>
            </ul>

            <p v-else class="empty-state">点击右上角刷新按钮，检查数据库、表结构和 AI 配置。</p>
        </section>
    </el-popover>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CircleCheckFilled, RefreshRight, WarningFilled } from '@element-plus/icons-vue'
import { useSelfCheck } from '@/hooks/useSelfCheck'

const { state, latestReport, runManualSelfCheck } = useSelfCheck()

const statusClass = computed(() => latestReport.value?.status || 'pending')
const statusIcon = computed(() => {
    if (!latestReport.value) return RefreshRight
    return latestReport.value.status === 'healthy' ? CircleCheckFilled : WarningFilled
})
const triggerLabel = computed(() => {
    if (state.running) return '自检中'
    if (!latestReport.value) return '自检'
    return `${latestReport.value.score}%`
})

const statusText = computed(() => {
    if (state.running) return '正在巡检关键链路'
    if (!latestReport.value) return '等待首次自检'
    const labels = {
        healthy: '系统健康',
        attention: '需要关注',
        critical: '关键风险'
    }
    return labels[latestReport.value.status]
})

const latestTime = computed(() => {
    if (!latestReport.value?.checked_at) return '尚未生成报告'
    return `更新于 ${formatClock(latestReport.value.checked_at)}`
})

function formatClock(value: string | number) {
    return new Date(value).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
    })
}

function formatCheckName(name: string) {
    const labels: Record<string, string> = {
        database_connection: '数据库连接',
        schema_integrity: '数据表结构',
        ai_config: 'AI 配置',
        ai_key: 'AI Key',
        browser_network: '浏览器网络',
        local_storage: '本地缓存',
        backend_self_check: '后端自检'
    }
    return labels[name] || name
}

function handleManualCheck() {
    runManualSelfCheck()
}
</script>

<style scoped>
.self-check-trigger {
    min-height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    padding: 0 10px;
    border: 0;
    border-radius: 10px;
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
    cursor: pointer;
    font-size: 13px;
    font-weight: 700;
}

.self-check-trigger.healthy {
    color: #0c7a43;
}

.self-check-trigger.attention {
    color: #9a5a00;
}

.self-check-trigger.critical {
    color: #b42318;
}

.trigger-icon,
.refresh-icon {
    width: 16px;
    height: 16px;
}

.self-check-panel {
    color: var(--text-primary);
}

.panel-header,
.score-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
}

.panel-kicker,
.check-list small,
.empty-state {
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
}

.panel-header h2 {
    margin: 5px 0 0;
    font-size: 22px;
    line-height: 1.1;
}

.refresh-button {
    width: 34px;
    height: 34px;
    display: grid;
    place-items: center;
    border: 0;
    border-radius: 10px;
    color: var(--text-primary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    cursor: pointer;
}

.refresh-button:disabled {
    cursor: wait;
    opacity: 0.6;
}

.score-row {
    margin-top: 18px;
    padding: 16px 0;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
}

.score-row strong {
    font-size: 46px;
    line-height: 1;
}

.score-row span {
    display: block;
    font-weight: 700;
}

.score-row small {
    display: block;
    margin-top: 5px;
    color: var(--text-muted);
}

.check-list {
    margin: 16px 0 0;
    padding: 0;
    display: grid;
    gap: 12px;
    list-style: none;
}

.check-list li {
    display: grid;
    grid-template-columns: 10px minmax(0, 1fr);
    gap: 10px;
}

.check-list li > span {
    width: 8px;
    height: 8px;
    margin-top: 6px;
    border-radius: 50%;
    background: #b42318;
}

.check-list li > span.ok {
    background: #0c7a43;
}

.check-list strong {
    display: block;
    font-size: 13px;
}

.check-list small {
    display: block;
    margin-top: 3px;
    line-height: 1.45;
}

.empty-state {
    margin: 16px 0 0;
    line-height: 1.6;
}
</style>
