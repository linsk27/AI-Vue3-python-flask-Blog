export default {
    height: 'auto',
    calcHeight: 30,
    tip: false,
    searchShow: true,
    searchMenuSpan: 6,
    border: true,
    index: true,
    viewBtn: true,
    selection: true,
    dialogClickModal: false,
    column: [
        {
            label: 'ID',
            prop: 'id',
            width: 80,
            display: false
        },
        {
            label: '用户名',
            prop: 'username',
            search: true,
            rules: [
                {
                    required: true,
                    message: '请输入用户名',
                    trigger: 'blur'
                }
            ]
        },
        {
            label: '邮箱',
            prop: 'email',
            search: true,
            rules: [
                {
                    required: false,
                    message: '请输入邮箱',
                    trigger: 'blur'
                }
            ]
        },
        {
            label: '头像',
            prop: 'avatar',
            type: 'upload',
            listType: 'picture-img',
            span: 24,
            width: 100,
            align: 'center',
            action: '/api/upload', // 配置上传地址
            propsHttp: {
                res: 'data',
                url: 'url',
                name: 'name'
            },
            loadText: '上传中...'
        },
        {
            label: '密码',
            prop: 'password',
            type: 'password',
            hide: true,
            addDisplay: true,
            editDisplay: true,
            rules: [
                {
                    required: true,
                    message: '请输入密码',
                    trigger: 'blur'
                }
            ]
        },
        {
            label: '角色',
            prop: 'role_id',
            type: 'select',
            dicData: [], // 动态获取
            props: {
                label: 'name',
                value: 'id'
            },
            dataType: 'number',
            rules: [
                {
                    required: true,
                    message: '请选择角色',
                    trigger: 'change'
                }
            ]
        },
        {
            label: '注册时间',
            prop: 'created_at',
            type: 'datetime',
            format: 'YYYY-MM-DD HH:mm:ss',
            valueFormat: 'YYYY-MM-DD HH:mm:ss',
            width: 160,
            display: false
        }
    ]
}
