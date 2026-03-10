<template>
  <el-dialog center
             :show-close="false"
             :close-on-press-escape="false"
             :close-on-click-modal="false"
             append-to-body
             v-model="dialogVisible"
             title="人机识别"
             width="400px">
    <center>
      <span>
        扫码下方二维码，回复<b>【模板验证码】</b><br />
        <span style="color:red">获得「模板验证码 + 交流群(一起摸🐟)」</span>
      </span>
      <br />
      <br />
      <img width="200"
           src="https://avuejs.com/images/icon/wechat.png" />
      <br />
      <br />
      <el-input v-model="value"
                placeholder="请输入验证码"></el-input>
    </center>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary"
                   @click="submit">确 认</el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script>
export default {
  data () {
    return {
      value: '',
      dialogVisible: false
    }
  },
  created () {
    if (window.localStorage.getItem('avue-cli_lock')) {
      return
    }
    //this.dialogVisible = true
  },
  methods: {
    submit () {
      if (this.value == '') {
        this.$message.error('验证码不能为空')
        return
      } else if (this.value != 'avue-cli') {
        this.$message.error('验证码不正确')
        return
      }
      this.dialogVisible = false
      window.localStorage.setItem('avue-cli_lock', true)
    }
  }

}
</script>