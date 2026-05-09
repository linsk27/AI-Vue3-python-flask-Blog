<template>
  <div v-loading="loading" class="ops-dashboard">
    <section class="ops-kpis">
      <article v-for="item in kpis" :key="item.label" class="ops-kpi-card">
        <span class="ops-kpi-card__label">{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small :class="item.state">{{ item.hint }}</small>
      </article>
    </section>

    <section class="ops-grid">
      <article class="ops-panel ops-panel--wide">
        <div class="ops-panel__head">
          <div>
            <span class="ops-eyebrow">Content Ops</span>
            <h2>真实内容概览</h2>
          </div>
          <el-button size="small" @click="loadDashboard">刷新</el-button>
        </div>
        <div class="ops-flow">
          <div v-for="step in contentFlow" :key="step.name" class="ops-flow__item">
            <span>{{ step.name }}</span>
            <strong>{{ step.count }}</strong>
            <small>{{ step.desc }}</small>
          </div>
        </div>
      </article>

      <article class="ops-panel">
        <div class="ops-panel__head">
          <div>
            <span class="ops-eyebrow">AI Gateway</span>
            <h2>模型服务状态</h2>
          </div>
        </div>
        <ul class="ops-list">
          <li>
            <span>AI 配置</span>
            <strong>{{ aiConfigs.length }}</strong>
          </li>
          <li>
            <span>启用配置</span>
            <strong :class="activeAiConfigs.length ? 'is-success' : 'is-warning'">{{ activeAiConfigs.length }}</strong>
          </li>
          <li>
            <span>Embedding</span>
            <strong>{{ contextStats.embedding_model || '后台配置' }}</strong>
          </li>
        </ul>
      </article>

      <article class="ops-panel">
        <div class="ops-panel__head">
          <div>
            <span class="ops-eyebrow">System</span>
            <h2>系统观察</h2>
          </div>
        </div>
        <ul class="ops-list">
          <li>
            <span>自检状态</span>
            <strong :class="systemReport.status === 'healthy' ? 'is-success' : 'is-warning'">{{ systemStatusText }}</strong>
          </li>
          <li>
            <span>健康分</span>
            <strong>{{ systemReport.score ?? '-' }}</strong>
          </li>
          <li>
            <span>最近检查</span>
            <strong>{{ systemReport.checked_at || '未运行' }}</strong>
          </li>
        </ul>
      </article>
    </section>
  </div>
</template>

<script>
import { getAiConfigs, getArticles, getContextStats, getSystemSelfCheck, getUsers } from '@/api/manager/dashboard'

const readData = result => {
  if (result.status !== 'fulfilled') return null
  return result.value.data && result.value.data.data
}

export default {
  data() {
    return {
      loading: false,
      articles: [],
      users: [],
      aiConfigs: [],
      contextStats: {},
      systemReport: {}
    }
  },
  computed: {
    activeAiConfigs() {
      return this.aiConfigs.filter(item => Number(item.is_active) === 1)
    },
    kpis() {
      return [
        { label: '文章总量', value: this.articles.length, hint: '来自文章接口', state: 'is-success' },
        { label: '用户账户', value: this.users.length, hint: '来自用户管理', state: '' },
        { label: '上下文包', value: this.contextStats.packs ?? 0, hint: 'RAG 工作区', state: 'is-success' },
        { label: 'AI 配置', value: this.aiConfigs.length, hint: `${this.activeAiConfigs.length} 个启用`, state: this.activeAiConfigs.length ? 'is-success' : 'is-warning' }
      ]
    },
    contentFlow() {
      const published = this.articles.filter(item => (item.status || 'published') === 'published').length
      const drafts = this.articles.filter(item => item.status === 'draft').length
      return [
        { name: '已发布', count: published, desc: '前台可见内容' },
        { name: '草稿', count: drafts, desc: '创作与编辑中' },
        { name: '上下文包', count: this.contextStats.packs ?? 0, desc: '可复用上下文' },
        { name: '资料来源', count: this.contextStats.sources ?? 0, desc: 'RAG 检索材料' }
      ]
    },
    systemStatusText() {
      if (this.systemReport.status === 'healthy') return '健康'
      if (this.systemReport.status === 'attention') return '关注'
      if (this.systemReport.status === 'critical') return '高风险'
      return '未检查'
    }
  },
  mounted() {
    this.loadDashboard()
  },
  methods: {
    loadDashboard() {
      this.loading = true
      Promise.allSettled([
        getArticles(),
        getUsers(),
        getAiConfigs(),
        getContextStats(),
        getSystemSelfCheck()
      ]).then(results => {
        this.articles = readData(results[0]) || []
        this.users = readData(results[1]) || []
        this.aiConfigs = readData(results[2]) || []
        this.contextStats = readData(results[3]) || {}
        this.systemReport = readData(results[4]) || {}
      }).finally(() => {
        this.loading = false
      })
    }
  }
}
</script>

<style scoped lang="scss">
.ops-dashboard {
  display: grid;
  gap: 14px;
}

.ops-kpis,
.ops-grid {
  display: grid;
  gap: 14px;
}

.ops-kpis {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.ops-kpi-card,
.ops-panel {
  border-radius: 6px;
  background: var(--admin-surface);
  box-shadow: var(--admin-shadow);
}

.ops-kpi-card {
  min-height: 120px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  &__label {
    color: var(--admin-muted);
    font-size: 13px;
    font-weight: 600;
  }

  strong {
    color: var(--admin-ink);
    font-size: 32px;
    line-height: 1;
  }

  small {
    color: var(--admin-ink-soft);
    font-size: 12px;
  }
}

.ops-grid {
  grid-template-columns: 1.3fr 1fr 1fr;
}

.ops-panel {
  padding: 18px;

  &--wide {
    min-height: 260px;
  }

  &__head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 18px;

    h2 {
      margin: 8px 0 0;
      color: var(--admin-ink);
      font-size: 18px;
      font-weight: 700;
    }
  }
}

.ops-eyebrow {
  color: var(--admin-primary);
  font-size: 12px;
  font-weight: 700;
}

.ops-flow {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;

  &__item {
    min-height: 150px;
    padding: 14px;
    border-radius: 6px;
    background: var(--admin-surface-subtle);

    span,
    small {
      display: block;
      color: var(--admin-ink-soft);
      font-size: 13px;
    }

    strong {
      display: block;
      margin: 18px 0 8px;
      color: var(--admin-ink);
      font-size: 30px;
    }
  }
}

.ops-list {
  display: grid;
  gap: 0;
  margin: 0;
  padding: 0;
  list-style: none;

  li {
    min-height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    border-bottom: 1px solid var(--admin-line);
    color: var(--admin-ink-soft);
    font-size: 13px;

    &:last-child {
      border-bottom: 0;
    }
  }

  strong {
    max-width: 180px;
    color: var(--admin-ink);
    font-size: 13px;
    overflow: hidden;
    text-align: right;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.is-success {
  color: var(--admin-success) !important;
}

.is-warning {
  color: #b76e00 !important;
}

@media (max-width: 1100px) {
  .ops-kpis,
  .ops-grid,
  .ops-flow {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .ops-kpis,
  .ops-grid,
  .ops-flow {
    grid-template-columns: 1fr;
  }
}
</style>
