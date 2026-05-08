import http from '@/api'

export interface AdminUser {
    id: number
    username: string
    avatar?: string
    role?: string
    role_id?: number | null
    email?: string
    created_at?: string
}

export interface AdminRole {
    id: number
    name: string
    description?: string
    permissions: number[]
    permissionNames?: string[]
    created_at?: string
    readonly?: boolean
}

export interface AdminPermission {
    id: number
    code: string
    name: string
}

export interface UserQuery {
    username?: string
    email?: string
}

export interface RolePayload {
    name: string
    description?: string
    permissions: number[]
}

const adminApi = {
    getUsers: (params?: UserQuery) => http.get<AdminUser[]>('/users', params),
    updateUser: (id: number, data: Partial<AdminUser> & { password?: string }) => http.put(`/users/${id}`, data),
    deleteUser: (id: number) => http.delete(`/users/${id}`),

    getRoles: () => http.get<AdminRole[]>('/roles'),
    createRole: (data: RolePayload) => http.post('/roles', data),
    updateRole: (id: number, data: RolePayload) => http.put(`/roles/${id}`, data),
    deleteRole: (id: number) => http.delete(`/roles/${id}`),
    getPermissions: () => http.get<AdminPermission[]>('/permissions')
}

export default adminApi
