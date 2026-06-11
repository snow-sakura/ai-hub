<template>
  <div class="chat-view">
    <!-- 桌面端：侧边栏内联显示 -->
    <AppSidebar v-if="isDesktop" />

    <!-- 移动端：侧边栏作为 overlay drawer -->
    <n-drawer
      v-else
      :show="sidebarVisible"
      :width="260"
      placement="left"
      :auto-focus="false"
      @update:show="sidebarVisible = $event"
    >
      <AppSidebar />
    </n-drawer>

    <div class="main-area">
      <!-- 移动端顶部栏：汉堡菜单按钮 + 标题 -->
      <div v-if="!isDesktop" class="mobile-header">
        <button class="hamburger-btn" @click="sidebarVisible = true" aria-label="打开侧边栏">
          <span class="hamburger-line" />
          <span class="hamburger-line" />
          <span class="hamburger-line" />
        </button>
        <span class="mobile-title">{{ activeTitle }}</span>
      </div>

      <ChatMessageList />
      <ChatInput />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '@/shared/components/layout/AppSidebar.vue'
import ChatMessageList from '@/modules/chat/components/ChatMessageList.vue'
import ChatInput from '@/modules/chat/components/ChatInput.vue'
import { useConversationStore } from '@/shared/stores/conversation'
import { useSettingsStore } from '@/shared/stores/settings'
import { useResponsive } from '@/shared/composables/useResponsive'

const convStore = useConversationStore()
const settingsStore = useSettingsStore()
const route = useRoute()
const { isDesktop } = useResponsive()
const sidebarVisible = ref(false)

/** 移动端切换对话时自动关闭抽屉 */
watch(() => convStore.activeConversationId, () => {
  if (!isDesktop.value) {
    sidebarVisible.value = false
  }
})

const activeTitle = computed(() => {
  if (!convStore.activeConversationId) return 'AI-HUB'
  const conv = convStore.conversations.find(c => c.id === convStore.activeConversationId)
  return conv?.title || 'AI-HUB'
})

onMounted(async () => {
  await Promise.all([
    convStore.fetchConversations('chat'),
    settingsStore.fetchModels(),
  ])
  // 没有选中任何对话时，自动选中最新一条
  if (!convStore.activeConversationId && convStore.conversations.length > 0) {
    await convStore.selectConversation(convStore.conversations[0].id)
  }
})

/** 处理首页入口参数 */
watch(() => route.query.panel, (panel) => {
  if (panel === 'knowledge') {
    setTimeout(() => {
      const panelEl = document.querySelector('.sidebar-footer')
      panelEl?.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }, 300)
  }
}, { immediate: true })
</script>

<style scoped>
.chat-view {
  display: flex;
  height: 100vh;
  background: var(--bg-primary);
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg-primary);
}

/* 移动端顶部栏 */
.mobile-header {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0 12px;
  gap: 10px;
  border-bottom: 1px solid rgba(180, 150, 120, 0.08);
  background: var(--bg-card);
  flex-shrink: 0;
}

.hamburger-btn {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  width: 32px;
  height: 32px;
  padding: 6px 5px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s;
}

.hamburger-btn:hover {
  background: var(--accent-bg);
}

.hamburger-line {
  display: block;
  height: 2px;
  background: var(--text-secondary);
  border-radius: 1px;
  transition: background 0.15s;
}

.mobile-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
