<template>
  <div 
    class="bg-white border-r border-gray-200 flex flex-col transition-all duration-200 ease-in-out"
    :style="{ width: navigationStore.sidebarWidth }"
  >
    <!-- 模块导航 -->
    <nav class="flex-1 px-2 py-4 space-y-1">
      <router-link
        v-for="module in navigationStore.modules"
        :key="module.id"
        :to="module.path"
        class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out group"
        :class="[
          navigationStore.currentModule === module.id
            ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-500'
            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
        ]"
        @click="navigationStore.setCurrentModule(module.id)"
      >
        <ModuleIcon :name="getIconName(module.icon)" class="mr-3 flex-shrink-0" />
        <span 
          v-if="!navigationStore.sidebarCollapsed"
          class="truncate"
        >
          {{ module.name }}
        </span>
      </router-link>
    </nav>

    <!-- 分隔线 -->
    <div class="border-t border-gray-200 mx-2"></div>

    <!-- 底部工具 -->
    <div class="px-2 py-4 space-y-1">
      <!-- 退出登录按钮 -->
      <button
        @click="handleLogout"
        class="flex items-center w-full px-3 py-2 text-sm font-medium text-red-600 rounded-md hover:bg-red-50 hover:text-red-700 transition-colors duration-150 ease-in-out"
        title="登出"
      >
        <!-- 退出登录图标 -->
        <svg class="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        <span v-if="!navigationStore.sidebarCollapsed">登出</span>
      </button>

      <!-- 折叠按钮 -->
      <button
        @click="navigationStore.toggleSidebar"
        class="flex items-center w-full px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-50 hover:text-gray-900 transition-colors duration-150 ease-in-out"
      >
        <svg v-if="navigationStore.sidebarCollapsed" class="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
        <svg v-else class="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
        <span v-if="!navigationStore.sidebarCollapsed">折叠</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNavigationStore } from '@/stores/navigationStore'
import { useAuthStore } from '@/stores/authStore'
import ModuleIcon from '@/components/common/ModuleIcon.vue'

const navigationStore = useNavigationStore()
const authStore = useAuthStore()

// 图标名称映射
const iconMap: Record<string, string> = {
  '📝': 'pencil',
  '⚡': 'sparkles',
  '🎯': 'beaker',
  '📚': 'collection',
  '👥': 'users',
  '🎨': 'palette'  // 绘图模块使用调色板图标
}

const getIconName = (emoji: string): string => {
  return iconMap[emoji] || 'home'
}

// 退出登录
const handleLogout = async () => {
  // 确认退出
  if (!confirm('确定要退出登录吗？')) {
    return
  }

  try {
    await authStore.logout()
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}
</script>
