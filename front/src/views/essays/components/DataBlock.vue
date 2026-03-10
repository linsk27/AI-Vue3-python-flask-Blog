<!--
 * @Author: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @Date: 2025-07-22 02:34:23
 * @LastEditors: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @LastEditTime: 2025-07-23 14:47:48
 * @FilePath: \performance\src\views\essays\components\DataBlock.vue
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
<template>
  <div class="data-block">
    <div><b>title:</b> {{ data.title }}</div>
    <div><b>description:</b> {{ data.description }}</div>
    <slot></slot>
  </div>
</template>
<script setup lang="ts">
defineProps<{ data: any }>()
</script>
<style scoped>
.data-block {
  background: #f4f6fa;
  border-radius: 8px;
  padding: 16px 18px;
  margin-bottom: 14px;
  width: 100%;
  font-size: 15px;
  box-shadow: 0 1px 4px #0001;
  border: 1px solid #e3e8ee;
}
</style> 