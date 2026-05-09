<template>
  <basic-container>
    <div class="admin-page-head">
      <div>
        <span class="admin-eyebrow">Permission Matrix</span>
        <h1 class="admin-page-title">角色权限</h1>
        <p class="admin-page-desc">用角色控制用户能否管理账号、文章、上下文包、AI 配置和系统自检。</p>
      </div>
      <div class="admin-status-note">
        推荐按职责配置角色：创作者、知识维护者、运营管理员、系统管理员，避免所有人都拥有全量权限。
      </div>
    </div>
    <avue-crud :option="option"
               :table-loading="loading"
               :data="data"
               :page.sync="page"
               :permission="permissionList"
               @row-del="rowDel"
               @row-update="rowUpdate"
               @row-save="rowSave"
               @search-change="searchChange"
               @search-reset="searchReset"
               @selection-change="selectionChange"
               @current-change="currentChange"
               @size-change="sizeChange"
               @refresh-change="refreshChange"
               @on-load="onLoad">
    </avue-crud>
  </basic-container>
</template>

<script>
import request from '@/axios';

export default {
  data() {
    return {
      loading: true,
      page: {
        pageSize: 10,
        currentPage: 1,
        total: 0
      },
      selectionList: [],
      data: [],
      option: {
        height: 'auto',
        calcHeight: 30,
        tip: false,
        searchShow: true,
        searchMenuSpan: 6,
        border: true,
        index: true,
        viewBtn: true,
        selection: true,
        dialogClickModal: false,
        column: [
          {
            label: 'ID',
            prop: 'id',
            width: 80,
            display: false
          },
          {
            label: '角色名称',
            prop: 'name',
            search: true,
            rules: [{
              required: true,
              message: "请输入角色名称",
              trigger: "blur"
            }]
          },
          {
            label: '角色描述',
            prop: 'description',
            rules: [{
              required: true,
              message: "请输入角色描述",
              trigger: "blur"
            }]
          },
          {
            label: '权限配置',
            prop: 'permissions',
            type: 'select',
            multiple: true,
            props: {
              label: 'name',
              value: 'id'
            },
            dicData: [], // Will be populated from API
            rules: [{
              required: false,
              message: "请选择权限",
              trigger: "change"
            }]
          },
          {
            label: '创建时间',
            prop: 'created_at',
            type: 'datetime',
            format: 'yyyy-MM-dd HH:mm:ss',
            valueFormat: 'yyyy-MM-dd HH:mm:ss',
            display: false
          }
        ]
      },
      permissionList: {
        addBtn: true,
        delBtn: true,
        editBtn: true,
        viewBtn: true
      }
    };
  },
  methods: {
    // Fetch permissions list for the select box
    getPermissionList() {
      request({
        url: '/api/permissions',
        method: 'get'
      }).then(res => {
        const column = this.option.column.find(item => item.prop === 'permissions');
        if (column) {
          column.dicData = res.data.data;
        }
      });
    },
    rowSave(row, done, loading) {
      request({
        url: '/api/roles',
        method: 'post',
        data: row
      }).then(() => {
        this.onLoad(this.page);
        this.$message({
          type: 'success',
          message: '操作成功!'
        });
        done();
      }, error => {
        window.console.log(error);
        loading();
      });
    },
    rowUpdate(row, index, done, loading) {
      request({
        url: '/api/roles/' + row.id,
        method: 'put',
        data: row
      }).then(() => {
        this.onLoad(this.page);
        this.$message({
          type: 'success',
          message: '操作成功!'
        });
        done();
      }, error => {
        window.console.log(error);
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
          return request({
            url: '/api/roles/' + row.id,
            method: 'delete'
          });
        })
        .then(() => {
          this.onLoad(this.page);
          this.$message({
            type: 'success',
            message: '操作成功!'
          });
        });
    },
    searchReset() {
      this.page.currentPage = 1;
      this.onLoad(this.page);
    },
    searchChange(params, done) {
      this.page.currentPage = 1;
      this.onLoad(this.page, params);
      done();
    },
    selectionChange(list) {
      this.selectionList = list;
    },
    selectionClear() {
      this.selectionList = [];
      if (this.$refs.crud) {
        this.$refs.crud.toggleSelection();
      }
    },
    currentChange(currentPage) {
      this.page.currentPage = currentPage;
    },
    sizeChange(pageSize) {
      this.page.pageSize = pageSize;
    },
    refreshChange() {
      this.onLoad(this.page, this.query);
    },
    onLoad(page, params = {}) {
      this.loading = true;
      request({
        url: '/api/roles',
        method: 'get',
        params: Object.assign({
          pageNum: page.currentPage,
          pageSize: page.pageSize
        }, params)
      }).then(res => {
        const data = res.data.data;
        this.page.total = data.length; // Assuming API returns all for now, or need to adjust if paginated
        this.data = data;
        this.loading = false;
        this.selectionClear();
      }).catch(error => {
        this.loading = false;
        console.error(error);
      });
    }
  },
  mounted() {
    this.getPermissionList();
  }
};
</script>

<style>
</style>
