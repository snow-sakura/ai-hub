<template>
  <div class="memory-manager">
    <div v-if="memories.length === 0" class="empty">
      暂无记忆，AI 会在对话中自动记住重要信息
    </div>
    <div v-else class="memory-list">
      <div v-for="mem in memories" :key="mem.id" class="memory-item">
        <div class="memory-content">
          <span class="memory-type-badge" :class="mem.memory_type">
            {{ typeLabels[mem.memory_type] || mem.memory_type }}
          </span>
          <span v-if="editingId !== mem.id" class="memory-text">{{ mem.content }}</span>
          <n-input
            v-else
            v-model:value="editText"
            size="small"
            @keydown.enter="saveEdit(mem.id)"
          />
        </div>
        <div class="memory-actions">
          <template v-if="editingId !== mem.id">
            <button class="mem-btn" @click="startEdit(mem)">✏️</button>
            <button class="mem-btn delete" @click="remove(mem.id)">🗑️</button>
          </template>
          <template v-else>
            <button class="mem-btn" @click="saveEdit(mem.id)">💾</button>
            <button class="mem-btn" @click="cancelEdit">✕</button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { ComfortMemory } from '@/modules/comfort/types/comfort'
import { getMemories, updateMemory, deleteMemory } from '@/modules/comfort/api/comfort'

const props = defineProps<{
  conversationId: string
}>()

const memories = ref<ComfortMemory[]>([])
const editingId = ref<string | null>(null)
const editText = ref('')

const typeLabels: Record<string, string> = {
  fact: '事实',
  preference: '偏好',
  event: '事件',
}

async function fetchMemories() {
  try {
    const res = await getMemories(props.conversationId)
    memories.value = res.data || []
  } catch (e) {
    console.error('获取记忆失败:', e)
  }
}

function startEdit(mem: ComfortMemory) {
  editingId.value = mem.id
  editText.value = mem.content
}

function cancelEdit() {
  editingId.value = null
  editText.value = ''
}

async function saveEdit(memId: string) {
  try {
    await updateMemory(memId, editText.value)
    const mem = memories.value.find(m => m.id === memId)
    if (mem) mem.content = editText.value
    cancelEdit()
  } catch (e) {
    console.error('更新记忆失败:', e)
  }
}

async function remove(memId: string) {
  try {
    await deleteMemory(memId)
    memories.value = memories.value.filter(m => m.id !== memId)
  } catch (e) {
    console.error('删除记忆失败:', e)
  }
}

onMounted(fetchMemories)
</script>

<style scoped>
.memory-manager {
  min-height: 60px;
}

.empty {
  text-align: center;
  padding: 16px;
  color: var(--text-muted);
  font-size: 14px;
}

.memory-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.memory-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-card);
  border-radius: 8px;
  border: 1px solid rgba(180, 150, 120, 0.08);
  border-left: 3px solid transparent;
  transition: border-left-color 0.2s ease, background 0.2s ease;
}

.memory-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.memory-type-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 999px;
  flex-shrink: 0;
  font-weight: 500;
}

.memory-type-badge.fact {
  background: rgba(123, 168, 125, 0.12);
  color: #7BA87D;
}

.memory-type-badge.preference {
  background: rgba(212, 165, 116, 0.15);
  color: #C67B5C;
}

.memory-type-badge.event {
  background: rgba(155, 142, 196, 0.15);
  color: #9B8EC4;
}

.memory-item:has(.memory-type-badge.fact) {
  border-left-color: #7BA87D;
}

.memory-item:has(.memory-type-badge.preference) {
  border-left-color: #C67B5C;
}

.memory-item:has(.memory-type-badge.event) {
  border-left-color: #9B8EC4;
}

.memory-text {
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.memory-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.mem-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background 0.15s;
}

.mem-btn:hover {
  background: var(--accent-bg);
}
</style>
