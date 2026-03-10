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
            label: '标题',
            prop: 'title',
            search: true,
            rules: [
                {
                    required: true,
                    message: '请输入标题',
                    trigger: 'blur'
                }
            ]
        },
        {
            label: '作者',
            prop: 'author_name',
            width: 120,
            display: false,
            addDisplay: false,
            editDisplay: false
        },
        {
            label: '分类',
            prop: 'category',
            search: true,
            type: 'select',
            dicData: [
                { label: '技术', value: 'tech' },
                { label: '生活', value: 'life' },
                { label: '其他', value: 'other' }
            ]
        },
        {
            label: '浏览量',
            prop: 'views',
            width: 80,
            align: 'center',
            addDisplay: false,
            editDisplay: false
        },
        {
            label: '点赞数',
            prop: 'likes',
            width: 80,
            align: 'center',
            addDisplay: false,
            editDisplay: false
        },
        {
            label: '状态',
            prop: 'status',
            type: 'select',
            search: true,
            dicData: [
                { label: '待审核', value: 'pending' },
                { label: '已发布', value: 'published' },
                { label: '草稿', value: 'draft' }
            ],
            value: 'published', // 默认值
            rules: [
                {
                    required: true,
                    message: '请选择状态',
                    trigger: 'change'
                }
            ],
            width: 100,
            align: 'center'
        },
        {
            label: '摘要',
            prop: 'summary',
            type: 'textarea',
            span: 24,
            hide: true
        },
        {
            label: '标签',
            prop: 'tags',
            type: 'select',
            multiple: true,
            allowCreate: true,
            filterable: true,
            dicData: [],
            hide: true
        },
        {
            label: '封面图',
            prop: 'cover_image',
            type: 'upload',
            listType: 'picture-img',
            imgWidth: 100,
            width: 140,
            align: 'center',
            span: 24,
            hide: false, // 在列表中显示
            action: '/api/upload', // 配置上传地址
            propsHttp: {
                res: 'data',
                url: 'url',
                name: 'name'
            },
            loadText: '上传中...'
        },
        {
            label: '内容',
            prop: 'content',
            type: 'textarea',
            minRows: 10,
            span: 24,
            hide: true,
            rules: [
                {
                    required: true,
                    message: '请输入内容',
                    trigger: 'blur'
                }
            ]
        },
        {
            label: '创建时间',
            prop: 'created_at',
            width: 160,
            display: false,
            addDisplay: false,
            editDisplay: false
        },
        {
            label: '更新时间',
            prop: 'updated_at',
            width: 160,
            display: false,
            addDisplay: false,
            editDisplay: false
        }
    ]
}
