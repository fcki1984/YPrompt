<template>
  <div class="h-full flex flex-col overflow-hidden p-2">
    <div class="bg-white rounded-lg shadow-sm p-4 mb-4 flex-shrink-0">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 class="text-xl lg:text-2xl font-bold text-gray-900">我的分享</h1>
          <p class="text-sm text-gray-500">管理演练分享链接，随时复制或撤销</p>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <button
            class="px-3 py-1.5 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
            @click="fetchShares"
          >
            刷新列表
          </button>
        </div>
      </div>
    </div>

    <div class="flex-1 min-h-0">
      <div class="bg-white rounded-lg shadow-sm p-4 h-full overflow-y-auto">
        <div v-if="isLoading" class="text-center text-gray-500 py-10">加载中...</div>
        <div v-else-if="shares.length === 0" class="text-center text-gray-500 py-10">
          暂无分享，前往演练生成一个吧。
        </div>
        <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div
            v-for="share in shares"
            :key="share.share_code"
            class="border border-gray-100 rounded-2xl p-4 flex flex-col gap-3 shadow-[0_6px_18px_rgba(15,23,42,0.06)] hover:border-blue-200 transition-colors cursor-pointer"
            @click="navigateToShare(share.share_code)"
          >
            <div class="space-y-2">
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="text-base font-semibold text-gray-900 truncate">{{ share.title || '未命名分享' }}</h3>
                <span
                  class="text-xs px-2 py-0.5 rounded-full"
                  :class="share.access_mode === 'public' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                >
                  {{ share.access_mode === 'public' ? '匿名访问' : '需登录' }}
                </span>
                <span
                  v-if="share.has_password"
                  class="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700"
                >
                  已设置密码
                </span>
                <span
                  v-if="!share.is_active"
                  class="text-xs px-2 py-0.5 rounded-full bg-gray-200 text-gray-600"
                >
                  已失效
                </span>
              </div>
              <div class="text-xs text-gray-500 break-all">
                链接：<span class="font-mono">/playground/share/{{ share.share_code }}</span>
              </div>
              <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                <span>访问：<span class="font-semibold text-gray-900">{{ share.view_count }}</span></span>
                <span>到期：{{ share.is_permanent ? '永久' : (share.expires_at || '未设置') }}</span>
                <span>创建：{{ share.create_time }}</span>
              </div>
            </div>
            <div class="flex flex-wrap gap-2 mt-auto">
              <button
                class="px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg text-xs hover:bg-blue-100"
                @click.stop="copyShareLink(share)"
              >
                复制链接
              </button>
              <button
                class="px-3 py-1.5 border border-gray-200 rounded-lg text-xs text-gray-700 hover:bg-gray-50"
                @click.stop="openEditModal(share)"
              >
                编辑设置
              </button>
              <button
                class="px-3 py-1.5 border border-red-100 text-red-600 rounded-lg text-xs hover:bg-red-50"
                @click.stop="deleteShare(share)"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <PlaygroundShareSettingsModal
      :is-open="!!editingShare"
      :share="editingShare"
      @close="closeEditModal"
      @updated="handleShareUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PlaygroundShareSettingsModal from '@/components/playground/PlaygroundShareSettingsModal.vue'
import {
  getMyPlaygroundShares,
  deletePlaygroundShare,
  type PlaygroundShareListItem
} from '@/services/apiService'
import { copyToClipboard } from '@/utils/clipboardUtils'
import { useNotificationStore } from '@/stores/notificationStore'

const router = useRouter()
const shares = ref<PlaygroundShareListItem[]>([])
const isLoading = ref(true)
const editingShare = ref<PlaygroundShareListItem | null>(null)
const notificationStore = useNotificationStore()

const fetchShares = async () => {
  isLoading.value = true
  try {
    const response = await getMyPlaygroundShares({ page: 1, limit: 50 })
    if (response.code === 200) {
      shares.value = response.data.items
    }
  } catch (error) {
    notificationStore.error('获取分享列表失败')
  } finally {
    isLoading.value = false
  }
}

const navigateToShare = (shareCode: string) => {
  router.push(`/playground/share/${shareCode}`)
}

const copyShareLink = async (share: PlaygroundShareListItem) => {
  const link = `${window.location.origin}/playground/share/${share.share_code}`
  await copyToClipboard(link)
  notificationStore.success('已复制分享链接')
}

const deleteShare = async (share: PlaygroundShareListItem) => {
  if (!confirm('确定要删除该分享吗？删除后链接将立即失效。')) return
  try {
    const response = await deletePlaygroundShare(share.share_code)
    if (response.code === 200) {
      notificationStore.success('已删除分享')
      fetchShares()
    } else {
      notificationStore.error(response.message || '删除失败')
    }
  } catch (error) {
    notificationStore.error('删除失败')
  }
}

const openEditModal = (share: PlaygroundShareListItem) => {
  editingShare.value = share
}

const closeEditModal = () => {
  editingShare.value = null
}

const handleShareUpdated = () => {
  notificationStore.success('分享设置已更新')
  closeEditModal()
  fetchShares()
}

onMounted(() => {
  fetchShares()
})
</script>
