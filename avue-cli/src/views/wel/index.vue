<template>
  <div>
    <div class="wel__header">
      <div class="wel__info">
        <img :src="userInfo.avatar"
             alt=""
             class="wel__info-img">
        <div class="wel__info-content">
          <div class="wel__info-title">
            {{$t('wel.info')}}
          </div>
          <div class="wel__info-subtitle">
            {{$t('wel.dept')}}
          </div>
        </div>
      </div>
      <div class="wel__extra">
        <div class="wel__extra-item">
          <p class="wel__extra-title">
            {{ $t('wel.count')}}
          </p>
          <p class="wel__extra-subtitle">
            56
          </p>
        </div>
        <div class="wel__extra-item">
          <p class="wel__extra-title">
            {{ $t('wel.team')}}
          </p>
          <p class="wel__extra-subtitle">
            8 <span>/ 24</span>
          </p>
        </div>
        <div class="wel__extra-item">
          <p class="wel__extra-title">

            {{ $t('wel.project')}}
          </p>
          <p class="wel__extra-subtitle">
            2,223
          </p>
        </div>
      </div>
    </div>
  </div>
  <dashboard></dashboard>
</template>

<script>
import { mapGetters } from "vuex";
import dashboard from './dashboard.vue'
export default {
  name: "wel",
  components: {
    dashboard
  },
  computed: {
    ...mapGetters(["userInfo"]),
  },
  created () { },
  methods: {}
};
</script>

<style scoped="scoped" lang="scss">
.wel {
  &__header {
    margin-bottom: 14px;
    padding: 24px;
    border-radius: 6px;
    background: var(--admin-surface);
    box-shadow: var(--admin-shadow);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 24px;
  }
  &__info {
    display: flex;
    align-items: center;
    &-img {
      border-radius: 72px;
      display: block;
      width: 72px;
      height: 72px;
      img {
        width: 100%;
        height: 100%;
        display: block;
      }
    }
    &-content {
      position: relative;
      margin-left: 24px;
      color: var(--admin-ink-soft);
      line-height: 22px;
    }
    &-title {
      font-size: 20px;
      line-height: 28px;
      font-weight: 700;
      color: var(--admin-ink);
      margin-bottom: 12px;
    }
    &-subtitle {
      position: relative;
      font-size: 14px;
      color: var(--admin-muted);
      line-height: 22px;
    }
  }
  &__extra {
    display: flex;
    align-items: center;
    &-item {
      position: relative;
      padding: 0 24px;
      &:last-child {
        &::after {
          display: none;
        }
      }
      &:after {
        background-color: var(--admin-line);
        position: absolute;
        top: 30px;
        right: 0;
        width: 1px;
        height: 40px;
        content: "";
      }
    }
    &-title {
      color: var(--admin-muted);
      font-size: 14px;
      line-height: 22px;
      margin-bottom: 4px;
    }
    &-subtitle {
      color: var(--admin-ink);
      font-size: 26px;
      line-height: 38px;
      margin: 0;
      span {
        color: var(--admin-muted);
        font-size: 20px;
      }
    }
  }
}

@media (max-width: 900px) {
  .wel {
    &__header {
      align-items: flex-start;
      flex-direction: column;
    }

    &__extra {
      width: 100%;
      justify-content: space-between;

      &-item {
        padding: 0 16px 0 0;
      }
    }
  }
}
</style>
