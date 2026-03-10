<template>
  <basic-container>
    <div>
      <el-tag>page:{{page}}</el-tag>
    </div>
    <div>
      <el-tag>search:{{search}}</el-tag>
    </div>
    <div>
      <el-tag>form:{{form}}</el-tag>
    </div>
    <avue-crud @on-load="onLoad"
               v-model="form"
               v-model:search="search"
               v-model:page="page"
               @row-save="rowSave"
               @row-update="rowUpdate"
               @row-del="rowUpdate"
               :option="option"
               :data="tableData"></avue-crud>
  </basic-container>
</template>
<script setup name="setup">
const data = reactive({
  tableData: [],
  option: {
    index: true,
    border: true,
    selection: true,
    rowKey: 'id',
    column: [{
      label: '姓名',
      prop: 'name',
      search: true,
      rules: [
        {
          required: true,
          message: '请输入姓名',
          trigger: 'blur'
        }
      ]
    }]
  },
  search: {},
  form: {},
  page: {
    total: 20
  }
})
const { tableData, option, form, page, search } = toRefs(data);
function onLoad () {
  if (page.value.currentPage == 1) {
    tableData.value = [{
      id: 1,
      name: '1-smallwei'
    }]
  } else {
    tableData.value = [{
      id: 1,
      name: '2-smallwei'
    }]
  }
}
function rowDel (row, index, done) {
  done(row)
}
function rowUpdate (row, index, done, loading) {
  done(row)
}
function rowSave (row, done, loading) {
  row.id = new Date().getTime()
  done(row)
}
</script>