<template>
  <div class="page-wrap">
    <div class="back-nav" @click="router.push('/ai-testing/testcases')">
      <span class="back-arrow">←</span>
      <span>返回用例列表</span>
    </div>

    <div v-if="store.currentCase" class="detail-content">
      <!-- 标题区 -->
      <header class="case-header">
        <div class="case-header-top">
          <h1 class="case-title">{{ store.currentCase.title }}</h1>
          <div class="case-actions">
            <n-button text type="primary" @click="router.push(`/ai-testing/testcases/${caseId}/edit`)">
              编辑
            </n-button>
            <n-button text type="error" @click="handleDelete">删除</n-button>
          </div>
        </div>
        <div class="case-meta">
          <PriorityBadge :priority="store.currentCase.priority" />
          <n-tag size="small" round :bordered="false">{{ store.currentCase.case_type }}</n-tag>
          <n-tag
            size="small" round :bordered="false"
            :type="store.currentCase.status === 'active' ? 'info' : store.currentCase.status === 'deprecated' ? 'warning' : 'default'"
          >
            {{ statusLabel }}
          </n-tag>
          <span v-if="store.currentCase.source === 'ai'" class="ai-badge">AI 生成</span>
          <span class="meta-text" v-if="store.currentCase.project_name">
            {{ store.currentCase.project_name }}
          </span>
          <span class="meta-text" v-if="store.currentCase.version">
            v{{ store.currentCase.version }}
          </span>
        </div>
      </header>

      <!-- 前置条件 -->
      <section v-if="store.currentCase.preconditions" class="content-section">
        <h3 class="section-title">前置条件</h3>
        <div class="md-content" v-html="renderMarkdown(store.currentCase.preconditions)"></div>
      </section>

      <!-- 测试步骤 -->
      <section v-if="store.currentCase.steps" class="content-section">
        <h3 class="section-title">测试步骤</h3>
        <div class="md-content" v-html="renderMarkdown(store.currentCase.steps)"></div>
      </section>

      <!-- 预期结果 -->
      <section v-if="store.currentCase.expected_results" class="content-section">
        <h3 class="section-title">预期结果</h3>
        <div class="md-content" v-html="renderMarkdown(store.currentCase.expected_results)"></div>
      </section>

      <!-- 标签 -->
      <section v-if="store.currentCase.tags.length > 0" class="content-section">
        <h3 class="section-title">标签</h3>
        <div class="tags-row">
          <n-tag v-for="tag in store.currentCase.tags" :key="tag" size="small" round :bordered="false">
            {{ tag }}
          </n-tag>
        </div>
      </section>

      <!-- 附件区域 -->
      <section class="content-section">
        <h3 class="section-title">附件</h3>
        <n-space vertical :size="8">
          <n-empty v-if="!attachmentStore.attachments.length" description="暂无附件" />
          <div v-for="att in attachmentStore.attachments" :key="att.id" class="attachment-item">
            <a :href="getAttachmentDownloadUrl(att.id)" target="_blank" class="attachment-link">
              {{ att.file_name }}
            </a>
            <n-text depth="3" style="font-size: 12px;">
              ({{ formatFileSize(att.file_size) }})
            </n-text>
            <n-button size="tiny" text type="error" @click="handleDeleteAttachment(att.id)">
              删除
            </n-button>
          </div>
          <!-- 上传按钮 -->
          <input
            ref="fileInput"
            type="file"
            style="display:none"
            @change="handleUploadAttachment"
          />
          <n-button size="small" @click="triggerFileUpload">上传附件</n-button>
        </n-space>
      </section>

      <!-- 评论区 -->
      <section class="content-section">
        <CommentSection :case-id="caseId" />
      </section>

      <!-- 底部信息 -->
      <footer class="case-footer">
        <span>创建于 {{ formatDate(store.currentCase.created_at) }}</span>
        <span>更新于 {{ formatDate(store.currentCase.updated_at) }}</span>
        <span v-if="store.currentCase.author">作者: {{ store.currentCase.author }}</span>
      </footer>
    </div>

    <div v-else class="loading-state">
      <n-spin size="medium" />
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NTag, NSpin, useMessage, useDialog } from 'naive-ui'
import { useTestCaseStore } from '@/modules/ai_testing/stores/testcase'
import { useAttachmentStore } from '@/modules/ai_testing/stores/attachment'
import PriorityBadge from '@/modules/ai_testing/components/common/PriorityBadge.vue'
import CommentSection from '@/modules/ai_testing/components/testcase/CommentSection.vue'
import { getAttachmentDownloadUrl } from '@/modules/ai_testing/api/attachment'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const store = useTestCaseStore()
const attachmentStore = useAttachmentStore()

const caseId = computed(() => route.params.id as string)
const fileInput = ref<HTMLInputElement | null>(null)

const statusLabel = computed(() => {
  const map: Record<string, string> = { draft: '草稿', active: '启用', deprecated: '废弃' }
  return map[store.currentCase?.status || ''] || ''
})

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return isNaN(d.getTime()) ? dateStr : d.toLocaleDateString('zh-CN')
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function triggerFileUpload() {
  fileInput.value?.click()
}

async function handleUploadAttachment(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const ok = await attachmentStore.upload(caseId.value, file)
  if (ok) {
    message.success('附件上传成功')
  } else {
    message.error('上传失败')
  }
  // 重置 input
  if (fileInput.value) fileInput.value.value = ''
}

async function handleDeleteAttachment(attachmentId: string) {
  await attachmentStore.remove(attachmentId)
  message.success('附件已删除')
}

function renderMarkdown(text: string): string {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    .replace(/\n/g, '<br>')
}

function handleDelete() {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除用例「${store.currentCase?.title}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      const ok = await store.deleteCase(caseId.value)
      if (ok) {
        message.success('用例已删除')
        router.push('/ai-testing/testcases')
      }
    },
  })
}

onMounted(() => {
  store.fetchCase(caseId.value)
  attachmentStore.fetchAttachments(caseId.value)
})
</script>

<style scoped>
.page-wrap {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}
.back-nav {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #5C4A38;
  cursor: pointer;
  margin-bottom: 24px;
  transition: color 0.15s ease;
}
.back-nav:hover { color: var(--accent, #3b82f6); }
.back-arrow { font-size: 16px; }
.case-header { margin-bottom: 32px; }
.case-header-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
}
.case-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary, #1a1a2e);
  letter-spacing: -0.02em;
  margin: 0;
  line-height: 1.25;
}
.case-actions { display: flex; gap: 12px; flex-shrink: 0; }
.case-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.ai-badge {
  font-size: 12px;
  font-weight: 500;
  color: #7c3aed;
  background: rgba(124, 58, 237, 0.08);
  padding: 2px 8px;
  border-radius: 999px;
}
.meta-text { font-size: 12px; color: #7A6855; }
.content-section {
  background: var(--bg-card, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #1a1a2e);
  margin: 0 0 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
.md-content {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
}
.md-content :deep(code) {
  background: rgba(0, 0, 0, 0.04);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}
.md-content :deep(strong) { font-weight: 600; }
.md-content :deep(li) { margin-left: 16px; margin-bottom: 4px; }
.tags-row { display: flex; flex-wrap: wrap; gap: 8px; }
.case-footer {
  display: flex;
  gap: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  font-size: 12px;
  color: #7A6855;
}
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 64px 0;
  color: #7A6855;
  font-size: 14px;
}
.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}
.attachment-link {
  color: var(--n-primary-color, #2080f0);
  text-decoration: none;
  font-size: 13px;
}
.attachment-link:hover { text-decoration: underline; }
</style>
