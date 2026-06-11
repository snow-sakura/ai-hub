<template>
  <div
    class="drop-zone"
    :class="{ dragging, 'has-file': uploadedFile }"
    @dragenter.prevent="onDragEnter"
    @dragover.prevent
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
    @click="triggerUpload"
  >
    <input
      ref="fileInput"
      type="file"
      accept=".pdf,.doc,.docx,.txt,.md"
      style="display: none"
      @change="onFileSelected"
    />

    <template v-if="!uploading && !uploadedFile">
      <div class="drop-icon">+</div>
      <div class="drop-text">拖拽或点击上传需求文档</div>
      <div class="drop-hint">支持 PDF、Word、TXT、Markdown 格式</div>
    </template>

    <template v-else-if="uploading">
      <n-spin size="small" />
      <div class="drop-text">正在解析...</div>
    </template>

    <template v-else-if="uploadedFile">
      <div class="file-info">
        <span class="file-icon">V</span>
        <span class="file-name">{{ uploadedFile }}</span>
        <n-button text type="error" size="tiny" @click.stop="clearFile">
          移除
        </n-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { uploadDocument } from '@/modules/ai_testing/api/generation'

const emit = defineEmits<{
  parsed: [{ text: string; file_name: string }]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const dragging = ref(false)
const uploading = ref(false)
const uploadedFile = ref('')

function triggerUpload() {
  fileInput.value?.click()
}

function onDragEnter() { dragging.value = true }
function onDragLeave() { dragging.value = false }
function onDrop(e: DragEvent) {
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) handleFile(file)
}

function onFileSelected(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) handleFile(file)
}

async function handleFile(file: File) {
  uploading.value = true
  try {
    const res = await uploadDocument(file)
    const data = res.data
    if (data) {
      uploadedFile.value = data.file_name
      emit('parsed', { text: data.text, file_name: data.file_name })
    }
  } catch {
    // 解析失败时保留原文件名
    uploadedFile.value = file.name
    emit('parsed', { text: '', file_name: file.name })
  } finally {
    uploading.value = false
  }
}

function clearFile() {
  uploadedFile.value = ''
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(0, 0, 0, 0.02);
}
.drop-zone:hover,
.drop-zone.dragging {
  border-color: var(--n-primary-color, #2080f0);
  background: rgba(32, 128, 240, 0.04);
}
.drop-zone.has-file {
  border-style: solid;
  border-color: var(--n-success-color, #18a058);
}
.drop-icon {
  font-size: 32px;
  color: var(--n-primary-color, #2080f0);
  margin-bottom: 8px;
  line-height: 1;
}
.drop-text {
  font-size: 14px;
  color: var(--text-primary, #333);
  margin-bottom: 4px;
}
.drop-hint {
  font-size: 12px;
  color: #999;
}
.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}
.file-icon {
  color: var(--n-success-color, #18a058);
  font-weight: bold;
}
.file-name {
  font-size: 14px;
  color: var(--text-primary, #333);
}
</style>
