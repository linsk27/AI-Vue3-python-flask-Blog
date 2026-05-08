import { useGlobalStore } from '@/store'
import { computed } from 'vue'

export function usePermission() {
    const globalStore = useGlobalStore()

    // 获取当前用户权限列表
    const permissions = computed(() => {
        return globalStore.userInfo?.permissions || []
    })

    // 检查是否有特定权限
    const hasPermission = (permission: string) => {
        // 后端同样把 admin 视为超级管理员，这里保持前端展示逻辑一致
        if (globalStore.userInfo?.role === 'admin') {
            return true
        }
        return permissions.value.includes(permission)
    }

    // 检查是否有任一权限
    const hasAnyPermission = (permissionList: string[]) => {
        if (globalStore.userInfo?.role === 'admin') {
            return true
        }
        return permissionList.some(p => permissions.value.includes(p))
    }

    // 检查是否包含所有权限
    const hasAllPermissions = (permissionList: string[]) => {
        if (globalStore.userInfo?.role === 'admin') {
            return true
        }
        return permissionList.every(p => permissions.value.includes(p))
    }

    return {
        permissions,
        hasPermission,
        hasAnyPermission,
        hasAllPermissions
    }
}
