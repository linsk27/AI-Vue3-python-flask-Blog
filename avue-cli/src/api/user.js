import request from '@/axios';
import { baseUrl } from '@/config/env';

const adminMenus = [{
  label: '内容运营',
  path: '/manager/content',
  icon: 'icon-wenzhang',
  component: 'page/index/layout',
  children: [{
    label: '文章管理',
    path: 'article',
    icon: 'icon-wenzhang',
    component: 'views/manager/article/index'
  }, {
    label: '上下文包',
    path: 'context',
    icon: 'icon-caidan',
    component: 'views/manager/context/index'
  }]
}, {
  label: 'AI 治理',
  path: '/manager/ai-ops',
  icon: 'icon-shezhi',
  component: 'page/index/layout',
  children: [{
    label: 'AI 配置',
    path: 'ai',
    icon: 'icon-shezhi',
    component: 'views/manager/ai/index'
  }, {
    label: 'Embedding',
    path: 'embedding',
    icon: 'icon-shezhi',
    component: 'views/manager/embedding/index'
  }, {
    label: '系统自检',
    path: 'system',
    icon: 'icon-shezhi',
    component: 'views/manager/system/index'
  }]
}, {
  label: '权限管理',
  path: '/manager/access',
  icon: 'icon-yonghu',
  component: 'page/index/layout',
  children: [{
    label: '账号管理',
    path: 'user',
    icon: 'icon-yonghu',
    component: 'views/manager/user/index'
  }, {
    label: '角色权限',
    path: 'role',
    icon: 'icon-shezhi',
    component: 'views/manager/role/index'
  }]
}]

const cloneMenus = () => JSON.parse(JSON.stringify(adminMenus))

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

export const getMenu = () => Promise.resolve({
  data: {
    status: 0,
    data: cloneMenus()
  }
});

export const getTopMenu = () => Promise.resolve({
  data: {
    status: 0,
    data: cloneMenus()
  }
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
