<template>
    <basic-container>
        <div class="admin-page-head">
            <div>
                <span class="admin-eyebrow">Context Pack Ops</span>
                <h1 class="admin-page-title">上下文包运营</h1>
                <p class="admin-page-desc">查看真实上下文包、来源数量、RAG 分块索引和向量构建状态。</p>
            </div>
            <el-button type="primary" :loading="loading" @click="loadData">刷新数据</el-button>
        </div>

        <section class="context-stats">
            <article v-for="item in statCards" :key="item.label" class="context-stat-card">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
            </article>
        </section>

        <el-card shadow="never" class="context-card">
            <el-table v-loading="loading" :data="packs" border>
                <el-table-column prop="name" label="名称" min-width="180" show-overflow-tooltip />
                <el-table-column prop="type" label="类型" width="120" />
                <el-table-column prop="visibility" label="可见性" width="100" />
                <el-table-column label="来源" width="100">
                    <template #default="{ row }">{{ sourceCount(row) }}</template>
                </el-table-column>
                <el-table-column prop="quality" label="质量" width="120">
                    <template #default="{ row }">
                        <el-progress :percentage="Number(row.quality || 0)" :show-text="false" />
                    </template>
                </el-table-column>
                <el-table-column prop="updated_at" label="更新时间" min-width="170" show-overflow-tooltip />
                <el-table-column label="RAG 操作" width="260" fixed="right">
                    <template #default="{ row }">
                        <el-button size="small" @click="handleInspect(row)">查看索引</el-button>
                        <el-button size="small" type="primary" :disabled="!row.canManage" @click="handleRebuild(row)">重建分块</el-button>
                        <el-button size="small" type="success" :disabled="!row.canManage" @click="handleEmbeddings(row)">生成向量</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <el-dialog v-model="indexDialog.visible" title="RAG 索引状态" width="620px">
            <div v-if="indexDialog.data" class="index-grid">
                <div v-for="item in indexMetrics" :key="item.label" class="index-metric">
                    <span>{{ item.label }}</span>
                    <strong>{{ item.value }}</strong>
                </div>
            </div>
            <template #footer>
                <el-button @click="indexDialog.visible = false">关闭</el-button>
            </template>
        </el-dialog>
    </basic-container>
</template>

<script>
import { buildEmbeddings, getList, getRagIndex, getStats, rebuildRagIndex } from '@/api/manager/context'

export default {
    data() {
        return {
            packs: [],
            stats: {},
            loading: false,
            indexDialog: {
                visible: false,
                data: null
            }
        }
    },
    computed: {
        statCards() {
            return [
                { label: '上下文包', value: this.stats.packs ?? this.packs.length },
                { label: '资料来源', value: this.stats.sources ?? this.packs.reduce((total, pack) => total + this.sourceCount(pack), 0) },
                { label: '关联文档', value: this.stats.articles ?? 0 }
            ]
        },
        indexMetrics() {
            const data = this.indexDialog.data || {}
            return [
                { label: '来源数', value: data.sources ?? 0 },
                { label: '分块数', value: data.chunks ?? 0 },
                { label: '已向量化分块', value: data.current_model_embedded_chunks ?? data.embedded_chunks ?? 0 },
                { label: '待向量化分块', value: data.pending_embedding_chunks ?? 0 },
                { label: 'Embedding 模型', value: data.embedding_model || '未配置' },
                { label: '预估待处理 token', value: data.pending_embedding_tokens_estimate ?? 0 }
            ]
        }
    },
    mounted() {
        this.loadData()
    },
    methods: {
        sourceCount(row) {
            return Array.isArray(row.sources) ? row.sources.length : 0
        },
        loadData() {
            this.loading = true
            Promise.all([getList(), getStats()]).then(([listRes, statsRes]) => {
                this.packs = listRes.data.data || []
                this.stats = statsRes.data.data || {}
            }).finally(() => {
                this.loading = false
            })
        },
        handleInspect(row) {
            getRagIndex(row.id).then(res => {
                this.indexDialog.data = res.data.data || {}
                this.indexDialog.visible = true
            })
        },
        handleRebuild(row) {
            this.$confirm('重建分块索引只会重新切分资料，不会调用向量模型。确认继续？', {
                confirmButtonText: '重建分块',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => rebuildRagIndex(row.id)).then(res => {
                this.$message.success('RAG 分块索引已重建')
                this.indexDialog.data = res.data.data && res.data.data.index
                this.indexDialog.visible = true
                this.loadData()
            })
        },
        handleEmbeddings(row) {
            this.$confirm('生成向量会调用已配置的 Embedding 模型并消耗额度。确认继续？', {
                confirmButtonText: '生成向量',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => buildEmbeddings(row.id)).then(res => {
                this.$message.success('向量构建任务已完成')
                this.indexDialog.data = res.data.data && res.data.data.index
                this.indexDialog.visible = true
                this.loadData()
            })
        }
    }
}
</script>

<style scoped lang="scss">
.context-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 14px;
}

.context-stat-card,
.context-card,
.index-metric {
    border-radius: 6px;
    background: var(--admin-surface);
}

.context-stat-card {
    min-height: 108px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: var(--admin-shadow);

    span {
        color: var(--admin-muted);
    }

    strong {
        color: var(--admin-ink);
        font-size: 32px;
        line-height: 1;
    }
}

.index-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
}

.index-metric {
    padding: 14px;
    border: 1px solid var(--admin-line);

    span {
        display: block;
        color: var(--admin-muted);
        margin-bottom: 8px;
    }

    strong {
        color: var(--admin-ink);
    }
}

@media (max-width: 900px) {
    .context-stats,
    .index-grid {
        grid-template-columns: 1fr;
    }
}
</style>
