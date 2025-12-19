<template>
  <div class="h-full flex flex-col overflow-hidden p-2">
    <!-- 顶栏 -->
    <div class="bg-white rounded-lg shadow-sm p-6 mb-4 flex-shrink-0">
      <div class="flex flex-col gap-4">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">提示词广场</h1>
            <p class="text-sm text-gray-500 mt-1">发现优质提示词</p>
          </div>
          
          <!-- 排序切换 -->
          <div class="flex items-center gap-2">
            <button
              @click="sortMode = 'hot'"
              :class="sortMode === 'hot' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
              class="px-4 py-2 rounded-lg transition-colors text-sm font-medium flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
              </svg>
              热门
            </button>
            <button
              @click="sortMode = 'latest'"
              :class="sortMode === 'latest' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
              class="px-4 py-2 rounded-lg transition-colors text-sm font-medium flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              最新
            </button>
          </div>
        </div>
        
        <!-- 搜索栏 -->
        <div class="flex gap-2 flex-wrap">
          <div class="relative flex-1 max-w-md">
            <span class="absolute left-3 top-2.5 text-gray-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </span>
            <input
              v-model="keyword"
              type="text"
              placeholder="搜索提示词..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-blue-500"
              @input="handleSearch"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- 内容区域 -->
    <div class="flex-1 bg-white rounded-lg shadow-sm overflow-hidden">
      <div class="h-full overflow-y-auto p-4">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="flex items-center justify-center h-32">
          <div class="flex items-center gap-2 text-gray-500">
            <div class="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <span>加载中...</span>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="prompts.length === 0" class="flex flex-col items-center justify-center h-64 text-center">
          <svg class="w-16 h-16 mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">暂无公开提示词</h3>
          <p class="text-gray-600">{{ keyword ? '未找到匹配的提示词' : '快去创建第一个公开提示词吧！' }}</p>
        </div>
        
        <!-- 提示词卡片列表 - 紧凑垂直布局 -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div
            v-for="prompt in prompts"
            :key="prompt.id"
            class="group bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-lg hover:border-blue-300 transition-all duration-200 flex flex-col"
            style="min-height: 280px"
          >
            <!-- 卡片主体 - 可点击查看详情 -->
            <div 
              class="flex-1 p-4 cursor-pointer"
              @click="handleViewPrompt(prompt.id)"
            >
              <!-- 头部：类型标签 + 版本 -->
              <div class="flex items-center justify-between mb-3">
                <span 
                  :class="prompt.prompt_type === 'system' 
                    ? 'bg-purple-100 text-purple-700' 
                    : 'bg-blue-100 text-blue-700'"
                  class="px-2.5 py-1 text-xs font-semibold rounded-full"
                >
                  {{ prompt.prompt_type === 'system' ? '系统提示词' : '用户提示词' }}
                </span>
                <span class="text-xs text-gray-400 font-mono">v{{ prompt.current_version || '1.0.0' }}</span>
              </div>
              
              <!-- 标题 -->
              <h3 class="text-base font-semibold text-gray-900 mb-2 line-clamp-2 leading-snug min-h-[2.5rem]">
                {{ prompt.title }}
              </h3>
              
              <!-- 描述 -->
              <p class="text-sm text-gray-600 line-clamp-3 mb-3 min-h-[3.75rem]">
                {{ prompt.description || '暂无描述' }}
              </p>
              
              <!-- 标签 -->
              <div v-if="prompt.tags" class="flex flex-wrap gap-1.5 mb-3">
                <span 
                  v-for="tag in (prompt.tags || '').split(',').filter(Boolean).slice(0, 3)"
                  :key="tag"
                  class="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
            
            <!-- 底部信息栏：统计数据 + 作者 -->
            <div class="px-4 pb-3 flex items-center justify-between text-xs text-gray-500">
              <!-- 左侧：统计信息 -->
              <div class="flex items-center gap-3">
                <span class="flex items-center gap-1" :title="`浏览 ${prompt.view_count || 0} 次`">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  {{ prompt.view_count || 0 }}
                </span>
                <span class="flex items-center gap-1" :title="`${prompt.like_count || 0} 个赞`">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  {{ prompt.like_count || 0 }}
                </span>
                <span class="flex items-center gap-1" :title="`${prompt.comment_count || 0} 条评论`">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  {{ prompt.comment_count || 0 }}
                </span>
              </div>
              
              <!-- 右侧：作者信息 -->
              <div class="flex items-center gap-1.5">
                <img 
                  v-if="prompt.author_avatar" 
                  :src="prompt.author_avatar" 
                  :alt="prompt.author_name"
                  class="w-4 h-4 rounded-full object-cover"
                />
                <div v-else class="w-4 h-4 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white" style="font-size: 8px; font-weight: 600;">
                  {{ (prompt.author_name || '?')[0].toUpperCase() }}
                </div>
                <span class="truncate max-w-[80px]">{{ prompt.author_name }}</span>
              </div>
            </div>
            
            <!-- 底部操作栏 -->
            <div class="border-t border-gray-100 px-4 py-2.5 bg-gray-50/50 flex items-center justify-between gap-2">
              <!-- 左侧按钮组 -->
              <div class="flex items-center gap-1">
                <!-- 复制按钮 -->
                <button
                  @click.stop="handleCopyPrompt(prompt)"
                  class="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                  title="复制提示词"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
                
                <!-- 点赞按钮 -->
                <button
                  @click.stop="handleLike(prompt)"
                  :class="prompt.is_liked ? 'text-red-500 bg-red-50' : 'text-gray-600 hover:text-red-500 hover:bg-red-50'"
                  class="p-1.5 rounded transition-colors"
                  title="点赞"
                >
                  <svg class="w-4 h-4" :fill="prompt.is_liked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </button>
              </div>
              
              <!-- 右侧：演练按钮 -->
              <button
                @click.stop="handlePlayground(prompt)"
                class="text-xs font-medium text-white bg-green-600 hover:bg-green-700 px-3 py-1.5 rounded transition-colors flex items-center gap-1"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                演练
              </button>
            </div>
          </div>
        </div>
        
        <!-- 分页 -->
        <div v-if="total > limit" class="flex items-center justify-center gap-2 mt-6">
          <button
            @click="changePage(page - 1)"
            :disabled="page <= 1"
            class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            上一页
          </button>
          <span class="text-sm text-gray-600">
            第 {{ page }} / {{ Math.ceil(total / limit) }} 页
          </span>
          <button
            @click="changePage(page + 1)"
            :disabled="page >= Math.ceil(total / limit)"
            class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 状态
const prompts = ref<any[]>([])
const isLoading = ref(true)
const page = ref(1)
const limit = ref(20)
const total = ref(0)
const sortMode = ref<'hot' | 'latest'>('hot')
const keyword = ref('')

// 防抖定时器
let searchTimer: NodeJS.Timeout | null = null

// 获取提示词列表
const fetchPrompts = async () => {
  try {
    isLoading.value = true
    const token = localStorage.getItem('yprompt_token')
    
    const params = new URLSearchParams({
      page: page.value.toString(),
      limit: limit.value.toString(),
      sort: sortMode.value
    })
    
    if (keyword.value) {
      params.append('keyword', keyword.value)
    }
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    const response = await fetch(`${API_BASE_URL}/api/community/prompts?${params}`, {
      method: 'GET',
      headers
    })
    
    const result = await response.json()
    
    if (result.code === 200) {
      prompts.value = result.data.items
      total.value = result.data.total
    }
  } catch (error) {
    console.error('获取提示词列表失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 搜索处理（防抖）
const handleSearch = () => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchPrompts()
  }, 500)
}

// 切换页码
const changePage = (newPage: number) => {
  page.value = newPage
  fetchPrompts()
}

// 查看提示词详情
const handleViewPrompt = (promptId: number) => {
  router.push(`/community/prompts/${promptId}`)
}

// 复制提示词
const handleCopyPrompt = async (prompt: any) => {
  try {
    await navigator.clipboard.writeText(prompt.final_prompt || '')
    alert('✅ 提示词已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    alert('❌ 复制失败，请手动复制')
  }
}

// 点赞/取消点赞
const handleLike = async (prompt: any) => {
  try {
    const token = localStorage.getItem('yprompt_token')
    if (!token) {
      alert('请先登录')
      return
    }
    
    const response = await fetch(`${API_BASE_URL}/api/community/prompts/${prompt.id}/like`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    const result = await response.json()
    
    if (result.code === 200) {
      // 更新本地状态
      prompt.is_liked = result.data.is_liked
      prompt.like_count = result.data.like_count
    } else {
      alert(result.message || '操作失败')
    }
  } catch (error) {
    console.error('点赞失败:', error)
    alert('操作失败，请重试')
  }
}

// 演练提示词
const handlePlayground = (prompt: any) => {
  // 跳转到演练，并传递 promptId 参数
  router.push({
    path: '/playground',
    query: { promptId: prompt.id }
  })
}

// 监听排序变化
watch(sortMode, () => {
  page.value = 1
  fetchPrompts()
})

onMounted(() => {
  fetchPrompts()
})
</script>
