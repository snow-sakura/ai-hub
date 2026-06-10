<template>
  <div class="conversation-list">
    <!-- 按日期分组 -->
    <template v-for="group in groupedConversations" :key="group.label">
      <div class="date-header">{{ group.label }}</div>
      <div
        v-for="conv in group.items"
        :key="conv.id"
        :class="['conv-item', { active: conv.id === convStore.activeConversationId }]"
        @click="convStore.selectConversation(conv.id)"
      >
        <div v-if="editingId !== conv.id" class="conv-content">
          <span class="conv-icon">💬</span>
          <span class="conv-title" :title="conv.title">{{ truncateTitle(conv.title) }}</span>
          <div class="conv-actions">
            <button class="action-btn" @click.stop="startEdit(conv)" title="重命名">✏️</button>
            <button class="action-btn" @click.stop="confirmDelete(conv)" title="删除">🗑️</button>
          </div>
        </div>
        <div v-else class="conv-edit">
          <n-input
            v-model:value="editTitle"
            size="small"
            @keydown.enter="finishEdit(conv.id)"
            @blur="finishEdit(conv.id)"
            autofocus
          />
        </div>
      </div>
    </template>

    <div v-if="convStore.conversations.length === 0" class="empty-hint">
      暂无对话，点击上方按钮新建
    </div>

    <div v-if="hasMore" class="show-more" @click="loadMore">
      查看更多（{{ remaining }} 条）▾
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useConversationStore } from '@/shared/stores/conversation'
import { useDialog } from 'naive-ui'
import type { Conversation } from '@/shared/types/conversation'

const convStore = useConversationStore()
const dialog = useDialog()
const editingId = ref<string | null>(null)
const editTitle = ref('')

const PAGE_SIZE = 10
const INITIAL_COUNT = 5

const visibleCount = ref(INITIAL_COUNT)

/** 已排序的列表：后端已按 updated_at DESC 返回，直接使用 */
const sorted = computed(() => convStore.conversations)

/** 当前展示的列表 */
const displayedConversations = computed(() =>
  sorted.value.slice(0, visibleCount.value)
)

/** 是否还有更多 */
const hasMore = computed(() =>
  visibleCount.value < sorted.value.length
)

/** 剩余条数 */
const remaining = computed(() =>
  sorted.value.length - visibleCount.value
)

/** 加载更多 */
function loadMore() {
  visibleCount.value += PAGE_SIZE
}

/** 按日期分组 */
interface ConversationGroup {
  label: string
  items: Conversation[]
}

const groupedConversations = computed<ConversationGroup[]>(() => {
  const groups: ConversationGroup[] = []
  const today = new Date()
  const todayStr = today.toDateString()
  const yesterdayStr = new Date(today.getTime() - 86400000).toDateString()

  let currentGroup: ConversationGroup | null = null

  for (const conv of displayedConversations.value) {
    const date = new Date(conv.updatedAt || conv.createdAt)
    const dateStr = date.toDateString()
    let label: string

    if (dateStr === todayStr) {
      label = '今天'
    } else if (dateStr === yesterdayStr) {
      label = '昨天'
    } else if (today.getTime() - date.getTime() < 7 * 86400000) {
      label = '本周'
    } else {
      label = '更早'
    }

    if (!currentGroup || currentGroup.label !== label) {
      currentGroup = { label, items: [] }
      groups.push(currentGroup)
    }
    currentGroup.items.push(conv)
  }

  return groups
})

/** 标题截断前10个字 */
function truncateTitle(title: string): string {
  if (!title) return '新对话'
  return title.length > 10 ? title.slice(0, 10) + '…' : title
}

function startEdit(conv: Conversation) {
  editingId.value = conv.id
  editTitle.value = conv.title
}

function finishEdit(id: string) {
  if (editTitle.value.trim()) {
    convStore.rename(id, editTitle.value.trim())
  }
  editingId.value = null
}

function confirmDelete(conv: Conversation) {
  dialog.warning({
    title: '删除对话',
    content: `确定要删除「${conv.title}」吗？此操作不可撤销。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: () => convStore.remove(conv.id),
  })
}
</script>

<style scoped>
.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.date-header {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  padding: 12px 12px 6px;
  letter-spacing: 0.5px;
}

.conv-item {
  padding: 9px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  margin-bottom: 2px;
}

.conv-item:hover {
  background: rgba(198, 123, 92, 0.05);
}

.conv-item.active {
  background: rgba(198, 123, 92, 0.08);
}

.conv-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.conv-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.conv-title {
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.conv-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.conv-item:hover .conv-actions {
  opacity: 1;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 11px;
  padding: 2px 4px;
  border-radius: 4px;
  line-height: 1;
}

.action-btn:hover {
  background: rgba(180, 150, 120, 0.05);
}

.conv-edit {
  padding: 0;
}

.empty-hint {
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
  padding: 24px 16px;
}

.show-more {
  text-align: center;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 10px 12px;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s;
}

.show-more:hover {
  background: rgba(198, 123, 92, 0.05);
  color: var(--accent);
}
</style>
