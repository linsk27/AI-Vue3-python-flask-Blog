import { ILoginParams, IRegisterParams, IUserInfo } from './interface'
import { LOGIN_API, REGISTER_API, USER_INFO_API } from './url.const'
import http from '@/api'

const authApi = {
    login: (params: ILoginParams) => {
        return http.post<IUserInfo>(LOGIN_API, params)
    },
    register: (params: IRegisterParams) => {
        return http.post(REGISTER_API, params)
    },
    getUserInfo: () => {
        return http.get<IUserInfo>(USER_INFO_API)
    }
}

export default authApi
