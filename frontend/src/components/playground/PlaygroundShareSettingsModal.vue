<template>
  <div v-if="isOpen && share" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">编辑分享设置</h3>
          <p class="text-sm text-gray-500">调整访问模式、有效期或密码</p>
        </div>
        <button class="text-gray-400 hover:text-gray-600" @click="handleClose">
          <X class="w-5 h-5" />
        </button>
      </div>
      <div class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700">分享标题</label>
          <input
            v-model="form.title"
            type="text"
            maxlength="200"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
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
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700">有效期</label>
          <div class="flex items-center gap-4 text-sm">
            <label class="flex items-center gap-1">
              <input type="radio" value="permanent" v-model="form.expireType" />
              永久
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
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700">访问密码</label>
          <p class="text-xs text-gray-500">无法查看原密码，可设置新密码或点击“清除密码”。</p>
          <input
            v-model="form.password"
            type="text"
            maxlength="64"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="输入新密码"
          />
          <label class="flex items-center gap-2 text-sm text-gray-600 mt-1">
            <input type="checkbox" v-model="form.removePassword" />
            清除已有密码
          </label>
        </div>
        <div v-if="errorMessage" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">
          {{ errorMessage }}
        </div>
      </div>
      <div class="flex items-center justify-end gap-3 px-5 py-4 border-t border-gray-100">
        <button class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg" @click="handleClose">取消</button>
        <button
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isSubmitting"
          @click="handleSubmit"
        >
          保存
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { updatePlaygroundShare, type PlaygroundShareListItem } from '@/services/apiService'

const props = defineProps<{
  isOpen: boolean
  share: PlaygroundShareListItem | null
}>()

const emit = defineEmits<{
  close: []
  updated: []
}>()

const form = reactive({
  title: '',
  accessMode: 'public',
  expireType: 'custom',
  expiresAt: '',
  password: '',
  removePassword: false
})

const isSubmitting = ref(false)
const errorMessage = ref('')

const toDateTimeLocal = (value?: string | null) => {
  if (!value) return ''
  return value.replace(' ', 'T').slice(0, 16)
}

const syncForm = () => {
  if (!props.share) return
  form.title = props.share.title || '提示词演练快照'
  form.accessMode = props.share.access_mode
  form.expireType = props.share.is_permanent ? 'permanent' : 'custom'
  form.expiresAt = props.share.expires_at ? toDateTimeLocal(props.share.expires_at) : ''
  form.password = ''
  form.removePassword = false
  errorMessage.value = ''
}

watch(
  () => props.share,
  () => {
    if (props.isOpen && props.share) {
      syncForm()
    }
  }
)

watch(
  () => props.isOpen,
  (val) => {
    if (val && props.share) {
      syncForm()
    }
  }
)

const handleClose = () => {
  emit('close')
}

const handleSubmit = async () => {
  if (!props.share) return
  if (form.expireType === 'custom' && !form.expiresAt) {
    errorMessage.value = '请选择到期时间'
    return
  }
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    const payload: Record<string, any> = {
      title: form.title,
      access_mode: form.accessMode,
      is_permanent: form.expireType === 'permanent'
    }
    if (form.expireType === 'custom') {
      payload.expires_at = form.expiresAt
    }
    if (form.removePassword) {
      payload.remove_password = true
    } else if (form.password.trim()) {
      payload.password = form.password.trim()
    }
    const response: any = await updatePlaygroundShare(props.share.share_code, payload)
    if (response.code !== 200) {
      throw new Error(response.message || '更新失败')
    }
    emit('updated')
  } catch (error: any) {
    errorMessage.value = error?.message || '更新失败'
  } finally {
    isSubmitting.value = false
  }
}
</script>
