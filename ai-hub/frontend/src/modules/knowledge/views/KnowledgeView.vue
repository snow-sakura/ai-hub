<template>
  <div
    class="knowledge-view"
    @dragenter="onDragEnter"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
  >
    <!-- 拖拽上传 overlay -->
    <transition name="fade">
      <div v-if="isDragging" class="drag-overlay">
        <div class="drag-hint">
          <span class="drag-icon">📄</span>
          <span class="drag-text">释放以上传文件</span>
          <span class="drag-sub">支持 PDF、Word、TXT 格式</span>
        </div>
      </div>
    </transition>

    <div class="knowledge-content">
      <!-- 顶部栏 -->
      <div class="kb-header">
        <div class="kb-header-left">
          <button class="back-btn" @click="router.push('/')">
            <span class="back-arrow">←</span>
            <span class="back-text">AI-HUB工作台</span>
          </button>
          <div class="kb-title-area">
            <h1 class="kb-title">📚 知识库管理</h1>
            <span class="kb-summary">共 {{ totalDocs }} 个文档 · {{ totalChunks }} 个片段</span>
          </div>
        </div>
        <div class="kb-header-right">
          <n-button
            size="small"
            quaternary
            @click="handleRebuild"
            :disabled="docs.length === 0"
            class="rebuild-btn"
          >
            重建索引
          </n-button>
          <n-upload
            :show-file-list="false"
            :custom-request="handleUpload"
            accept=".pdf,.doc,.docx,.txt"
            :multiple="true"
          >
            <n-button
              type="primary"
              size="small"
              :loading="knowledgeStore.isUploading"
              class="upload-btn"
            >
              <template #icon><span class="upload-icon">+</span></template>
              上传文档
            </n-button>
          </n-upload>
        </div>
      </div>

      <!-- 统计卡片行 -->
      <div class="stats-row">
        <div class="stat-card">
          <span class="stat-value">{{ totalDocs }}</span>
          <span class="stat-label">文档总数</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ totalChunks }}</span>
          <span class="stat-label">片段总数</span>
        </div>
        <div class="stat-card">
          <div class="stat-types">
            <span
              v-for="item in fileTypeBreakdown"
              :key="item.label"
              class="type-tag"
            >
              {{ item.icon }} {{ item.label }} {{ item.count }}
            </span>
          </div>
          <span class="stat-label">按类型</span>
        </div>
      </div>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索文件名..."
        />
      </div>

      <!-- 内容区：loading / error / empty / table -->
      <div v-if="loading" class="state-box">
        <n-spin size="small" />
        <span class="state-text">加载中...</span>
      </div>

      <div v-else-if="knowledgeStore.loadError" class="state-box error">
        <span class="state-icon">⚠️</span>
        <span class="state-text">{{ knowledgeStore.loadError }}</span>
        <n-button size="tiny" @click="loadDocuments">重试</n-button>
      </div>

      <div v-else-if="filteredDocuments.length === 0 && !searchQuery" class="state-box">
        <span class="state-icon">📂</span>
        <span class="state-text">知识库为空，上传文档开始使用</span>
        <n-upload
          :show-file-list="false"
          :custom-request="handleUpload"
          accept=".pdf,.doc,.docx,.txt"
        >
          <n-button size="tiny" type="primary">上传文档</n-button>
        </n-upload>
      </div>

      <div v-else-if="filteredDocuments.length === 0 && searchQuery" class="state-box">
        <span class="state-icon">🔍</span>
        <span class="state-text">没有匹配「{{ searchQuery }}」的文档</span>
      </div>

      <div v-else class="doc-table">
        <!-- 表头 -->
        <div class="doc-table-header">
          <span class="col-name">文件名</span>
          <span class="col-type">类型</span>
          <span class="col-size">大小</span>
          <span class="col-chunks">片段</span>
          <span class="col-date">上传日期</span>
          <span class="col-action">操作</span>
        </div>

        <!-- 虚拟滚动数据行 -->
        <div ref="scrollRef" class="doc-table-body">
          <div :style="{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }">
            <div
              v-for="vrow in virtualizer.getVirtualItems()"
              :key="String(vrow.key)"
              :style="{ transform: `translateY(${vrow.start}px)` }"
              class="doc-table-row"
            >
              <span class="col-name" :title="filteredDocuments[vrow.index].filename">
                <span class="file-icon">{{ getFileIcon(filteredDocuments[vrow.index].fileType) }}</span>
                <span class="file-name">{{ filteredDocuments[vrow.index].filename }}</span>
              </span>
              <span class="col-type">
                <span class="type-badge">{{ getFileTypeLabel(filteredDocuments[vrow.index].fileType) }}</span>
              </span>
              <span class="col-size">{{ formatFileSize(filteredDocuments[vrow.index].fileSize) }}</span>
              <span class="col-chunks">{{ filteredDocuments[vrow.index].chunkCount }}</span>
              <span class="col-date">{{ formatDate(filteredDocuments[vrow.index].createdAt) }}</span>
              <span class="col-action">
                <button class="delete-btn" @click="confirmDelete(filteredDocuments[vrow.index])" title="删除文档">🗑️</button>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useVirtualizer } from '@tanstack/vue-virtual'
import { useRouter } from 'vue-router'
import { useKnowledgeStore } from '@/modules/knowledge/stores/knowledge'
import { useDialog } from 'naive-ui'
import type { KnowledgeDoc } from '@/modules/knowledge/types/knowledge'
import type { UploadCustomRequestOptions } from 'naive-ui'

const router = useRouter()
const knowledgeStore = useKnowledgeStore()
const dialog = useDialog()

/* ---------- 状态 ---------- */
const loading = ref(true)
const searchQuery = ref('')
const isDragging = ref(false)
let dragCounter = 0  // 防闪烁计数器

/* ---------- 安全访问 documents（防止 Pinia 初始化未完成时崩溃） ---------- */
const docs = computed(() => knowledgeStore?.documents ?? [])

/* ---------- 统计计算 ---------- */
const totalDocs = computed(() => docs.value.length)

const totalChunks = computed(() =>
  docs.value.reduce((sum, d) => sum + d.chunkCount, 0)
)

const fileTypeBreakdown = computed(() => {
  const map = new Map<string, { icon: string; label: string; count: number }>()
  for (const doc of docs.value) {
    const key = doc.fileType.toLowerCase()
    const existing = map.get(key)
    if (existing) {
      existing.count++
    } else {
      const { icon, label } = getFileTypeMeta(key)
      map.set(key, { icon, label, count: 1 })
    }
  }
  return Array.from(map.values())
})

/* ---------- 搜索过滤 ---------- */
const filteredDocuments = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return docs.value
  return docs.value.filter(d =>
    d.filename.toLowerCase().includes(q)
  )
})

/* ---------- 虚拟滚动（必须在所有 computed 之后，避免 TDZ 引用） ---------- */
const scrollRef = ref<HTMLDivElement>()
const virtualizer = useVirtualizer({
  get count() { return filteredDocuments.value.length },
  getScrollElement: () => scrollRef.value ?? null,
  estimateSize: () => 44,
  overscan: 5,
})

/* ---------- 生命周期 ---------- */
onMounted(async () => {
  await loadDocuments()
})

async function loadDocuments() {
  loading.value = true
  await knowledgeStore.fetchDocuments()
  loading.value = false
}

/* ---------- 文件类型工具 ---------- */
const FILE_TYPE_MAP: Record<string, { icon: string; label: string }> = {
  pdf: { icon: '📕', label: 'PDF' },
  doc: { icon: '📘', label: 'Word' },
  docx: { icon: '📘', label: 'Word' },
  txt: { icon: '📄', label: 'TXT' },
}

function getFileTypeMeta(fileType: string): { icon: string; label: string } {
  return FILE_TYPE_MAP[fileType.toLowerCase()] || { icon: '📄', label: fileType.toUpperCase() }
}

function getFileIcon(fileType: string): string {
  return getFileTypeMeta(fileType).icon
}

function getFileTypeLabel(fileType: string): string {
  return getFileTypeMeta(fileType).label
}

/* ---------- 工具函数 ---------- */
function formatFileSize(bytes: number): string {
  if (!bytes && bytes !== 0) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(isoStr: string): string {
  if (!isoStr) return '-'
  try {
    const d = new Date(isoStr)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  } catch {
    return isoStr
  }
}

/* ---------- 上传 ---------- */
async function handleUpload(options: UploadCustomRequestOptions) {
  const file = options.file?.file
  if (!file) return
  try {
    await knowledgeStore.upload(file)
    options.onFinish()
  } catch {
    options.onError()
  }
}

/* ---------- 拖拽上传 ---------- */
function onDragOver(e: DragEvent) {
  if (e.dataTransfer?.types.includes('Files')) {
    e.preventDefault()
  }
}

function onDragEnter(e: DragEvent) {
  dragCounter++
  if (e.dataTransfer?.types.includes('Files')) {
    isDragging.value = true
  }
}

function onDragLeave() {
  dragCounter--
  if (dragCounter <= 0) {
    dragCounter = 0
    isDragging.value = false
  }
}

async function onDrop(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
  dragCounter = 0
  const files = Array.from(e.dataTransfer?.files || [])
  const validExts = /\.(pdf|doc|docx|txt)$/i
  for (const file of files) {
    if (validExts.test(file.name)) {
      await knowledgeStore.upload(file)
    }
  }
}

/* ---------- 删除 ---------- */
function confirmDelete(doc: KnowledgeDoc) {
  dialog.warning({
    title: '删除文档',
    content: `确定要删除「${doc.filename}」吗？此操作不可撤销。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: () => knowledgeStore.remove(doc.id),
  })
}

/* ---------- 重建索引 ---------- */
async function handleRebuild() {
  dialog.info({
    title: '重建索引',
    content: '确定要重建知识库索引吗？所有文档将重新处理，这可能需要一些时间。',
    positiveText: '确认重建',
    negativeText: '取消',
    onPositiveClick: async () => {
      await knowledgeStore.rebuild()
      await knowledgeStore.fetchDocuments()
    },
  })
}
</script>

<style scoped>
/* ===== 页面容器 ===== */
.knowledge-view {
  min-height: 100vh;
  background: var(--bg-primary);
  overflow-y: auto;
  position: relative;
}

.knowledge-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 48px 24px 80px;
}

/* ===== 拖拽 overlay ===== */
.drag-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(198, 123, 92, 0.06);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.drag-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 48px 64px;
  border: 2px dashed var(--accent);
  border-radius: 20px;
  background: rgba(255, 253, 249, 0.95);
  animation: borderPulse 2s ease-in-out infinite;
}

.drag-icon {
  font-size: 40px;
}

.drag-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.drag-sub {
  font-size: 12px;
  color: var(--text-muted);
}

/* ===== 顶部栏 ===== */
.kb-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 28px;
  gap: 16px;
  flex-wrap: wrap;
}

.kb-header-left {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.kb-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  padding: 4px 10px;
  border-radius: 6px;
  transition: all 0.15s;
  width: fit-content;
}

.back-btn:hover {
  color: var(--accent);
  background: var(--accent-bg);
}

.back-arrow {
  font-size: 14px;
}

.kb-title-area {
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}

.kb-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.kb-summary {
  font-size: 13px;
  color: var(--text-muted);
}

.upload-icon {
  font-size: 14px;
  font-weight: 700;
}

.rebuild-btn {
  flex-shrink: 0;
}

/* ===== 统计卡片 ===== */
.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 140px;
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.1);
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--accent);
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.stat-types {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.type-tag {
  font-size: 11px;
  color: var(--text-primary);
  background: var(--accent-bg);
  padding: 2px 8px;
  border-radius: 999px;
  font-weight: 500;
}

/* ===== 搜索栏 ===== */
.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 10px;
  margin-bottom: 16px;
  transition: border-color 0.2s;
}

.search-bar:focus-within {
  border-color: rgba(198, 123, 92, 0.35);
  box-shadow: 0 0 0 3px rgba(198, 123, 92, 0.08);
}

.search-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13px;
  color: var(--text-primary);
  font-family: inherit;
}

.search-input::placeholder {
  color: var(--text-muted);
}

/* ===== 状态占位 ===== */
.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 64px 24px;
  background: var(--bg-card);
  border-radius: 12px;
  border: var(--border);
  margin: 24px 0;
  color: var(--text-muted);
}

.state-box.error {
  color: var(--danger);
}

.state-icon {
  font-size: 40px;
}

.state-text {
  font-size: 14px;
}

/* ===== 文档表格 ===== */
.doc-table {
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.1);
  border-radius: 12px;
  overflow: hidden;
}

.doc-table-header {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  background: var(--bg-secondary);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

/* 虚拟滚动容器 */
.doc-table-body {
  overflow: auto;
  max-height: 60vh;
}

.doc-table-body .doc-table-row {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

.doc-table-row {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-top: var(--border);
  transition: background 0.12s;
  font-size: 14px;
}

.doc-table-row:hover {
  background: var(--accent-bg);
}

.col-name {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.file-icon {
  font-size: 22px;
  flex-shrink: 0;
  line-height: 1;
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}

.col-type {
  width: 70px;
  flex-shrink: 0;
}

.type-badge {
  font-size: 11px;
  padding: 2px 7px;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 500;
}

.col-size {
  width: 80px;
  flex-shrink: 0;
  color: var(--text-secondary);
}

.col-chunks {
  width: 70px;
  flex-shrink: 0;
  color: var(--text-secondary);
}

.col-date {
  width: 100px;
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 12px;
}

.col-action {
  width: 60px;
  flex-shrink: 0;
  text-align: center;
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 4px 6px;
  border-radius: 6px;
  opacity: 0;
  transition: all 0.15s;
}

.doc-table-row:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(212, 116, 92, 0.1);
}

/* ===== 淡入动画 ===== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .knowledge-content {
    padding: 24px 16px 60px;
  }

  .kb-title {
    font-size: 20px;
  }

  .col-date,
  .col-size {
    display: none;
  }
}

/* ===== 边框脉冲动画 ===== */
@keyframes borderPulse {
  0%, 100% { border-color: var(--accent); }
  50% { border-color: rgba(198, 123, 92, 0.3); }
}
</style>
