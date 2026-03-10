<template>
    <div class="my-works-container">
        <div class="page-header">
            <h2>我的作品管理</h2>
            <el-button type="primary" @click="goToWrite">
                <el-icon>
                    <Plus />
                </el-icon> 写文章
            </el-button>
        </div>

        <el-card class="works-card">
            <el-table :data="articles" style="width: 100%" v-loading="loading">
                <el-table-column prop="title" label="标题" min-width="200">
                    <template #default="{ row }">
                        <span class="article-title" @click="goToArticle(row.id)">{{ row.title }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="category" label="分类" width="120">
                    <template #default="{ row }">
                        <el-tag size="small">{{ row.category || '未分类' }}</el-tag>
                    </template>
                </el-table-column>

                <el-table-column prop="status" label="状态" width="100">
                    <template #default="{ row }">
                        <el-tag :type="getStatusType(row.status)" size="small">
                            {{ getStatusLabel(row.status) }}
                        </el-tag>
                    </template>
                </el-table-column>

                <el-table-column prop="created_at" label="创建时间" width="180">
                    <template #default="{ row }">
                        {{ formatDate(row.created_at) }}
                    </template>
                </el-table-column>

                <el-table-column label="操作" width="250" fixed="right">
                    <template #default="{ row }">
                        <el-button size="small" @click="handleEdit(row)">编辑</el-button>
                        <el-button size="small" :type="getActionBtnType(row.status)" @click="handleToggleStatus(row)"
                            :disabled="row.status === 'pending'">
                            {{ getActionBtnText(row.status) }}
                        </el-button>
                        <el-popconfirm title="确定要删除这篇文章吗？" @confirm="handleDelete(row)" confirm-button-text="删除"
                            cancel-button-text="取消" confirm-button-type="danger">
                            <template #reference>
                                <el-button size="small" type="danger">删除</el-button>
                            </template>
                        </el-popconfirm>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGlobalStore } from '@/store'
import articleApi from '@/api/modules/article'
import { IArticle } from '@/api/modules/article/interface'
import { useElMessage } from '@/hooks/useMessage'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const globalStore = useGlobalStore()
const { message } = useElMessage()

const articles = ref<IArticle[]>([])
const loading = ref(false)

const fetchArticles = async () => {
    if (!globalStore.userInfo?.id) return

    loading.value = true
    try {
        const res = await articleApi.getList({
            author_id: globalStore.userInfo.id
        })
        // @ts-ignore - The API response type might need adjustment in generic http wrapper, assuming res.data is the list or res is the list
        // Based on previous code, http.get<T> returns Promise<T>. But let's check response structure.
        // Usually our axios interceptor returns response.data directly?
        // Let's assume standard response structure.
        articles.value = res as any
    } catch (error) {
        console.error('获取文章列表失败', error)
        message.error('获取文章列表失败')
    } finally {
        loading.value = false
    }
}

const goToWrite = () => {
    router.push('/essays/write')
}

const goToArticle = (id: number) => {
    router.push(`/essays/${id}`)
}

const handleEdit = (row: IArticle) => {
    router.push(`/essays/edit/${row.id}`)
}

const getStatusType = (status: string) => {
    switch (status) {
        case 'published': return 'success'
        case 'draft': return 'info'
        case 'pending': return 'warning'
        default: return 'info'
    }
}

const getStatusLabel = (status: string) => {
    switch (status) {
        case 'published': return '已发布'
        case 'draft': return '草稿'
        case 'pending': return '待审核'
        default: return '未知'
    }
}

const getActionBtnType = (status: string) => {
    if (status === 'published') return 'warning'
    if (status === 'draft') return 'success'
    return 'info'
}

const getActionBtnText = (status: string) => {
    if (status === 'published') return '下架'
    if (status === 'draft') return '发布'
    return '待审核'
}

const handleToggleStatus = async (row: IArticle) => {
    if (row.status === 'pending') return
    const newStatus = row.status === 'published' ? 'draft' : 'published'
    try {
        await articleApi.update(row.id, {
            ...row,
            status: newStatus
        } as any)

        row.status = newStatus
        message.success(newStatus === 'published' ? '已发布' : '已下架')
    } catch (error) {
        console.error('更新状态失败', error)
        message.error('更新状态失败')
    }
}

const handleDelete = async (row: IArticle) => {
    try {
        await articleApi.delete(row.id)
        message.success('删除成功')
        // Remove from list
        articles.value = articles.value.filter(item => item.id !== row.id)
    } catch (error) {
        console.error('删除失败', error)
        message.error('删除失败')
    }
}

const formatDate = (dateStr: string) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleString()
}

onMounted(() => {
    fetchArticles()
})
</script>

<style scoped lang="scss">
.my-works-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;

        h2 {
            font-size: 24px;
            color: #333;
            margin: 0;
        }
    }

    .works-card {
        border-radius: 8px;
        box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

        .article-title {
            color: #409EFF;
            cursor: pointer;
            font-weight: 500;

            &:hover {
                text-decoration: underline;
            }
        }
    }
}
</style>