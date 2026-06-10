<template>
  <teleport to="body">
    <transition name="preview-fade">
      <div v-if="visible" class="file-preview-overlay" @click="close">
        <div class="preview-modal" @click.stop>
          <div class="modal-header">
            <div class="file-info">
              <span class="file-icon">{{ getFileIcon(fileName) }}</span>
              <span class="file-name">{{ fileName }}</span>
              <span class="file-size" v-if="fileSize">{{ formatSize(fileSize) }}</span>
            </div>
            <div class="modal-actions">
              <a class="action-btn" :href="fileUrl" :download="fileName" title="下载">
                ⬇ 下载
              </a>
              <button class="action-btn close-action" @click="close">✕</button>
            </div>
          </div>
          <div class="modal-body">
            <!-- PDF 预览 -->
            <iframe
              v-if="isPdf"
              :src="fileUrl"
              class="pdf-viewer"
              frameborder="0"
            />
            <!-- 图片预览 -->
            <div v-else-if="isImage" class="image-viewer">
              <img :src="fileUrl" :alt="fileName" />
            </div>
            <!-- 文本预览 -->
            <pre v-else-if="isText" class="text-viewer">{{ textContent }}</pre>
            <!-- 不支持的格式 -->
            <div v-else class="unsupported">
              <span class="unsupported-icon">{{ getFileIcon(fileName) }}</span>
              <p>此文件类型暂不支持在线预览</p>
              <a class="download-link" :href="fileUrl" :download="fileName">
                点击下载 {{ fileName }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  fileUrl: string
  fileName: string
  fileSize?: number
  textContent?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const visible = ref(false)

const ext = computed(() => {
  const parts = props.fileName.split('.')
  return parts.length > 1 ? parts.pop()!.toLowerCase() : ''
})

const isPdf = computed(() => ext.value === 'pdf')
const isImage = computed(() => ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'].includes(ext.value))
const isText = computed(() => ['txt', 'md', 'json', 'csv', 'log', 'yml', 'yaml'].includes(ext.value))

function getFileIcon(name: string): string {
  const e = name.split('.').pop()?.toLowerCase() || ''
  const icons: Record<string, string> = {
    pdf: '📄', doc: '📝', docx: '📝', xls: '📊', xlsx: '📊',
    ppt: '📋', pptx: '📋', zip: '📦', rar: '📦',
    png: '🖼️', jpg: '🖼️', jpeg: '🖼️', gif: '🖼️',
    mp3: '🎵', mp4: '🎬', txt: '📃', md: '📃',
    py: '🐍', js: '📜', ts: '📜', html: '🌐',
  }
  return icons[e] || '📎'
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function close() {
  visible.value = false
  emit('close')
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}

onMounted(() => {
  visible.value = true
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.file-preview-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-modal {
  width: 80vw;
  max-width: 900px;
  height: 80vh;
  background: rgba(18, 18, 26, 0.95);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  font-size: 20px;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.file-size {
  font-size: 12px;
  color: var(--text-muted);
}

.modal-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
  color: var(--neon-blue);
}

.close-action:hover {
  background: rgba(236, 72, 153, 0.1);
  border-color: rgba(236, 72, 153, 0.3);
  color: var(--neon-pink);
}

.modal-body {
  flex: 1;
  overflow: auto;
  padding: 0;
}

.pdf-viewer {
  width: 100%;
  height: 100%;
}

.image-viewer {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 20px;
}

.image-viewer img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.text-viewer {
  padding: 20px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  font-family: 'SF Mono', 'Fira Code', monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.unsupported {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
}

.unsupported-icon {
  font-size: 64px;
}

.unsupported p {
  color: var(--text-secondary);
}

.download-link {
  color: var(--neon-blue);
  text-decoration: none;
  padding: 8px 20px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.download-link:hover {
  background: rgba(0, 212, 255, 0.1);
}

.preview-fade-enter-active {
  transition: opacity 0.3s ease;
}

.preview-fade-leave-active {
  transition: opacity 0.2s ease;
}

.preview-fade-enter-from,
.preview-fade-leave-to {
  opacity: 0;
}
</style>
