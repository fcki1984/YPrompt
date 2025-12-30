<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
    <div class="bg-white rounded-lg max-w-md w-full p-6">
      <h3 class="text-lg font-semibold mb-4">
        {{ editing ? '编辑模型' : '添加模型' }}
      </h3>

      <div class="space-y-4">
        <!-- 模型名称 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">模型名称</label>
          <input
            :value="name"
            @input="$emit('update:name', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="例如：gemini-2.5-flash-lite"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- 模型ID -->
        <div>
          <div class="flex items-center justify-between mb-1">
            <label class="block text-sm font-medium text-gray-700">模型ID</label>
            <button
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
            placeholder="例如：gemini-1.5-pro"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />

          <!-- 模型列表 -->
          <div v-if="availableModels.length > 0 || searchKeyword.trim()" class="mt-2">
            <p class="text-xs text-gray-600 mb-2">点击选择模型：</p>

            <!-- 搜索框 -->
            <div class="mb-2">
              <input
                :value="searchKeyword"
                @input="$emit('update:searchKeyword', ($event.target as HTMLInputElement).value)"
                type="text"
                placeholder="🔍 输入关键词筛选模型... (支持多个关键词用空格分隔)"
                class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-transparent placeholder-gray-400"
              />
            </div>

            <!-- 搜索结果提示 -->
            <div v-if="searchKeyword.trim() && availableModels.length === 0" class="text-xs text-gray-500 mb-2">
              未找到包含 "{{ searchKeyword }}" 的模型
            </div>
            <div v-else-if="searchKeyword.trim() || supportsImage" class="text-xs text-gray-500 mb-2">
              <span v-if="supportsImage" class="text-blue-600">
                仅显示支持图像生成的模型 ·
              </span>
              找到 {{ availableModels.length }} 个匹配的模型
            </div>

            <!-- 模型列表 -->
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

          <!-- 错误提示 -->
          <div v-if="error" class="mt-2">
            <p class="text-xs text-red-600">{{ error }}</p>
          </div>
        </div>

        <!-- 支持图像生成 -->
        <div>
          <div class="flex items-center space-x-2">
            <input
              :checked="supportsImage"
              @change="$emit('update:supportsImage', ($event.target as HTMLInputElement).checked)"
              type="checkbox"
              id="supportsImage"
              class="rounded"
            />
            <label for="supportsImage" class="text-sm text-gray-700">
              支持图像生成
            </label>
          </div>
          <p class="text-xs text-gray-500 mt-1 ml-5">
            勾选后,模型列表将自动过滤,仅显示支持图像生成的模型(模型ID包含 image/imagen 等关键词)
          </p>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="flex justify-end space-x-3 mt-6">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          取消
        </button>
        <button
          @click="$emit('save')"
          :disabled="!name || !id"
          class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
        >
          {{ editing ? '保存' : '添加' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  editing: boolean
  id: string
  name: string
  supportsImage: boolean
  searchKeyword: string
  availableModels: string[]
  loading: boolean
  error: string
}>()

defineEmits<{
  'update:id': [value: string]
  'update:name': [value: string]
  'update:supportsImage': [value: boolean]
  'update:searchKeyword': [value: string]
  'fetch-models': []
  'select-model': [modelId: string]
  'save': []
  'close': []
}>()
</script>
