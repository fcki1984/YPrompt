<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col">
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">分享演练快照</h3>
          <p class="text-sm text-gray-500">生成唯一链接，与他人共享当前对话与渲染结果</p>
        </div>
        <button class="text-gray-400 hover:text-gray-600" @click="handleClose">
          <X class="w-5 h-5" />
        </button>
      </div>
      <div class="flex-1 overflow-y-auto px-5 py-4 space-y-5">
        <div v-if="!snapshot" class="p-4 bg-yellow-50 text-yellow-700 rounded-lg text-sm">
          暂无可分享的对话内容。
        </div>
        <template v-else>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-700">分享标题</label>
              <input
                v-model="form.title"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="例如：营销落地页提示词测试"
                maxlength="200"
              />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-700">访问模式</label>
              <div class="flex items-center gap-4 text-sm">
                <label class="flex items-center gap-1">
                  <input type="radio" value="public" v-model="form.accessMode" />
                  匿名可访问
                </label>
                <label class="flex items-center gap-1">
                  <input type="radio" value="auth_only" v-model="form.accessMode" />
                  需登录
                </label>
              </div>
            </div>
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-700">有效期</label>
              <div class="flex items-center gap-3 text-sm">
                <label class="flex items-center gap-1">
                  <input type="radio" value="permanent" v-model="form.expireType" />
                  永久有效
                </label>
                <label class="flex items-center gap-1">
                  <input type="radio" value="custom" v-model="form.expireType" />
                  自定义
                </label>
              </div>
              <input
                v-if="form.expireType === 'custom'"
                type="datetime-local"
                v-model="form.expiresAt"
                class="w-full mt-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-700">访问密码（可选）</label>
              <input
                v-model="form.password"
                type="text"
                maxlength="64"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="留空表示无需密码"
              />
            </div>
          </div>

          <div class="p-3 rounded-xl bg-gray-50 text-sm text-gray-600">
            <p>• 当前模型：<span class="font-medium text-gray-900">{{ providerInfo?.name || '未配置' }} · {{ providerInfo?.modelName || '未知模型' }}</span></p>
            <p>• 消息数量：<span class="font-medium text-gray-900">{{ snapshot.messages.length }}</span> 条</p>
            <p>• 提醒：分享暂不包含附件内容，敏感信息请自行审查。</p>
          </div>

          <div v-if="errorMessage" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">
            {{ errorMessage }}
          </div>

          <div v-if="shareResult" class="p-4 bg-green-50 border border-green-100 rounded-xl space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-green-800">分享链接已生成</span>
              <span class="text-xs text-green-700">可复制给任何人</span>
            </div>
            <div class="flex gap-2">
              <input
                :value="shareLink"
                readonly
                class="flex-1 px-3 py-2 border border-green-200 rounded-lg bg-white text-sm text-gray-800"
              />
              <button
                class="px-3 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700"
                @click="copyShareLink"
              >
                复制
              </button>
            </div>
            <p class="text-xs text-green-700">可在“我的分享”中随时撤销或调整访问设置。</p>
          </div>
        </template>
      </div>
      <div class="flex items-center justify-end gap-3 px-5 py-4 border-t border-gray-100">
        <button class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg" @click="handleClose">取消</button>
        <button
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!snapshot || isSubmitting"
          @click="handleSubmit"
        >
          {{ shareResult ? '重新生成' : '生成链接' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { createPlaygroundShare, type PlaygroundSharePayload } from '@/services/apiService'
import { copyToClipboard } from '@/utils/clipboardUtils'
import { useNotificationStore } from '@/stores/notificationStore'

interface ShareMessage {
  id?: string
  role: 'user' | 'model'
  text: string
  displayText?: string
  timestamp?: number
}

interface SnapshotPayload {
  messages: ShareMessage[]
  artifact: { type: string; content: string } | null
}

interface ProviderInfo {
  id: string
  name: string
  modelId: string
  modelName: string
  streamMode: boolean
}

const props = defineProps<{
  isOpen: boolean
  snapshot: SnapshotPayload | null
  systemPrompt: string
  providerInfo: ProviderInfo | null
  promptId?: number  // 关联的提示词ID（从详情页进入时传入）
}>()

const emit = defineEmits<{
  close: []
  shared: []
}>()

const defaultExpire = () => {
  const now = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
  const iso = now.toISOString()
  return iso.slice(0, 16)
}

const form = reactive({
  title: '',
  accessMode: 'public',
  expireType: 'custom',
  expiresAt: defaultExpire(),
  password: ''
})

const isSubmitting = ref(false)
const errorMessage = ref('')
const shareResult = ref<{ share_code: string; share_path: string } | null>(null)

const shareLink = computed(() => {
  if (!shareResult.value) return ''
  if (typeof window === 'undefined') {
    return shareResult.value.share_path
  }
  return `${window.location.origin}${shareResult.value.share_path}`
})

const notificationStore = useNotificationStore()

const resetForm = () => {
  form.title = ''
  form.accessMode = 'public'
  form.expireType = 'custom'
  form.expiresAt = defaultExpire()
  form.password = ''
  errorMessage.value = ''
  shareResult.value = null
}

const handleClose = () => {
  resetForm()
  emit('close')
}

watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      resetForm()
      if (props.snapshot?.messages?.length) {
        const firstUser = props.snapshot.messages.find((msg) => msg.role === 'user')
        if (firstUser?.text) {
          form.title = firstUser.text.slice(0, 30)
        }
      }
    }
  }
)

const handleSubmit = async () => {
  if (!props.snapshot || !props.providerInfo) {
    errorMessage.value = '暂无可分享的内容或模型配置'
    return
  }
  if (form.expireType === 'custom' && !form.expiresAt) {
    errorMessage.value = '请选择到期时间'
    return
  }
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    const normalizedMessages = props.snapshot.messages.map((msg, index) => ({
      id: msg.id || `share-${index}`,
      role: msg.role,
      text: msg.text,
      displayText: msg.displayText,
      timestamp: msg.timestamp
    }))

    const payload: PlaygroundSharePayload = {
      title: form.title || '提示词演练快照',
      systemPrompt: props.systemPrompt,
      provider: props.providerInfo,
      artifact: props.snapshot.artifact,
      messages: normalizedMessages,
      is_permanent: form.expireType === 'permanent',
      expires_at: form.expireType === 'permanent' ? undefined : form.expiresAt,
      access_mode: form.accessMode as 'public' | 'auth_only',
      password: form.password || undefined,
      prompt_id: props.promptId  // 关联提示词ID
    }
    const response: any = await createPlaygroundShare(payload)
    if (response.code !== 200) {
      throw new Error(response.message || '创建分享失败')
    }
    shareResult.value = response.data
    emit('shared')
  } catch (error: any) {
    errorMessage.value = error?.message || '创建分享失败'
  } finally {
    isSubmitting.value = false
  }
}

const copyShareLink = async () => {
  if (!shareLink.value) return
  try {
    await copyToClipboard(shareLink.value)
    notificationStore.success('已复制分享链接')
  } catch (error) {
    console.error('复制失败', error)
    notificationStore.error('复制失败，请稍后再试')
  }
}
</script>
