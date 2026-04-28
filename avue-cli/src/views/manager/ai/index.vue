<template>
    <basic-container>
        <div class="admin-page-head">
            <div>
                <span class="admin-eyebrow">AI Gateway</span>
                <h1 class="admin-page-title">模型配置中心</h1>
                <p class="admin-page-desc">管理前台 AI 对话、摘要和文章生成使用的 OpenAI 兼容接口配置。</p>
            </div>
            <div class="admin-status-note">
                同一时间只应启用一个配置。启用后，新的 AI 请求会立即读取该模型与密钥。
            </div>
        </div>

        <avue-crud :option="option" :table-loading="loading" :data="data" @on-load="onLoad"
            @search-change="searchChange" @search-reset="searchReset" @row-save="rowSave"
            @row-update="rowUpdate" @row-del="rowDel" @refresh-change="refreshChange" ref="crud">
            <template #is_active="{ row }">
                <el-switch v-model="row.is_active" :active-value="1" :inactive-value="0"
                    @change="handleStatusChange(row)" />
            </template>
        </avue-crud>
    </basic-container>
</template>

<script>
import { getList, add, update, del, activate } from "@/api/manager/ai";
import option from "@/option/manager/ai";

export default {
    data() {
        return {
            option,
            data: [],
            loading: false
        };
    },
    methods: {
        onLoad(page, params = {}) {
            this.loading = true;
            getList(params).then(res => {
                this.data = res.data.data;
                this.loading = false;
            }).catch(() => {
                this.loading = false;
            });
        },
        rowSave(row, done, loading) {
            add(row).then(() => {
                this.$message.success('模型配置已新增');
                done();
                this.onLoad();
            }).catch(() => {
                loading();
            });
        },
        rowUpdate(row, index, done, loading) {
            update(row).then(() => {
                this.$message.success('模型配置已更新');
                done();
                this.onLoad();
            }).catch(() => {
                loading();
            });
        },
        rowDel(row) {
            this.$confirm('删除后该模型配置将不可恢复，确认继续？', {
                confirmButtonText: '删除配置',
                cancelButtonText: '取消',
                type: 'warning'
            })
                .then(() => del(row))
                .then(() => {
                    this.$message.success('模型配置已删除');
                    this.onLoad();
                });
        },
        handleStatusChange(row) {
            if (row.is_active === 0) {
                update({ id: row.id, is_active: 0 }).then(() => {
                    this.$message.success('配置已停用');
                    this.onLoad();
                });
            } else {
                activate(row.id).then(() => {
                    this.$message.success('配置已启用');
                    this.onLoad();
                });
            }
        },
        refreshChange() {
            this.onLoad();
        },
        searchChange(params, done) {
            this.onLoad(null, params);
            done();
        },
        searchReset() {
            this.onLoad();
        }
    }
};
</script>
