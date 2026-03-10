/*
 * @Author: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @Date: 2025-07-23 15:11:47
 * @LastEditors: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @LastEditTime: 2025-07-23 16:46:54
 * @FilePath: \performance\src\views\essays\articles\index.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
// src/views/essays/articles/index.ts
export const articles = [
    {
        id: 'vue2-vs-vue3',
        title: 'Vue2 vs Vue3 响应式原理深度对比',
        summary: '对比 Vue2 和 Vue3 响应式原理，配合交互演示。',
        component: () => import('./vue2-vs-vue3.vue'),
        tags: ['Vue', '响应式', '原理']
    },
    {
        id: '伪元素',
        title: 'CSS 伪元素详解',
        summary: '深入探讨 CSS 伪元素的用法和实现原理。',
        component: () => import('./pseudo-elements.vue'),
        tags: ['CSS', '伪元素', '原理']
    }
]
