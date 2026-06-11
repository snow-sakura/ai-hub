<template>
  <n-space vertical :size="12">
    <n-divider />

    <!-- 评论列表 -->
    <n-space vertical :size="8">
      <n-empty v-if="!comments?.length" description="暂无评论" />

      <n-card
        v-for="comment in comments"
        :key="comment.id"
        size="small"
        :bordered="true"
        style="margin-bottom: 4px;"
      >
        <template #header>
          <n-space :size="8" align="center">
            <n-avatar round :size="24">
              {{ comment.author?.charAt(0) || '?' }}
            </n-avatar>
            <n-text style="font-size: 13px; font-weight: 500;">{{ comment.author || '匿名' }}</n-text>
            <n-text depth="3" style="font-size: 12px;">{{ comment.created_at }}</n-text>
          </n-space>
        </template>

        <!-- 编辑模式 -->
        <template v-if="editingId === comment.id">
          <n-input
            v-model:value="editContent"
            type="textarea"
            :rows="3"
            :maxlength="5000"
            show-count
          />
          <n-space :size="8" style="margin-top: 8px;">
            <n-button size="tiny" type="primary" @click="handleUpdate(comment.id)">保存</n-button>
            <n-button size="tiny" @click="editingId = ''">取消</n-button>
          </n-space>
        </template>

        <!-- 展示模式 -->
        <template v-else>
          <div style="white-space: pre-wrap; font-size: 13px; line-height: 1.6;">
            {{ comment.content }}
          </div>
          <n-space :size="8" style="margin-top: 8px;">
            <n-button size="tiny" text @click="startEdit(comment)">编辑</n-button>
            <n-button size="tiny" text type="error" @click="handleDelete(comment.id)">删除</n-button>
          </n-space>
        </template>
      </n-card>
    </n-space>

    <!-- 输入框 -->
    <n-card size="small" :bordered="true">
      <n-input
        v-model:value="newContent"
        type="textarea"
        :rows="3"
        placeholder="输入评论..."
        :maxlength="5000"
        show-count
      />
      <n-space :size="8" style="margin-top: 8px; justify-content: flex-end;">
        <n-button
          type="primary"
          size="small"
          :disabled="!newContent.trim()"
          :loading="isSubmitting"
          @click="handleCreate"
        >
          发表评论
        </n-button>
      </n-space>
    </n-card>
  </n-space>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useCommentStore } from '@/modules/ai_testing/stores/comment'
import type { CaseComment } from '@/modules/ai_testing/types/comment'

const props = defineProps<{ caseId: string }>()

const commentStore = useCommentStore()

const comments = commentStore.comments
const newContent = ref('')
const editingId = ref('')
const editContent = ref('')
const isSubmitting = ref(false)

async function handleCreate() {
  if (!newContent.value.trim()) return
  isSubmitting.value = true
  try {
    await commentStore.create(props.caseId, { content: newContent.value.trim() })
    newContent.value = ''
  } finally {
    isSubmitting.value = false
  }
}

function startEdit(comment: CaseComment) {
  editingId.value = comment.id
  editContent.value = comment.content
}

async function handleUpdate(commentId: string) {
  if (!editContent.value.trim()) return
  await commentStore.update(commentId, editContent.value.trim())
  editingId.value = ''
  editContent.value = ''
}

async function handleDelete(commentId: string) {
  await commentStore.remove(commentId)
}
</script>
