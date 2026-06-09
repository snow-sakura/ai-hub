<template>
  <teleport to="body">
    <transition name="preview-fade">
      <div v-if="visible" class="image-preview-overlay" @click="close">
        <div class="preview-container" @click.stop>
          <div class="preview-toolbar">
            <button class="tool-btn" @click="rotateLeft" title="左旋转">↺</button>
            <button class="tool-btn" @click="rotateRight" title="右旋转">↻</button>
            <button class="tool-btn" @click="zoomIn" title="放大">+</button>
            <button class="tool-btn" @click="zoomOut" title="缩小">−</button>
            <button class="tool-btn" @click="resetView" title="重置">⊙</button>
            <a class="tool-btn download-btn" :href="src" :download="alt || 'image'" title="下载">⬇</a>
            <button class="tool-btn close-btn" @click="close" title="关闭">✕</button>
          </div>
          <div class="image-wrapper">
            <img
              ref="imgRef"
              :src="src"
              :alt="alt"
              class="preview-image"
              :style="imageStyle"
              @load="onLoad"
              draggable="false"
            />
          </div>
          <div v-if="alt" class="image-caption">{{ alt }}</div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  src: string
  alt?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const visible = ref(false)
const imgRef = ref<HTMLImageElement>()
const scale = ref(1)
const rotation = ref(0)

const imageStyle = computed(() => ({
  transform: `scale(${scale.value}) rotate(${rotation.value}deg)`,
  transition: 'transform 0.3s ease',
}))

function zoomIn() {
  scale.value = Math.min(scale.value + 0.25, 5)
}

function zoomOut() {
  scale.value = Math.max(scale.value - 0.25, 0.25)
}

function rotateLeft() {
  rotation.value -= 90
}

function rotateRight() {
  rotation.value += 90
}

function resetView() {
  scale.value = 1
  rotation.value = 0
}

function close() {
  visible.value = false
  emit('close')
}

function onLoad() {
  // image loaded
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
  if (e.key === '+' || e.key === '=') zoomIn()
  if (e.key === '-') zoomOut()
  if (e.key === 'ArrowLeft') rotateLeft()
  if (e.key === 'ArrowRight') rotateRight()
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
.image-preview-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 90vw;
  max-height: 90vh;
}

.preview-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  background: rgba(18, 18, 26, 0.8);
  padding: 6px 12px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.tool-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  text-decoration: none;
}

.tool-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  color: var(--neon-blue);
}

.close-btn:hover {
  background: rgba(236, 72, 153, 0.2);
  color: var(--neon-pink);
}

.image-wrapper {
  overflow: hidden;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 80vw;
  max-height: 75vh;
  object-fit: contain;
  border-radius: 8px;
}

.image-caption {
  margin-top: 12px;
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
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
