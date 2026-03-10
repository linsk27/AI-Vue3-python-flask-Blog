// 让文件读懂import.meta.env等相关导入ts问题，防止报错
/// <reference types="vite/client" />
declare module '*.vue' {
    import { DefineComponent } from 'vue'
    const component: DefineComponent<{}, {}, any>
    export default component
}
