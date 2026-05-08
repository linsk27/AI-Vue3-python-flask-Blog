<template>
    <div class="access-page">
        <header class="access-header">
            <div>
                <span class="eyebrow">Access Control</span>
                <h1>权限管理</h1>
                <p>管理账号、角色与权限边界。</p>
            </div>
            <button class="refresh-btn" type="button" :disabled="loading" @click="loadAll">
                <RefreshRight class="button-icon" />
                <span>{{ loading ? '刷新中' : '刷新' }}</span>
            </button>
        </header>

        <section class="metric-grid">
            <article class="metric-card">
                <User class="metric-icon" />
                <span>用户</span>
                <strong>{{ users.length }}</strong>
            </article>
            <article class="metric-card">
                <Key class="metric-icon" />
                <span>角色</span>
                <strong>{{ roles.length }}</strong>
            </article>
            <article class="metric-card">
                <Lock class="metric-icon" />
                <span>权限点</span>
                <strong>{{ permissions.length }}</strong>
            </article>
        </section>

        <div class="panel-switch">
            <button type="button" :class="{ active: activePanel === 'users' }" @click="activePanel = 'users'">
                用户
            </button>
            <button type="button" :class="{ active: activePanel === 'roles' }" @click="activePanel = 'roles'">
                角色
            </button>
        </div>

        <section v-if="activePanel === 'users'" class="panel-section">
            <div class="panel-heading">
                <div>
                    <h2>用户角色</h2>
                    <p>调整用户所属角色，角色权限会在下次登录或刷新用户信息后生效。</p>
                </div>
                <div class="filter-row">
                    <el-input v-model="userFilters.username" clearable placeholder="用户名" />
                    <el-input v-model="userFilters.email" clearable placeholder="邮箱" />
                    <el-button :loading="loadingUsers" @click="loadUsers">筛选</el-button>
                </div>
            </div>

            <el-table :data="users" stripe class="access-table" v-loading="loadingUsers">
                <el-table-column prop="username" label="用户" min-width="160">
                    <template #default="{ row }">
                        <div class="user-cell">
                            <el-avatar :size="30" :src="row.avatar || defaultAvatar" />
                            <div>
                                <strong>{{ row.username }}</strong>
                                <small>ID {{ row.id }}</small>
                            </div>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column prop="email" label="邮箱" min-width="180">
                    <template #default="{ row }">
                        <el-input v-model="row.email" placeholder="未设置" />
                    </template>
                </el-table-column>
                <el-table-column label="角色" min-width="190">
                    <template #default="{ row }">
                        <el-select v-model="row.role_id" placeholder="选择角色" filterable>
                            <el-option v-for="role in roles" :key="role.id" :label="formatRoleLabel(role)" :value="role.id" />
                        </el-select>
                    </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" min-width="170">
                    <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
                </el-table-column>
                <el-table-column label="操作" width="210" fixed="right">
                    <template #default="{ row }">
                        <el-button size="small" type="primary" :loading="savingUserId === row.id" @click="saveUser(row)">
                            保存
                        </el-button>
                        <el-popconfirm
                            title="确定删除这个用户吗？"
                            confirm-button-text="删除"
                            cancel-button-text="取消"
                            @confirm="deleteUser(row)"
                        >
                            <template #reference>
                                <el-button size="small" :disabled="row.id === globalStore.userInfo?.id">删除</el-button>
                            </template>
                        </el-popconfirm>
                    </template>
                </el-table-column>
            </el-table>
        </section>

        <section v-else class="panel-section">
            <div class="panel-heading">
                <div>
                    <h2>角色权限</h2>
                    <p>角色决定账号能否使用 AI、上下文包、系统自检和后台管理。</p>
                </div>
            </div>

            <form class="role-create" @submit.prevent="createRole">
                <el-input v-model="roleForm.name" placeholder="角色标识，例如 editor" />
                <el-input v-model="roleForm.description" placeholder="角色说明" />
                <el-select v-model="roleForm.permissions" multiple filterable collapse-tags collapse-tags-tooltip placeholder="权限点">
                    <el-option v-for="permission in permissions" :key="permission.id" :label="formatPermission(permission)" :value="permission.id" />
                </el-select>
                <el-button type="primary" native-type="submit" :loading="creatingRole">创建角色</el-button>
            </form>

            <div class="role-list">
                <article v-for="role in roles" :key="role.id" class="role-card">
                    <div class="role-card-head">
                        <div>
                            <strong>{{ formatRoleLabel(role) }}</strong>
                            <span>{{ role.description || '未填写说明' }}</span>
                        </div>
                        <el-tag :type="isBuiltinRole(role) ? 'warning' : 'info'">
                            {{ isBuiltinRole(role) ? '内置' : '自定义' }}
                        </el-tag>
                    </div>

                    <el-select
                        v-model="role.permissions"
                        multiple
                        filterable
                        collapse-tags
                        collapse-tags-tooltip
                        class="permission-select"
                        :disabled="isBuiltinRole(role)"
                        placeholder="选择权限点"
                    >
                        <el-option v-for="permission in permissions" :key="permission.id" :label="formatPermission(permission)" :value="permission.id" />
                    </el-select>

                    <div class="role-actions">
                        <el-button size="small" type="primary" :disabled="isBuiltinRole(role)" :loading="savingRoleId === role.id" @click="saveRole(role)">
                            保存权限
                        </el-button>
                        <el-popconfirm
                            title="确定删除这个角色吗？"
                            confirm-button-text="删除"
                            cancel-button-text="取消"
                            @confirm="deleteRole(role)"
                        >
                            <template #reference>
                                <el-button size="small" :disabled="isBuiltinRole(role)">删除</el-button>
                            </template>
                        </el-popconfirm>
                    </div>
                </article>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Key, Lock, RefreshRight, User } from '@element-plus/icons-vue'
import adminApi, { type AdminPermission, type AdminRole, type AdminUser } from '@/api/modules/admin'
import { useElMessage } from '@/hooks/useMessage'
import { useGlobalStore } from '@/store'

const { message } = useElMessage()
const globalStore = useGlobalStore()
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const activePanel = ref<'users' | 'roles'>('users')
const loadingUsers = ref(false)
const loadingRoles = ref(false)
const creatingRole = ref(false)
const savingUserId = ref<number | null>(null)
const savingRoleId = ref<number | null>(null)
const users = ref<AdminUser[]>([])
const roles = ref<AdminRole[]>([])
const permissions = ref<AdminPermission[]>([])
const userFilters = reactive({
    username: '',
    email: ''
})
const roleForm = reactive({
    name: '',
    description: '',
    permissions: [] as number[]
})

const loading = computed(() => loadingUsers.value || loadingRoles.value)
const builtinRoles = new Set(['admin', 'user'])

const formatTime = (value?: string) => {
    if (!value) return '-'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return value
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const formatRoleLabel = (role: AdminRole) => {
    const labels: Record<string, string> = {
        admin: '管理员',
        user: '普通用户'
    }
    return labels[role.name] || role.name
}

const formatPermission = (permission: AdminPermission) => {
    return `${permission.name || permission.code} (${permission.code})`
}

const isBuiltinRole = (role: AdminRole) => Boolean(role.readonly) || builtinRoles.has(role.name)

const loadUsers = async () => {
    loadingUsers.value = true
    try {
        users.value = await adminApi.getUsers({
            username: userFilters.username.trim() || undefined,
            email: userFilters.email.trim() || undefined
        })
    } finally {
        loadingUsers.value = false
    }
}

const loadRolesAndPermissions = async () => {
    loadingRoles.value = true
    try {
        const [roleList, permissionList] = await Promise.all([
            adminApi.getRoles(),
            adminApi.getPermissions()
        ])
        roles.value = roleList.map(role => ({
            ...role,
            permissions: Array.isArray(role.permissions) ? role.permissions : []
        }))
        permissions.value = permissionList
    } finally {
        loadingRoles.value = false
    }
}

const loadAll = async () => {
    await Promise.all([loadRolesAndPermissions(), loadUsers()])
}

const saveUser = async (user: AdminUser) => {
    if (!user.username?.trim()) {
        message.warning('用户名不能为空')
        return
    }

    savingUserId.value = user.id
    try {
        await adminApi.updateUser(user.id, {
            username: user.username.trim(),
            avatar: user.avatar || '',
            email: user.email || '',
            role_id: user.role_id || null
        })
        message.success('用户已更新')
        await loadUsers()
    } finally {
        savingUserId.value = null
    }
}

const deleteUser = async (user: AdminUser) => {
    await adminApi.deleteUser(user.id)
    message.success('用户已删除')
    await loadUsers()
}

const createRole = async () => {
    if (!roleForm.name.trim()) {
        message.warning('角色标识不能为空')
        return
    }

    creatingRole.value = true
    try {
        await adminApi.createRole({
            name: roleForm.name.trim(),
            description: roleForm.description.trim(),
            permissions: roleForm.permissions
        })
        roleForm.name = ''
        roleForm.description = ''
        roleForm.permissions = []
        message.success('角色已创建')
        await loadRolesAndPermissions()
    } finally {
        creatingRole.value = false
    }
}

const saveRole = async (role: AdminRole) => {
    if (isBuiltinRole(role)) {
        message.warning('Built-in roles are read-only')
        return
    }

    savingRoleId.value = role.id
    try {
        await adminApi.updateRole(role.id, {
            name: role.name,
            description: role.description || '',
            permissions: role.permissions || []
        })
        message.success('角色权限已更新')
        await loadRolesAndPermissions()
    } finally {
        savingRoleId.value = null
    }
}

const deleteRole = async (role: AdminRole) => {
    await adminApi.deleteRole(role.id)
    message.success('角色已删除')
    await loadRolesAndPermissions()
}

onMounted(loadAll)
</script>

<style scoped>
.access-page {
    width: var(--page-width);
    min-height: calc(100vh - 140px);
    margin: 0 auto;
    padding: 48px 0 76px;
    color: var(--text-primary);
}

.access-header,
.panel-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 20px;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    height: 24px;
    padding: 0 10px;
    border-radius: 999px;
    color: var(--badge-fg);
    background: var(--badge-bg);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
}

.access-header h1,
.panel-heading h2 {
    margin: 14px 0 0;
    font-size: 44px;
    line-height: 1.08;
}

.panel-heading h2 {
    font-size: 30px;
}

.access-header p,
.panel-heading p,
.role-card-head span,
.user-cell small {
    color: var(--text-secondary);
}

.refresh-btn,
.panel-switch button,
.role-create button {
    min-height: 38px;
    border: 0;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
}

.refresh-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0 14px;
    color: var(--button-fg);
    background: var(--button-bg);
}

.button-icon,
.metric-icon {
    width: 18px;
    height: 18px;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin: 24px 0 18px;
}

.metric-card,
.panel-section,
.role-card {
    background: var(--surface);
    box-shadow: var(--card-shadow);
}

.metric-card {
    min-height: 112px;
    padding: 20px;
    border-radius: 12px;
    display: grid;
    gap: 8px;
}

.metric-card span {
    color: var(--text-secondary);
    font-weight: 600;
}

.metric-card strong {
    font-size: 34px;
    line-height: 1;
}

.metric-icon {
    color: var(--focus-blue);
}

.panel-switch {
    display: inline-flex;
    padding: 4px;
    border-radius: 12px;
    background: var(--surface-subtle);
    box-shadow: var(--ring);
}

.panel-switch button {
    min-width: 84px;
    padding: 0 14px;
    color: var(--text-secondary);
    background: transparent;
}

.panel-switch button.active {
    color: var(--button-fg);
    background: var(--button-bg);
}

.panel-section {
    margin-top: 16px;
    padding: 22px;
    border-radius: 12px;
}

.filter-row,
.role-create {
    display: grid;
    gap: 10px;
}

.filter-row {
    grid-template-columns: 160px 190px 86px;
    align-items: center;
}

.role-create {
    grid-template-columns: minmax(150px, 0.7fr) minmax(180px, 1fr) minmax(260px, 1.4fr) auto;
    margin: 18px 0;
}

.access-table {
    margin-top: 18px;
}

.user-cell,
.role-card-head,
.role-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.user-cell > div,
.role-card-head > div {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.role-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 14px;
}

.role-card {
    padding: 18px;
    border-radius: 12px;
}

.role-card-head {
    justify-content: space-between;
}

.permission-select {
    width: 100%;
    margin-top: 14px;
}

.role-actions {
    justify-content: flex-end;
    margin-top: 14px;
}

@media (max-width: 900px) {
    .access-header,
    .panel-heading {
        align-items: flex-start;
        flex-direction: column;
    }

    .metric-grid,
    .role-create,
    .filter-row {
        grid-template-columns: 1fr;
    }
}
</style>
