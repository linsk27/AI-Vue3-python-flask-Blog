<template>
    <div class="my-likes-container">
        <div class="page-header">
            <h2>我的喜欢</h2>
        </div>

        <el-card class="likes-card">
            <el-table :data="articles" style="width: 100%" v-loading="loading">
                <el-table-column prop="title" label="标题" min-width="200">
                    <template #default="{ row }">
                        <span class="article-title" @click="goToArticle(row.id)">{{ row.title }}</span>
                    </template>
                </el-table-column>
                
                <el-table-column prop="author_name" label="作者" width="120">
                    <template #default="{ row }">
                        <span>{{ row.author_name || '未知' }}</span>
                    </template>
                </el-table-column>
                
                <el-table-column prop="category" label="分类" width="120">
                    <template #default="{ row }">
                        <el-tag size="small">{{ row.category || '未分类' }}</el-tag>
                    </template>
                </el-table-column>
                
                <el-table-column prop="created_at" label="发布时间" width="180">
                    <template #default="{ row }">
                        {{ formatDate(row.created_at) }}
                    </template>
                </el-table-column>
                
                <el-table-column label="操作" width="120" fixed="right">
                    <template #default="{ row }">
                        <el-button 
                            size="small" 
                            type="danger" 
                            plain
                            @click="handleUnlike(row)"
                        >
                            取消喜欢
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
            
            <div v-if="!loading && articles.length === 0" class="empty-state">
                <el-empty description="暂无喜欢的文章" />
            </div>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import articleApi from '@/api/modules/article'
import { IArticle } from '@/api/modules/article/interface'
import { useElMessage } from '@/hooks/useMessage'

const router = useRouter()
const { message } = useElMessage()

const articles = ref<IArticle[]>([])
const loading = ref(false)

const fetchLikedArticles = async () => {
    loading.value = true
    try {
        const res = await articleApi.getMyLikes()
        // @ts-ignore
        articles.value = res.data || res
    } catch (error) {
        console.error('获取喜欢列表失败', error)
        message.error('获取喜欢列表失败')
    } finally {
        loading.value = false
    }
}

const goToArticle = (id: number) => {
    router.push(`/essays/${id}`)
}

const handleUnlike = async (row: IArticle) => {
    try {
        await articleApi.toggleLike(row.id)
        message.success('已取消喜欢')
        // Remove from list
        articles.value = articles.value.filter(item => item.id !== row.id)
    } catch (error) {
        console.error('操作失败', error)
        message.error('操作失败')
    }
}

const formatDate = (dateStr: string) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
    fetchLikedArticles()
})
</script>

<style scoped lang="scss">
.my-likes-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    
    .page-header {
        margin-bottom: 20px;
        
        h2 {
            font-size: 24px;
            color: #333;
            margin: 0;
        }
    }
    
    .likes-card {
        border-radius: 8px;
        box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
        min-height: 400px;
        
        .article-title {
            color: #409EFF;
            cursor: pointer;
            font-weight: 500;
            
            &:hover {
                text-decoration: underline;
            }
        }
    }
    
    .empty-state {
        display: flex;
        justify-content: center;
        padding: 40px 0;
    }
}
</style>