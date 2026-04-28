<template>
  <el-color-picker size="small"
                   class="theme-picker"
                   popper-class="theme-picker-dropdown"
                   v-model="themeVal"></el-color-picker>
</template>

<script>
import { mapGetters } from "vuex"; // default color
export default {
  name: "topColor",
  data () {
    return {
      themeVal: '#409EFF'
    };
  },
  created () {
    this.themeVal = this.colorName;
  },
  watch: {
    themeVal (val, oldVal) {
      this.$store.commit("SET_COLOR_NAME", val);
      this.updateTheme(val, oldVal);
    }
  },
  computed: {
    ...mapGetters(["colorName"])
  },
  methods: {
    hexToRgb (str) {
      let hexs = '';
      str = str.replace('#', '');
      hexs = str.match(/../g);
      for (let i = 0; i < 3; i++) hexs[i] = parseInt(hexs[i], 16);
      return hexs;
    },
    // r 代表红色 | g 代表绿色 | b 代表蓝色
    rgbToHex (r, g, b) {
      let hexs = [r.toString(16), g.toString(16), b.toString(16)];
      for (let i = 0; i < 3; i++) if (hexs[i].length == 1) hexs[i] = `0${hexs[i]}`;
      return `#${hexs.join('')}`;
    },

    getDarkColor (color, level) {
      let rgb = this.hexToRgb(color);
      for (let i = 0; i < 3; i++) rgb[i] = Math.floor(rgb[i] * (1 - level));
      return this.rgbToHex(rgb[0], rgb[1], rgb[2]);
    },

    // color 颜色值字符串 | level 加深的程度，限0-1之间
    getLightColor (color, level) {
      let rgb = this.hexToRgb(color);
      for (let i = 0; i < 3; i++) rgb[i] = Math.floor((255 - rgb[i]) * level + rgb[i]);
      return this.rgbToHex(rgb[0], rgb[1], rgb[2]);
    },

    updateTheme (e) {
      if (!e) return
      // e就是选择了的颜色
      const pre = "--el-color-primary";
      const el = document.documentElement;
      el.style.setProperty(pre, e);
      el.style.setProperty("--admin-primary", e);
      el.style.setProperty("--admin-primary-hover", this.getDarkColor(e, 0.16));
      el.style.setProperty("--admin-primary-soft", this.getLightColor(e, 0.92));
      // 这里是覆盖原有颜色的核心代码
      for (let i = 1; i < 10; i += 1) {
        document.documentElement.style.setProperty(`${pre}-light-${i}`, `${this.getLightColor(e, i / 10)}`)
      }
    }
  }
};
</script>
