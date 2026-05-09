<template>
  <div class="login-container"
       @keyup.enter="handleLogin">
    <div class="login-time">
      {{time}}
    </div>
    <div class="login-weaper">
      <div class="login-left animate__animated animate__fadeInLeft">
        <div class="login-product-mark">知</div>
        <p class="title">知境 ContextForge 管理台</p>
        <p class="login-subtitle">面向管理员的运营治理入口，集中处理账号权限、内容资产、AI 模型、Embedding 与 RAG 索引。</p>
        <div class="login-feature-list">
          <div class="login-feature-item">
            <strong>账号权限</strong>
            <span>用户、角色与后台访问边界统一维护</span>
          </div>
          <div class="login-feature-item">
            <strong>内容资产</strong>
            <span>文章、上下文包和资料来源清晰管理</span>
          </div>
          <div class="login-feature-item">
            <strong>AI 与 RAG</strong>
            <span>模型配置、向量索引和系统自检集中处理</span>
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
