<template>
  <div class="avue-logo">
    <transition name="fade">
      <span
            v-if="getScreen(isCollapse)"
            class="avue-logo_mark"
            key="0">
        {{website.logo}}
      </span>
    </transition>
    <transition-group name="fade">
      <template v-if="getScreen(!isCollapse)">
        <span class="avue-logo_brand"
              key="1">
          <span class="avue-logo_mark">{{website.logo}}</span>
          <span class="avue-logo_copy">
            <strong>{{website.title}}</strong>
            <small>ContextForge Ops</small>
          </span>
        </span>
      </template>
    </transition-group>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
export default {
  name: "logo",
  data () {
    return {};
  },
  created () { },
  computed: {
    ...mapGetters(["isCollapse"])
  },
  methods: {}
};
</script>
