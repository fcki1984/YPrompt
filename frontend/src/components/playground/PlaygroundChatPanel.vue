<template>
  <div 
    class="bg-white rounded-lg shadow-sm flex flex-col h-full overflow-hidden border border-gray-100 relative"
    @dragover.prevent="handleGlobalDragOver"
    @dragenter.prevent="handleGlobalDragEnter"
    @dragleave.prevent="handleGlobalDragLeave"
    @drop.prevent="handleGlobalDrop"
  >
    <!-- Header -->
    <div class="p-4 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
      <div class="h-6">AI对话</div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600">流式:</span>
          <button
            @click="$emit('toggle-stream')"
            :class="[
              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none',
              isStreamMode ? 'bg-blue-500' : 'bg-gray-300'
            ]"
            :title="isStreamMode ? '关闭流式输出' : '开启流式输出'"
          >
            <span
              :class="[
                'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                isStreamMode ? 'translate-x-6' : 'translate-x-1'
              ]"
            />
          </button>
        </div>

        <button
          class="p-2 rounded-lg border transition-colors"
          :class="hasSystemPrompt ? 'border-blue-200 bg-blue-50 text-blue-600' : 'border-gray-200 text-gray-500 hover:bg-gray-50'"
          @click="$emit('open-system-prompt')"
          title="设置系统提示词"
        >
          <FileText class="w-4 h-4" />
        </button>

        <button
          @click="$emit('clear')"
          class="p-2 rounded-lg border border-gray-200 text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors"
          title="重新开始"
        >
          <RefreshCw class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Messages -->
    <div ref="scrollRef" class="flex-1 overflow-y-auto bg-gray-50 px-4 py-6 space-y-5">
      <div
        v-if="messages.length === 0"
        class="h-full flex flex-col items-center justify-center text-gray-400 p-6 text-center"
      >
        <div class="w-16 h-16 rounded-2xl bg-white border border-gray-200 flex items-center justify-center mb-4">
          <Sparkles class="w-8 h-8 text-gray-300" />
        </div>
        <p class="text-base font-medium text-gray-700 mb-2">欢迎使用提示词演练</p>
        <p class="text-sm text-gray-500 max-w-xs">
          对话生成结果会在右侧实时渲染
        </p>
      </div>

      <div
        v-for="msg in messages"
        :key="msg.id"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        class="flex group"
      >
        <div 
          v-if="!(msg.role === 'model' && msg.isStreaming && !hasMessageContent(msg))"
          class="flex flex-col w-full"
          :class="msg.isEditing ? 'max-w-full sm:max-w-2xl' : 'max-w-xs lg:max-w-md'"
        >
          <div
            :class="[
              msg.isEditing 
                ? 'bg-transparent border-0 shadow-none p-0' 
                : msg.role === 'user' 
                  ? 'bg-blue-500 text-white px-4 py-3 rounded-lg' 
                  : 'bg-gray-100 text-gray-800 px-4 py-3 rounded-lg',
              !msg.isEditing && (msg.role === 'user' ? 'ml-auto' : 'mr-auto'),
              'transition-all duration-300 relative'
            ]"
          >
            <div v-if="msg.isEditing" class="relative">
              <div class="relative border border-blue-300 rounded-2xl overflow-hidden bg-white">
                <div class="relative">
                  <textarea
                    :value="msg.editingText"
                    @input="$emit('edit-input', { messageId: msg.id, value: ($event.target as HTMLTextAreaElement).value })"
                    class="w-full p-4 border-0 resize-none focus:outline-none text-gray-800 bg-white min-h-[80px] max-h-[200px] overflow-y-auto text-base"
                    @keydown="$emit('edit-keydown', { messageId: msg.id, event: $event })"
                    placeholder="编辑消息内容..."
                  ></textarea>
                </div>
              </div>
            </div>
            
            <div v-else>
              <div
                v-if="msg.role === 'model'"
                v-html="renderMarkdown(msg.displayText || msg.text)"
                class="prose prose-sm max-w-none prose-headings:text-gray-800 prose-p:text-gray-800 prose-li:text-gray-800 prose-strong:text-gray-800"
              ></div>
              <div 
                v-else 
                v-html="renderUserMessage(msg.text)"
                class="text-white [&_h1]:text-xl [&_h1]:font-bold [&_h1]:text-white [&_h1]:mb-2 [&_h2]:text-lg [&_h2]:font-bold [&_h2]:text-white [&_h2]:mb-2 [&_h3]:text-base [&_h3]:font-bold [&_h3]:text-white [&_h3]:mb-1 [&_h4]:text-sm [&_h4]:font-bold [&_h4]:text-white [&_h5]:text-sm [&_h5]:font-bold [&_h5]:text-white [&_h6]:text-sm [&_h6]:font-bold [&_h6]:text-white [&_p]:text-white [&_p]:mb-2 [&_strong]:font-bold [&_strong]:text-white [&_b]:font-bold [&_b]:text-white [&_em]:italic [&_em]:text-white [&_i]:italic [&_i]:text-white [&_ul]:list-disc [&_ul]:list-inside [&_ul]:text-white [&_ul]:mb-2 [&_ol]:list-decimal [&_ol]:list-inside [&_ol]:text-white [&_ol]:mb-2 [&_li]:text-white [&_li]:mb-1 [&_code]:bg-blue-600 [&_code]:text-blue-100 [&_code]:px-1 [&_code]:rounded [&_code]:font-mono [&_pre]:bg-blue-600 [&_pre]:text-blue-100 [&_pre]:p-2 [&_pre]:rounded [&_pre]:overflow-x-auto [&_a]:text-blue-200 [&_a]:underline [&_blockquote]:border-l-2 [&_blockquote]:border-blue-300 [&_blockquote]:pl-2 [&_blockquote]:text-blue-100"
              ></div>
            </div>
          </div>
          
          <div 
            v-if="msg.attachments && msg.attachments.length > 0 && !msg.isEditing"
            class="mt-2"
            :class="msg.role === 'user' ? 'ml-auto max-w-xs lg:max-w-md' : 'mr-auto max-w-xs lg:max-w-md'"
          >
            <div class="text-xs text-gray-500 mb-1">附件 ({{ msg.attachments.length }})</div>
            <div class="flex gap-2 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 pb-1">
              <div
                v-for="attachment in msg.attachments"
                :key="attachment.id"
                class="flex-shrink-0 flex items-center gap-2 px-2 py-1.5 rounded-md text-xs border min-w-0"
                :class="msg.role === 'user' ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-100'"
              >
                <div class="flex items-center gap-2 min-w-0">
                  <div class="flex-shrink-0">
                    <svg v-if="attachment.type === 'image'" class="w-3 h-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <svg v-else-if="attachment.type === 'document'" class="w-3 h-3 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <svg v-else-if="attachment.type === 'audio'" class="w-3 h-3 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                    </svg>
                    <svg v-else-if="attachment.type === 'video'" class="w-3 h-3 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <svg v-else class="w-3 h-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                  </div>
                  <div class="min-w-0 flex-1">
                    <div 
                      class="truncate max-w-20 font-medium text-xs"
                      :class="msg.role === 'user' ? 'text-blue-700' : 'text-gray-700'"
                      :title="attachment.name"
                    >
                      {{ attachment.name }}
                    </div>
                    <div 
                      class="text-xs"
                      :class="msg.role === 'user' ? 'text-blue-500' : 'text-gray-500'"
                    >
                      {{ (attachment.size / 1024).toFixed(1) }}KB
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div 
            v-if="!msg.isProgress"
            class="flex space-x-1 mt-2 transition-opacity duration-200"
            :class="[
              msg.isEditing ? 'opacity-100 justify-end' : 'opacity-0 group-hover:opacity-100 ' + (msg.role === 'user' ? 'justify-end' : 'justify-start')
            ]"
          >
            <template v-if="msg.isEditing">
              <button
                @click="msg.role === 'user' ? $emit('resend', msg.id) : $emit('save-edit', msg.id)"
                class="p-1.5 text-gray-500 hover:text-blue-600 transition-colors rounded-lg hover:bg-gray-100"
                :title="msg.role === 'user' ? '保存并重新发送' : '保存编辑'"
                :disabled="isStreaming"
              >
                <Send class="w-3.5 h-3.5" />
              </button>
              
              <button
                @click="$emit('cancel-edit', msg.id)"
                class="p-1.5 text-gray-500 hover:text-red-600 transition-colors rounded-lg hover:bg-gray-100"
                title="取消编辑"
              >
                <X class="w-3.5 h-3.5" />
              </button>
            </template>
            
            <template v-else>
              <template v-if="!msg.isStreaming">
                <button
                  v-if="msg.role === 'model'"
                  @click="$emit('regenerate-message', msg.id)"
                  class="p-1.5 text-gray-500 hover:text-blue-600 transition-colors rounded-lg hover:bg-gray-100"
                  title="重新生成回复"
                  :disabled="isStreaming"
                >
                  <RefreshCw class="w-3.5 h-3.5" />
                </button>
                
                <button
                  v-if="msg.role === 'user'"
                  @click="$emit('resend-user', msg.id)"
                  class="p-1.5 text-gray-500 hover:text-blue-600 transition-colors rounded-lg hover:bg-gray-100"
                  title="重新发送消息"
                  :disabled="isStreaming"
                >
                  <Send class="w-3.5 h-3.5" />
                </button>
                
                <button
                  @click="$emit('start-edit', msg.id)"
                  class="p-1.5 text-gray-500 hover:text-green-600 transition-colors rounded-lg hover:bg-gray-100"
                  title="编辑消息"
                >
                  <Edit2 class="w-3.5 h-3.5" />
                </button>
                
                <button
                  @click="$emit('delete-message', msg.id)"
                  class="p-1.5 text-gray-500 hover:text-red-600 transition-colors rounded-lg hover:bg-gray-100"
                  title="删除消息"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
                
                <button
                  @click="$emit('copy-message', msg.id)"
                  class="p-1.5 text-gray-500 hover:text-blue-600 transition-colors rounded-lg hover:bg-gray-100"
                  title="复制消息内容"
                >
                  <Copy class="w-3.5 h-3.5" />
                </button>
              </template>
            </template>
          </div>
        </div>

        <div
          v-else
          class="flex flex-col w-full max-w-xs lg:max-w-md"
        >
          <div class="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-auto">
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="p-3 border-t border-gray-200 bg-white flex-shrink-0">
      <div class="max-w-4xl mx-auto relative">
        <input
          ref="fileInputRef"
          type="file"
          multiple
          accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.md,.csv,.json,.xml,.html,.css,.js,.ts,.py,.java,.c,.cpp,.yaml,.yml"
          class="hidden"
          @change="handleFileSelect"
        />
        <div v-if="currentAttachments.length > 0" class="mb-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">已选择 {{ currentAttachments.length }} 个附件</span>
            <button
              @click="clearAttachments"
              class="text-xs text-red-500 hover:text-red-600"
            >
              清空全部
            </button>
          </div>
          <div class="flex gap-2 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
            <div
              v-for="attachment in currentAttachments"
              :key="attachment.id"
              class="flex-shrink-0 flex items-center gap-2 bg-white px-3 py-2 rounded-md border border-gray-200 min-w-0"
            >
              <div class="flex items-center gap-2 min-w-0 flex-1">
                <div class="flex-shrink-0">
                  <svg v-if="attachment.type === 'image'" class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <svg v-else-if="attachment.type === 'document'" class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <svg v-else-if="attachment.type === 'audio'" class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                  <svg v-else-if="attachment.type === 'video'" class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <svg v-else class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-xs font-medium text-gray-700 truncate max-w-24" :title="attachment.name">
                    {{ attachment.name }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ (attachment.size / 1024).toFixed(1) }}KB
                  </div>
                </div>
              </div>
              <button
                @click="removeAttachment(attachment.id)"
                class="flex-shrink-0 w-4 h-4 text-gray-400 hover:text-red-500 transition-colors"
                title="移除附件"
              >
                <X class="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
        <div 
          class="relative border border-gray-300 rounded-2xl focus-within:outline-none focus-within:border-gray-300 overflow-hidden" 
          style="height: 120px;"
        >
          <div class="absolute top-0 left-0 right-0" style="bottom: 48px;">
            <textarea
              ref="textareaRef"
              v-model="inputVal"
              rows="1"
              class="w-full h-full px-3 pt-3 pb-1 border-0 outline-none resize-none text-base overflow-y-auto bg-transparent"
              :placeholder="placeholderText"
              @keydown="handleKeydown"
            ></textarea>
          </div>
          <div class="absolute bottom-0 left-0 right-0 h-12 flex items-center justify-between px-3 bg-transparent pointer-events-none">
            <button
              @click="triggerFileSelect"
              class="w-8 h-8 rounded-full text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors flex items-center justify-center pointer-events-auto"
              title="支持拖拽上传图片、文档、音频等格式，单个文件最大25MB"
            >
              <div class="relative">
                <Paperclip class="w-4 h-4" />
                <span 
                  v-if="currentAttachments.length > 0" 
                  class="absolute -top-1 -right-1 bg-blue-500 text-white text-xs rounded-full w-3 h-3 flex items-center justify-center"
                  style="font-size: 9px;"
                >
                  {{ currentAttachments.length }}
                </span>
              </div>
            </button>
            <button
              @click="sendMessage"
              :disabled="!inputVal.trim() || isStreaming"
              class="w-8 h-8 rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center pointer-events-auto"
            >
              <ArrowUp class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="isGlobalDragging"
      class="absolute inset-0 bg-blue-50 bg-opacity-90 flex items-center justify-center z-40 border-2 border-dashed border-blue-400 rounded-lg"
    >
      <div class="text-center">
        <Upload class="w-12 h-12 mx-auto mb-4 text-blue-500" />
        <div class="text-lg font-medium text-blue-700 mb-2">
          释放文件以上传
        </div>
        <div class="text-sm text-blue-600">
          支持图片、文档、音频等格式
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUpdated } from 'vue'
import { Sparkles, RefreshCw, ArrowUp, FileText, Edit2, Trash2, Copy, Send, X, Paperclip, Upload } from 'lucide-vue-next'
import { marked } from 'marked'
import { useChatAttachments } from '@/components/chat/composables/useChatAttachments'
import type { MessageAttachment } from '@/stores/promptStore'

interface PlaygroundMessage {
  id: string
  role: 'user' | 'model'
  text: string
  displayText?: string
  isStreaming?: boolean
  isProgress?: boolean
  attachments?: MessageAttachment[]
  isEditing?: boolean
  editingText?: string
}

const props = defineProps<{
  messages: PlaygroundMessage[]
  isStreaming: boolean
  isStreamMode: boolean
  hasSystemPrompt: boolean
  currentModelName: string
}>()

const emit = defineEmits<{
  'send': [payload: { text: string; attachments: MessageAttachment[] }]
  'clear': []
  'toggle-stream': []
  'open-system-prompt': []
  'start-edit': [messageId: string]
  'save-edit': [messageId: string]
  'cancel-edit': [messageId: string]
  'delete-message': [messageId: string]
  'copy-message': [messageId: string]
  'regenerate-message': [messageId: string]
  'resend-user': [messageId: string]
  'resend': [messageId: string]
  'edit-input': [payload: { messageId: string; value: string }]
  'edit-keydown': [payload: { messageId: string; event: KeyboardEvent }]
}>()

const inputVal = ref('')
const scrollRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const placeholderText = computed(() => 'Shift+Enter 换行')

const messages = computed(() => props.messages)

const {
  currentAttachments,
  isGlobalDragging,
  fileInputRef,
  handleFileSelect,
  removeAttachment,
  clearAttachments,
  handleGlobalDragEnter,
  handleGlobalDragOver,
  handleGlobalDragLeave,
  handleGlobalDrop
} = useChatAttachments()

const scrollToBottom = () => {
  if (!scrollRef.value) return
  const el = scrollRef.value
  const distance = el.scrollHeight - el.scrollTop - el.clientHeight
  if (distance < 300) {
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }
}

const highlightCode = () => {
  if (!scrollRef.value || props.isStreaming) return
  const blocks = scrollRef.value.querySelectorAll('pre code')
  blocks.forEach((block) => {
    const codeEl = block as HTMLElement & { dataset: DOMStringMap }
    if (!(window as any).hljs || codeEl.dataset.highlighted) return
    ;(window as any).hljs.highlightElement(codeEl)
    codeEl.dataset.highlighted = 'yes'
  })
}

const syncLucideIcons = () => {
  if (typeof window !== 'undefined' && (window as any).lucide?.createIcons) {
    (window as any).lucide.createIcons()
  }
}

watch(
  () => props.messages,
  () => {
    nextTick(() => {
      scrollToBottom()
      highlightCode()
      syncLucideIcons()
    })
  },
  { deep: true }
)

watch(
  () => props.isStreaming,
  (val) => {
    if (!val) {
      nextTick(() => {
        highlightCode()
        syncLucideIcons()
      })
    }
  }
)

onMounted(() => {
  syncLucideIcons()
  nextTick(() => {
    textareaRef.value?.focus()
  })
})

onUpdated(syncLucideIcons)

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const sendMessage = () => {
  if (!inputVal.value.trim() || props.isStreaming) return
  const attachmentsPayload = currentAttachments.value.map(att => ({ ...att }))
  emit('send', { text: inputVal.value, attachments: attachmentsPayload })
  inputVal.value = ''
  clearAttachments()
  nextTick(() => {
    textareaRef.value?.focus()
  })
}

const triggerFileSelect = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

const renderMarkdown = (content: string): string => {
  try {
    const result = marked(content, {
      breaks: true,
      gfm: true
    })
    return typeof result === 'string' ? result : String(result)
  } catch (error) {
    return content
  }
}

const renderUserMessage = (content: string): string => {
  try {
    const hasMarkdown = /^#|^\*\*|^##|^\*|^-|\*\*.*\*\*|^1\.|```/.test(content) || 
                       content.includes('**') || content.includes('##') || content.includes('# ')
    
    if (hasMarkdown || content.length > 50) {
      const result = marked(content, {
        breaks: true,
        gfm: true
      })
      return typeof result === 'string' ? result : String(result)
    } else {
      return content.replace(/\n/g, '<br>')
    }
  } catch (error) {
    try {
      const result = marked(content, { breaks: true, gfm: true })
      return typeof result === 'string' ? result : String(result)
    } catch {
      return content.replace(/\n/g, '<br>')
    }
  }
}

const hasMessageContent = (msg: PlaygroundMessage) => {
  const content = msg.displayText || msg.text
  return Boolean(content && content.trim().length)
}

</script>
