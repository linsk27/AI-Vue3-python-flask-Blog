<template>
    <el-form class="login-form" status-icon :rules="loginRules" ref="loginForm" :model="loginForm" label-width="0">
        <el-form-item prop="username">
            <el-input @keyup.enter="handleLogin" v-model="loginForm.username" auto-complete="off"
                :placeholder="$t('login.username')">
                <template #prefix>
                    <i class="icon-yonghu"></i>
                </template>
            </el-input>
        </el-form-item>
        <el-form-item prop="password">
            <el-input @keyup.enter="handleLogin" type="password" show-password v-model="loginForm.password"
                auto-complete="off" :placeholder="$t('login.password')">
                <template #prefix>
                    <i class="icon-mima"></i>
                </template>
            </el-input>
        </el-form-item>
        <el-form-item prop="code">
            <el-input @keyup.enter="handleLogin" :maxlength="code.len" v-model="loginForm.code" auto-complete="off"
                :placeholder="$t('login.code')">
                <template #prefix>
                    <i class="icon-yanzhengma"></i>
                </template>
                <template #append>
                    <div class="login-code">
                        <span class="login-code-img" @click="refreshCode" v-if="code.type == 'text'">{{ code.value
                        }}</span>
                        <img :src="code.src" class="login-code-img" @click="refreshCode" v-else />
                        <!-- <i class="icon-shuaxin login-code-icon" @click="refreshCode"></i> -->
                    </div>
                </template>
            </el-input>
        </el-form-item>

        <el-form-item>
            <el-button type="primary" @click.prevent="handleLogin" class="login-submit">{{ $t('login.submit')
            }}</el-button>
        </el-form-item>
    </el-form>
</template>

<script>
import { randomLenNum } from "utils/util";
import { mapGetters } from "vuex";
export default {
    name: "userlogin",
    data() {
        const validateCode = (rule, value, callback) => {
            if (this.code.value != value) {
                this.loginForm.code = "";
                this.refreshCode();
                callback(new Error("请输入正确的验证码"));
            } else {
                callback();
            }
        };
        return {
            loginForm: {
                username: "",
                password: "",
                code: "",
                redomStr: ""
            },
            checked: false,
            code: {
                src: "",
                value: "",
                len: 4,
                type: "text"
            },
            loginRules: {
                username: [
                    { required: true, message: "请输入管理员账号", trigger: "blur" }
                ],
                password: [
                    { required: true, message: "请输入登录密码", trigger: "blur" },
                    { min: 5, message: "密码长度不能少于 5 位", trigger: "blur" }
                ],
                code: [
                    { required: true, message: "请输入验证码", trigger: "blur" },
                    { min: 4, max: 4, message: "验证码长度为 4 位", trigger: "blur" },
                    { required: true, trigger: "blur", validator: validateCode }
                ]
            }
        };
    },
    created() {
        this.refreshCode();
    },
    mounted() { },
    computed: {
        ...mapGetters(["tagWel"])
    },
    props: [],
    methods: {
        refreshCode() {
            this.loginForm.redomStr = randomLenNum(this.code.len, true);
            this.code.type == "text"
                ? (this.code.value = randomLenNum(this.code.len))
                : (this.code.src = `/${this.loginForm.redomStr}`);
            this.loginForm.code = this.code.value;
        },
        handleLogin() {
            this.$refs.loginForm.validate(valid => {
                if (valid) {
                    this.$store.dispatch("LoginByUsername", this.loginForm).then((res) => {
                        // 获取用户信息
                        const userInfo = this.$store.getters.userInfo;
                        // 校验角色，如果不是管理员则禁止登录
                        if (userInfo && userInfo.role !== 'admin') {
                            this.$message.error("当前账号没有后台访问权限，请使用管理员账号登录");
                            this.$store.dispatch("LogOut");
                            return;
                        }
                        this.$router.push(this.tagWel);
                    }).catch(error => {
                        // 错误提示优化，使用后端返回的 msg
                        const msg = error.response?.data?.msg || error.message || '登录失败，请检查账号或服务状态';
                        this.$message.error(msg);
                    });
                }
            });
        }
    }
};
</script>

<style></style>
