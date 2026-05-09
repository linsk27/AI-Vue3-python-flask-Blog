const top = [
    {
        label: '管理台',
        path: '/wel/index',
        icon: 'el-icon-monitor',
        meta: {
            i18n: 'dashboard'
        },
        parentId: 0
    }
]

const first = [
    {
        label: '系统治理',
        path: '/manager/access',
        component: 'Layout',
        icon: 'icon-caidan',
        meta: {
            keepAlive: true
        },
        children: [
            {
                label: '账号管理',
                path: 'user',
                component: 'views/manager/user/index',
                icon: 'icon-user',
                meta: {
                    keepAlive: true
                }
            },
            {
                label: '角色权限',
                path: 'role',
                component: 'views/manager/role/index',
                icon: 'icon-role',
                meta: {
                    keepAlive: true
                }
            },
            {
                label: '系统自检',
                path: 'system',
                component: 'views/manager/system/index',
                icon: 'icon-caidan',
                meta: {
                    keepAlive: true
                }
            }
        ]
    },
    {
        label: '内容运营',
        path: '/manager/content',
        component: 'Layout',
        icon: 'icon-caidan',
        meta: {
            keepAlive: true
        },
        children: [
            {
                label: '文章管理',
                path: 'article',
                component: 'views/manager/article/index',
                icon: 'icon-caidan',
                meta: {
                    keepAlive: true
                }
            },
            {
                label: '上下文包',
                path: 'context',
                component: 'views/manager/context/index',
                icon: 'icon-caidan',
                meta: {
                    keepAlive: true
                }
            }
        ]
    },
    {
        label: 'AI 与 RAG',
        path: '/manager/ai-center',
        component: 'Layout',
        icon: 'icon-caidan',
        meta: {
            keepAlive: true
        },
        children: [
            {
                label: '模型配置',
                path: 'model',
                component: 'views/manager/ai/index',
                icon: 'icon-caidan',
                meta: {
                    keepAlive: true
                }
            },
            {
                label: 'Embedding 配置',
                path: 'embedding',
                component: 'views/manager/embedding/index',
                icon: 'icon-caidan',
                meta: {
                    keepAlive: true
                }
            }
        ]
    }
]

export default [
    {
        url: '/user/getMenu',
        method: 'get',
        response: ({ query }) => {
            return {
                data: query.type && Number(query.type) !== 0 ? [] : first
            }
        }
    },
    {
        url: '/user/getTopMenu',
        method: 'get',
        response: () => {
            return {
                data: top
            }
        }
    }
]
