<template>
  <div class="avue-top">
    <div
      v-if="setting.collapse && !isHorizontal"
      class="top-bar__left"
      role="button"
      tabindex="0"
      aria-label="切换侧边栏"
      @click="setCollapse"
      @keydown.enter.prevent="setCollapse"
      @keydown.space.prevent="setCollapse"
    >
      <button
        class="avue-breadcrumb"
        :class="{ 'avue-breadcrumb--active': isCollapse }"
        type="button"
        tabindex="-1"
      >
        <i class="icon-navicon"></i>
      </button>
    </div>

    <div class="top-bar__title">
      <div class="top-console-title">
        <span class="top-console-title__main">管理控制台</span>
        <span class="top-console-title__sub">内容、权限与 AI 服务配置</span>
      </div>
      <top-search class="top-bar__item" v-if="setting.search"></top-search>
    </div>

    <div class="top-bar__right">
      <div v-if="setting.color" class="top-bar__item">
        <top-color></top-color>
      </div>
      <div v-if="setting.lock" class="top-bar__item">
        <top-lock></top-lock>
      </div>
      <div v-if="setting.theme" class="top-bar__item">
        <top-theme></top-theme>
      </div>
      <div class="top-bar__item">
        <top-lang></top-lang>
      </div>
      <div class="top-bar__item" v-if="setting.fullscren">
        <top-full></top-full>
      </div>
      <div class="top-bar__item" v-if="setting.debug">
        <top-logs></top-logs>
      </div>
      <div class="top-user">
        <img class="top-bar__img" :src="userInfo.avatar">
        <el-dropdown>
          <span class="el-dropdown-link">
            {{ userInfo.username }}
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>
                <router-link to="/">{{ $t('navbar.dashboard') }}</router-link>
              </el-dropdown-item>
              <el-dropdown-item>
                <router-link to="/info/index">{{ $t('navbar.userinfo') }}</router-link>
              </el-dropdown-item>
              <el-dropdown-item>
                <router-link to="/info/setting">{{ $t('navbar.setting') }}</router-link>
              </el-dropdown-item>
              <el-dropdown-item @click="logout" divided>{{ $t('navbar.logOut') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <top-setting></top-setting>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import topLock from "./top-lock.vue";
import topSearch from "./top-search.vue";
import topTheme from "./top-theme.vue";
import topLogs from "./top-logs.vue";
import topColor from "./top-color.vue";
import topLang from "./top-lang.vue";
import topFull from "./top-full.vue";
import topSetting from "../setting.vue";

export default {
  name: "top",
  components: {
    topLock,
    topSearch,
    topTheme,
    topLogs,
    topColor,
    topLang,
    topFull,
    topSetting
  },
  computed: {
    ...mapGetters([
      "setting",
      "userInfo",
      "isCollapse",
      "isHorizontal"
    ])
  },
  methods: {
    setCollapse () {
      this.$store.commit("SET_COLLAPSE");
    },
    logout () {
      this.$confirm(this.$t("logoutTip"), this.$t("tip"), {
        confirmButtonText: this.$t("submitText"),
        cancelButtonText: this.$t("cancelText"),
        type: "warning"
      }).then(() => {
        this.$store.dispatch("LogOut").then(() => {
          this.$router.push({ path: "/login" });
        });
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.top-console-title {
  height: 100%;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #1f2328;

  &__main {
    font-size: 15px;
    font-weight: 700;
  }

  &__sub {
    color: #7b8494;
    font-size: 12px;
    font-weight: 500;
  }
}
</style>
