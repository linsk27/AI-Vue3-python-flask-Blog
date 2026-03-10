<template>
    <basic-container>
        <avue-crud :option="option" :table-loading="loading" :data="data" @on-load="onLoad"
            @search-change="searchChange" @search-reset="searchReset" @row-save="rowSave" @row-update="rowUpdate"
            @row-del="rowDel" @refresh-change="refreshChange" :upload-before="uploadBefore" :upload-after="uploadAfter">
        </avue-crud>
    </basic-container>
</template>

<script>
import { getList, update, del, add } from "@/api/manager/user";
import request from '@/axios';
import option from "@/option/manager/user";

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
    created() {
        this.getRoleList();
    },
    methods: {
        getRoleList() {
            request({
                url: '/api/roles',
                method: 'get'
            }).then(res => {
                const column = this.option.column.find(item => item.prop === 'role_id');
                if (column) {
                    column.dicData = res.data.data;
                }
            });
        },
        onLoad(page, params = {}) {
            this.loading = true;
            // 处理搜索参数，Avue 默认的搜索参数在 params 中
            // 如果 params 中包含搜索字段（如 username），直接传给后端

            // 确保分页参数正确合并
            const query = Object.assign({}, params, this.page);

            // 清理空值，避免传递不必要的参数
            for (let key in query) {
                if (query[key] === '') delete query[key]
            }

            getList(query).then(res => {
                const data = res.data.data;
                // 将密码字段置空，不显示真实密码
                this.data = data.map(item => {
                    item.password = '******';
                    return item;
                });
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
        },
        uploadBefore(file, done, loading) {
            // console.log('上传前', file);
            done();
        },
        uploadAfter(res, done, loading) {
            // console.log('上传后', res);
            done();
        }
    }
};
</script>
