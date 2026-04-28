<template>
  <div class="login-container"
       @keyup.enter="handleLogin">
    <div class="login-time">
      {{time}}
    </div>
    <div class="login-weaper">
      <div class="login-left animate__animated animate__fadeInLeft">
        <div class="login-product-mark">AI</div>
        <p class="title">智汇内容与 AI 配置控制台</p>
        <p class="login-subtitle">集中管理用户、文章、权限与模型密钥。所有关键配置都会即时影响前台服务。</p>
        <div class="login-feature-list">
          <div class="login-feature-item">
            <strong>内容运营</strong>
            <span>文章、分类与发布状态统一维护</span>
          </div>
          <div class="login-feature-item">
            <strong>权限管理</strong>
            <span>后台访问与用户身份集中校验</span>
          </div>
          <div class="login-feature-item">
            <strong>AI 服务</strong>
            <span>模型密钥、启用状态与调用配置</span>
          </div>
        </div>
      </div>
      <div class="login-border animate__animated animate__fadeInRight">
        <div class="login-main">
          <p class="login-title">
            管理员登录
            <top-lang></top-lang>
          </p>
          <userLogin v-if="activeName==='user'"></userLogin>
          <codeLogin v-else-if="activeName==='code'"></codeLogin>
          <faceLogin v-else-if="activeName==='face'"></faceLogin>
          <div class="login-menu">
            <a href="#"
               @click.stop="activeName='user'">{{ $t('login.userLogin') }}</a>
            <a href="#"
               @click.stop="activeName='code'">{{ $t('login.phoneLogin') }}</a>
            <a href="#"
               @click.stop="activeName='face'">{{ $t('login.faceLogin') }}</a>
          </div>
          <thirdLogin></thirdLogin>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import userLogin from "./userlogin.vue";
import codeLogin from "./codelogin.vue";
import thirdLogin from "./thirdlogin.vue";
import faceLogin from "./facelogin.vue";
import { validatenull } from "@/utils/validate";
import topLang from "@/page/index/top/top-lang.vue";
export default {
  name: "login",
  components: {
    userLogin,
    codeLogin,
    thirdLogin,
    faceLogin,
    topLang
  },
  data () {
    return {
      time: "",
      activeName: "user"
    };
  },
  watch: {
    $route () {
      const params = this.$route.query;
      this.socialForm = params
      if (!validatenull(this.socialForm.state)) {
        const loading = this.$loading({
          lock: true,
          text: `${this.socialForm.state === "WX" ? "微信" : "QQ"
            }登录中,请稍后。。。`,
          spinner: "el-icon-loading"
        });
        setTimeout(() => {
          loading.close();
        }, 2000);
      }
    }
  },
  created () {
    this.getTime();
    setInterval(() => {
      this.getTime();
    }, 1000);
  },
  mounted () { },
  props: [],
  methods: {
    getTime () {
      this.time = this.$dayjs().format('YYYY年MM月DD日 HH:mm:ss')
    }
  }
};
</script>
