<template>
  <div>
    <div class="mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium">AI服务提供商</h3>
        <button
          @click="$emit('show-add-provider-type')"
          class="flex items-center space-x-1 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
        >
          <Plus class="w-4 h-4" />
          <span>添加提供商</span>
        </button>
      </div>
    
      <div class="mb-4 border border-blue-200 rounded-lg overflow-hidden">
        <button
          @click="showApiHelp = !showApiHelp"
          class="w-full px-4 py-3 bg-blue-50 hover:bg-blue-100 transition-colors flex items-center justify-between text-sm font-medium text-blue-800"
        >
          <span>📖 API配置说明</span>
          <span class="transform transition-transform" :class="{ 'rotate-180': showApiHelp }">▼</span>
        </button>
        <div v-show="showApiHelp" class="p-4 bg-blue-50 border-t border-blue-200">
          <div class="text-sm text-blue-700 space-y-2">
            <div><strong>OpenAI及兼容服务：</strong>API URL填写完整路径，如 <code class="bg-blue-100 px-1 rounded break-all text-xs">https://api.openai.com/v1/chat/completions</code></div>
            <div><strong>OpenAI Responses：</strong>使用 <code class="bg-blue-100 px-1 rounded break-all text-xs">https://api.openai.com/v1/responses</code> 以兼容 /v1/responses 协议，规避部分上游对 system prompt 的限制</div>
            <div><strong>Anthropic Claude：</strong>API URL填写 <code class="bg-blue-100 px-1 rounded break-all text-xs">https://api.anthropic.com/v1/messages</code></div>
            <div><strong>Google Gemini：</strong>API URL填写 <code class="bg-blue-100 px-1 rounded break-all text-xs">https://generativelanguage.googleapis.com/v1beta</code>（系统会自动根据模型拼接路径）</div>
            <div><strong>自定义提供商：</strong>大多数第三方服务使用OpenAI兼容格式，URL结构为 <code class="bg-blue-100 px-1 rounded break-all text-xs">https://你的域名/v1/chat/completions</code></div>
            <div class="text-xs text-blue-600 mt-2">支持代理地址、中转API等各种自定义URL</div>
          </div>
          
          <div class="mt-3 pt-3 border-t border-blue-200">
            <h4 class="text-sm font-medium text-blue-800 mb-2">附件多模态支持</h4>
            <div class="text-sm text-blue-700 space-y-1">
              <div><strong>OpenAI：</strong>支持图片（GPT-4 Vision及更高版本）
                <div class="text-xs text-blue-600 ml-4">• API支持格式：PNG, JPEG, WEBP, GIF</div>
                <div class="text-xs text-blue-600 ml-4">• 注意：ChatGPT网页版支持PDF/Office文档，但API不支持</div>
              </div>
              <div><strong>Anthropic Claude：</strong>支持图片（Claude 3系列）
                <div class="text-xs text-blue-600 ml-4">• 图片格式：PNG, JPEG, WEBP, GIF</div>
                <div class="text-xs text-blue-600 ml-4">• PDF文档：Claude 3.5+（最多100页）</div>
              </div>
              <div><strong>Google Gemini：</strong>全面支持图片、文档（PDF/Office）、音频、视频等多模态
                <div class="text-xs text-blue-600 ml-4">• 图片：PNG, JPEG, WEBP, GIF, BMP, TIFF, SVG, HEIC</div>
                <div class="text-xs text-blue-600 ml-4">• 文档：PDF, Office(Word/Excel/PPT), TXT, Markdown, CSV等</div>
                <div class="text-xs text-blue-600 ml-4">• 音频：WAV, MP3, AAC, OGG, FLAC</div>
                <div class="text-xs text-blue-600 ml-4">• 视频：MP4, MOV, AVI, WebM等</div>
              </div>
              <div class="text-xs text-blue-600 mt-2">💡 如需上传表格等文档，建议使用 Google Gemini 模型</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="providers.length === 0" class="text-center py-8 text-gray-500">
        <Settings class="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p>还没有配置任何AI提供商</p>
        <p class="text-sm">点击上方按钮添加您的第一个AI服务</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="provider in providers"
          :key="provider.id"
          class="border rounded-lg p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center space-x-3">
              <input
                v-model="provider.enabled"
                type="checkbox"
                class="rounded"
                @change="$emit('save')"
              />
              <h4 class="font-medium">{{ provider.name }}</h4>
              <span class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {{ provider.type }}
              </span>
              <CheckCircle v-if="provider.enabled && provider.apiKey" class="w-4 h-4 text-green-600" title="已配置" />
              
              <div v-if="batchTestingStates[provider.id]?.isTesting" class="flex items-center space-x-2 text-sm">
                <span class="text-blue-600">
                  {{ batchTestingStates[provider.id].isAborted ? '已停止测试' : `测试中 ${batchTestingStates[provider.id].currentModelIndex}/${batchTestingStates[provider.id].totalModels}` }}
                </span>
                <div class="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-blue-500 transition-all duration-300"
                    :style="{ width: `${(batchTestingStates[provider.id].currentModelIndex / batchTestingStates[provider.id].totalModels) * 100}%` }"
                  ></div>
                </div>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="$emit('edit-provider', provider)"
                class="text-blue-500 hover:text-blue-700"
                title="编辑提供商"
              >
                <Settings class="w-4 h-4" />
              </button>
              <button
                @click="$emit('batch-test', provider)"
                :disabled="!provider.apiKey || provider.models.length === 0"
                class="text-green-500 hover:text-green-700 disabled:opacity-50 transition-colors"
                :title="getBatchTestButtonTitle(provider)"
              >
                <Square v-if="batchTestingStates[provider.id]?.isTesting" class="w-4 h-4" :class="{ 'animate-pulse': testingProvider === provider.id }" />
                <Zap v-else class="w-4 h-4" />
              </button>
              <button
                @click="$emit('delete-provider', provider.id)"
                class="text-red-500 hover:text-red-700"
                title="删除提供商"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">API密钥</label>
              <input
                v-model="provider.apiKey"
                type="password"
                placeholder="输入API密钥"
                autocomplete="off"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                @input="$emit('save')"
              />
            </div>
            <div v-if="provider.allowCustomUrl || provider.type === 'custom'">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                API URL
                <span v-if="provider.type !== 'custom'" class="text-xs text-gray-500">(可选，留空使用官方完整地址)</span>
              </label>
              <input
                v-model="provider.baseUrl"
                type="url"
                :placeholder="getDefaultBaseUrl(provider.type)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                @input="$emit('save')"
              />
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-gray-700">可用模型</label>
              <button
                @click="$emit('show-add-model', provider.id)"
                class="text-sm text-blue-500 hover:text-blue-700"
              >
                添加模型
              </button>
            </div>
            <div class="space-y-2 max-h-32 overflow-y-auto">
              <div
                v-for="model in provider.models"
                :key="model.id"
                class="relative flex items-center justify-between p-2 bg-gray-50 rounded min-w-0 overflow-x-auto"
              >
                <div class="flex items-center space-x-2 flex-shrink-0">
                  <input
                    v-model="model.enabled"
                    type="checkbox"
                    class="rounded flex-shrink-0"
                    @change="$emit('save')"
                  />
                  <span class="text-sm font-medium whitespace-nowrap">{{ model.name }}</span>
                  
                  <div class="flex items-center space-x-1 flex-shrink-0">
                    <span v-if="model.capabilities?.reasoning" 
                          class="inline-flex items-center text-xs bg-purple-100 text-purple-800 rounded-full w-4 h-4 justify-center"
                          :title="getReasoningTypeDescription(model.capabilities.reasoningType)">
                      🧠
                    </span>
                    <span v-if="model.capabilities?.testResult?.connected" 
                          class="inline-flex items-center text-xs bg-green-100 text-green-800 rounded-full w-4 h-4 justify-center">
                      ✅
                    </span>
                    <span v-if="model.testStatus === 'failed'" 
                          class="inline-flex items-center text-xs bg-red-100 text-red-800 rounded-full w-4 h-4 justify-center">
                      ❌
                    </span>
                  </div>
                  
                  <span 
                    v-if="model.apiType"
                    class="text-xs px-1.5 py-0.5 rounded text-white flex-shrink-0"
                    :class="getApiTypeColor(model.apiType)"
                  >
                    {{ getApiTypeLabel(model.apiType) }}
                  </span>
                </div>
                
                <div class="flex items-center space-x-1 flex-shrink-0">
                  <button
                    @click="$emit('test-model', provider.id, model.id, model.testStatus)"
                    :disabled="!provider.apiKey"
                    :class="[
                      'transition-colors text-sm',
                      model.testStatus === 'testing' ? 'text-blue-600 hover:text-blue-800' : 
                      model.testStatus === 'success' ? 'text-green-500 hover:text-green-700' :
                      model.testStatus === 'failed' ? 'text-red-500 hover:text-red-700' :
                      'text-gray-400 hover:text-blue-500'
                    ]"
                    :title="getTestButtonTitle(model)"
                  >
                    <Square v-if="model.testStatus === 'testing'" class="w-3 h-3 animate-pulse" />
                    <Zap v-else class="w-3 h-3" />
                  </button>
                  <button
                    @click="$emit('edit-model', provider.id, model)"
                    class="text-blue-500 hover:text-blue-700"
                    title="编辑模型"
                  >
                    <Settings class="w-3 h-3" />
                  </button>
                  <button
                    @click="$emit('delete-model', provider.id, model.id)"
                    class="text-red-500 hover:text-red-700"
                    title="删除模型"
                  >
                    <X class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Settings, Plus, CheckCircle, Zap, Square, Trash2, X } from 'lucide-vue-next'
import type { ProviderConfig } from '@/stores/settingsStore'
import { useSettingsStore } from '@/stores/settingsStore'

const settingsStore = useSettingsStore()
const showApiHelp = ref(false)

defineProps<{
  providers: ProviderConfig[]
  batchTestingStates: Record<string, any>
  testingProvider: string | null
  getDefaultBaseUrl: (type: string) => string
  getTestButtonTitle: (model: any) => string
  getBatchTestButtonTitle: (provider: any) => string
  getApiTypeColor: (apiType: string) => string
  getApiTypeLabel: (apiType: string) => string
}>()

defineEmits<{
  'show-add-provider-type': []
  'edit-provider': [provider: ProviderConfig]
  'delete-provider': [providerId: string]
  'batch-test': [provider: ProviderConfig]
  'show-add-model': [providerId: string]
  'edit-model': [providerId: string, model: any]
  'delete-model': [providerId: string, modelId: string]
  'test-model': [providerId: string, modelId: string, testStatus: string | undefined]
  'save': []
}>()

const getReasoningTypeDescription = (reasoningType: any) => {
  return settingsStore.getReasoningTypeDescription(reasoningType)
}
</script>
