<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg max-w-4xl w-full h-[90vh] flex flex-col overflow-hidden" @click.stop>
      <!-- 头部 -->
      <div class="flex items-center justify-between p-6 border-b flex-shrink-0">
        <div class="flex items-center space-x-4">
          <h2 class="text-xl font-semibold">绘图设置</h2>
          <div class="flex space-x-1">
            <button
              @click="activeTab = 'models'"
              :class="[
                'px-3 py-1 rounded text-sm font-medium transition-colors',
                activeTab === 'models'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-800'
              ]"
            >
              AI模型
            </button>
            <button
              @click="activeTab = 'params'"
              :class="[
                'px-3 py-1 rounded text-sm font-medium transition-colors',
                activeTab === 'params'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-800'
              ]"
            >
              模型参数
            </button>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="p-1 hover:bg-gray-100 rounded"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- 内容 -->
      <div class="flex-1 overflow-y-auto p-6">
        <!-- AI模型标签页 -->
        <DrawingProvidersTab
          v-if="activeTab === 'models'"
          :providers="drawingStore.providers"
          @show-add-provider-type="providerMgmt.showAddProviderTypeDialog.value = true"
          @edit-provider="providerMgmt.editProvider"
          @delete-provider="providerMgmt.deleteProvider"
          @show-add-model="modelMgmt.showAddModel"
          @edit-model="modelMgmt.editModel"
          @delete-model="modelMgmt.deleteModel"
          @save="drawingStore.saveProviders"
          :get-default-base-url="providerMgmt.getDefaultBaseUrl"
        />

        <!-- 模型参数标签页 -->
        <DrawingParamsTab v-if="activeTab === 'params'" />
      </div>

      <!-- 底部按钮 -->
      <div class="flex justify-end space-x-3 p-4 border-t bg-gray-50 flex-shrink-0">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          取消
        </button>
        <button
          @click="handleSave"
          class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
        >
          保存设置
        </button>
      </div>
    </div>
  </div>

  <!-- 提供商类型选择对话框 -->
  <DrawingProviderTypeDialog
    v-if="providerMgmt.showAddProviderTypeDialog.value"
    @select="providerMgmt.selectProviderType"
    @close="providerMgmt.showAddProviderTypeDialog.value = false"
  />

  <!-- 提供商编辑对话框 -->
  <DrawingProviderDialog
    v-if="providerMgmt.showAddProvider.value"
    :editing="!!providerMgmt.editingProvider.value"
    :provider-type="providerMgmt.selectedProviderType.value"
    v-model:name="providerMgmt.newProvider.value.name"
    v-model:base-url="providerMgmt.newProvider.value.baseURL"
    v-model:api-key="providerMgmt.newProvider.value.apiKey"
    :get-default-base-url="providerMgmt.getDefaultBaseUrl"
    @save="providerMgmt.saveProvider"
    @close="providerMgmt.closeProviderDialog"
  />

  <!-- 模型编辑对话框 -->
  <DrawingModelDialog
    v-if="modelMgmt.showAddModelDialog.value"
    :editing="!!modelMgmt.editingModel.value"
    v-model:id="modelMgmt.newModel.value.id"
    v-model:name="modelMgmt.newModel.value.name"
    v-model:supports-image="modelMgmt.newModel.value.supportsImage"
    v-model:search-keyword="modelMgmt.modelSearchKeyword.value"
    :available-models="modelMgmt.getCurrentProviderModels.value"
    :loading="modelMgmt.loadingModels.value"
    :error="modelMgmt.modelFetchError.value"
    @fetch-models="modelMgmt.fetchAvailableModels"
    @select-model="modelMgmt.selectModel"
    @save="modelMgmt.addCustomModel"
    @close="modelMgmt.closeAddModelDialog"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { X } from 'lucide-vue-next'
import { useDrawingStore } from '@/stores/drawingStore'
import { useDrawingProviderManagement } from './composables/useDrawingProviderManagement'
import { useDrawingModelManagement } from './composables/useDrawingModelManagement'
import DrawingProvidersTab from './tabs/DrawingProvidersTab.vue'
import DrawingParamsTab from './tabs/DrawingParamsTab.vue'
import DrawingProviderTypeDialog from './dialogs/DrawingProviderTypeDialog.vue'
import DrawingProviderDialog from './dialogs/DrawingProviderDialog.vue'
import DrawingModelDialog from './dialogs/DrawingModelDialog.vue'

const drawingStore = useDrawingStore()
const activeTab = ref<'models' | 'params'>('models')

const providerMgmt = useDrawingProviderManagement()
const modelMgmt = useDrawingModelManagement()

const emit = defineEmits<{
  'close': []
}>()

// 保存设置并关闭
const handleSave = () => {
  // 保存提供商配置
  drawingStore.saveProviders()
  // 保存模型参数配置
  drawingStore.saveSettings()
  // 关闭对话框
  emit('close')
}
</script>
