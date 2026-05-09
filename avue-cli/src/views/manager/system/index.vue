<template>
    <basic-container>
        <div class="admin-page-head">
            <div>
                <span class="admin-eyebrow">System Health</span>
                <h1 class="admin-page-title">系统自检</h1>
                <p class="admin-page-desc">手动检查数据库、核心表、AI 配置和 RAG 索引状态，不再后台自动循环消耗资源。</p>
            </div>
            <el-button type="primary" :loading="loading" @click="handleRun">立即自检</el-button>
        </div>

        <section class="system-summary">
            <article class="summary-card">
                <span>健康分</span>
                <strong>{{ report.score ?? '-' }}</strong>
                <small>{{ statusText }}</small>
            </article>
            <article class="summary-card">
                <span>通过项</span>
                <strong>{{ report.ok_count ?? 0 }} / {{ report.total ?? 0 }}</strong>
                <small>{{ report.duration_ms ? `${report.duration_ms} ms` : '未运行' }}</small>
            </article>
            <article class="summary-card">
                <span>检查时间</span>
                <strong class="summary-card__time">{{ report.checked_at || '-' }}</strong>
                <small>由管理员手动触发</small>
            </article>
        </section>

        <el-card shadow="never" class="system-card">
            <template #header>
                <span>检查项</span>
            </template>
            <el-table v-loading="loading" :data="report.checks || []" border>
                <el-table-column prop="name" label="项目" width="180" />
                <el-table-column prop="detail" label="说明" />
                <el-table-column prop="severity" label="等级" width="120" />
                <el-table-column label="状态" width="120">
                    <template #default="{ row }">
                        <el-tag :type="row.ok ? 'success' : 'danger'">{{ row.ok ? '正常' : '异常' }}</el-tag>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <el-card shadow="never" class="system-card">
            <template #header>
                <span>最近记录</span>
            </template>
            <el-table :data="history" border>
                <el-table-column prop="checked_at" label="时间" min-width="180" />
                <el-table-column prop="status" label="状态" width="120" />
                <el-table-column prop="score" label="健康分" width="100" />
                <el-table-column prop="duration_ms" label="耗时 ms" width="110" />
            </el-table>
        </el-card>
    </basic-container>
</template>

<script>
import { getSelfCheck, getSelfCheckHistory, runSelfCheck } from '@/api/manager/system'

export default {
    data() {
        return {
            report: {},
            history: [],
            loading: false
        }
    },
    computed: {
        statusText() {
            const status = this.report.status
            if (status === 'healthy') return '系统健康'
            if (status === 'attention') return '需要关注'
            if (status === 'critical') return '存在高风险'
            return '等待检查'
        }
    },
    mounted() {
        this.loadReport()
        this.loadHistory()
    },
    methods: {
        loadReport() {
            this.loading = true
            getSelfCheck().then(res => {
                this.report = res.data.data || {}
            }).finally(() => {
                this.loading = false
            })
        },
        loadHistory() {
            getSelfCheckHistory().then(res => {
                this.history = (res.data.data && res.data.data.reports) || []
            })
        },
        handleRun() {
            this.loading = true
            runSelfCheck().then(res => {
                this.report = res.data.data || {}
                this.$message.success('系统自检完成')
                this.loadHistory()
            }).finally(() => {
                this.loading = false
            })
        }
    }
}
</script>

<style scoped lang="scss">
.system-summary {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 14px;
}

.summary-card,
.system-card {
    border-radius: 6px;
    background: var(--admin-surface);
}

.summary-card {
    min-height: 126px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: var(--admin-shadow);

    span,
    small {
        color: var(--admin-muted);
    }

    strong {
        color: var(--admin-ink);
        font-size: 32px;
        line-height: 1.1;
    }

    &__time {
        font-size: 16px !important;
        word-break: break-all;
    }
}

.system-card {
    margin-bottom: 14px;
}

@media (max-width: 900px) {
    .system-summary {
        grid-template-columns: 1fr;
    }
}
</style>
