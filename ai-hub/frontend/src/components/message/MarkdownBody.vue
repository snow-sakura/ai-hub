<template>
  <div class="markdown-body" ref="bodyRef" v-html="rendered" @click="handleClick" />
  <ImagePreview
    v-if="previewImage"
    :src="previewImage.src"
    :alt="previewImage.alt"
    @close="previewImage = null"
  />
  <FilePreview
    v-if="previewFile"
    :file-url="previewFile.url"
    :file-name="previewFile.name"
    @close="previewFile = null"
  />
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useMarkdownRenderer } from '../../composables/useMarkdownRenderer'
import ImagePreview from './ImagePreview.vue'
import FilePreview from './FilePreview.vue'

const props = defineProps<{ content: string }>()
const { render } = useMarkdownRenderer()

const bodyRef = ref<HTMLElement>()
const rendered = computed(() => render(props.content || ''))

const previewImage = ref<{ src: string; alt: string } | null>(null)
const previewFile = ref<{ url: string; name: string } | null>(null)

const IMAGE_EXTS = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg']
const FILE_EXTS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'txt', 'csv']

function handleClick(e: MouseEvent) {
  const target = e.target as HTMLElement

  // 点击图片 → 打开预览
  if (target.tagName === 'IMG') {
    const img = target as HTMLImageElement
    previewImage.value = { src: img.src, alt: img.alt || '' }
    return
  }

  // 点击文件链接 → 打开预览
  if (target.tagName === 'A') {
    const link = target as HTMLAnchorElement
    const href = link.href || ''
    const ext = href.split('.').pop()?.toLowerCase()?.split('?')[0] || ''

    if (IMAGE_EXTS.includes(ext)) {
      previewImage.value = { src: href, alt: link.textContent || '' }
      e.preventDefault()
    } else if (FILE_EXTS.includes(ext)) {
      const name = link.textContent || href.split('/').pop() || 'file'
      previewFile.value = { url: href, name }
      e.preventDefault()
    }
  }
}
</script>

<style>
.markdown-body {
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
}

.markdown-body p {
  margin: 0 0 12px;
}

.markdown-body p:last-child {
  margin-bottom: 0;
}

.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  margin: 16px 0 8px;
  color: var(--text-primary);
}

.markdown-body h1 { font-size: 1.4em }
.markdown-body h2 { font-size: 1.2em }
.markdown-body h3 { font-size: 1.1em }

.markdown-body ul, .markdown-body ol {
  padding-left: 24px;
  margin: 8px 0;
}

.markdown-body li {
  margin: 4px 0;
}

.markdown-body code {
  background: rgba(198, 123, 92, 0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  color: var(--accent);
}

.markdown-body .code-block {
  margin: 12px 0;
  border-radius: 8px;
  overflow-x: auto;
  border: 1px solid rgba(180, 150, 120, 0.1);
}

.markdown-body .code-block code {
  display: block;
  padding: 16px;
  background: #F8F9FB;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-primary);
}

.markdown-body blockquote {
  border-left: 3px solid var(--accent);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--text-secondary);
}

.markdown-body a {
  color: var(--accent);
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

.markdown-body table {
  border-collapse: collapse;
  margin: 8px 0;
  width: 100%;
}

.markdown-body th, .markdown-body td {
  border: 1px solid rgba(180, 150, 120, 0.1);
  padding: 8px 12px;
  text-align: left;
}

.markdown-body th {
  background: var(--accent-bg);
}

.markdown-body img {
  max-width: 100%;
  border-radius: 8px;
  margin: 8px 0;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.markdown-body img:hover {
  transform: scale(1.02);
  box-shadow: var(--shadow-md);
}

.markdown-body hr {
  border: none;
  border-top: 1px solid rgba(180, 150, 120, 0.1);
  margin: 16px 0;
}
</style>
