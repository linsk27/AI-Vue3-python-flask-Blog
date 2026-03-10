import request from '@/axios';
import { baseUrl } from '@/config/env';

export const loginByUsername = (username, password, code, redomStr) => request({
  url: '/api/login', // 连接真实后端登录接口
  method: 'post',
  meta: {
    isToken: false
  },
  data: {
    username,
    password
  }
})

export const getUserInfo = () => request({
  // 获取用户信息的逻辑可以暂时简化，或者复用登录返回的信息
  // 也可以实现一个 /api/me 接口
  // 这里暂时用一个 mock 或者需要后端配合
  // 假设后端登录返回了用户信息，前端存储了。如果需要刷新用户信息，需要后端提供接口。
  // 暂时先保留原样或指向一个空接口，或者让后端提供 /api/me
  url: '/api/user/info', // 假设后端有这个接口，或者我们需要实现它
  method: 'get'
});

export const refreshToken = () => request({
  url: baseUrl + '/user/refresh',
  method: 'post'
})

export const getMenu = (type = 0) => request({
  url: baseUrl + '/user/getMenu',
  method: 'get',
  params: {
    type
  }
});

export const getTopMenu = () => request({
  url: baseUrl + '/user/getTopMenu',
  method: 'get'
});

export const sendLogs = (list) => request({
  url: baseUrl + '/user/logout',
  method: 'post',
  data: list
})

export const logout = () => request({
  url: baseUrl + '/user/logout',
  meta: {
    isToken: false
  },
  method: 'get'
})