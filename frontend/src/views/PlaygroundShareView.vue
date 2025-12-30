<template>
  <div class="h-full flex flex-col overflow-hidden p-2 relative">
    <SettingsModal />
    <SystemPromptModal
      :is-open="showSystemPromptModal"
      v-model="systemPromptDraft"
      :title="'查看系统提示词'"
      @close="showSystemPromptModal = false"
      @save="handleSystemPromptSave"
    />

    <div class="bg-white rounded-lg shadow-sm p-4 mb-4 flex-shrink-0">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="min-w-0">
          <h1 class="text-xl lg:text-2xl font-bold text-gray-900">{{ shareData?.title || '分享快照' }}</h1>
          <p class="text-sm text-gray-500">
            分享者：{{ shareData?.owner?.name || '未知' }} · 访问次数：{{ shareData?.view_count || 0 }}
          </p>
          <p v-if="shareData?.provider" class="text-xs text-gray-400">
            分享记录：{{ shareData?.provider?.name }} · {{ shareData?.provider?.modelName }}
          </p>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <label class="text-sm font-medium text-gray-700 whitespace-nowrap">AI模型:</label>
          <select
            v-model="settingsStore.selectedProvider"
            @change="onProviderChange"
            class="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 min-w-0 flex-1 sm:flex-none"
          >
            <option value="">选择提供商</option>
            <option
              v-for="provider in availableProviders"
              :key="provider.id"
              :value="provider.id"
            >
              {{ provider.name }}
            </option>
          </select>
          <select
            v-model="settingsStore.selectedModel"
            :disabled="!settingsStore.selectedProvider"
            class="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 disabled:opacity-50 min-w-0 flex-1 sm:flex-none"
          >
            <option value="">选择模型</option>
            <option
              v-for="model in availableModels"
              :key="model.id"
              :value="model.id"
            >
              {{ model.name }}
            </option>
          </select>
        </div>
      </div>
      <div v-if="shareData" class="mt-3 flex flex-wrap gap-2 text-xs">
        <span class="px-2 py-0.5 rounded-full" :class="shareData.access_mode === 'public' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
          {{ shareData.access_mode === 'public' ? '匿名访问' : '需登录' }}
        </span>
        <span class="px-2 py-0.5 rounded-full bg-gray-100 text-gray-700">
          {{ shareData.is_permanent ? '永久有效' : `到期：${shareData.expires_at || '未设置'}` }}
        </span>
        <span v-if="shareData.has_password" class="px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">
          已设置密码
        </span>
      </div>
    </div>

    <div v-if="needsLogin" class="bg-white rounded-lg shadow p-6 flex flex-col items-center gap-3 text-center">
      <p class="text-gray-700">该分享需要登录后访问，请先登录。</p>
      <button class="px-4 py-2 bg-blue-600 text-white rounded-lg" @click="goLogin">前往登录</button>
    </div>

    <div v-else-if="needPassword" class="bg-white rounded-lg shadow p-6 flex flex-col gap-3 max-w-md">
      <p class="text-gray-700">该分享已设置访问密码，请输入密码继续。</p>
      <form @submit.prevent="fetchShare">
        <!-- 隐藏的用户名字段，用于消除浏览器密码表单警告 -->
        <input
          type="text"
          name="username"
          autocomplete="username"
          style="display: none;"
          aria-hidden="true"
          tabindex="-1"
        />
        <input
          v-model="passwordInput"
          type="password"
          name="share-password"
          autocomplete="current-password"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          placeholder="请输入密码"
        />
      </form>
      <div class="flex items-center gap-2">
        <button class="px-4 py-2 bg-blue-600 text-white rounded-lg" @click="fetchShare">确定</button>
        <button class="px-4 py-2 text-gray-600" @click="passwordInput = ''">重置</button>
      </div>
      <p v-if="errorMessage" class="text-sm text-red-500">{{ errorMessage }}</p>
    </div>

    <div v-else-if="errorMessage" class="bg-white rounded-lg shadow p-6 text-center text-red-600">
      {{ errorMessage }}
    </div>

    <div v-else class="flex-1 min-h-0" v-if="shareData">
      <PlaygroundApp
        ref="playgroundAppRef"
        :system-prompt="systemPrompt"
        :prefill-payload="prefillPayload"
        @open-system-prompt="openSystemPromptModal"
      />
    </div>

    <div v-if="isLoading" class="absolute inset-0 bg-white bg-opacity-70 flex items-center justify-center text-gray-600">
      加载中...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PlaygroundApp from '@/components/playground/PlaygroundApp.js'
import SettingsModal from '@/components/settings/SettingsModal.vue'
import SystemPromptModal from '@/components/modules/optimize/components/SystemPromptModal.vue'
import { fetchPlaygroundShare, type PlaygroundShareDetail } from '@/services/apiService'
import { useSettingsStore } from '@/stores/settingsStore'
import '@/utils/playgroundGlobals'
import '@/style/playground.css'

const route = useRoute()
const router = useRouter()
const playgroundAppRef = ref<any | null>(null)

const shareData = ref<PlaygroundShareDetail | null>(null)
const systemPrompt = ref('')
const systemPromptDraft = ref('')
const showSystemPromptModal = ref(false)
const prefillPayload = ref<any | null>(null)
const isLoading = ref(false)
const errorMessage = ref('')
const needPassword = ref(false)
const needsLogin = ref(false)
const passwordInput = ref('')
const settingsStore = useSettingsStore()
const hasAppliedShareProvider = ref(false)

const availableProviders = computed(() => settingsStore.getAvailableProviders())
const availableModels = computed(() => {
  if (!settingsStore.selectedProvider) return []
  return settingsStore.getAvailableModels(settingsStore.selectedProvider)
})

const onProviderChange = () => {
  settingsStore.selectedModel = ''
  const models = availableModels.value
  if (models.length > 0) {
    settingsStore.selectedModel = models[0].id
  }
  settingsStore.saveSettings()
}

const applyShareProviderDefaults = () => {
  if (hasAppliedShareProvider.value || !shareData.value?.provider) {
    return
  }
  const providerInfo = shareData.value.provider
  const provider = availableProviders.value.find((item) => item.id === providerInfo.id)
  if (!provider) {
    hasAppliedShareProvider.value = true
    return
  }
  if (settingsStore.selectedProvider !== provider.id) {
    settingsStore.selectedProvider = provider.id
  }
  const models = settingsStore.getAvailableModels(provider.id)
  const matchModel = models.find((item) => item.id === providerInfo.modelId)
  if (matchModel) {
    settingsStore.selectedModel = matchModel.id
  } else if (!settingsStore.selectedModel && models.length > 0) {
    settingsStore.selectedModel = models[0].id
  }
  hasAppliedShareProvider.value = true
}

const shareCode = computed(() => route.params.code as string)

const openSystemPromptModal = () => {
  systemPromptDraft.value = systemPrompt.value
  showSystemPromptModal.value = true
}

const handleSystemPromptSave = () => {
  systemPrompt.value = systemPromptDraft.value
}

const fetchShare = async () => {
  if (!shareCode.value) return
  isLoading.value = true
  errorMessage.value = ''
  needPassword.value = false
  needsLogin.value = false
  try {
    const response = await fetchPlaygroundShare(shareCode.value, passwordInput.value || undefined)
    if (response.code === 200 && response.data) {
      shareData.value = response.data
      systemPrompt.value = response.data.system_prompt || ''
      hasAppliedShareProvider.value = false
      const mappedMessages = Array.isArray(response.data.messages)
        ? response.data.messages.map((msg, index) => ({
            id: msg.id || `share-${index}`,
            role: msg.role === 'model' ? 'model' : 'user',
            text: msg.text || '',
            displayText: msg.displayText,
            timestamp: msg.timestamp || Date.now() + index
          }))
        : []
      const snapshot = {
        timestamp: Date.now(),
        promptId: 0,
        title: response.data.title,
        messages: mappedMessages,
        artifact: response.data.artifact || null
      }
      prefillPayload.value = snapshot
      if (playgroundAppRef.value && typeof playgroundAppRef.value.loadSnapshot === 'function') {
        playgroundAppRef.value.loadSnapshot({
          messages: mappedMessages,
          artifact: response.data.artifact || null
        })
      }
      applyShareProviderDefaults()
      passwordInput.value = ''
    } else if (response.code === 403 && response.need_password) {
      shareData.value = null
      needPassword.value = true
      errorMessage.value = response.message || '需要访问密码'
    } else if (response.code === 401) {
      shareData.value = null
      needsLogin.value = true
      errorMessage.value = response.message || '请先登录'
    } else {
      shareData.value = null
      errorMessage.value = response.message || '无法加载分享内容'
    }
  } catch (error: any) {
    shareData.value = null
    errorMessage.value = error?.message || '加载失败'
  } finally {
    isLoading.value = false
  }
}

const goLogin = () => {
  router.push({ path: '/login', query: { redirect: `/playground/share/${shareCode.value}` } })
}

watch(
  () => shareCode.value,
  () => {
    hasAppliedShareProvider.value = false
    fetchShare()
  },
  { immediate: true }
)

watch(availableProviders, () => {
  applyShareProviderDefaults()
})

watch(
  () => shareData.value,
  () => {
    applyShareProviderDefaults()
  }
)
</script>
