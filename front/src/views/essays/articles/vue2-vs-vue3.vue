<!--
 * @Author: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @Date: 2025-05-03 15:45:21
 * @LastEditors: linsk27 14062626+linsk27@user.noreply.gitee.com
 * @LastEditTime: 2025-07-23 16:07:49
 * @FilePath: \performance\src\views\index.vue
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
<template>
    <div class="teach-page">
        <div class="header-row">
            <h1>Vue2 vs Vue3 响应式原理深度对比</h1>
            <button class="reset-btn" @click="resetAll">重置演示</button>
        </div>
        <p class="desc">本页面通过自实现代码和交互演示，深入对比 <b>Vue2</b>（Object.defineProperty）与 <b>Vue3</b>（Proxy）响应式原理的本质区别。</p>

        <div class="compare-row">
            <!-- Vue2 响应式原理区 -->
            <section class="compare-card">
                <h2>Vue2 响应式原理（Object.defineProperty）</h2>
                <div class="sub-title">只能劫持初始化时已存在属性，新增属性无响应</div>
                <DataBlock :data="vue2View" :key="vue2Version" />
                <div class="btns">
                    <button @click="vue2Change">修改 title</button>
                    <button @click="vue2AddProp">新增属性 a</button>
                    <button @click="vue2ForceUpdate">手动刷新视图</button>
                </div>
                <div class="explain">
                    <ul>
                        <li>修改已存在属性，视图可响应（需手动刷新）</li>
                        <li>尝试新增属性 <code>a</code>，视图不会响应（即使手动刷新，模板也不会显示新属性）</li>
                    </ul>
                    <div v-if="vue2AddMsg" class="tip">{{ vue2AddMsg }}</div>
                </div>
                <div class="code-block">
                    <div class="code-title">核心实现</div>
                    <pre v-pre><code>// Vue2 响应式原理
const data2 = &#123; title: '首页', description: '欢迎来到首页' &#125;
const vue2View = &#123;&#125;
for (const key in data2) &#123;
  Object.defineProperty(vue2View, key, &#123;
    get() &#123; return data2[key] &#125;,
    set(val) &#123; data2[key] = val &#125;
  &#125;)
&#125;
// 新增属性不会被劫持，视图不会响应
</code></pre>
                </div>
            </section>

            <!-- Vue3 响应式原理区 -->
            <section class="compare-card">
                <h2>Vue3 响应式原理<br>（Proxy）</h2>
                <div class="sub-title">可劫持所有属性，新增/删除属性也能响应</div>
                <DataBlock :data="vue3View" :key="vue3Version">
                    <template #default>
                        <div v-if="'a' in vue3View"><b>a:</b> {{ vue3View.a }}</div>
                    </template>
                </DataBlock>
                <div class="btns">
                    <button @click="vue3Change">修改 title</button>
                    <button @click="vue3AddProp">新增属性 a</button>
                    <button @click="vue3ForceUpdate">手动刷新视图</button>
                </div>
                <div class="explain">
                    <ul>
                        <li>修改已存在属性，视图可响应（需手动刷新）</li>
                        <li>新增属性 <code>a</code>，视图也能响应（手动刷新后可见）</li>
                    </ul>
                    <div class="tip" style="margin-top:10px;">
                        <b>补充说明：</b> 本页面自实现的 Proxy 只是还原原理，<br>
                        只有用 Vue 框架的 reactive/ref，才会自动刷新视图。<br>
                        <b>Vue3：</b> Proxy 能追踪所有属性，新增/删除属性都能响应。
                    </div>
                </div>
                <div class="code-block">
                    <div class="code-title">核心实现</div>
                    <pre v-pre><code>// Vue3 响应式原理
            const data3 = &#123; title: '首页', description: '欢迎来到首页' &#125;
            const vue3View = new Proxy(data3, &#123;
            get(target, key) &#123; return target[key] &#125;,
            set(target, key, val) &#123; target[key] = val; return true &#125;
            &#125;)
            // 新增属性也能被劫持，视图可响应
        </code></pre>
                </div>
            </section>
        </div>
        <!-- 实际数据结构展示区 -->
        <section class="card">
            <h2>实际数据结构（观察数据变化）</h2>
            <div class="data-struct-row">
                <div class="data-struct-block">
                    <div class="data-struct-title">Vue2 data2</div>
                    <pre class="data-struct-json">{{ data2Snapshot }}</pre>
                </div>
                <div class="data-struct-block">
                    <div class="data-struct-title">Vue3 data3</div>
                    <pre class="data-struct-json">{{ data3Snapshot }}</pre>
                </div>
            </div>
            <div class="tip" style="margin-top:8px;">你可以点击上方按钮，观察数据结构的实时变化。</div>
        </section>
        <!-- Vue 2 进阶：Dep/Watcher -->
        <section class="card">
            <h2>Vue 2 响应式进阶：Dep/Watcher 体系</h2>
            <div class="explain">
                <p><b>你完全正确！</b>以上演示为了简化，省略了 Vue 2 响应式的核心：<b>Dep/Watcher</b> 体系，这才是实现自动更新的关键。</p>
                <ul>
                    <li><b>Dep (Dependency):</b> 每个响应式属性都有一个 <code>Dep</code> 实例，它像一个订阅者列表，存放所有依赖此属性的 "Watcher"。</li>
                    <li><b>Watcher (或 Effect):</b> 当一段代码依赖某个属性时，它就被包装成一个 "Watcher"。当属性变化，Watcher 就会重新执行。</li>
                </ul>
                <p><b>工作流程：</b></p>
                <ol>
                    <li><b>依赖收集:</b> Watcher 运行时，会读取属性，触发 <code>get</code>。<code>get</code> 会调用
                        <code>dep.depend()</code> 将当前
                        Watcher 添加到订阅者列表。
                    </li>
                    <li><b>派发更新:</b> 修改属性时，触发 <code>set</code>。<code>set</code> 会调用
                        <code>dep.notify()</code>，通知所有订阅者（Watcher）重新执行，从而实现视图的自动更新。
                    </li>
                </ol>
            </div>
            <div class="data-block" style="background: #fffbe6; border-color: #fdd835;">
                <div><b>自动更新的标题:</b> {{ depDemo.title }}</div>
            </div>
            <div class="btns">
                <button @click="changeDepDemoTitle">修改标题 (视图将自动更新)</button>
            </div>
            <div class="code-block">
                <div class="code-title">Dep/Watcher 核心实现</div>
                <pre v-pre><code>class Dep {
                constructor() { this.subscribers = new Set() }
                depend() { if (activeEffect) this.subscribers.add(activeEffect) }
                notify() { this.subscribers.forEach(effect => effect()) }
                }

                let activeEffect = null
                function watchEffect(effect) {
                activeEffect = effect
                effect()
                activeEffect = null
                }

                function defineReactive(obj, key, val) {
                const dep = new Dep()
                Object.defineProperty(obj, key, {
                get() {
                dep.depend() // 依赖收集
                return val
                },
                set(newVal) {
                val = newVal
                dep.notify() // 派发更新
                }
                })
                }

                // Demo
                const reactiveDepDemo = {}
                defineReactive(reactiveDepDemo, 'title', '初始标题')

                // 这个 watchEffect 会自动追踪依赖
                // 当 reactiveDepDemo.title 变化时，它会自动重新执行
                watchEffect(() => {
                // 这行代码读取了 title，触发 get，将自身（effect）添加到了 dep 的订阅者列表
                // 在真实 Vue 中，这里会是更新 DOM 的操作
                console.log('新标题是:', reactiveDepDemo.title)
                depDemo.value.title = reactiveDepDemo.title // 更新视图
                })
            </code></pre>
            </div>
        </section>



        <section class="summary-card">
            <h2>Vue2 vs Vue3 响应式原理对比总结</h2>
            <ul>
                <li><b>Vue2：</b> 只能劫持初始化时已存在属性，新增/删除属性无响应，数组变动需特殊API。</li>
                <li><b>Vue3：</b> Proxy 可劫持所有属性，新增/删除属性、数组等都能响应，能力更强。</li>
                <li>Vue3 响应式原理是对 Vue2 的本质升级，解决了 Vue2 的所有响应式局限。</li>
            </ul>
        </section>
    </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'
import DataBlock from '../components/DataBlock.vue'
// --- Vue2 响应式原理自实现 ---
const data2: Record<string, any> = {
    title: '首页',
    description: '欢迎来到首页'
}
const vue2View: Record<string, any> = {}
for (const key in data2) {
    Object.defineProperty(vue2View, key, {
        get() { return data2[key] },
        set(val) { data2[key] = val }
    })
}
const vue2Version = ref(0)
const vue2AddMsg = ref('')
function vue2Change() {
    vue2View.title = 'Vue2: 修改后的标题'
    // 不刷新视图
}
function vue2AddProp() {
    data2.a = '新属性'
    vue2AddMsg.value = '新增属性 a 不会被响应式系统追踪，模板不会自动显示新属性。'
}
function vue2ForceUpdate() {
    vue2Version.value++
}
function vue2Reset() {
    data2.title = '首页'
    data2.description = '欢迎来到首页'
    delete data2.a
    vue2AddMsg.value = ''
    vue2Version.value++
}

// --- Vue3 响应式原理自实现 ---
const data3: Record<string, any> = {
    title: '首页',
    description: '欢迎来到首页'
}
const vue3View = new Proxy(data3, {
    get(target, key) { return target[key as string] },
    set(target, key, val) { target[key as string] = val; return true }
})
const vue3Version = ref(0)
function vue3Change() {
    vue3View.title = 'Vue3: 修改后的标题'
}
function vue3AddProp() {
    vue3View.a = '新属性'
}
function vue3ForceUpdate() {
    vue3Version.value++
}
function vue3Reset() {
    data3.title = '首页'
    data3.description = '欢迎来到首页'
    delete data3.a
    vue3Version.value++
}
function resetAll() {
    vue2Reset()
    vue3Reset()
    depDemoReset()
}

// --- Dep/Watcher Demo ---
class Dep {
    subscribers: Set<Function>
    constructor() {
        this.subscribers = new Set()
    }
    depend() {
        if (activeEffect) {
            this.subscribers.add(activeEffect)
        }
    }
    notify() {
        this.subscribers.forEach(effect => effect())
    }
}

let activeEffect: Function | null = null
function watchEffect(effect: Function) {
    activeEffect = effect
    effect()
    activeEffect = null
}

const depDemo = ref({ title: '初始标题' })
const reactiveDepDemo: { title?: string } = {}
defineReactive(reactiveDepDemo, 'title', '初始标题')

// The effect that updates our view model (the ref)
watchEffect(() => {
    depDemo.value.title = reactiveDepDemo.title!
})

function defineReactive(obj: Record<string, any>, key: string, val: any) {
    const dep = new Dep()
    Object.defineProperty(obj, key, {
        get() {
            dep.depend()
            return val
        },
        set(newVal) {
            val = newVal
            dep.notify()
        }
    })
}

function changeDepDemoTitle() {
    reactiveDepDemo.title = `Updated at ${new Date().toLocaleTimeString()}`
}
function depDemoReset() {
    defineReactive(reactiveDepDemo, 'title', '初始标题')
    depDemo.value.title = '初始标题'
}

// 数据结构快照
const data2Snapshot = ref(JSON.stringify(data2, null, 2))
const data3Snapshot = ref(JSON.stringify(data3, null, 2))
watch(vue2Version, () => {
    data2Snapshot.value = JSON.stringify(data2, null, 2)
})
watch(vue3Version, () => {
    data3Snapshot.value = JSON.stringify(data3, null, 2)
})
</script>

<style scoped>
.teach-page {
    margin: 0 auto;
    border-radius: 0;
    box-shadow: none;
    font-family: 'Inter', 'Segoe UI', 'PingFang SC', 'Hiragino Sans', Arial, sans-serif;
}

.header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
    padding: 0 0 0 0;
}

.reset-btn {
    background: #FF7F50;
    color: #fff;
    border: none;
    border-radius: 5px;
    padding: 7px 22px;
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(255, 127, 80, 0.2);
    transition: background 0.2s, color 0.2s, box-shadow 0.2s;
}

.reset-btn:hover {
    background: #E67E22;
    color: #fff;
    box-shadow: 0 4px 16px rgba(255, 127, 80, 0.3);
}

.desc {
    color: #333;
    margin-bottom: 32px;
    font-size: 17px;
    letter-spacing: 0.2px;
    padding: 0 0 0 0;
}

.compare-row {
    display: flex;
    gap: 24px;
    margin-bottom: 44px;
    padding: 0 0 0 0;
    flex-wrap: wrap;
}

.compare-card {
    flex: 1 1 320px;
    border-radius: 10px;
    border: 1px solid #e3e8ee;
    padding: 18px 12px 14px 12px;
    min-width: 220px;
    background: transparent;
    box-shadow: none;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    transition: border 0.2s;
    margin-bottom: 0;
}

.compare-card:hover {
    border: 1px solid #FF7F50;
    background: #fff8f5;
}

.compare-card h2 {
    font-size: 20px;
    color: #FF7F50;
    margin-bottom: 6px;
    letter-spacing: 0.2px;
    font-weight: 600;
}

.sub-title {
    color: #FF7F50;
    font-size: 14px;
    margin-bottom: 12px;
    font-weight: 500;
}

.data-block {
    box-sizing: border-box;
    background: #f4f6fa;
    border-radius: 8px;
    padding: 16px 18px;
    margin-bottom: 14px;
    width: 100%;
    font-size: 15px;
    box-shadow: 0 1px 4px #0001;
    border: 1px solid #e3e8ee;
}

.btns {
    margin: 8px 0 10px 0;
}

.btns button {
    background: #FF7F50;
    color: #fff;
    border: none;
    border-radius: 5px;
    padding: 7px 18px;
    margin-right: 10px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    box-shadow: 0 1px 6px rgba(255, 127, 80, 0.2);
    transition: background 0.2s, box-shadow 0.2s;
}

.btns button:hover {
    background: #E67E22;
    box-shadow: 0 2px 12px rgba(255, 127, 80, 0.3);
}

.explain {
    color: #666;
    font-size: 14px;
    margin-top: 2px;
    margin-bottom: 2px;

    ul {
        padding: 0;
    }
}

.card {
    border-radius: 10px;
    /* border: 1px solid #e3e8ee; */
    background: transparent;
    box-shadow: none;
    padding: 16px 10px;
    margin-bottom: 24px;
}

.summary-card {
    border-radius: 10px;
    border: 1px solid rgba(255, 127, 80, 0.15);
    background: #fff8f5;
    box-shadow: none;
    padding: 18px 12px;
    margin-bottom: 28px;
    margin-top: 18px;
}

.summary-card h2 {
    color: #FF7F50;
    font-size: 20px;
    margin-bottom: 10px;
    letter-spacing: 0.2px;
    font-weight: 600;
}

.summary-card ul {
    font-size: 15px;
    color: #222;
    margin-bottom: 0;
    line-height: 1.8;
}

.code-block {
    background: #23272f;
    color: #e6e6e6;
    border-radius: 6px;
    margin: 14px 0;
    padding: 12px 10px;
    font-size: 14px;
    overflow-x: auto;
    box-shadow: 0 1px 6px #0002;
    border: 1px solid #23272f;

    pre {
        margin: 0;
        white-space: pre-wrap;
        word-break: break-all;
    }
}

.code-title {
    color: #FF7F50;
    font-weight: 600;
    margin-bottom: 4px;
}

.data-struct-row {
    display: flex;
    gap: 24px;
    margin-bottom: 0;
    padding: 0 0 0 0;
    flex-wrap: wrap;
}

.data-struct-block {
    flex: 1 1 320px;
    background: #f7f9fb;
    border-radius: 8px;
    padding: 12px 10px;
    min-width: 180px;
    box-shadow: 0 1px 4px #0001;
    border: 1px solid #e3e8ee;
}

.data-struct-title {
    color: #FF7F50;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 6px;
}

.data-struct-json {
    font-size: 14px;
    color: #333;
    background: #f4f6fa;
    border-radius: 4px;
    padding: 8px 10px;
    margin: 0;
    white-space: pre-wrap;
    word-break: break-all;
    border: 1px solid #e3e8ee;
}

.tip {
    color: #d32f2f;
    font-size: 14px;
    margin-top: 8px;
}

@media (max-width: 900px) {
    .teach-page {
        max-width: 100vw;
        padding: 0 4vw 32px 4vw;
    }

    .compare-row,
    .data-struct-row {
        flex-direction: column;
        gap: 16px;
        padding: 0;
    }

    .compare-card,
    .data-struct-block {
        min-width: unset;
        padding: 12px 4vw 10px 4vw;
    }

    .card,
    .summary-card {
        padding: 12px 4vw;
    }
}

@media (max-width: 600px) {
    .teach-page {
        padding: 0 2vw 24px 2vw;
    }

    .compare-card,
    .data-struct-block,
    .card,
    .summary-card {
        padding-left: 2vw;
        padding-right: 2vw;
    }
}
</style>
