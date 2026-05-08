import { RouteRecordRaw } from 'vue-router'

export default [
    {
        path: '/admin/access',
        component: () => import('@/views/admin/AccessControl.vue'),
        meta: {
            title: '权限管理',
            requiresAuth: true,
            permissions: ['user:manage', 'role:manage']
        }
    },
    {
        path: '/admin/settings',
        component: () => import('@/views/admin/SystemSettings.vue'),
        meta: {
            title: '后台设置',
            requiresAuth: true,
            anyPermissions: ['ai:manage', 'system:observe']
        }
    }
] as RouteRecordRaw[]
