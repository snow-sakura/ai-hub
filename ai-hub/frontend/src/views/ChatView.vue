<template>
  <div class="chat-view">
    <AppSidebar />
    <div class="main-area">
      <ChatMessageList />
      <ChatInput />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '../components/layout/AppSidebar.vue'
import ChatMessageList from '../components/chat/ChatMessageList.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import { useConversationStore } from '../stores/conversation'
import { useSettingsStore } from '../stores/settings'

const convStore = useConversationStore()
const settingsStore = useSettingsStore()
const route = useRoute()

onMounted(async () => {
  await Promise.all([
    convStore.fetchConversations(),
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
</style>
