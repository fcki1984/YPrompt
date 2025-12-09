<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
    <div class="bg-white rounded-lg max-w-md w-full p-6">
      <h3 class="text-lg font-semibold mb-4">{{ editing ? '编辑模型' : '添加模型' }}</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">模型名称</label>
          <input
            :value="name"
            @input="$emit('update:name', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="例如：DeepSeek Chat"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <div class="flex items-center justify-between mb-1">
            <label class="block text-sm font-medium text-gray-700">模型ID</label>
            <button
              v-if="provider?.type !== 'anthropic'"
              @click="$emit('fetch-models')"
              :disabled="loading"
              class="text-xs text-blue-500 hover:text-blue-700 disabled:opacity-50"
            >
              {{ loading ? '获取中...' : '🔄 获取模型列表' }}
            </button>
          </div>
          <input
            :value="id"
            @input="$emit('update:id', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="例如：deepseek-chat"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          
          <div v-if="availableModels.length > 0" class="mt-2">
            <p class="text-xs text-gray-600 mb-2">点击选择模型：</p>
            
            <div class="mb-2">
              <input
                :value="searchKeyword"
                @input="$emit('update:searchKeyword', ($event.target as HTMLInputElement).value)"
                type="text"
                placeholder="🔍 输入关键词筛选模型... (支持多个关键词用空格分隔)"
                class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-transparent placeholder-gray-400"
              />
            </div>
            
            <div v-if="searchKeyword.trim() && availableModels.length === 0" class="text-xs text-gray-500 mb-2">
              未找到包含 "{{ searchKeyword }}" 的模型
            </div>
            <div v-else-if="searchKeyword.trim()" class="text-xs text-gray-500 mb-2">
              找到 {{ availableModels.length }} 个匹配的模型
            </div>
            
            <div class="max-h-32 overflow-y-auto border border-gray-200 rounded">
              <div
                v-for="modelId in availableModels"
                :key="modelId"
                @click="$emit('select-model', modelId)"
                class="px-3 py-2 text-sm cursor-pointer hover:bg-blue-50 border-b border-gray-100 last:border-b-0"
              >
                <span class="font-mono">{{ modelId }}</span>
              </div>
            </div>
          </div>
          
          <div v-if="error" class="mt-2">
            <p class="text-xs text-red-600">{{ error }}</p>
          </div>
        </div>

        <div v-if="provider?.type === 'custom'">
          <label class="block text-sm font-medium text-gray-700 mb-1">API类型</label>
          <select
            :value="apiType"
            @change="$emit('update:apiType', ($event.target as HTMLSelectElement).value)"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">选择API类型</option>
            <option value="openai">OpenAI 兼容</option>
            <option value="openai-responses">OpenAI Responses</option>
            <option value="anthropic">Anthropic 兼容</option>
            <option value="google">Gemini 兼容</option>
          </select>
          <p class="text-xs text-gray-500 mt-1">
            选择此模型使用的API协议类型。大多数第三方代理服务使用OpenAI兼容格式。
          </p>
        </div>
      </div>

      <div class="flex justify-end space-x-3 mt-6">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          取消
        </button>
        <button
          @click="$emit('save')"
          :disabled="!name || !id || (provider?.type === 'custom' && !apiType)"
          class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
        >
          {{ editing ? '保存' : '添加' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ProviderConfig } from '@/stores/settingsStore'

defineProps<{
  editing: boolean
  provider: ProviderConfig | undefined
  name: string
  id: string
  apiType: string
  searchKeyword: string
  availableModels: string[]
  loading: boolean
  error: string
}>()

defineEmits<{
  'update:name': [value: string]
  'update:id': [value: string]
  'update:apiType': [value: string]
  'update:searchKeyword': [value: string]
  'fetch-models': []
  'select-model': [modelId: string]
  save: []
  close: []
}>()
</script>
