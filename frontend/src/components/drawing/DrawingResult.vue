<template>
  <div class="drawing-result h-full flex flex-col bg-white rounded-lg shadow-sm overflow-hidden">
    <!-- 头部 -->
    <div class="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
      <h3 class="font-semibold text-gray-900">生成结果</h3>
      <div class="flex items-center space-x-2">
        <button
          @click="clearAllImages"
          :disabled="images.length === 0"
          class="text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          清空历史
        </button>
      </div>
    </div>

    <!-- 结果区域 -->
    <div class="flex-1 overflow-y-auto p-4">
      <!-- 无结果提示 -->
      <div v-if="images.length === 0" class="h-full flex flex-col items-center justify-center text-gray-500">
        <ImageIcon class="w-16 h-16 mb-4 opacity-50" />
        <p class="text-lg mb-2">暂无生成结果</p>
        <p class="text-sm">开始对话生成图片吧</p>
      </div>

      <!-- 图片网格 -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        <div
          v-for="image in images"
          :key="image.id"
          class="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow flex flex-col"
        >
          <!-- 图片区域 - 固定高度 -->
          <div class="relative group cursor-pointer flex-shrink-0 h-48 bg-gray-100" @click="openImagePreview(image)">
            <img
              :src="`data:${image.mimeType};base64,${image.imageData}`"
              :alt="image.prompt"
              class="w-full h-full object-cover"
            />

            <!-- 悬停操作栏 -->
            <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
              <div class="flex space-x-2">
                <button
                  @click.stop="downloadImage(image)"
                  class="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors"
                  title="下载图片"
                >
                  <Download class="w-5 h-5 text-gray-700" />
                </button>
                <button
                  @click.stop="deleteImage(image.id)"
                  class="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors"
                  title="删除图片"
                >
                  <Trash2 class="w-5 h-5 text-red-600" />
                </button>
              </div>
            </div>
          </div>

          <!-- 信息区域 - 固定在底部 -->
          <div class="p-3 bg-gray-50 flex-shrink-0">
            <!-- 提示词 -->
            <p class="text-sm text-gray-700 mb-2 line-clamp-2" :title="image.prompt">
              {{ image.prompt }}
            </p>

            <!-- 详细信息 -->
            <div class="flex items-center justify-between text-xs text-gray-500">
              <div class="flex items-center space-x-3">
                <span>{{ image.generationConfig.aspectRatio }}</span>
                <span>{{ image.generationConfig.imageSize }}</span>
              </div>
              <span>{{ formatTime(image.timestamp) }}</span>
            </div>

            <!-- 展开详情按钮 -->
            <button
              @click="toggleDetails(image.id)"
              class="mt-2 text-xs text-blue-600 hover:text-blue-700 flex items-center space-x-1"
            >
              <span>{{ expandedDetails.includes(image.id) ? '收起' : '展开' }}详情</span>
              <ChevronDown
                :class="[
                  'w-4 h-4 transition-transform',
                  expandedDetails.includes(image.id) ? 'rotate-180' : ''
                ]"
              />
            </button>

            <!-- 详细信息 -->
            <div
              v-if="expandedDetails.includes(image.id)"
              class="mt-2 pt-2 border-t border-gray-200 space-y-2 text-xs"
            >
              <!-- 完整提示词 -->
              <div class="space-y-1">
                <div class="text-gray-600 font-medium">提示词:</div>
                <div class="text-gray-900 bg-gray-100 rounded p-2 break-words">{{ image.prompt }}</div>
              </div>

              <!-- 图片配置 -->
              <div class="space-y-1">
                <div class="text-gray-600 font-medium">图片配置:</div>
                <div class="bg-gray-100 rounded p-2 space-y-1">
                  <div class="flex justify-between">
                    <span class="text-gray-600">宽高比:</span>
                    <span class="text-gray-900">{{ image.generationConfig.aspectRatio }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">图片大小:</span>
                    <span class="text-gray-900">{{ image.generationConfig.imageSize }}</span>
                  </div>
                </div>
              </div>

              <!-- 基础生成参数 -->
              <div class="space-y-1">
                <div class="text-gray-600 font-medium">生成参数:</div>
                <div class="bg-gray-100 rounded p-2 space-y-1">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Temperature:</span>
                    <span class="text-gray-900">{{ image.generationConfig.temperature }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Top P:</span>
                    <span class="text-gray-900">{{ image.generationConfig.topP }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Top K:</span>
                    <span class="text-gray-900">{{ image.generationConfig.topK }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">最大输出Token:</span>
                    <span class="text-gray-900">{{ image.generationConfig.maxOutputTokens }}</span>
                  </div>
                  <!-- candidateCount 已移除 - 大多数Gemini模型不支持此参数 -->
                </div>
              </div>

              <!-- 惩罚参数（如果非零才显示） -->
              <div
                v-if="image.generationConfig.presencePenalty !== 0 || image.generationConfig.frequencyPenalty !== 0"
                class="space-y-1"
              >
                <div class="text-gray-600 font-medium">惩罚参数:</div>
                <div class="bg-gray-100 rounded p-2 space-y-1">
                  <div v-if="image.generationConfig.presencePenalty !== 0" class="flex justify-between">
                    <span class="text-gray-600">Presence Penalty:</span>
                    <span class="text-gray-900">{{ image.generationConfig.presencePenalty }}</span>
                  </div>
                  <div v-if="image.generationConfig.frequencyPenalty !== 0" class="flex justify-between">
                    <span class="text-gray-600">Frequency Penalty:</span>
                    <span class="text-gray-900">{{ image.generationConfig.frequencyPenalty }}</span>
                  </div>
                </div>
              </div>

              <!-- 高级参数 -->
              <div
                v-if="image.generationConfig.seed || image.generationConfig.responseLogprobs"
                class="space-y-1"
              >
                <div class="text-gray-600 font-medium">高级参数:</div>
                <div class="bg-gray-100 rounded p-2 space-y-1">
                  <div v-if="image.generationConfig.seed" class="flex justify-between">
                    <span class="text-gray-600">Seed:</span>
                    <span class="text-gray-900">{{ image.generationConfig.seed }}</span>
                  </div>
                  <div v-if="image.generationConfig.responseLogprobs" class="flex justify-between">
                    <span class="text-gray-600">响应日志概率:</span>
                    <span class="text-gray-900">启用</span>
                  </div>
                  <div v-if="image.generationConfig.logprobs" class="flex justify-between">
                    <span class="text-gray-600">Logprobs:</span>
                    <span class="text-gray-900">{{ image.generationConfig.logprobs }}</span>
                  </div>
                  <div v-if="image.generationConfig.enableEnhancedCivicAnswers" class="flex justify-between">
                    <span class="text-gray-600">增强公民诚信:</span>
                    <span class="text-gray-900">启用</span>
                  </div>
                </div>
              </div>

              <!-- 响应格式 -->
              <div class="space-y-1">
                <div class="text-gray-600 font-medium">响应格式:</div>
                <div class="bg-gray-100 rounded p-2 space-y-1">
                  <div class="flex justify-between">
                    <span class="text-gray-600">模态:</span>
                    <span class="text-gray-900">{{ image.generationConfig.responseModalities.join(', ') }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">MIME类型:</span>
                    <span class="text-gray-900">{{ image.generationConfig.responseMimeType }}</span>
                  </div>
                  <div v-if="image.generationConfig.mediaResolution !== 'MEDIA_RESOLUTION_UNSPECIFIED'" class="flex justify-between">
                    <span class="text-gray-600">媒体分辨率:</span>
                    <span class="text-gray-900">{{ image.generationConfig.mediaResolution }}</span>
                  </div>
                </div>
              </div>

              <!-- 工具配置 -->
              <div
                v-if="image.generationConfig.useGoogleSearch || image.generationConfig.useCodeExecution || (image.generationConfig.functionDeclarations && image.generationConfig.functionDeclarations.length > 0)"
                class="space-y-1"
              >
                <div class="text-gray-600 font-medium">工具配置:</div>
                <div class="bg-gray-100 rounded p-2 space-y-1">
                  <div v-if="image.generationConfig.useGoogleSearch" class="flex justify-between">
                    <span class="text-gray-600">Google搜索:</span>
                    <span class="text-gray-900 text-green-600">✓ 启用</span>
                  </div>
                  <div v-if="image.generationConfig.useCodeExecution" class="flex justify-between">
                    <span class="text-gray-600">代码执行:</span>
                    <span class="text-gray-900 text-green-600">✓ 启用</span>
                  </div>
                  <div v-if="image.generationConfig.functionDeclarations && image.generationConfig.functionDeclarations.length > 0" class="flex justify-between">
                    <span class="text-gray-600">自定义函数:</span>
                    <span class="text-gray-900">{{ image.generationConfig.functionDeclarations.length }} 个</span>
                  </div>
                  <div v-if="image.generationConfig.functionCallingMode && image.generationConfig.functionCallingMode !== 'FUNCTION_CALLING_CONFIG_MODE_UNSPECIFIED'" class="flex justify-between">
                    <span class="text-gray-600">调用模式:</span>
                    <span class="text-gray-900">{{ image.generationConfig.functionCallingMode }}</span>
                  </div>
                </div>
              </div>

              <!-- 停止序列（如果有） -->
              <div v-if="image.generationConfig.stopSequences && image.generationConfig.stopSequences.length > 0" class="space-y-1">
                <div class="text-gray-600 font-medium">停止序列:</div>
                <div class="bg-gray-100 rounded p-2">
                  <div class="text-gray-900">{{ image.generationConfig.stopSequences.join(', ') }}</div>
                </div>
              </div>

              <!-- 安全设置 -->
              <div v-if="image.generationConfig.safetySettings && image.generationConfig.safetySettings.length > 0" class="space-y-1">
                <div class="text-gray-600 font-medium">安全设置:</div>
                <div class="bg-gray-100 rounded p-2 space-y-1">
                  <div
                    v-for="(setting, index) in image.generationConfig.safetySettings"
                    :key="index"
                    class="flex justify-between text-xs"
                  >
                    <span class="text-gray-600">{{ formatSafetyCategory(setting.category) }}:</span>
                    <span class="text-gray-900">{{ formatSafetyThreshold(setting.threshold) }}</span>
                  </div>
                </div>
              </div>

              <!-- 时间戳 -->
              <div class="space-y-1">
                <div class="text-gray-600 font-medium">生成时间:</div>
                <div class="bg-gray-100 rounded p-2">
                  <div class="text-gray-900">{{ formatFullTime(image.timestamp) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片预览模态框 -->
    <div
      v-if="previewImage"
      class="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
      @click="closeImagePreview"
    >
      <div class="max-w-6xl max-h-full" @click.stop>
        <img
          :src="`data:${previewImage.mimeType};base64,${previewImage.imageData}`"
          :alt="previewImage.prompt"
          class="max-w-full max-h-[90vh] object-contain"
        />
      </div>
      <button
        @click="closeImagePreview"
        class="absolute top-4 right-4 p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-full text-white"
      >
        <X class="w-6 h-6" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Download, Trash2, ChevronDown, X, ImageIcon } from 'lucide-vue-next'
import { useDrawingStore } from '@/stores/drawingStore'
import type { GeneratedImage } from '@/stores/drawingStore'

const drawingStore = useDrawingStore()

// 状态
const images = ref<GeneratedImage[]>([])
const expandedDetails = ref<string[]>([])
const previewImage = ref<GeneratedImage | null>(null)

// 监听 store 的变化
watch(
  () => drawingStore.generatedImages,
  (newImages) => {
    images.value = newImages
  },
  { deep: true, immediate: true }
)

// 方法：格式化时间
const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 小于1分钟
  if (diff < 60 * 1000) {
    return '刚刚'
  }
  // 小于1小时
  if (diff < 60 * 60 * 1000) {
    return `${Math.floor(diff / (60 * 1000))}分钟前`
  }
  // 小于1天
  if (diff < 24 * 60 * 60 * 1000) {
    return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  }
  // 其他
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 方法：格式化完整时间
const formatFullTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 方法：格式化安全类别
const formatSafetyCategory = (category: string): string => {
  const categoryMap: Record<string, string> = {
    'HARM_CATEGORY_HARASSMENT': '骚扰',
    'HARM_CATEGORY_HATE_SPEECH': '仇恨言论',
    'HARM_CATEGORY_SEXUALLY_EXPLICIT': '色情内容',
    'HARM_CATEGORY_DANGEROUS_CONTENT': '危险内容',
    'HARM_CATEGORY_DEROGATORY': '贬损',
    'HARM_CATEGORY_TOXICITY': '有毒内容',
    'HARM_CATEGORY_VIOLENCE': '暴力',
    'HARM_CATEGORY_SEXUAL': '性内容',
    'HARM_CATEGORY_MEDICAL': '医疗',
    'HARM_CATEGORY_DANGEROUS': '危险',
    'HARM_CATEGORY_CIVIC_INTEGRITY': '公民诚信'
  }
  return categoryMap[category] || category
}

// 方法：格式化安全阈值
const formatSafetyThreshold = (threshold: string): string => {
  const thresholdMap: Record<string, string> = {
    'BLOCK_NONE': '不阻止',
    'BLOCK_ONLY_HIGH': '仅阻止高风险',
    'BLOCK_MEDIUM_AND_ABOVE': '阻止中等及以上',
    'BLOCK_LOW_AND_ABOVE': '阻止低及以上',
    'OFF': '关闭'
  }
  return thresholdMap[threshold] || threshold
}

// 方法：切换详情展开
const toggleDetails = (imageId: string) => {
  const index = expandedDetails.value.indexOf(imageId)
  if (index > -1) {
    expandedDetails.value.splice(index, 1)
  } else {
    expandedDetails.value.push(imageId)
  }
}

// 方法：下载图片
const downloadImage = (image: GeneratedImage) => {
  const link = document.createElement('a')
  link.href = `data:${image.mimeType};base64,${image.imageData}`
  link.download = `drawing_${image.timestamp}.${image.mimeType.split('/')[1]}`
  link.click()
}

// 方法：删除图片
const deleteImage = (imageId: string) => {
  if (confirm('确定要删除这张图片吗？')) {
    drawingStore.deleteImage(imageId)
  }
}

// 方法：清空所有图片
const clearAllImages = () => {
  if (confirm('确定要清空所有生成的图片吗？')) {
    drawingStore.clearImages()
    expandedDetails.value = []
  }
}

// 方法：打开图片预览
const openImagePreview = (image: GeneratedImage) => {
  previewImage.value = image
}

// 方法：关闭图片预览
const closeImagePreview = () => {
  previewImage.value = null
}
</script>

<style scoped>
/* 滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 文本截断 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
