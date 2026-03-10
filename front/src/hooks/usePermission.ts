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
        // 如果是管理员，通常拥有所有权限，或者特定超级权限
        // 这里假设 role 为 admin 的用户拥有所有权限
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
