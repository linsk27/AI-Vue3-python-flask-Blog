<template>
    <basic-container>
        <div class="admin-page-head">
            <div>
                <span class="admin-eyebrow">RAG Embedding</span>
                <h1 class="admin-page-title">Embedding 配置</h1>
                <p class="admin-page-desc">配置语义检索使用的 OpenAI 兼容向量模型。未启用时，前台只使用关键词检索。</p>
            </div>
            <div class="admin-status-note">
                保存后需要到上下文包页面为资料重建向量，语义检索才会真正生效。
            </div>
        </div>

        <section class="embedding-layout">
            <el-card shadow="never" class="embedding-card">
                <el-form v-loading="loading" :model="form" label-width="132px">
                    <el-form-item label="启用语义检索">
                        <el-switch v-model="form.enabled" />
                    </el-form-item>
                    <el-form-item label="供应商">
                        <el-select v-model="form.provider" placeholder="选择供应商">
                            <el-option label="OpenAI" value="openai" />
                            <el-option label="火山方舟" value="volcano" />
                            <el-option label="SiliconFlow" value="siliconflow" />
                            <el-option label="自定义兼容接口" value="custom" />
                        </el-select>
                    </el-form-item>
                    <el-form-item label="模型">
                        <el-input v-model="form.model" placeholder="例如 text-embedding-3-small" />
                    </el-form-item>
                    <el-form-item label="Base URL">
                        <el-input v-model="form.base_url" placeholder="留空则使用供应商默认地址" />
                    </el-form-item>
                    <el-form-item label="API Key">
                        <el-input v-model="form.api_key" type="password" show-password placeholder="留空沿用已保存或环境变量中的 Key" />
                    </el-form-item>
                    <el-form-item label="备注">
                        <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="记录用途、成本策略或负责人" />
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
                        <el-button :loading="validating" @click="handleValidate">本地校验</el-button>
                        <el-button @click="loadConfig">刷新</el-button>
                    </el-form-item>
                </el-form>
            </el-card>

            <el-card shadow="never" class="embedding-card">
                <template #header>
                    <span>当前状态</span>
                </template>
                <ul class="status-list">
                    <li>
                        <span>配置来源</span>
                        <strong>{{ current.source || '未配置' }}</strong>
                    </li>
                    <li>
                        <span>当前模型</span>
                        <strong>{{ current.model || '未启用' }}</strong>
                    </li>
                    <li>
                        <span>语义检索</span>
                        <el-tag :type="current.embedding_configured ? 'success' : 'info'">
                            {{ current.embedding_configured ? '可用' : '未启用' }}
                        </el-tag>
                    </li>
                </ul>
                <el-alert
                    class="embedding-alert"
                    title="成本提示"
                    type="info"
                    :closable="false"
                    description="Embedding 会按资料分块和查询次数消耗供应商额度。建议先对高价值上下文包启用，并用预估 token 数控制范围。"
                />
            </el-card>
        </section>

        <el-card v-if="validation" shadow="never" class="validation-card">
            <template #header>
                <span>校验结果</span>
            </template>
            <el-table :data="validation.checks || []" border>
                <el-table-column prop="name" label="项目" width="180" />
                <el-table-column prop="detail" label="说明" />
                <el-table-column label="状态" width="120">
                    <template #default="{ row }">
                        <el-tag :type="row.ok ? 'success' : 'danger'">{{ row.ok ? '通过' : '需处理' }}</el-tag>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </basic-container>
</template>

<script>
import { getConfig, saveConfig, validateConfig } from '@/api/manager/embedding'

const defaultForm = () => ({
    enabled: false,
    provider: 'openai',
    model: '',
    base_url: '',
    api_key: '',
    notes: ''
})

export default {
    data() {
        return {
            form: defaultForm(),
            current: {},
            validation: null,
            loading: false,
            saving: false,
            validating: false
        }
    },
    mounted() {
        this.loadConfig()
    },
    methods: {
        loadConfig() {
            this.loading = true
            getConfig().then(res => {
                const data = res.data.data || {}
                this.current = data
                this.form = {
                    enabled: Boolean(data.enabled),
                    provider: data.provider || 'openai',
                    model: data.model || '',
                    base_url: data.base_url || '',
                    api_key: '',
                    notes: data.notes || ''
                }
            }).finally(() => {
                this.loading = false
            })
        },
        handleSave() {
            this.saving = true
            saveConfig(this.form).then(res => {
                this.$message.success('Embedding 配置已保存')
                this.current = res.data.data || {}
                this.form.api_key = ''
            }).finally(() => {
                this.saving = false
            })
        },
        handleValidate() {
            this.validating = true
            validateConfig(this.form).then(res => {
                this.validation = res.data.data || null
                this.$message.success('校验完成')
            }).finally(() => {
                this.validating = false
            })
        }
    }
}
</script>

<style scoped lang="scss">
.embedding-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.7fr);
    gap: 14px;
}

.embedding-card,
.validation-card {
    border-radius: 6px;
}

.status-list {
    display: grid;
    gap: 12px;
    margin: 0;
    padding: 0;
    list-style: none;

    li {
        min-height: 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        border-bottom: 1px solid var(--admin-line);
        color: var(--admin-ink-soft);

        &:last-child {
            border-bottom: 0;
        }
    }

    strong {
        color: var(--admin-ink);
    }
}

.embedding-alert,
.validation-card {
    margin-top: 14px;
}

@media (max-width: 960px) {
    .embedding-layout {
        grid-template-columns: 1fr;
    }
}
</style>
