export default {
    height: 'auto',
    calcHeight: 30,
    tip: false,
    searchShow: true,
    searchMenuSpan: 6,
    border: true,
    index: true,
    viewBtn: true,
    selection: false,
    menuWidth: 176,
    menuAlign: 'center',
    menuHeaderAlign: 'center',
    dialogClickModal: false,
    rowKey: 'id',
    refreshBtn: true,
    columnBtn: true,
    searchBtn: true,
    menu: true,
    addBtn: true,
    editBtn: true,
    delBtn: true,
    addTitle: '新增模型配置',
    editTitle: '编辑模型配置',
    viewTitle: '查看模型配置',
    emptyText: '暂无模型配置。请新增并启用一个可用配置。',
    dragHandler: false,
    rowDrag: false,
    columnDrag: false,
    sortable: false,
    column: [
        {
            label: 'ID',
            prop: 'id',
            width: 80,
            display: false
        },
        {
            label: '模型提供商',
            prop: 'provider',
            type: 'select',
            search: true,
            dicData: [
                { label: '火山方舟', value: 'volcano' },
                { label: 'DeepSeek', value: 'deepseek' }
            ],
            rules: [
                {
                    required: true,
                    message: '请选择模型提供商',
                    trigger: 'change'
                }
            ]
        },
        {
            label: '模型名称',
            prop: 'model',
            search: true,
            rules: [
                {
                    required: true,
                    message: '请输入模型名称',
                    trigger: 'blur'
                }
            ]
        },
        {
            label: 'API Key',
            prop: 'api_key',
            type: 'password',
            hide: true,
            rules: [
                {
                    required: true,
                    message: '请输入 API Key',
                    trigger: 'blur'
                }
            ]
        },
        {
            label: 'API Key',
            prop: 'api_key_masked',
            display: false,
            width: 160
        },
        {
            label: 'Base URL',
            prop: 'base_url',
            hide: true,
            rules: [
                {
                    required: true,
                    message: '请输入 Base URL',
                    trigger: 'blur'
                }
            ]
        },
        {
            label: '启用状态',
            prop: 'is_active',
            type: 'switch',
            value: 0,
            dicData: [
                { label: '停用', value: 0 },
                { label: '启用', value: 1 }
            ],
            slot: true,
            width: 110,
            align: 'center'
        },
        {
            label: '系统提示词',
            prop: 'system_prompt',
            type: 'textarea',
            minRows: 4,
            hide: true,
            span: 24
        },
        {
            label: '创建时间',
            prop: 'created_at',
            width: 170,
            display: false,
            addDisplay: false,
            editDisplay: false
        }
    ]
}
