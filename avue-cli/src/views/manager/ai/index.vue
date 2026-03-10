<template>
    <basic-container>
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
            option: option,
            data: [],
            loading: false
        };
    },
    methods: {
        onLoad(page, params = {}) {
            this.loading = true;
            getList(params).then(res => {
                const data = res.data.data;
                // 直接赋值，后端返回的数据已经包含了 id
                this.data = data;
                this.loading = false;
            }).catch(() => {
                this.loading = false;
            });
        },
        rowSave(row, done, loading) {
            add(row).then(() => {
                this.$message.success('新增成功');
                done();
                this.onLoad();
            }).catch(() => {
                loading();
            });
        },
        rowUpdate(row, index, done, loading) {
            update(row).then(() => {
                this.$message.success('修改成功');
                done();
                this.onLoad();
            }).catch(() => {
                loading();
            });
        },
        rowDel(row) {
            this.$confirm('确定删除该配置?', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
                .then(() => {
                    return del(row);
                })
                .then(() => {
                    this.$message.success('删除成功');
                    this.onLoad();
                });
        },
        handleStatusChange(row) {
            // 乐观更新，如果只有这一行是启用的
            if (row.is_active === 0) {
                update({ id: row.id, is_active: 0 }).then(() => {
                    this.$message.success('已禁用');
                    this.onLoad();
                });
            } else {
                // 启用
                activate(row.id).then(() => {
                    this.$message.success('已启用');
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
