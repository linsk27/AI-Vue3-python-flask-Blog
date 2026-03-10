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
    dialogClickModal: false,
    rowKey: 'id',
    refreshBtn: true,
    columnBtn: true,
    searchBtn: true,
    menu: true,
    addBtn: true,
    editBtn: true,
    delBtn: true,
    dragHandler: false, // 禁用行拖拽
    rowDrag: false, // 彻底禁用行拖拽
    columnDrag: false, // 彻底禁用列拖拽
    sortable: false, // 禁用排序
    column: [
        {
            label: 'ID',
            prop: 'id',
            width: 80,
            display: false
        },
        {
            label: '提供商',
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
                    message: '请选择提供商',
                    trigger: 'change'
                }
            ]
        },
        {
            label: '模型',
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
            width: 150
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
                { label: '禁用', value: 0 },
                { label: '启用', value: 1 }
            ],
            slot: true,
            width: 100,
            align: 'center'
        },
        {
            label: '系统提示词',
            prop: 'system_prompt',
            type: 'textarea',
            minRows: 3,
            hide: true,
            span: 24
        },
        {
            label: '创建时间',
            prop: 'created_at',
            width: 160,
            display: false,
            addDisplay: false,
            editDisplay: false
        }
    ]
}
