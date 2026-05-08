<template>
    <div class="packs-page">
        <section class="packs-hero">
            <div>
                <span class="eyebrow">ContextForge Workspace</span>
                <h1>把项目知识变成可复用的 AI 上下文资产。</h1>
                <p>
                    上下文包把文档、部署记录、代码决策、AI 对话和交付材料放在同一个语义容器里，
                    让问答、摘要、复盘、答辩和写作都能沿着同一条知识线索推进。
                </p>
                <div class="hero-actions">
                    <button class="primary-button" type="button" @click="openCreateDialog">
                        <Plus class="button-icon" />
                        <span>新建上下文包</span>
                    </button>
                    <router-link class="secondary-button" to="/ai-center/chat">带上下文提问</router-link>
                </div>
            </div>

            <aside class="forge-console" aria-label="上下文锻造状态">
                <div class="console-topbar">
                    <span></span>
                    <span></span>
                    <span></span>
                    <strong>contextforge.run</strong>
                </div>
                <div class="console-body">
                    <div v-for="signal in forgeSignals" :key="signal.label" class="signal-row">
                        <span :class="signal.status"></span>
                        <div>
                            <strong>{{ signal.label }}</strong>
                            <small>{{ signal.detail }}</small>
                        </div>
                    </div>
                </div>
            </aside>
        </section>

        <section class="metrics-grid" aria-label="上下文资产指标">
            <article v-for="metric in workspaceMetrics" :key="metric.label" class="metric-card">
                <strong>{{ metric.value }}</strong>
                <span>{{ metric.label }}</span>
            </article>
        </section>

        <section v-if="isLoading" class="empty-panel">
            <strong>正在读取数据库中的上下文包...</strong>
            <span>这里只会展示后端返回的真实数据。</span>
        </section>

        <section v-else-if="!packs.length" class="empty-panel">
            <strong>还没有真实上下文包</strong>
            <span>新建上下文包后，可以从真实知识库文章中加入资料来源，AI 对话会按需检索相关片段。</span>
            <button class="primary-button" type="button" @click="openCreateDialog">
                <Plus class="button-icon" />
                <span>新建上下文包</span>
            </button>
        </section>

        <section v-else class="workbench">
            <aside class="type-rail">
                <span class="rail-label">包类型</span>
                <button
                    v-for="type in packTypes"
                    :key="type.value"
                    type="button"
                    class="type-button"
                    :class="{ active: selectedType === type.value }"
                    @click="selectedType = type.value"
                >
                    <span>{{ type.label }}</span>
                    <strong>{{ countByType(type.value) }}</strong>
                </button>
            </aside>

            <main class="pack-grid">
                <template v-if="filteredPacks.length">
                    <article
                        v-for="pack in filteredPacks"
                        :key="pack.id"
                        class="pack-card"
                        :class="{ active: selectedPack?.id === pack.id }"
                        @click="selectPack(pack.id)"
                    >
                        <div class="pack-card-top">
                            <span>{{ getTypeLabel(pack.type) }}</span>
                            <div class="pack-meta-pills">
                                <strong>{{ pack.stage }}</strong>
                                <em :class="getOwnershipClass(pack)">{{ getOwnershipLabel(pack) }}</em>
                            </div>
                        </div>
                        <h2>{{ pack.name }}</h2>
                        <p v-if="pack.description">{{ pack.description }}</p>
                        <div class="pack-score">
                            <span>Context Quality</span>
                            <strong>{{ pack.quality }}%</strong>
                        </div>
                        <div class="progress-line" aria-hidden="true">
                            <span :style="{ width: `${pack.quality}%` }"></span>
                        </div>
                        <div class="pack-tags" v-if="pack.tags.length">
                            <span v-for="tag in pack.tags" :key="tag">{{ tag }}</span>
                        </div>
                    </article>
                </template>
                <div v-else class="empty-panel inline-empty">
                    <strong>这个分类暂无真实上下文包</strong>
                    <span>切回“全部”或新建一个对应类型的包。</span>
                </div>
            </main>
        </section>

        <section class="detail-panel" v-if="selectedPack">
            <header class="detail-header">
                <div>
                    <span class="eyebrow">Active Pack</span>
                    <h2>{{ selectedPack.name }}</h2>
                    <div class="detail-badges">
                        <span :class="getOwnershipClass(selectedPack)">{{ getOwnershipLabel(selectedPack) }}</span>
                        <span>{{ canManageSelectedPack ? '可维护资料来源' : '只读引用' }}</span>
                    </div>
                    <p v-if="selectedPack.intent">{{ selectedPack.intent }}</p>
                </div>
                <div class="detail-actions">
                    <router-link class="secondary-button" :to="{ path: '/ai-center/chat', query: { pack: selectedPack.id } }">带此包提问</router-link>
                    <button
                        v-if="canManageSelectedPack"
                        class="secondary-button"
                        type="button"
                        :disabled="isSaving || !selectedPack.sources.length"
                        title="本地刷新分块索引，不调用 AI"
                        @click="rebuildRagIndex(selectedPack)"
                    >
                        <Refresh class="button-icon" />
                        <span>刷新知识索引</span>
                    </button>
                    <button
                        v-if="canManageSelectedPack"
                        class="secondary-button"
                        type="button"
                        :disabled="isSaving || !selectedPack.sources.length || !selectedPackRagIndex?.embedding_configured"
                        :title="selectedPackRagIndex?.embedding_configured ? '先预估调用量，再确认生成；默认只补缺失或旧模型向量' : '未配置 embedding，不会自动产生费用'"
                        @click="buildEmbeddingIndex(selectedPack)"
                    >
                        <Refresh class="button-icon" />
                        <span>补齐语义索引</span>
                    </button>
                    <button class="secondary-button" type="button" :disabled="!canExportSelectedPack" @click="copyPrompt(selectedPack)">复制提问提示词</button>
                    <button class="primary-button" type="button" :disabled="!canExportSelectedPack" @click="exportPack(selectedPack)">
                        <Download class="button-icon" />
                        <span>导出 Markdown</span>
                    </button>
                </div>
            </header>

            <div class="detail-metrics">
                <div>
                    <span>资料数量</span>
                    <strong>{{ selectedPack.sources.length }}</strong>
                </div>
                <div>
                    <span>Token 预算</span>
                    <strong>{{ selectedPack.tokenBudget }}</strong>
                </div>
                <div>
                    <span>新鲜度</span>
                    <strong>{{ selectedPack.freshness }}</strong>
                </div>
                <div>
                    <span>RAG 索引</span>
                    <strong>{{ selectedPackRagIndexLabel }}</strong>
                </div>
                <div>
                    <span>语义向量</span>
                    <strong>{{ selectedPackEmbeddingLabel }}</strong>
                </div>
            </div>

            <div class="detail-layout" v-if="hasPackInsights">
                <article class="insight-panel" v-if="selectedPack.summary">
                    <h3>AI 洞察摘要</h3>
                    <p>{{ selectedPack.summary }}</p>
                </article>
                <article class="insight-panel" v-if="selectedPack.keyPoints.length">
                    <h3>关键线索</h3>
                    <ul>
                        <li v-for="point in selectedPack.keyPoints" :key="point">{{ point }}</li>
                    </ul>
                </article>
                <article class="insight-panel" v-if="selectedPack.nextAction">
                    <h3>下一步动作</h3>
                    <p>{{ selectedPack.nextAction }}</p>
                </article>
            </div>

            <div class="rag-preview-panel" v-if="selectedPack.sources.length">
                <div class="rag-preview-head">
                    <div>
                        <h3>RAG 检索预览</h3>
                        <p>{{ semanticPreviewDescription }}</p>
                    </div>
                    <label class="semantic-toggle" :class="{ 'is-disabled': !canUseSemanticPreview }" :title="semanticPreviewHint">
                        <input v-model="retrievalPreviewAllowEmbedding" type="checkbox" :disabled="!canUseSemanticPreview" />
                        <span>{{ canUseSemanticPreview ? '允许语义预览' : '语义预览不可用' }}</span>
                        <small>{{ semanticPreviewHint }}</small>
                    </label>
                </div>

                <div class="rag-preview-controls">
                    <el-input
                        v-model="retrievalPreviewQuery"
                        placeholder="输入一个问题，查看会命中哪些上下文片段"
                        @keyup.enter="previewRetrieval(selectedPack)"
                    />
                    <button
                        class="secondary-button"
                        type="button"
                        :disabled="retrievalPreviewLoading"
                        @click="previewRetrieval(selectedPack)"
                    >
                        {{ retrievalPreviewLoading ? '检索中...' : '预览命中' }}
                    </button>
                </div>

                <div v-if="selectedPackRetrievalPreview?.retrieval" class="rag-preview-result">
                    <div class="rag-preview-meta">
                        <span>{{ getRetrievalModeLabel(selectedPackRetrievalPreview.retrieval) }}</span>
                        <span>命中 {{ selectedPackRetrievalPreview.retrieval.snippets.length }} 段</span>
                        <span>约 {{ selectedPackRetrievalPreview.retrieval.used_tokens_estimate }} tokens</span>
                        <span>{{ selectedPackRetrievalPreview.retrieval.embedding_used ? '已调用 embedding' : '未调用 embedding' }}</span>
                        <span v-if="selectedPackRetrievalPreview.retrieval.semantic_requested && selectedPackRetrievalPreview.retrieval.mode !== 'semantic'">
                            回退原因：{{ getSemanticReasonLabel(selectedPackRetrievalPreview.retrieval.semantic_unavailable_reason) }}
                        </span>
                    </div>

                    <div v-if="selectedPackRetrievalPreview.retrieval.snippets.length" class="rag-preview-list">
                        <article v-for="snippet in selectedPackRetrievalPreview.retrieval.snippets" :key="snippet.id" class="rag-snippet">
                            <div>
                                <strong>{{ snippet.id }} {{ snippet.title }}</strong>
                                <small>相关度 {{ snippet.score }} · {{ snippet.tokens_estimate }} tokens</small>
                            </div>
                            <p>{{ snippet.content_preview || '无预览内容' }}</p>
                        </article>
                    </div>
                    <p v-else class="source-empty compact">没有命中明显相关的片段，可以换一个问法或补充资料。</p>
                </div>
            </div>

            <div class="source-actions" v-if="canManageSelectedPack && articleOptions.length">
                <el-select
                    v-model="detailArticleIds"
                    class="source-select"
                    multiple
                    filterable
                    collapse-tags
                    placeholder="从知识库选择文章加入当前上下文包"
                >
                    <el-option
                        v-for="article in articleOptions"
                        :key="article.id"
                        :label="article.title"
                        :value="article.id"
                    />
                </el-select>
                <button class="secondary-button" type="button" :disabled="!detailArticleIds.length || isSaving" @click="addSelectedArticles(selectedPack)">
                    加入选中文章
                </button>
            </div>
            <p v-else-if="!canManageSelectedPack" class="source-empty">这个上下文包可以用于 AI 提问、复制提示词和导出 Markdown，但只有创建者或管理员可以添加或移除资料来源。</p>
            <p v-else-if="!isArticleLoading" class="source-empty">知识库暂无真实文章可加入。请先新建文档。</p>

            <div v-if="selectedPack.sources.length" class="source-table" aria-label="上下文来源">
                <div class="source-table-head">
                    <span>来源</span>
                    <span>类型</span>
                    <span>权重</span>
                    <span>状态</span>
                    <span>操作</span>
                </div>
                <div v-for="source in selectedPack.sources" :key="source.id || source.title" class="source-row">
                    <span>{{ source.title }}</span>
                    <span>{{ source.type }}</span>
                    <span>{{ source.weight }}</span>
                    <span>{{ source.status }}</span>
                    <button
                        class="text-action danger"
                        type="button"
                        :disabled="!source.id || isSaving || !canManageSelectedPack"
                        @click.stop="removeSource(selectedPack, source)"
                    >
                        移除
                    </button>
                </div>
            </div>
            <p v-else class="source-empty">这个上下文包还没有真实资料来源。</p>
        </section>

        <section class="pipeline-panel" v-if="selectedPack?.sources.length">
            <div>
                <span class="eyebrow">Autonomous Pipeline</span>
                <h2>从收集到复用，系统按 AI 工作流组织材料。</h2>
            </div>
            <div class="pipeline-grid">
                <article v-for="step in pipeline" :key="step.title" class="pipeline-step">
                    <span>{{ step.index }}</span>
                    <h3>{{ step.title }}</h3>
                    <p>{{ step.description }}</p>
                </article>
            </div>
        </section>

        <el-dialog v-model="createDialogVisible" width="560px" custom-class="pack-dialog">
            <template #header>
                <div class="dialog-heading">
                    <span class="eyebrow">New Pack</span>
                    <h2>新建上下文包</h2>
                </div>
            </template>
            <div class="dialog-body">
                <label class="field-label">名称</label>
                <el-input v-model="draftPack.name" placeholder="例如：答辩材料上下文包" />

                <label class="field-label">类型</label>
                <el-select v-model="draftPack.type" class="full-input">
                    <el-option v-for="type in creatableTypes" :key="type.value" :label="type.label" :value="type.value" />
                </el-select>

                <label class="field-label">目标</label>
                <el-input v-model="draftPack.intent" placeholder="这个上下文包准备用来解决什么问题？" />

                <label class="field-label">描述</label>
                <el-input v-model="draftPack.description" type="textarea" :rows="3" placeholder="简单描述这个包里会放哪些材料" />

                <label class="field-label">标签</label>
                <el-input v-model="draftPack.tags" placeholder="用逗号分隔，例如：部署,答辩,AI" />

                <label class="field-label" v-if="articleOptions.length">接入知识库文章</label>
                <el-select v-if="articleOptions.length" v-model="selectedArticleIds" class="full-input" multiple filterable collapse-tags placeholder="选择文章加入这个上下文包">
                    <el-option
                        v-for="article in articleOptions"
                        :key="article.id"
                        :label="article.title"
                        :value="article.id"
                    />
                </el-select>
                <p v-else class="source-empty compact">知识库暂无真实文章，创建后可以再加入。</p>
            </div>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="createDialogVisible = false">取消</el-button>
                    <el-button type="primary" :loading="isSaving" @click="createPack">创建</el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { Download, Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { aiOpsService } from '@/api/modules/ai'
import type { AIRetrievalMeta, AIRetrievalPreview } from '@/api/modules/ai/interface'
import articleApi from '@/api/modules/article'
import type { IArticle } from '@/api/modules/article/interface'
import contextPackApi, { type ContextPack, type ContextPackRagIndex, type ContextPackStats } from '@/api/modules/contextPacks'
import { useElMessage } from '@/hooks/useMessage'
import { useGlobalStore } from '@/store'

const { message } = useElMessage()
const globalStore = useGlobalStore()

const packTypes = [
    { value: 'all', label: '全部' },
    { value: 'project', label: '项目' },
    { value: 'deploy', label: '部署' },
    { value: 'research', label: '研究' },
    { value: 'learning', label: '学习' },
    { value: 'writing', label: '写作' }
]

const creatableTypes = packTypes.filter(type => type.value !== 'all')
const selectedType = ref('all')
const selectedPackId = ref<number | null>(null)
const createDialogVisible = ref(false)
const isLoading = ref(false)
const isArticleLoading = ref(false)
const isSaving = ref(false)
const packs = ref<ContextPack[]>([])
const articleOptions = ref<IArticle[]>([])
const workspaceStats = ref<ContextPackStats | null>(null)
const selectedArticleIds = ref<number[]>([])
const detailArticleIds = ref<number[]>([])
const ragIndexStats = ref<Record<number, ContextPackRagIndex>>({})
const ragIndexLoadingPackId = ref<number | null>(null)
const retrievalPreviewQuery = ref('')
const retrievalPreviewAllowEmbedding = ref(false)
const retrievalPreviewLoading = ref(false)
const retrievalPreview = ref<AIRetrievalPreview | null>(null)
const retrievalPreviewPackId = ref<number | null>(null)

const draftPack = reactive({
    name: '',
    type: 'project',
    intent: '',
    description: '',
    tags: ''
})

const filteredPacks = computed(() => {
    if (selectedType.value === 'all') return packs.value
    return packs.value.filter(pack => pack.type === selectedType.value)
})

const selectedPack = computed(() => {
    return packs.value.find(pack => pack.id === selectedPackId.value) || filteredPacks.value[0] || null
})

const hasPackInsights = computed(() => {
    const pack = selectedPack.value
    return Boolean(pack?.summary || pack?.keyPoints.length || pack?.nextAction)
})

const currentUser = computed(() => globalStore.userInfo)

const isLoggedIn = computed(() => Boolean(globalStore.token && currentUser.value?.id))

const isAdminUser = computed(() => {
    const user = currentUser.value
    return Boolean(user?.role === 'admin' || user?.permissions?.some(permission => ['user:manage', 'context_pack:manage'].includes(permission)))
})

const canManageSelectedPack = computed(() => {
    return Boolean(selectedPack.value && canManagePack(selectedPack.value))
})

const canExportSelectedPack = computed(() => {
    const pack = selectedPack.value
    return Boolean(pack && (pack.sources.length || pack.intent || pack.summary || pack.keyPoints.length))
})

const selectedPackRagIndex = computed(() => {
    const pack = selectedPack.value
    return pack ? ragIndexStats.value[pack.id] : null
})

const selectedPackRetrievalPreview = computed(() => {
    const pack = selectedPack.value
    if (!pack || retrievalPreviewPackId.value !== pack.id) return null
    return retrievalPreview.value
})

const canUseSemanticPreview = computed(() => {
    const stats = selectedPackRagIndex.value
    return Boolean(stats?.embedding_configured && (stats.current_model_embedded_chunks ?? 0) > 0)
})

const semanticPreviewHint = computed(() => {
    const stats = selectedPackRagIndex.value
    if (!selectedPack.value) return '先选择上下文包'
    if (!stats) return '正在读取索引状态'
    if (!stats.embedding_configured) return '未配置向量模型，预览会使用关键词检索'
    if (!stats.chunks) return '请先刷新知识索引'
    if (!(stats.current_model_embedded_chunks ?? 0)) return '还没有当前模型的向量块，请先补齐语义索引'
    return `将使用 ${stats.embedding_model || '当前模型'} 生成一次查询向量`
})

const semanticPreviewDescription = computed(() => {
    if (canUseSemanticPreview.value) {
        return '默认使用关键词索引；勾选语义预览时，会调用一次 embedding 生成查询向量。'
    }
    return '当前仅可使用关键词索引；配置并补齐向量后才会启用语义预览。'
})

const selectedPackRagIndexLabel = computed(() => {
    const pack = selectedPack.value
    if (!pack) return '待选择'
    if (!pack.sources.length) return '待补充'
    const stats = selectedPackRagIndex.value
    if (ragIndexLoadingPackId.value === pack.id && !stats) return '读取中'
    if (!stats) return '未读取'

    const pendingSources = stats.pending_sources ?? Math.max((stats.sources || 0) - (stats.indexed_sources || 0), 0)
    if (pendingSources > 0) return `${stats.chunks} 块 · ${pendingSources} 待刷新`
    if (stats.stale_embedding_chunks) return `${stats.chunks} 块 · ${stats.stale_embedding_chunks} 旧向量`
    if (stats.embedded_chunks) return `${stats.chunks} 块 · ${stats.embedded_chunks} 向量`
    if (stats.embedding_configured) return `${stats.chunks} 块 · 待语义`
    return stats.chunks ? `${stats.chunks} 块 · 关键词` : '待刷新'
})

const selectedPackEmbeddingLabel = computed(() => {
    const pack = selectedPack.value
    if (!pack) return '待选择'
    if (!pack.sources.length) return '待补充'
    const stats = selectedPackRagIndex.value
    if (!stats) return '未读取'
    if (!stats.embedding_configured) return '未启用'
    if (!stats.chunks) return '待刷新'
    if (stats.stale_embedding_chunks) return `${stats.current_model_embedded_chunks ?? 0}/${stats.chunks} · 需更新`
    if (typeof stats.current_model_embedded_chunks === 'number') return `${stats.current_model_embedded_chunks}/${stats.chunks}`
    if (stats.embedded_chunks) return `${stats.embedded_chunks}/${stats.chunks}`
    return '待生成'
})

const semanticReasonLabels: Record<string, string> = {
    semantic_not_requested: '未请求语义检索',
    empty_query: '问题为空',
    embedding_not_configured: '未配置向量模型',
    no_current_model_embeddings: '当前包没有当前模型生成的向量块',
    query_embedding_not_created: '查询向量未生成',
    query_embedding_failed: '查询向量生成失败',
    embedding_dimension_mismatch: '查询向量和索引向量维度不一致',
    embedding_validation_failed: '向量校验失败'
}

function getSemanticReasonLabel(reason?: string) {
    if (!reason) return '未满足语义检索条件'
    return semanticReasonLabels[reason] || reason
}

function getRetrievalModeLabel(retrieval: AIRetrievalMeta | null) {
    if (!retrieval) return '未检索'
    if (retrieval.mode === 'semantic') return '语义检索'
    if (retrieval.semantic_requested && retrieval.semantic_unavailable_reason) {
        return '关键词检索（语义已回退）'
    }
    return '关键词检索'
}

const workspaceMetrics = computed(() => {
    const packCount = packs.value.length
    const sourceCount = packs.value.reduce((total, pack) => total + pack.sources.length, 0)
    const avgQuality = packCount
        ? `${Math.round(packs.value.reduce((total, pack) => total + pack.quality, 0) / packCount)}%`
        : '0%'

    return [
        { value: packCount, label: '上下文包' },
        { value: sourceCount, label: '资料来源' },
        { value: avgQuality, label: '平均质量' }
    ]
})

const forgeSignals = computed(() => [
    {
        label: 'Database',
        detail: isLoading.value ? '正在读取真实数据' : `已加载 ${workspaceStats.value?.packs ?? packs.value.length} 个真实上下文包`,
        status: isLoading.value ? 'warm' : 'ok'
    },
    {
        label: 'Knowledge base',
        detail: isArticleLoading.value ? '正在读取知识库文章' : `${workspaceStats.value?.articles ?? articleOptions.value.length} 篇真实文章可作为来源`,
        status: articleOptions.value.length ? 'ok' : 'warm'
    },
    {
        label: 'Sources',
        detail: `${workspaceStats.value?.sources ?? workspaceMetrics.value[1].value} 条真实资料来源已接入`,
        status: (workspaceStats.value?.sources ?? 0) > 0 ? 'ok' : 'warm'
    }
])

const pipeline = [
    { index: '01', title: '收集材料', description: '把文档、错误日志、截图、代码文件和 AI 对话归到同一条上下文线索。' },
    { index: '02', title: '锻造结构', description: '为每份材料标记来源、权重、状态、用途和与目标之间的关系。' },
    { index: '03', title: '压缩语义', description: '生成摘要、关键线索、风险点和下一步动作，降低 AI 问答时的噪音。' },
    { index: '04', title: '复用交付', description: '导出 Markdown、复制提示词，或进入 AI 工作台继续生成内容。' }
]

async function loadPacks() {
    isLoading.value = true
    try {
        packs.value = await contextPackApi.getList()
        workspaceStats.value = await contextPackApi.getStats()
        if (!selectedPackId.value && packs.value.length) {
            selectedPackId.value = packs.value[0].id
        }
        if (selectedPackId.value && !packs.value.some(pack => pack.id === selectedPackId.value)) {
            selectedPackId.value = packs.value[0]?.id ?? null
        }
        const activePack = packs.value.find(pack => pack.id === selectedPackId.value)
        if (activePack) {
            void loadRagIndexForPack(activePack, { silent: true })
        }
    } catch (error) {
        console.error('Load context packs failed:', error)
        packs.value = []
        workspaceStats.value = null
        message.error('上下文包加载失败')
    } finally {
        isLoading.value = false
    }
}

async function loadArticles() {
    isArticleLoading.value = true
    try {
        const articles = await articleApi.getList()
        articleOptions.value = Array.isArray(articles) ? articles.slice(0, 80) : []
    } catch (error) {
        console.error('Load article options failed:', error)
        articleOptions.value = []
    } finally {
        isArticleLoading.value = false
    }
}

async function loadRagIndexForPack(pack: ContextPack, options: { force?: boolean; silent?: boolean } = {}) {
    if (!pack.sources.length) {
        ragIndexStats.value = {
            ...ragIndexStats.value,
            [pack.id]: {
                sources: 0,
                indexed_sources: 0,
                chunks: 0,
                tokens_estimate: 0,
                pending_sources: 0,
                latest_updated_at: ''
            }
        }
        return
    }

    if (!options.force && ragIndexStats.value[pack.id]) return

    ragIndexLoadingPackId.value = pack.id
    try {
        const index = await contextPackApi.getRagIndex(pack.id)
        ragIndexStats.value = {
            ...ragIndexStats.value,
            [pack.id]: index
        }
    } catch (error) {
        console.error('Load RAG index status failed:', error)
        if (!options.silent) {
            message.error('RAG 索引状态读取失败')
        }
    } finally {
        if (ragIndexLoadingPackId.value === pack.id) {
            ragIndexLoadingPackId.value = null
        }
    }
}

function countByType(type: string) {
    if (type === 'all') return packs.value.length
    return packs.value.filter(pack => pack.type === type).length
}

function getTypeLabel(value: string) {
    return packTypes.find(type => type.value === value)?.label || value
}

function canManagePack(pack: ContextPack) {
    if (typeof pack.canManage === 'boolean') return pack.canManage
    if (!isLoggedIn.value) return false
    if (isAdminUser.value) return true
    return pack.user_id !== null && pack.user_id !== undefined && Number(pack.user_id) === Number(currentUser.value?.id)
}

function getOwnershipLabel(pack: ContextPack) {
    if (canManagePack(pack)) return pack.user_id ? '我的包' : '系统包'
    if (pack.user_id === null || pack.visibility === 'public') return '公共只读'
    return '只读'
}

function getOwnershipClass(pack: ContextPack) {
    return {
        'ownership-badge': true,
        mine: canManagePack(pack) && Boolean(pack.user_id),
        system: canManagePack(pack) && !pack.user_id,
        readonly: !canManagePack(pack)
    }
}

function selectPack(id: number) {
    selectedPackId.value = id
    detailArticleIds.value = []
    retrievalPreview.value = null
    retrievalPreviewPackId.value = null
}

async function previewRetrieval(pack: ContextPack) {
    const query = retrievalPreviewQuery.value.trim()
    if (!query) {
        message.warning('请输入要预览的问题')
        return
    }

    if (!pack.sources.length) {
        message.warning('请先加入资料来源')
        return
    }

    retrievalPreviewLoading.value = true
    try {
        const allowSemantic = retrievalPreviewAllowEmbedding.value && canUseSemanticPreview.value
        if (retrievalPreviewAllowEmbedding.value && !allowSemantic) {
            message.info(semanticPreviewHint.value)
        }

        const result = await aiOpsService.previewContextPackRetrieval(pack.id, {
            query,
            context_token_budget: 2600,
            allow_embedding: allowSemantic
        })
        retrievalPreview.value = result
        retrievalPreviewPackId.value = pack.id
        const modeLabel = getRetrievalModeLabel(result.retrieval)
        const hitCount = result.retrieval?.snippets.length ?? 0
        if (result.retrieval?.semantic_requested && result.retrieval.mode !== 'semantic') {
            message.info(`${modeLabel}完成，命中 ${hitCount} 段；${getSemanticReasonLabel(result.retrieval.semantic_unavailable_reason)}`)
        } else {
            message.success(`${modeLabel}预览完成，命中 ${hitCount} 段`)
        }
    } catch (error: any) {
        console.error('Preview RAG retrieval failed:', error)
        message.error(error?.msg || error?.response?.data?.msg || 'RAG 检索预览失败')
    } finally {
        retrievalPreviewLoading.value = false
    }
}

function openCreateDialog() {
    if (!isLoggedIn.value) {
        message.warning('请先登录后再创建上下文包')
        return
    }

    draftPack.name = ''
    draftPack.type = 'project'
    draftPack.intent = ''
    draftPack.description = ''
    draftPack.tags = ''
    selectedArticleIds.value = []
    createDialogVisible.value = true
}

async function createPack() {
    if (!draftPack.name.trim()) {
        message.warning('请填写上下文包名称')
        return
    }

    const tags = draftPack.tags
        .split(/[,，]/)
        .map(tag => tag.trim())
        .filter(Boolean)

    isSaving.value = true
    try {
        const pack = await contextPackApi.create({
            name: draftPack.name.trim(),
            type: draftPack.type,
            description: draftPack.description.trim(),
            intent: draftPack.intent.trim(),
            tags,
            article_ids: selectedArticleIds.value.map(Number).filter(Number.isFinite)
        })

        packs.value.unshift(pack)
        workspaceStats.value = await contextPackApi.getStats()
        selectedPackId.value = pack.id
        selectedType.value = 'all'
        await loadRagIndexForPack(pack, { force: true, silent: true })
        createDialogVisible.value = false
        message.success('上下文包已创建并保存到数据库')
    } catch (error) {
        console.error('Create context pack failed:', error)
        message.error('创建上下文包失败')
    } finally {
        isSaving.value = false
    }
}

async function addSelectedArticles(pack: ContextPack) {
    if (!detailArticleIds.value.length) return
    if (!canManagePack(pack)) {
        message.warning('只有创建者或管理员可以维护这个上下文包')
        return
    }

    isSaving.value = true
    try {
        const articleIds = detailArticleIds.value.map(Number).filter(Number.isFinite)
        const payload = { article_ids: articleIds }
        let updatedPack: ContextPack
        try {
            updatedPack = await contextPackApi.addSources(pack.id, payload)
        } catch (error: any) {
            if (error?.response?.status !== 404) throw error
            updatedPack = await contextPackApi.addSourcesCompat(pack.id, payload)
        }
        replacePack(updatedPack)
        workspaceStats.value = await contextPackApi.getStats()
        await loadRagIndexForPack(updatedPack, { force: true, silent: true })
        detailArticleIds.value = []
        message.success('知识库文章已加入上下文包')
    } catch (error: any) {
        console.error('Add sources failed:', error)
        message.error(error?.msg || error?.response?.data?.msg || '加入资料失败')
    } finally {
        isSaving.value = false
    }
}

function replacePack(pack: ContextPack) {
    const index = packs.value.findIndex(item => item.id === pack.id)
    if (index >= 0) {
        packs.value.splice(index, 1, pack)
    } else {
        packs.value.unshift(pack)
    }
    selectedPackId.value = pack.id
}

function writeTextToClipboard(text: string) {
    if (navigator.clipboard?.writeText) {
        return navigator.clipboard.writeText(text)
    }

    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.setAttribute('readonly', 'true')
    textarea.style.position = 'fixed'
    textarea.style.left = '-9999px'
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    return Promise.resolve()
}

function sanitizeFilename(name: string) {
    return name
        .trim()
        .replace(/[\\/:*?"<>|]/g, '-')
        .replace(/\s+/g, '-')
        .slice(0, 80) || 'context-pack'
}

function downloadTextFile(filename: string, content: string, mime = 'text/markdown;charset=utf-8') {
    const blob = new Blob([content], { type: mime })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = filename
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
}

async function exportPack(pack: ContextPack) {
    try {
        const data = await contextPackApi.exportMarkdown(pack.id)
        downloadTextFile(`${sanitizeFilename(pack.name)}.md`, data.markdown)
        message.success('Markdown 文件已导出')
    } catch (error) {
        console.error('Export markdown failed:', error)
        message.error('导出失败')
    }
}

async function copyPrompt(pack: ContextPack) {
    try {
        const data = await contextPackApi.exportMarkdown(pack.id)
        await writeTextToClipboard(data.prompt)
        message.success('提问提示词已复制')
    } catch (error) {
        console.error('Copy prompt failed:', error)
        message.error('复制提示词失败')
    }
}

async function rebuildRagIndex(pack: ContextPack) {
    if (!canManagePack(pack)) {
        message.warning('只有创建者或管理员可以刷新知识索引')
        return
    }

    if (!pack.sources.length) {
        message.warning('请先加入资料来源后再刷新知识索引')
        return
    }

    isSaving.value = true
    try {
        const result = await contextPackApi.rebuildRagIndex(pack.id)
        replacePack(result.pack)
        ragIndexStats.value = {
            ...ragIndexStats.value,
            [pack.id]: result.index
        }
        message.success(`知识索引已刷新：${result.index.sources} 份资料，${result.index.chunks} 个片段`)
    } catch (error: any) {
        console.error('Rebuild RAG index failed:', error)
        message.error(error?.msg || error?.response?.data?.msg || '刷新知识索引失败')
    } finally {
        isSaving.value = false
    }
}

async function buildEmbeddingIndex(pack: ContextPack) {
    if (!canManagePack(pack)) {
        message.warning('只有创建者或管理员可以生成语义索引')
        return
    }

    if (!pack.sources.length) {
        message.warning('请先加入资料来源后再生成语义索引')
        return
    }

    if (!selectedPackRagIndex.value?.embedding_configured) {
        message.warning('Embedding 未配置，当前不会调用付费接口')
        return
    }

    isSaving.value = true
    try {
        const previewResult = await contextPackApi.buildEmbeddings(pack.id, { dry_run: true })
        replacePack(previewResult.pack)
        ragIndexStats.value = {
            ...ragIndexStats.value,
            [pack.id]: previewResult.index
        }

        const planned = previewResult.index.planned_embeddings
            ?? previewResult.index.embedding_target_chunks
            ?? previewResult.index.pending_embedding_chunks
            ?? 0
        const plannedTokens = previewResult.index.planned_embedding_tokens_estimate
            ?? previewResult.index.embedding_target_tokens_estimate
            ?? previewResult.index.pending_embedding_tokens_estimate
            ?? 0
        const skipped = previewResult.index.skipped_embeddings
            ?? previewResult.index.embedding_skip_current_model_chunks
            ?? 0
        const stale = previewResult.index.stale_embedding_chunks ?? 0

        if (!planned) {
            message.success(`语义索引已是最新：${skipped} 个片段已匹配当前模型`)
            return
        }

        await ElMessageBox.confirm(
            `本次将调用 embedding 接口 ${planned} 次，预计处理约 ${plannedTokens} tokens。已匹配当前模型的 ${skipped} 个片段会跳过${stale ? `，另有 ${stale} 个旧模型向量会更新` : ''}。`,
            '确认补齐语义索引',
            {
                confirmButtonText: '确认生成',
                cancelButtonText: '取消',
                type: 'warning'
            }
        )

        const result = await contextPackApi.buildEmbeddings(pack.id, { force: false })
        replacePack(result.pack)
        ragIndexStats.value = {
            ...ragIndexStats.value,
            [pack.id]: result.index
        }
        message.success(`语义索引已补齐：生成 ${result.index.generated_embeddings ?? 0} 个，跳过 ${result.index.skipped_embeddings ?? 0} 个`)
    } catch (error: any) {
        if (error === 'cancel' || error === 'close') {
            message.info('已取消生成语义索引')
            return
        }
        console.error('Build embedding index failed:', error)
        message.error(error?.msg || error?.response?.data?.msg || '生成语义索引失败')
    } finally {
        isSaving.value = false
    }
}

async function removeSource(pack: ContextPack, source: ContextPack['sources'][number]) {
    if (!source.id) return
    if (!canManagePack(pack)) {
        message.warning('只有创建者或管理员可以移除资料来源')
        return
    }

    isSaving.value = true
    try {
        const updatedPack = await contextPackApi.deleteSource(pack.id, source.id)
        replacePack(updatedPack)
        workspaceStats.value = await contextPackApi.getStats()
        await loadRagIndexForPack(updatedPack, { force: true, silent: true })
        message.success('资料来源已移除')
    } catch (error: any) {
        console.error('Remove source failed:', error)
        message.error(error?.msg || error?.response?.data?.msg || '移除资料失败')
    } finally {
        isSaving.value = false
    }
}

watch(
    selectedPack,
    pack => {
        if (pack) {
            void loadRagIndexForPack(pack, { silent: true })
        }
    },
    { immediate: false }
)

watch(
    canUseSemanticPreview,
    canUse => {
        if (!canUse) retrievalPreviewAllowEmbedding.value = false
    },
    { immediate: true }
)

onMounted(() => {
    loadPacks()
    loadArticles()
})
</script>

<style scoped>
.packs-page {
    width: var(--page-width);
    min-height: calc(100vh - 160px);
    margin: 0 auto;
    padding: 64px 0 80px;
    color: var(--text-primary);
}

.packs-hero {
    min-height: 520px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(340px, 460px);
    align-items: center;
    gap: 48px;
}

.eyebrow,
.field-label,
.rail-label,
.pack-card-top,
.pack-score,
.source-table,
.pipeline-step > span {
    font-family: var(--font-mono);
}

.eyebrow,
.field-label {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 9999px;
    background: var(--badge-bg);
    color: var(--badge-fg);
    font-size: 12px;
    font-weight: 700;
}

.field-label {
    margin: 14px 0 8px;
    padding: 0;
    background: transparent;
    color: var(--text-muted);
    text-transform: uppercase;
}

.packs-hero h1 {
    max-width: 900px;
    margin: 18px 0 18px;
    font-size: clamp(42px, 6.4vw, 74px);
    font-weight: 700;
    line-height: 1.02;
}

.packs-hero p {
    max-width: 720px;
    margin: 0;
    color: var(--text-secondary);
    font-size: 18px;
    line-height: 1.75;
}

.hero-actions,
.detail-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.hero-actions {
    margin-top: 30px;
}

.primary-button,
.secondary-button,
.type-button {
    min-height: 40px;
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
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}

.primary-button {
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.primary-button:hover,
.secondary-button:hover,
.type-button:hover {
    transform: translateY(-1px);
}

.primary-button:disabled,
.secondary-button:disabled {
    cursor: not-allowed;
    opacity: 0.55;
    transform: none;
}

.secondary-button,
.type-button {
    color: var(--text-primary);
    background: var(--surface);
    box-shadow: var(--ring);
}

.button-icon {
    width: 16px;
    height: 16px;
}

.forge-console,
.metric-card,
.type-rail,
.pack-card,
.detail-panel,
.pipeline-panel {
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.forge-console {
    overflow: hidden;
}

.console-topbar {
    min-height: 42px;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 14px;
    border-bottom: 1px solid var(--line);
}

.console-topbar span {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--line);
}

.console-topbar strong {
    margin-left: auto;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
}

.console-body {
    padding: 22px;
    display: grid;
    gap: 14px;
}

.signal-row {
    display: grid;
    grid-template-columns: 10px minmax(0, 1fr);
    gap: 12px;
}

.signal-row > span {
    width: 8px;
    height: 8px;
    margin-top: 7px;
    border-radius: 50%;
    background: #f59e0b;
}

.signal-row > span.ok {
    background: #0c7a43;
}

.signal-row strong,
.signal-row small {
    display: block;
}

.signal-row small {
    margin-top: 4px;
    color: var(--text-secondary);
    line-height: 1.5;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}

.metric-card {
    min-height: 120px;
    padding: 22px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.metric-card strong {
    font-size: 38px;
    line-height: 1;
}

.metric-card span {
    color: var(--text-secondary);
}

.empty-panel {
    min-height: 220px;
    display: grid;
    place-items: center;
    align-content: center;
    gap: 12px;
    padding: 28px;
    border-radius: 8px;
    text-align: center;
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.empty-panel strong {
    font-size: 24px;
}

.empty-panel span,
.source-empty {
    color: var(--text-secondary);
    line-height: 1.7;
}

.inline-empty {
    grid-column: 1 / -1;
}

.workbench {
    display: grid;
    grid-template-columns: 220px minmax(0, 1fr);
    gap: 12px;
}

.type-rail {
    align-self: start;
    position: sticky;
    top: 104px;
    padding: 16px;
}

.rail-label {
    display: block;
    margin-bottom: 12px;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.type-button {
    width: 100%;
    justify-content: space-between;
    margin-bottom: 8px;
}

.type-button.active {
    color: var(--button-fg);
    background: var(--button-bg);
}

.pack-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.pack-card {
    min-height: 280px;
    padding: 22px;
    cursor: pointer;
    transition: transform 180ms ease, box-shadow 180ms ease;
}

.pack-card:hover,
.pack-card.active {
    transform: translateY(-2px);
    box-shadow: var(--card-shadow), 0 12px 28px rgba(0, 0, 0, 0.08);
}

.pack-card-top,
.pack-score {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 700;
}

.pack-meta-pills,
.detail-badges {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}

.pack-card-top strong {
    color: var(--accent-blue);
}

.ownership-badge,
.detail-badges span {
    min-height: 24px;
    display: inline-flex;
    align-items: center;
    border-radius: 9999px;
    padding: 0 8px;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    box-shadow: var(--ring);
    font-style: normal;
    font-size: 12px;
    font-weight: 700;
}

.ownership-badge.mine {
    color: #0c7a43;
    background: rgba(12, 122, 67, 0.1);
}

.ownership-badge.system {
    color: var(--accent-blue);
    background: rgba(37, 99, 235, 0.1);
}

.ownership-badge.readonly {
    color: var(--text-muted);
}

.detail-badges {
    margin: -2px 0 12px;
}

.pack-card h2 {
    margin: 22px 0 10px;
    font-size: 25px;
    line-height: 1.2;
}

.pack-card p {
    margin: 0;
    color: var(--text-secondary);
    line-height: 1.7;
}

.pack-score {
    margin-top: 24px;
}

.pack-score strong {
    color: var(--text-primary);
    font-size: 18px;
}

.progress-line {
    height: 7px;
    margin-top: 10px;
    overflow: hidden;
    border-radius: 9999px;
    background: var(--surface-subtle);
}

.progress-line span {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-green), var(--accent-coral));
}

.pack-tags {
    margin-top: 18px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.pack-tags span {
    min-height: 26px;
    display: inline-flex;
    align-items: center;
    padding: 0 9px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 700;
}

.detail-panel,
.pipeline-panel {
    margin-top: 56px;
    padding: 28px;
}

.detail-header {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: end;
    gap: 24px;
}

.detail-header h2,
.pipeline-panel h2,
.dialog-heading h2 {
    margin: 14px 0 10px;
    font-size: clamp(30px, 5vw, 48px);
    line-height: 1.06;
}

.detail-header p {
    max-width: 760px;
    margin: 0;
    color: var(--text-secondary);
    line-height: 1.7;
}

.detail-metrics {
    margin-top: 22px;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
}

.detail-metrics div {
    min-height: 86px;
    padding: 16px;
    border-radius: 8px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.detail-metrics span,
.detail-metrics strong {
    display: block;
}

.detail-metrics span {
    color: var(--text-muted);
    font-size: 13px;
}

.detail-metrics strong {
    margin-top: 10px;
    font-size: 28px;
}

.detail-layout,
.pipeline-grid {
    margin-top: 12px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.insight-panel,
.pipeline-step {
    padding: 18px;
    border-radius: 8px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.insight-panel h3,
.pipeline-step h3 {
    margin: 0 0 10px;
    font-size: 17px;
}

.insight-panel p,
.insight-panel li,
.pipeline-step p {
    color: var(--text-secondary);
    line-height: 1.7;
}

.insight-panel ul {
    margin: 0;
    padding-left: 18px;
}

.source-table {
    margin-top: 12px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: var(--ring);
}

.rag-preview-panel {
    margin-top: 12px;
    padding: 16px;
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--ring);
}

.rag-preview-head,
.rag-preview-controls,
.rag-preview-meta,
.rag-snippet {
    display: flex;
    gap: 12px;
    align-items: center;
}

.rag-preview-head {
    justify-content: space-between;
}

.rag-preview-head h3 {
    margin: 0;
    font-size: 17px;
}

.rag-preview-head p {
    margin: 6px 0 0;
    color: var(--text-secondary);
    line-height: 1.6;
}

.semantic-toggle {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    flex: 0 0 auto;
    column-gap: 8px;
    row-gap: 2px;
    align-items: center;
    color: var(--text-secondary);
    font-weight: 700;
    cursor: pointer;
}

.semantic-toggle.is-disabled {
    cursor: not-allowed;
    opacity: 0.72;
}

.semantic-toggle input {
    width: 16px;
    height: 16px;
    accent-color: var(--primary);
}

.semantic-toggle input:disabled {
    cursor: not-allowed;
}

.semantic-toggle small {
    grid-column: 2;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 500;
    line-height: 1.35;
}

.rag-preview-controls {
    margin-top: 14px;
    align-items: stretch;
}

.rag-preview-controls .el-input {
    min-width: 0;
}

.rag-preview-result {
    margin-top: 14px;
}

.rag-preview-meta {
    flex-wrap: wrap;
    gap: 8px;
}

.rag-preview-meta span {
    padding: 5px 9px;
    border-radius: 999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    font-size: 12px;
    font-weight: 700;
}

.rag-preview-list {
    margin-top: 10px;
    display: grid;
    gap: 10px;
}

.rag-snippet {
    justify-content: space-between;
    align-items: flex-start;
    padding: 12px;
    border-radius: 8px;
    background: var(--surface-subtle);
}

.rag-snippet div {
    min-width: 180px;
}

.rag-snippet strong,
.rag-snippet small {
    display: block;
}

.rag-snippet strong {
    color: var(--text-primary);
    line-height: 1.5;
}

.rag-snippet small {
    margin-top: 4px;
    color: var(--text-muted);
}

.rag-snippet p {
    margin: 0;
    flex: 1;
    min-width: 0;
    color: var(--text-secondary);
    line-height: 1.65;
    word-break: break-word;
}

.source-actions {
    margin-top: 12px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 10px;
}

.source-select {
    width: 100%;
}

.source-empty {
    margin: 12px 0 0;
    padding: 14px;
    border-radius: 8px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.source-empty.compact {
    margin-top: 8px;
    padding: 10px 12px;
    font-size: 13px;
}

.source-table-head,
.source-row {
    display: grid;
    grid-template-columns: minmax(0, 1.8fr) 1fr 0.8fr 0.8fr auto;
    gap: 12px;
    padding: 12px 14px;
    align-items: center;
}

.source-table-head {
    color: var(--text-muted);
    background: var(--surface-subtle);
    font-size: 12px;
    font-weight: 700;
}

.source-row {
    border-top: 1px solid var(--line);
    color: var(--text-secondary);
    background: var(--surface);
    font-size: 13px;
}

.text-action {
    min-height: 28px;
    border: 0;
    border-radius: 7px;
    padding: 0 10px;
    background: var(--surface-subtle);
    color: var(--text-secondary);
    font: inherit;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
}

.text-action:hover {
    color: var(--text-primary);
}

.text-action:disabled {
    cursor: not-allowed;
    opacity: 0.45;
}

.text-action.danger:hover {
    color: #b42318;
}

.pipeline-panel {
    display: block;
}

.pipeline-grid {
    margin-top: 22px;
    grid-template-columns: repeat(4, minmax(0, 1fr));
}

.pipeline-step > span {
    color: var(--accent-blue);
    font-size: 12px;
    font-weight: 700;
}

.pipeline-step p {
    margin: 0;
    font-size: 14px;
}

.dialog-body {
    display: grid;
}

.full-input {
    width: 100%;
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

@media (max-width: 1080px) {
    .packs-hero,
    .workbench,
    .detail-header {
        grid-template-columns: 1fr;
    }

    .type-rail {
        position: static;
    }

    .pipeline-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 760px) {
    .packs-page {
        padding-top: 42px;
    }

    .metrics-grid,
    .pack-grid,
    .detail-metrics,
    .detail-layout,
    .pipeline-grid {
        grid-template-columns: 1fr;
    }

    .source-table-head {
        display: none;
    }

    .source-actions {
        grid-template-columns: 1fr;
    }

    .rag-preview-head,
    .rag-preview-controls,
    .rag-snippet {
        align-items: stretch;
        flex-direction: column;
    }

    .semantic-toggle {
        align-self: flex-start;
    }

    .rag-snippet div {
        min-width: 0;
    }

    .source-row {
        grid-template-columns: 1fr;
    }
}
</style>
