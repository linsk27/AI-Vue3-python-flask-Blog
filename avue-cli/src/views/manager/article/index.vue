<template>
    <basic-container>
        <avue-crud :option="option" :table-loading="loading" :data="data" @on-load="onLoad"
            @search-change="searchChange" @search-reset="searchReset" @row-save="rowSave" @row-update="rowUpdate"
            @row-del="rowDel" @refresh-change="refreshChange">
        </avue-crud>
    </basic-container>
</template>

<script>
import { getList, add, update, del } from "@/api/manager/article";
import option from "@/option/manager/article";

export default {
    data() {
        return {
            option: option,
            data: [],
            loading: false,
            page: {
                pageSize: 10,
                currentPage: 1,
                total: 0
            }
        };
    },
    methods: {
        onLoad(page, params = {}) {
            this.loading = true;

            // 确保分页参数正确合并
            const query = Object.assign({}, params, this.page);

            // 清理空值
            for (let key in query) {
                if (query[key] === '') delete query[key]
            }

            getList(query).then(res => {
                const data = res.data.data;
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
                this.onLoad(this.page);
            }).catch(() => {
                loading();
            });
        },
        rowUpdate(row, index, done, loading) {
            update(row).then(() => {
                this.$message.success('修改成功');
                done();
                this.onLoad(this.page);
            }).catch(() => {
                loading();
            });
        },
        rowDel(row) {
            this.$confirm('确定将选择数据删除?', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            })
                .then(() => {
                    return del(row);
                })
                .then(() => {
                    this.$message.success('删除成功');
                    this.onLoad(this.page);
                });
        },
        refreshChange() {
            this.onLoad(this.page, this.query);
        },
        searchChange(params, done) {
            this.query = params;
            this.page.currentPage = 1;
            this.onLoad(this.page, params);
            done();
        },
        searchReset() {
            this.query = {};
            this.onLoad(this.page);
        }
    }
};
</script>
