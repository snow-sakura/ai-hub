<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="brand-row">
        <span class="brand-title" @click="goHome" title="返回首页">
          <span class="brand-icon">✦</span>
          AI-HUB工作台
        </span>
        <n-button size="tiny" quaternary circle @click="goHome" title="返回首页">
          <template #icon>
            <span style="font-size: 15px; color: var(--text-secondary)">⌂</span>
          </template>
        </n-button>
      </div>
      <n-button size="small" type="primary" @click="createNew" block>
        + 新对话
      </n-button>
    </div>
    <ConversationList />
  </aside>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import ConversationList from '@/shared/components/sidebar/ConversationList.vue'
import { useConversationStore } from '@/shared/stores/conversation'

const router = useRouter()
const convStore = useConversationStore()

function createNew() {
  convStore.create()
}

function goHome() {
  router.push('/')
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-sidebar);
  border-right: 1px solid rgba(180, 150, 120, 0.1);
  overflow: hidden;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid rgba(180, 150, 120, 0.1);
}

.brand-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.brand-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: opacity 0.15s ease;
}

.brand-title:hover {
  opacity: 0.7;
}

.brand-icon {
  font-size: 18px;
}
</style>
