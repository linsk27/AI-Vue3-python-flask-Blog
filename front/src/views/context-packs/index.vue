<template>
    <div class="packs-page">
        <section class="packs-header">
            <div>
                <span class="eyebrow">Context Packs / 上下文包</span>
                <h1>把多份资料打包成可复用的 AI 上下文。</h1>
                <p>
                    上下文包可以组合文档、链接、笔记和 AI 对话，适合项目交接、答辩准备、技术复习、论文阅读和内容创作。
                </p>
            </div>
            <button class="primary-button" type="button" @click="openCreateDialog">
                <Plus class="icon" />
                <span>新建上下文包</span>
            </button>
        </section>

        <section class="packs-layout">
            <aside class="pack-sidebar">
                <h2>包类型</h2>
                <button
                    v-for="type in packTypes"
                    :key="type.value"
                    type="button"
                    class="type-button"
                    :class="{ active: selectedType === type.value }"
                    @click="selectedType = type.value"
                >
                    {{ type.label }}
                </button>

                <div class="sidebar-note">
                    <strong>{{ filteredPacks.length }}</strong>
                    <span>个上下文包</span>
                </div>
            </aside>

            <main class="pack-grid">
                <article
                    v-for="pack in filteredPacks"
                    :key="pack.id"
                    class="pack-card"
                    :class="{ active: selectedPack?.id === pack.id }"
                    @click="selectPack(pack.id)"
                >
                    <div class="pack-card-header">
                        <span>{{ getTypeLabel(pack.type) }}</span>
                        <strong>{{ pack.documents.length }} 份文档</strong>
                    </div>
                    <h2>{{ pack.name }}</h2>
                    <p>{{ pack.description }}</p>
                    <div class="pack-tags">
                        <span v-for="tag in pack.tags" :key="tag">{{ tag }}</span>
                    </div>
                    <div class="pack-actions">
                        <button type="button" @click.stop="selectPack(pack.id)">查看详情</button>
                        <button type="button" @click.stop="exportPack(pack)">导出 Markdown</button>
                    </div>
                </article>
            </main>
        </section>

        <section class="detail-panel" v-if="selectedPack">
            <div class="detail-header">
                <div>
                    <span class="eyebrow">Pack Detail</span>
                    <h2>{{ selectedPack.name }}</h2>
                    <p>{{ selectedPack.intent }}</p>
                </div>
                <div class="detail-actions">
                    <router-link to="/ai-center/chat" class="panel-button">用此上下文提问</router-link>
                    <button class="panel-button" type="button" @click="exportPack(selectedPack)">导出</button>
                </div>
            </div>

            <div class="detail-grid">
                <article class="detail-card">
                    <h3>包摘要</h3>
                    <p>{{ selectedPack.summary }}</p>
                </article>
                <article class="detail-card">
                    <h3>关键线索</h3>
                    <ul>
                        <li v-for="point in selectedPack.keyPoints" :key="point">{{ point }}</li>
                    </ul>
                </article>
                <article class="detail-card">
                    <h3>包含文档</h3>
                    <div class="doc-list">
                        <span v-for="doc in selectedPack.documents" :key="doc">{{ doc }}</span>
                    </div>
                </article>
            </div>
        </section>

        <section class="roadmap-panel">
            <span class="eyebrow">下一阶段</span>
            <h2>上下文包后续会接入真实文档、AI 摘要和多文档问答。</h2>
            <div class="roadmap-grid">
                <article v-for="item in roadmap" :key="item.title">
                    <strong>{{ item.title }}</strong>
                    <p>{{ item.description }}</p>
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
                <el-input v-model="draftPack.name" placeholder="例如：软著材料上下文包" />

                <label class="field-label">类型</label>
                <el-select v-model="draftPack.type" class="full-input">
                    <el-option v-for="type in creatableTypes" :key="type.value" :label="type.label" :value="type.value" />
                </el-select>

                <label class="field-label">用途</label>
                <el-input v-model="draftPack.intent" placeholder="这个上下文包准备用来解决什么问题？" />

                <label class="field-label">描述</label>
                <el-input v-model="draftPack.description" type="textarea" :rows="3" placeholder="简单描述这个包里会放哪些材料" />

                <label class="field-label">标签</label>
                <el-input v-model="draftPack.tags" placeholder="用逗号分隔，例如：软著,项目,架构" />
            </div>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="createDialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="createPack">创建</el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { useElMessage } from '@/hooks/useMessage'

interface ContextPack {
    id: number
    name: string
    type: string
    description: string
    intent: string
    summary: string
    keyPoints: string[]
    documents: string[]
    tags: string[]
}

const { message } = useElMessage()

const packTypes = [
    { value: 'all', label: '全部' },
    { value: 'project', label: '项目' },
    { value: 'research', label: '研究' },
    { value: 'learning', label: '学习' },
    { value: 'writing', label: '写作' },
    { value: 'handoff', label: '交接' }
]

const creatableTypes = packTypes.filter(type => type.value !== 'all')
const selectedType = ref('all')
const createDialogVisible = ref(false)
const draftPack = reactive({
    name: '',
    type: 'project',
    intent: '',
    description: '',
    tags: ''
})

const packs = ref<ContextPack[]>([
    {
        id: 1,
        name: '毕业答辩上下文包',
        type: 'project',
        documents: ['项目需求说明', '系统架构设计', '数据库表设计', '答辩 Q&A'],
        description: '集中整理毕设系统的需求、架构、截图、创新点和答辩话术。',
        intent: '用于快速生成答辩讲稿、项目介绍、软著材料和简历描述。',
        summary: '这个上下文包围绕项目交付材料组织，适合输出项目简介、功能模块、技术亮点和答辩问答。',
        keyPoints: ['功能模块要能对应截图', '技术亮点要落在 AI 与权限管理', '数据库设计需要能支撑文档和用户体系'],
        tags: ['答辩', '项目', '软著']
    },
    {
        id: 2,
        name: 'Vue 3 面试上下文包',
        type: 'learning',
        documents: ['Composition API 笔记', '响应式原理', 'Router 与 Pinia', '常见面试题'],
        description: '把 Vue3 学习资料整理为可复习、可问答、可生成面试题的上下文。',
        intent: '用于复习核心概念、生成问答卡片和模拟面试。',
        summary: '这个上下文包聚焦 Vue3 常见知识点，可用于快速复习和生成技术问答。',
        keyPoints: ['响应式原理是核心', '组合式 API 要结合场景说明', '路由和状态管理要放进项目语境'],
        tags: ['Vue', '前端', '面试']
    },
    {
        id: 3,
        name: 'Flask 后端重构上下文包',
        type: 'project',
        documents: ['API 路由设计', '权限校验风险', 'AI 配置接口', '数据库迁移记录'],
        description: '记录 Flask 后端从博客接口向文档工作台接口演进的关键决策。',
        intent: '用于后端重构、接口说明、风险检查和后续开源文档。',
        summary: '这个上下文包用于追踪后端改造边界，重点是接口兼容、字段迁移和权限安全。',
        keyPoints: ['保留 articles 兼容层', '逐步引入 documents 语义', '管理接口需要统一鉴权'],
        tags: ['Flask', '后端', '重构']
    }
])

const selectedPackId = ref(packs.value[0]?.id)

const filteredPacks = computed(() => {
    if (selectedType.value === 'all') return packs.value
    return packs.value.filter(pack => pack.type === selectedType.value)
})

const selectedPack = computed(() => {
    return packs.value.find(pack => pack.id === selectedPackId.value) || filteredPacks.value[0]
})

function getTypeLabel(value: string) {
    return packTypes.find(type => type.value === value)?.label || value
}

function selectPack(id: number) {
    selectedPackId.value = id
}

function openCreateDialog() {
    draftPack.name = ''
    draftPack.type = 'project'
    draftPack.intent = ''
    draftPack.description = ''
    draftPack.tags = ''
    createDialogVisible.value = true
}

function createPack() {
    if (!draftPack.name.trim()) {
        message.warning('请填写上下文包名称')
        return
    }

    const tags = draftPack.tags
        .split(/[，,]/)
        .map(tag => tag.trim())
        .filter(Boolean)

    const pack: ContextPack = {
        id: Date.now(),
        name: draftPack.name.trim(),
        type: draftPack.type,
        description: draftPack.description.trim() || '一个新的上下文包，等待添加文档和资料。',
        intent: draftPack.intent.trim() || '用于组织相关资料，并在需要时提供给 AI 作为上下文。',
        summary: '暂未生成 AI 摘要。后续会接入后端接口，基于包内文档生成完整洞察。',
        keyPoints: ['添加相关文档', '补充来源链接', '生成包摘要'],
        documents: ['待添加文档'],
        tags: tags.length ? tags : ['未分类']
    }

    packs.value.unshift(pack)
    selectedPackId.value = pack.id
    createDialogVisible.value = false
    message.success('上下文包已创建')
}

function exportPack(pack: ContextPack) {
    const markdown = [
        `# ${pack.name}`,
        '',
        `类型：${getTypeLabel(pack.type)}`,
        '',
        `用途：${pack.intent}`,
        '',
        `## 摘要`,
        pack.summary,
        '',
        `## 关键线索`,
        ...pack.keyPoints.map(point => `- ${point}`),
        '',
        `## 包含文档`,
        ...pack.documents.map(doc => `- ${doc}`),
        '',
        `## 标签`,
        pack.tags.map(tag => `#${tag}`).join(' ')
    ].join('\n')

    navigator.clipboard?.writeText(markdown)
    message.success('Markdown 已复制到剪贴板')
}

const roadmap = [
    {
        title: '接入真实文档',
        description: '从知识库选择文档加入上下文包，并支持排序、移除和来源备注。'
    },
    {
        title: 'AI 包洞察',
        description: '基于包内所有文档生成摘要、关键线索、风险点和复习问题。'
    },
    {
        title: '多文档问答',
        description: '让 AI 只基于选中的上下文包回答问题，并把有价值回答保存为文档。'
    }
]
</script>

<style scoped>
.packs-page {
    width: var(--page-width);
    min-height: calc(100vh - 160px);
    margin: 0 auto;
    padding: 72px 0 80px;
    color: var(--text-primary);
}

.packs-header {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: end;
    gap: 32px;
    margin-bottom: 28px;
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
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
}

.field-label {
    margin: 14px 0 8px;
    background: transparent;
    color: var(--text-muted);
    padding: 0;
    text-transform: uppercase;
}

.packs-header h1 {
    max-width: 900px;
    margin: 16px 0 14px;
    font-size: clamp(42px, 7vw, 76px);
    font-weight: 650;
    line-height: 0.98;
    letter-spacing: 0;
}

.packs-header p {
    max-width: 720px;
    margin: 0;
    color: var(--text-secondary);
    font-size: 18px;
    line-height: 1.75;
}

.primary-button,
.pack-actions button,
.type-button,
.panel-button {
    border: 0;
    border-radius: 10px;
    font: inherit;
    font-weight: 600;
    cursor: pointer;
    transition: background 180ms ease, color 180ms ease, box-shadow 180ms ease;
}

.primary-button {
    min-height: 42px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 0 16px;
    color: var(--button-fg);
    background: var(--button-bg);
    box-shadow: var(--ring);
}

.primary-button:hover {
    background: var(--button-hover);
}

.icon {
    width: 16px;
    height: 16px;
}

.packs-layout {
    display: grid;
    grid-template-columns: 220px minmax(0, 1fr);
    gap: 12px;
}

.pack-sidebar,
.pack-card,
.roadmap-panel,
.detail-panel {
    background: var(--surface);
    border-radius: 12px;
    box-shadow: var(--card-shadow);
}

.pack-sidebar {
    align-self: start;
    padding: 18px;
    position: sticky;
    top: 104px;
}

.pack-sidebar h2 {
    margin: 0 0 12px;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.type-button {
    width: 100%;
    min-height: 36px;
    margin-bottom: 8px;
    padding: 0 10px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    text-align: left;
    box-shadow: var(--ring);
}

.type-button:hover,
.type-button.active {
    color: var(--text-primary);
    background: var(--surface-hover);
}

.sidebar-note {
    margin-top: 16px;
    padding: 14px;
    border-radius: 10px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    display: grid;
    gap: 4px;
}

.sidebar-note strong {
    font-size: 28px;
    line-height: 1;
}

.sidebar-note span {
    color: var(--text-secondary);
    font-size: 13px;
}

.pack-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.pack-card {
    min-height: 300px;
    padding: 22px;
    display: flex;
    flex-direction: column;
    cursor: pointer;
    transition: transform 180ms ease, box-shadow 180ms ease;
}

.pack-card:hover,
.pack-card.active {
    transform: translateY(-2px);
    box-shadow: rgba(0, 0, 0, 0.12) 0 0 0 1px,
        rgba(0, 0, 0, 0.06) 0 8px 18px -12px;
}

.pack-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
}

.pack-card h2 {
    margin: 18px 0 10px;
    font-size: 24px;
    font-weight: 650;
    line-height: 1.2;
}

.pack-card p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 15px;
    line-height: 1.7;
}

.pack-tags,
.doc-list {
    margin-top: 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.pack-tags span,
.doc-list span {
    min-height: 26px;
    display: inline-flex;
    align-items: center;
    padding: 0 10px;
    border-radius: 9999px;
    color: var(--text-secondary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
    font-size: 12px;
    font-weight: 600;
}

.pack-actions {
    margin-top: auto;
    padding-top: 24px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.pack-actions button,
.panel-button {
    min-height: 34px;
    display: inline-flex;
    align-items: center;
    padding: 0 12px;
    color: var(--text-primary);
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.pack-actions button:hover,
.panel-button:hover {
    background: var(--surface-hover);
}

.detail-panel {
    margin-top: 56px;
    padding: 28px;
}

.detail-header {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: end;
    gap: 24px;
    margin-bottom: 22px;
}

.detail-header h2,
.roadmap-panel h2,
.dialog-heading h2 {
    margin: 14px 0 10px;
    font-size: clamp(28px, 5vw, 44px);
    font-weight: 650;
    line-height: 1.08;
}

.detail-header p {
    margin: 0;
    color: var(--text-secondary);
    line-height: 1.7;
}

.detail-actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 8px;
}

.detail-grid,
.roadmap-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.detail-card,
.roadmap-grid article {
    padding: 18px;
    border-radius: 12px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.detail-card h3 {
    margin: 0 0 10px;
    font-size: 16px;
}

.detail-card p,
.detail-card li,
.roadmap-grid p {
    color: var(--text-secondary);
    line-height: 1.65;
}

.detail-card ul {
    margin: 0;
    padding-left: 18px;
}

.roadmap-panel {
    margin-top: 56px;
    padding: 28px;
}

.roadmap-grid strong {
    display: block;
    margin-bottom: 8px;
    font-size: 16px;
}

.roadmap-grid p {
    margin: 0;
    font-size: 14px;
}

.dialog-heading h2 {
    margin-bottom: 0;
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

@media (max-width: 1100px) {
    .pack-grid,
    .detail-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 820px) {
    .packs-header,
    .packs-layout,
    .detail-header,
    .detail-grid,
    .roadmap-grid {
        grid-template-columns: 1fr;
    }

    .pack-sidebar {
        position: static;
    }

    .detail-actions {
        justify-content: flex-start;
    }
}

@media (max-width: 560px) {
    .pack-grid {
        grid-template-columns: 1fr;
    }
}
</style>
