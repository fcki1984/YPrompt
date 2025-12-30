<template>
  <div class="space-y-6">
    <!-- 当前模型信息 -->
    <div v-if="currentModel && currentProvider" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-sm font-medium text-gray-900">当前图像生成模型</h3>
          <p class="text-sm text-gray-600 mt-1">
            {{ currentProvider.name }} - {{ currentModel.name }}
          </p>
        </div>
        <div class="flex items-center space-x-2">
          <span v-if="currentModel.supportsImage" class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
            支持图像生成
          </span>
        </div>
      </div>
    </div>

    <!-- 无模型选中提示 -->
    <div v-else class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <p class="text-sm text-yellow-800">
        请先在「AI模型」标签页选择一个支持图像生成的模型
      </p>
    </div>

    <!-- 参数配置表单 -->
    <div v-if="currentModel" class="space-y-6">
      <!-- 标题和重置按钮 -->
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900">
          {{ currentModel.supportsImage ? '图像生成参数配置' : '模型参数配置' }}
        </h3>
        <button
          @click="handleReset"
          class="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          重置为默认值
        </button>
      </div>

      <!-- imageConfig: 图像配置 (仅图像模型) -->
      <div v-if="currentModel.supportsImage" class="border-b pb-6">
        <h4 class="font-medium mb-4 text-gray-800">图像配置 (imageConfig)</h4>

        <!-- aspectRatio: 宽高比 - 图形化选择 -->
        <div class="mb-5">
          <label class="block text-sm font-medium text-gray-700 mb-3">
            aspectRatio (宽高比)
          </label>
          <div class="grid grid-cols-5 gap-3">
            <button
              v-for="ratio in aspectRatios"
              :key="ratio.value"
              @click="config.aspectRatio = ratio.value; saveConfig()"
              :class="[
                'p-3 border-2 rounded-lg transition-all hover:shadow-md',
                config.aspectRatio === ratio.value
                  ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                  : 'border-gray-200 hover:border-blue-300'
              ]"
              :title="`${ratio.value} - ${ratio.label}`"
            >
              <div class="flex flex-col items-center">
                <!-- 可视化宽高比 -->
                <div
                  class="bg-gradient-to-br from-blue-400 to-blue-600 mb-2 rounded shadow-sm"
                  :style="{ width: `${ratio.width}px`, height: `${ratio.height}px` }"
                ></div>
                <div class="text-xs font-bold text-gray-700">{{ ratio.value }}</div>
                <div class="text-xs text-gray-500 mt-0.5">{{ ratio.label }}</div>
              </div>
            </button>
          </div>
          <p class="text-xs text-gray-500 mt-2">
            10种宽高比可选，适用于不同场景（正方形、横版、竖版、宽屏等）
          </p>
        </div>

        <!-- imageSize: 图像尺寸 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            imageSize (图像分辨率)
          </label>
          <div class="flex space-x-3">
            <button
              v-for="size in imageSizes"
              :key="size.value"
              @click="config.imageSize = size.value; saveConfig()"
              :class="[
                'flex-1 px-4 py-3 border-2 rounded-lg transition-all',
                config.imageSize === size.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700 font-semibold'
                  : 'border-gray-200 hover:border-gray-300 text-gray-700'
              ]"
            >
              <div class="text-center">
                <div class="font-bold">{{ size.value }}</div>
                <div class="text-xs text-gray-500 mt-1">{{ size.resolution }}</div>
              </div>
            </button>
          </div>
          <p class="text-xs text-gray-500 mt-2">
            注意：2K和4K仅 gemini-3-pro-image-preview 支持，其他模型只支持1K
          </p>
        </div>
      </div>

      <!-- 非图像模型提示 -->
      <div v-if="!currentModel.supportsImage" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start space-x-3">
          <Info class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div class="flex-1">
            <h3 class="text-sm font-medium text-blue-900 mb-1">文本生成模型参数</h3>
            <p class="text-sm text-blue-700">
              当前选择的是文本生成模型，以下参数用于控制文本生成的质量和行为
            </p>
          </div>
        </div>
      </div>

      <!-- 基础生成参数 -->
      <div class="border-b pb-6">
        <h4 class="font-medium mb-4 text-gray-800">基础生成参数</h4>
        <div class="space-y-4">

          <!-- candidateCount 已移除 - 大多数Gemini模型不支持此参数 -->
          <!-- 图像批量生成功能通过前端并发请求实现，不依赖API的candidateCount参数 -->

          <!-- temperature -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-gray-700">
                temperature (温度)
              </label>
              <input
                type="number"
                v-model.number="config.temperature"
                @input="saveConfig"
                min="0"
                max="2"
                step="0.1"
                class="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <input
              type="range"
              v-model.number="config.temperature"
              @input="saveConfig"
              min="0"
              max="2"
              step="0.1"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <p class="text-xs text-gray-500">
              控制随机性和创造力，范围0.0-2.0。默认0.9。较高值更有创意，较低值更确定性。
            </p>
          </div>

          <!-- topP -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-gray-700">
                topP (核采样)
              </label>
              <input
                type="number"
                v-model.number="config.topP"
                @input="saveConfig"
                min="0"
                max="1"
                step="0.05"
                class="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <input
              type="range"
              v-model.number="config.topP"
              @input="saveConfig"
              min="0"
              max="1"
              step="0.05"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <p class="text-xs text-gray-500">
              核采样阈值，范围0.0-1.0。默认1.0。例如0.9表示考虑累积概率达90%的词元。建议调整temperature或topP其中一个。
            </p>
          </div>

          <!-- topK -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-gray-700">
                topK (Top-K采样)
              </label>
              <input
                type="number"
                v-model.number="config.topK"
                @input="saveConfig"
                min="1"
                max="40"
                step="1"
                class="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <input
              type="range"
              v-model.number="config.topK"
              @input="saveConfig"
              min="1"
              max="40"
              step="1"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <p class="text-xs text-gray-500">
              从前K个最可能的词元中采样，范围1-40。默认32。限制候选词元数量。
            </p>
          </div>

          <!-- maxOutputTokens -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-gray-700">
                maxOutputTokens (最大输出令牌)
              </label>
              <input
                type="number"
                v-model.number="config.maxOutputTokens"
                @input="saveConfig"
                min="1"
                :max="currentModel.supportsImage ? 32768 : 65536"
                step="1"
                class="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <input
              type="range"
              v-model.number="config.maxOutputTokens"
              @input="saveConfig"
              min="1"
              :max="currentModel.supportsImage ? 32768 : 65536"
              step="100"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <p class="text-xs text-gray-500">
              {{ currentModel.supportsImage
                ? '最大输出令牌数,范围1-32,768。默认2048。控制输出长度（文本描述部分）。'
                : '最大输出令牌数,范围1-65,536。默认2048。控制生成文本的最大长度。'
              }}
            </p>
          </div>

          <!-- stopSequences -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">
              stopSequences (停止序列)
            </label>
            <div class="space-y-2">
              <input
                v-for="(_seq, index) in config.stopSequences"
                :key="index"
                v-model="config.stopSequences[index]"
                @input="saveConfig"
                type="text"
                :placeholder="`停止序列 ${index + 1}`"
                class="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 text-sm"
              />
              <div class="flex space-x-2">
                <button
                  v-if="config.stopSequences.length < 5"
                  @click="config.stopSequences.push(''); saveConfig()"
                  class="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  + 添加停止序列
                </button>
                <button
                  v-if="config.stopSequences.length > 0"
                  @click="config.stopSequences.pop(); saveConfig()"
                  class="px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600"
                >
                  - 删除最后一个
                </button>
              </div>
            </div>
            <p class="text-xs text-gray-500">
              遇到这些字符串时停止生成，最多5个。主要用于文本生成部分。
            </p>
          </div>

        </div>
      </div>

      <!-- 惩罚参数 -->
      <div class="border-b pb-6">
        <h4 class="font-medium mb-4 text-gray-800">惩罚参数</h4>
        <div class="space-y-4">

          <!-- presencePenalty -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-gray-700">
                presencePenalty (存在惩罚)
              </label>
              <input
                type="number"
                v-model.number="config.presencePenalty"
                @input="saveConfig"
                min="-2"
                max="2"
                step="0.1"
                class="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <input
              type="range"
              v-model.number="config.presencePenalty"
              @input="saveConfig"
              min="-2"
              max="2"
              step="0.1"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <p class="text-xs text-gray-500">
              对已出现词元的惩罚，范围-2.0到2.0。默认无。正值鼓励多样性，负值鼓励重复。
            </p>
          </div>

          <!-- frequencyPenalty -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-gray-700">
                frequencyPenalty (频率惩罚)
              </label>
              <input
                type="number"
                v-model.number="config.frequencyPenalty"
                @input="saveConfig"
                min="-2"
                max="2"
                step="0.1"
                class="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <input
              type="range"
              v-model.number="config.frequencyPenalty"
              @input="saveConfig"
              min="-2"
              max="2"
              step="0.1"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <p class="text-xs text-gray-500">
              基于词元出现频率的惩罚，范围-2.0到2.0。默认无。正值降低重复词元概率。
            </p>
          </div>

        </div>
      </div>

      <!-- 响应格式配置 -->
      <div class="border-b pb-6">
        <h4 class="font-medium mb-4 text-gray-800">响应格式配置</h4>
        <div class="space-y-4">

          <!-- responseModalities (输出模态) - 仅图像模型显示 -->
          <div v-if="currentModel.supportsImage" class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">
              responseModalities (输出模态)
            </label>
            <div class="space-y-2">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  :checked="config.responseModalities.includes('TEXT')"
                  @change="toggleModality('TEXT', ($event.target as HTMLInputElement).checked)"
                  class="rounded"
                />
                <span class="text-sm text-gray-700">TEXT (文本) - 返回文本描述</span>
              </label>
              <label class="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  :checked="config.responseModalities.includes('IMAGE')"
                  @change="toggleModality('IMAGE', ($event.target as HTMLInputElement).checked)"
                  class="rounded"
                />
                <span class="text-sm text-gray-700">IMAGE (图像) - 返回生成的图像</span>
              </label>
            </div>
            <p class="text-xs text-gray-500">
              控制输出类型。默认：['TEXT', 'IMAGE']。可以只选IMAGE仅返回图像，或同时选择两者。
            </p>
          </div>

          <!-- responseMimeType - 仅非图像模型显示 -->
          <!-- 图像生成模型会自动使用 application/json，不需要用户配置 -->
          <div v-if="!currentModel.supportsImage" class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">
              responseMimeType (响应MIME类型)
            </label>
            <select
              v-model="config.responseMimeType"
              @change="saveConfig"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            >
              <option value="text/plain">text/plain (纯文本，默认)</option>
              <option value="application/json">application/json (JSON格式)</option>
            </select>
            <p class="text-xs text-gray-500">
              输出MIME类型。可选择纯文本或JSON格式的结构化输出。
            </p>
          </div>

          <!-- responseSchema (JSON Schema编辑器) -->
          <div class="space-y-2">
            <label class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">
                responseSchema (结构化响应Schema)
              </span>
              <button
                v-if="config.responseSchema"
                @click="config.responseSchema = undefined; responseSchemaJson = ''; saveConfig()"
                class="text-xs text-red-600 hover:text-red-700"
              >
                清除Schema
              </button>
            </label>
            <textarea
              v-model="responseSchemaJson"
              @input="updateResponseSchema"
              placeholder='示例: {"type":"OBJECT","properties":{"description":{"type":"STRING"},"imageUrl":{"type":"STRING"}},"required":["imageUrl"]}'
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 font-mono text-xs"
            ></textarea>
            <p class="text-xs text-gray-500">
              可选的JSON Schema定义，用于结构化响应。需与responseMimeType="application/json"配合使用。
              支持类型: STRING, NUMBER, BOOLEAN, OBJECT, ARRAY, INTEGER, NULL
            </p>
            <div v-if="responseSchemaError" class="text-xs text-red-600">
              警告 JSON格式错误: {{ responseSchemaError }}
            </div>
          </div>

        </div>
      </div>

      <!-- 工具配置 (tools) -->
      <div class="border-b pb-6">
        <h4 class="font-medium mb-4 text-gray-800">工具配置 (tools)</h4>

        <!-- Google Search -->
        <div class="space-y-2">
          <label class="flex items-center space-x-2 cursor-pointer">
            <input
              v-model="config.useGoogleSearch"
              @change="saveConfig"
              type="checkbox"
              class="rounded"
            />
            <span class="text-sm font-medium text-gray-700">
              启用搜索接地 (Search Grounding)
            </span>
          </label>
          <p v-if="currentModel.supportsImage" class="text-xs text-gray-500">
            使用Google搜索根据实时信息生成图像（例如：天气预报、股市图表、近期活动）。
            <strong>仅 gemini-3-pro-image-preview 支持</strong>。启用后会在API请求中添加 tools: [{"google_search": {}}]
          </p>
          <p v-else class="text-xs text-gray-500">
            使用Google搜索获取实时信息来增强文本生成（例如：最新新闻、实时数据等）。
            启用后会在API请求中添加 tools: [{"google_search": {}}]
          </p>
          <div v-if="config.useGoogleSearch" class="mt-2 p-3 bg-blue-50 border border-blue-200 rounded text-xs text-blue-800">
            <template v-if="currentModel.supportsImage">
              提示：启用后可以使用类似"Visualize the current weather forecast for San Francisco"这样的提示词
            </template>
            <template v-else>
              提示：启用后可以获取最新的信息,如"今天的新闻"、"最新的技术趋势"等
            </template>
          </div>
        </div>

        <!-- 图像模型限制说明 -->
        <div v-if="currentModel.supportsImage" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p class="text-xs text-yellow-800 font-medium mb-1">注意：图像生成模型限制</p>
          <ul class="text-xs text-yellow-700 list-disc list-inside space-y-0.5">
            <li><strong>不支持</strong>代码执行 (Code Execution)</li>
            <li><strong>不支持</strong>函数调用 (Function Calling)</li>
            <li><strong>不支持</strong>文件搜索 (File Search)</li>
            <li><strong>不支持</strong>Google地图接地 (Google Maps Grounding)</li>
            <li>搜索接地 (Search Grounding) 仅 gemini-3-pro-image-preview 支持</li>
          </ul>
        </div>

        <!-- 代码执行 (仅文本模型) -->
        <div v-if="!currentModel.supportsImage" class="mt-4 space-y-2">
          <label class="flex items-center space-x-2 cursor-pointer">
            <input
              v-model="config.useCodeExecution"
              @change="saveConfig"
              type="checkbox"
              class="rounded"
            />
            <span class="text-sm font-medium text-gray-700">
              启用代码执行 (Code Execution)
            </span>
          </label>
          <p class="text-xs text-gray-500">
            允许模型执行Python代码来完成任务（例如：数据分析、数学计算等）。
            <strong>仅支持文本生成模型</strong>。启用后会在API请求中添加 tools: [{"code_execution": {}}]
          </p>
        </div>
      </div>


      <!-- 高级参数 -->
      <div class="border-b pb-6">
        <h4 class="font-medium mb-4 text-gray-800">高级参数</h4>
        <div class="space-y-4">

          <!-- seed -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">
              seed (随机种子)
            </label>
            <input
              v-model.number="config.seed"
              @input="saveConfig"
              type="number"
              placeholder="留空则随机生成"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500">
              设置随机种子以获得可重复的结果。留空则每次生成不同图像。
            </p>
          </div>

          <!-- mediaResolution -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">
              mediaResolution (输入媒体分辨率)
            </label>
            <select
              v-model="config.mediaResolution"
              @change="saveConfig"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            >
              <option value="MEDIA_RESOLUTION_UNSPECIFIED">未指定 (MEDIA_RESOLUTION_UNSPECIFIED，默认)</option>
              <option value="MEDIA_RESOLUTION_LOW">低 - 64令牌 (MEDIA_RESOLUTION_LOW)</option>
              <option value="MEDIA_RESOLUTION_MEDIUM">中 - 256令牌 (MEDIA_RESOLUTION_MEDIUM)</option>
              <option value="MEDIA_RESOLUTION_HIGH">高 - 256令牌+重构 (MEDIA_RESOLUTION_HIGH)</option>
            </select>
            <p class="text-xs text-gray-500">
              控制输入图像的处理分辨率。较高分辨率消耗更多令牌但保留更多细节。
            </p>
          </div>

          <!-- enableEnhancedCivicAnswers -->
          <div class="space-y-2">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input
                v-model="config.enableEnhancedCivicAnswers"
                @change="saveConfig"
                type="checkbox"
                class="rounded"
              />
              <span class="text-sm font-medium text-gray-700">
                enableEnhancedCivicAnswers (增强公民诚信回答)
              </span>
            </label>
            <p class="text-xs text-gray-500">
              启用增强公民诚信回答（模型特定功能）。默认false。
            </p>
          </div>

          <!-- responseLogprobs -->
          <div class="space-y-2">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input
                v-model="config.responseLogprobs"
                @change="saveConfig"
                type="checkbox"
                class="rounded"
              />
              <span class="text-sm font-medium text-gray-700">
                responseLogprobs (包含日志概率)
              </span>
            </label>
            <p class="text-xs text-gray-500">
              是否在响应中包含词元的日志概率信息（用于调试和分析）。默认false。
            </p>
          </div>

          <!-- logprobs (仅在启用responseLogprobs时显示) -->
          <div v-if="config.responseLogprobs" class="space-y-2 ml-6">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-gray-700">
                logprobs (日志概率数量)
              </label>
              <input
                type="number"
                v-model.number="config.logprobs"
                @input="saveConfig"
                min="0"
                max="20"
                step="1"
                class="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <p class="text-xs text-gray-500">
              返回前N个词元的日志概率，范围0-20。需要先启用responseLogprobs。
            </p>
          </div>

        </div>
      </div>

      <!-- 安全设置 -->
      <div class="border-b pb-6">
        <h4 class="font-medium mb-4 text-gray-800">安全设置 (safetySettings)</h4>
        <p class="text-xs text-gray-500 mb-3">
          配置内容过滤阈值，用于检测有害内容（包括图像安全）。支持动态添加/删除安全类别。
        </p>
        <div class="space-y-3">
          <div
            v-for="(setting, index) in config.safetySettings"
            :key="index"
            class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
          >
            <!-- 类别选择（下拉） -->
            <div class="flex-1">
              <select
                v-model="setting.category"
                @change="saveConfig"
                class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="HARM_CATEGORY_UNSPECIFIED">未指定 (UNSPECIFIED)</option>
                <option value="HARM_CATEGORY_DEROGATORY">贬低 (DEROGATORY)</option>
                <option value="HARM_CATEGORY_TOXICITY">毒性 (TOXICITY)</option>
                <option value="HARM_CATEGORY_VIOLENCE">暴力 (VIOLENCE)</option>
                <option value="HARM_CATEGORY_SEXUAL">性内容 (SEXUAL)</option>
                <option value="HARM_CATEGORY_MEDICAL">医疗 (MEDICAL)</option>
                <option value="HARM_CATEGORY_DANGEROUS">危险 (DANGEROUS)</option>
                <option value="HARM_CATEGORY_HARASSMENT">骚扰 (HARASSMENT)</option>
                <option value="HARM_CATEGORY_HATE_SPEECH">仇恨言论 (HATE_SPEECH)</option>
                <option value="HARM_CATEGORY_SEXUALLY_EXPLICIT">露骨性内容 (SEXUALLY_EXPLICIT)</option>
                <option value="HARM_CATEGORY_DANGEROUS_CONTENT">危险内容 (DANGEROUS_CONTENT)</option>
                <option value="HARM_CATEGORY_CIVIC_INTEGRITY">公民诚信 (CIVIC_INTEGRITY)</option>
              </select>
            </div>

            <!-- 阈值选择 -->
            <select
              v-model="setting.threshold"
              @change="saveConfig"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="HARM_BLOCK_THRESHOLD_UNSPECIFIED">未指定 (UNSPECIFIED)</option>
              <option value="BLOCK_NONE">不阻止 (BLOCK_NONE)</option>
              <option value="BLOCK_ONLY_HIGH">仅高风险 (BLOCK_ONLY_HIGH)</option>
              <option value="BLOCK_MEDIUM_AND_ABOVE">中等及以上 (BLOCK_MEDIUM_AND_ABOVE)</option>
              <option value="BLOCK_LOW_AND_ABOVE">低及以上 (BLOCK_LOW_AND_ABOVE)</option>
              <option value="OFF">关闭 (OFF)</option>
            </select>

            <!-- 删除按钮 -->
            <button
              @click="removeSafetySetting(index)"
              class="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
              title="删除此安全设置"
            >
              删除
            </button>
          </div>

          <!-- 添加新设置按钮 -->
          <button
            @click="addSafetySetting"
            class="w-full px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-600 hover:border-blue-400 hover:text-blue-600 transition-colors"
          >
            + 添加新的安全类别
          </button>
        </div>
      </div>

      <!-- 参数说明（可折叠） -->
      <div class="border border-gray-200 rounded-lg overflow-hidden">
        <button
          @click="showHelp = !showHelp"
          class="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between text-sm font-medium text-gray-700"
        >
          <span>参数使用说明</span>
          <span class="transform transition-transform" :class="{ 'rotate-180': showHelp }">▼</span>
        </button>
        <div v-show="showHelp" class="p-4 bg-white border-t border-gray-200">
          <!-- 图像生成模型说明 -->
          <div v-if="currentModel.supportsImage" class="text-xs text-gray-600 space-y-3">
            <div class="pb-2 border-b border-gray-100">
              <p class="font-semibold text-gray-800 mb-2">Gemini 图像生成模型参数</p>
              <p class="leading-relaxed">
                本页面参数基于 Gemini API 官方文档（2025年最新版本）。
                所有参数在调用图像生成模型时自动应用。
              </p>
            </div>

            <div>
              <p class="font-semibold text-gray-800 mb-1">支持的图像生成模型</p>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li><strong>gemini-3-pro-image-preview</strong>: Gemini 3 Pro 图像生成预览版，支持搜索接地和思考功能，输出限制 32,768 tokens</li>
                <li><strong>gemini-2.5-flash-image</strong>: Gemini 2.5 Flash 图像生成，快速生成，支持缓存，输出限制 32,768 tokens</li>
                <li><strong>gemini-2.0-flash-preview-image-generation</strong>: Gemini 2.0 Flash 图像生成预览版，输出限制 8,192 tokens</li>
              </ul>
            </div>

            <div>
              <p class="font-semibold text-gray-800 mb-1">参数调优建议</p>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li><strong>temperature vs topP</strong>: 建议只调整其中一个，不要同时调整</li>
                <li><strong>创意生成</strong>: temperature 1.0-1.5，topP 0.9-1.0</li>
                <li><strong>精确控制</strong>: temperature 0.5-0.8，topP 0.7-0.9</li>
                <li><strong>多样性</strong>: 增加presencePenalty (0.5-1.5)</li>
                <li><strong>一致性</strong>: 使用固定的seed值</li>
              </ul>
            </div>

            <div>
              <p class="font-semibold text-gray-800 mb-1">工具支持</p>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li><strong>gemini-3-pro-image-preview</strong>: 支持搜索接地 (Search Grounding)、思考 (Thinking)、结构化输出</li>
                <li><strong>gemini-2.5-flash-image</strong>: 支持结构化输出、缓存，不支持搜索接地和思考</li>
                <li><strong>所有图像模型</strong>: 均不支持代码执行、函数调用、文件搜索</li>
              </ul>
            </div>

            <div class="pt-2 border-t border-gray-100">
              <p class="flex items-start">
                <span class="mr-2">参考来源</span>
                <span class="leading-relaxed">
                  <strong>Google AI for Developers 官方文档</strong> - Gemini API 图像生成模型（2025年版本）
                </span>
              </p>
            </div>
          </div>

          <!-- 文本生成模型说明 -->
          <div v-else class="text-xs text-gray-600 space-y-3">
            <div class="pb-2 border-b border-gray-100">
              <p class="font-semibold text-gray-800 mb-2">Gemini 文本生成模型参数</p>
              <p class="leading-relaxed">
                本页面参数适用于 Gemini API 的文本生成模型（2025年最新版本）。
                这些参数控制模型的输出质量、创造性和行为。
              </p>
            </div>

            <div>
              <p class="font-semibold text-gray-800 mb-1">常用文本模型</p>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li><strong>gemini-3-pro-preview</strong>: Gemini 3 Pro 预览版，最智能的多模态模型，输出限制 65,536 tokens</li>
                <li><strong>gemini-3-flash-preview</strong>: Gemini 3 Flash 预览版，速度优化的智能模型，输出限制 65,536 tokens</li>
                <li><strong>gemini-2.5-flash</strong>: Gemini 2.5 Flash，性价比最佳，输出限制 65,536 tokens</li>
                <li><strong>gemini-2.5-flash-lite</strong>: Gemini 2.5 Flash-Lite，超快速模型，输出限制 65,536 tokens</li>
                <li><strong>gemini-2.5-pro</strong>: Gemini 2.5 Pro，高级思考模型，输出限制 65,536 tokens</li>
                <li><strong>gemini-2.0-flash</strong>: Gemini 2.0 Flash，第二代工作模型，输出限制 8,192 tokens</li>
              </ul>
            </div>

            <div>
              <p class="font-semibold text-gray-800 mb-1">参数调优建议</p>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li><strong>temperature vs topP</strong>: 建议只调整其中一个，不要同时调整</li>
                <li><strong>创意写作</strong>: temperature 0.9-1.2，topP 0.9-1.0</li>
                <li><strong>精确回答</strong>: temperature 0.3-0.7，topP 0.7-0.9</li>
                <li><strong>代码生成</strong>: temperature 0.2-0.5，presencePenalty 0</li>
                <li><strong>减少重复</strong>: presencePenalty 0.5-1.0，frequencyPenalty 0.5-1.0</li>
                <li><strong>可复现结果</strong>: 使用固定的seed值</li>
              </ul>
            </div>

            <div>
              <p class="font-semibold text-gray-800 mb-1">工具支持（根据模型）</p>
              <ul class="list-disc list-inside space-y-1 ml-2">
                <li><strong>代码执行 (Code Execution)</strong>: Gemini 3.x, 2.5 Pro/Flash/Flash-Lite, 2.0 Flash 支持</li>
                <li><strong>搜索接地 (Search Grounding)</strong>: 大多数文本模型支持</li>
                <li><strong>函数调用 (Function Calling)</strong>: 大多数文本模型支持</li>
                <li><strong>文件搜索 (File Search)</strong>: Gemini 3.x, 2.5 系列支持</li>
                <li><strong>结构化输出 (Structured Outputs)</strong>: 所有模型支持</li>
                <li><strong>思考模式 (Thinking)</strong>: Gemini 3.x, 2.5 系列支持</li>
              </ul>
            </div>

            <div class="pt-2 border-t border-gray-100">
              <p class="flex items-start">
                <span class="mr-2">参考来源</span>
                <span class="leading-relaxed">
                  <strong>Google AI for Developers 官方文档</strong> - Gemini API 文本生成模型（2025年版本）
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Info } from 'lucide-vue-next'
import { useDrawingStore } from '@/stores/drawingStore'
import { useNotificationStore } from '@/stores/notificationStore'

const drawingStore = useDrawingStore()
const notificationStore = useNotificationStore()
const config = computed(() => drawingStore.generationConfig)
const currentProvider = computed(() => drawingStore.getCurrentProvider())
const currentModel = computed(() => drawingStore.getCurrentModel())
const showHelp = ref(false)

// responseSchema处理
const responseSchemaJson = ref('')
const responseSchemaError = ref('')

// 初始化responseSchemaJson
if (config.value.responseSchema) {
  try {
    responseSchemaJson.value = JSON.stringify(config.value.responseSchema, null, 2)
  } catch (e) {
    responseSchemaJson.value = ''
  }
}

// 更新responseSchema
const updateResponseSchema = () => {
  if (!responseSchemaJson.value.trim()) {
    config.value.responseSchema = undefined
    responseSchemaError.value = ''
    saveConfig()
    return
  }

  try {
    const parsed = JSON.parse(responseSchemaJson.value)
    config.value.responseSchema = parsed
    responseSchemaError.value = ''
    saveConfig()
  } catch (e) {
    responseSchemaError.value = e instanceof Error ? e.message : '无效的JSON格式'
  }
}

// 宽高比选项（10种，带可视化）
const aspectRatios = [
  { value: '1:1' as const, label: '正方形', width: 50, height: 50 },
  { value: '2:3' as const, label: '竖版', width: 40, height: 60 },
  { value: '3:2' as const, label: '横版', width: 60, height: 40 },
  { value: '3:4' as const, label: '竖版', width: 40, height: 53 },
  { value: '4:3' as const, label: '横版', width: 53, height: 40 },
  { value: '4:5' as const, label: '竖版', width: 40, height: 50 },
  { value: '5:4' as const, label: '横版', width: 50, height: 40 },
  { value: '9:16' as const, label: '手机竖屏', width: 36, height: 64 },
  { value: '16:9' as const, label: '宽屏', width: 64, height: 36 },
  { value: '21:9' as const, label: '超宽', width: 70, height: 30 }
]

// 图像尺寸选项
const imageSizes = [
  { value: '1K' as const, resolution: '1024×1024' },
  { value: '2K' as const, resolution: '2048×2048' },
  { value: '4K' as const, resolution: '4096×4096' }
]

const saveConfig = () => {
  drawingStore.saveSettings()
}

// 切换输出模态
const toggleModality = (modality: 'TEXT' | 'IMAGE', checked: boolean) => {
  if (checked) {
    if (!config.value.responseModalities.includes(modality)) {
      config.value.responseModalities.push(modality)
    }
  } else {
    const index = config.value.responseModalities.indexOf(modality)
    if (index > -1) {
      config.value.responseModalities.splice(index, 1)
    }
  }
  saveConfig()
}

// 添加新的安全设置
const addSafetySetting = () => {
  config.value.safetySettings.push({
    category: 'HARM_CATEGORY_UNSPECIFIED',
    threshold: 'BLOCK_MEDIUM_AND_ABOVE'
  })
  saveConfig()
}

// 删除安全设置
const removeSafetySetting = (index: number) => {
  config.value.safetySettings.splice(index, 1)
  saveConfig()
}

const handleReset = () => {
  // 重置为默认值（基于官方文档）
  drawingStore.generationConfig = {
    // imageConfig
    aspectRatio: '1:1',
    imageSize: '1K',

    // 基础生成参数
    temperature: 0.9,
    topP: 1.0,
    topK: 32,
    maxOutputTokens: 2048,
    // candidateCount 已移除 - 大多数Gemini模型不支持
    stopSequences: [],

    // 惩罚参数
    presencePenalty: 0,
    frequencyPenalty: 0,

    // 响应格式
    responseModalities: ['TEXT', 'IMAGE'],  // 默认同时返回文本和图像
    responseMimeType: 'text/plain',
    responseSchema: undefined,

    // 工具配置
    useGoogleSearch: false,  // 默认不启用Google搜索
    useCodeExecution: false,  // 图像模型不支持
    functionDeclarations: [],  // 图像模型不支持
    functionCallingMode: 'FUNCTION_CALLING_CONFIG_MODE_UNSPECIFIED',

    // 高级参数
    seed: undefined,
    mediaResolution: 'MEDIA_RESOLUTION_UNSPECIFIED',
    enableEnhancedCivicAnswers: false,
    responseLogprobs: false,
    logprobs: 0,

    // 安全设置（默认4个常用类别）
    safetySettings: [
      { category: 'HARM_CATEGORY_HARASSMENT', threshold: 'BLOCK_MEDIUM_AND_ABOVE' },
      { category: 'HARM_CATEGORY_HATE_SPEECH', threshold: 'BLOCK_MEDIUM_AND_ABOVE' },
      { category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold: 'BLOCK_MEDIUM_AND_ABOVE' },
      { category: 'HARM_CATEGORY_DANGEROUS_CONTENT', threshold: 'BLOCK_MEDIUM_AND_ABOVE' }
    ]
  }

  // 清空responseSchemaJson
  responseSchemaJson.value = ''
  responseSchemaError.value = ''

  drawingStore.saveSettings()

  // 显示成功通知
  notificationStore.success('参数已重置为默认值', 2000)
}
</script>
