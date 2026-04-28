<template>
  <div class="ops-dashboard">
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
            <h2>内容运营概览</h2>
          </div>
          <span class="ops-badge">实时</span>
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
            <span>当前启用配置</span>
            <strong>1</strong>
          </li>
          <li>
            <span>流式接口</span>
            <strong class="is-success">在线</strong>
          </li>
          <li>
            <span>配置建议</span>
            <strong>定期轮换 Key</strong>
          </li>
        </ul>
      </article>

      <article class="ops-panel">
        <div class="ops-panel__head">
          <div>
            <span class="ops-eyebrow">Security</span>
            <h2>权限治理</h2>
          </div>
        </div>
        <ul class="ops-list">
          <li>
            <span>管理员入口</span>
            <strong class="is-success">已限制</strong>
          </li>
          <li>
            <span>角色权限</span>
            <strong>按模块维护</strong>
          </li>
          <li>
            <span>敏感字段</span>
            <strong>部分脱敏</strong>
          </li>
        </ul>
      </article>
    </section>
  </div>
</template>

<script>
export default {
  data() {
    return {
      kpis: [
        { label: '文章总量', value: '128', hint: '本周新增 12 篇', state: 'is-success' },
        { label: '用户账户', value: '42', hint: '管理员 1 名', state: '' },
        { label: 'AI 配置', value: '2', hint: '1 个正在启用', state: 'is-success' },
        { label: '待处理评论', value: '6', hint: '需要人工复核', state: 'is-warning' }
      ],
      contentFlow: [
        { name: '草稿', count: 18, desc: '创作与编辑中' },
        { name: '已发布', count: 96, desc: '前台可见内容' },
        { name: '互动', count: 314, desc: '评论与点赞' },
        { name: '归档', count: 14, desc: '历史内容沉淀' }
      ]
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

.ops-eyebrow,
.ops-badge {
  color: var(--admin-primary);
  font-size: 12px;
  font-weight: 700;
}

.ops-badge {
  padding: 4px 8px;
  border-radius: 999px;
  background: var(--admin-primary-soft);
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
    color: var(--admin-ink);
    font-size: 13px;
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
