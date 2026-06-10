<template>
  <div v-if="visible" class="reasoning-block" :class="{ 'reasoning-block--expanded': isExpanded }">
    <!-- 折叠栏 -->
    <div class="reasoning-bar" @click="toggle">
      <span class="reasoning-bar-icon">🧠</span>
      <span class="reasoning-bar-label">{{ barLabel }}</span>
      <span v-if="isStreaming" class="reasoning-dots">
        <span class="dot" /><span class="dot" /><span class="dot" />
      </span>
      <span v-else :class="['reasoning-arrow', { 'reasoning-arrow--open': isExpanded }]">▾</span>
    </div>

    <!-- 推理内容 -->
    <div v-if="isExpanded || isStreaming" class="reasoning-content">
      {{ content }}<span v-if="isStreaming" class="reasoning-cursor">▊</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'

const props = defineProps<{
  content: string
  isStreaming: boolean
}>()

const isExpanded = ref(true)
const contentRef = ref<HTMLElement>()
const startTime = Date.now()
const elapsed = ref('0秒')

/** 流式态自动展开 */
watch(() => props.isStreaming, (streaming) => {
  if (streaming) {
    isExpanded.value = true
  }
})

/** 空态隐藏 */
const visible = computed(() => props.content.length > 0 || props.isStreaming)

/** 耗时计算 */
let timer: ReturnType<typeof setInterval> | null = null

function startTimer() {
  stopTimer()
  timer = setInterval(() => {
    const secs = Math.floor((Date.now() - startTime) / 1000)
    elapsed.value = secs < 60 ? `${secs}秒` : `${Math.floor(secs / 60)}分${secs % 60}秒`
  }, 1000)
}

function stopTimer() {
  if (timer !== null) {
    clearInterval(timer)
    timer = null
  }
}

watch(() => props.isStreaming, (streaming) => {
  if (streaming) startTimer()
  else stopTimer()
}, { immediate: true })

onUnmounted(stopTimer)

/** 折叠栏文案 */
const barLabel = computed(() => {
  if (props.isStreaming) return `深度思考 ${elapsed.value}...`
  if (props.content.length > 0) return `已深度思考（${elapsed.value}）`
  return '思考中...'
})

function toggle() {
  if (!props.isStreaming) {
    isExpanded.value = !isExpanded.value
  }
}

/** 流式时自动滚动到底部 */
watch(() => props.content, () => {
  if (props.isStreaming) {
    nextTick(() => {
      const el = document.querySelector('.reasoning-content')
      if (el) el.scrollTop = el.scrollHeight
    })
  }
})
</script>

<style scoped>
.reasoning-block {
  width: 100%;
  margin-bottom: 8px;
}

/* --- 折叠栏 --- */
.reasoning-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(180, 160, 140, 0.04);
  border: 1px solid rgba(180, 160, 140, 0.12);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.reasoning-bar:hover {
  background: rgba(180, 160, 140, 0.07);
  border-color: rgba(180, 160, 140, 0.2);
}

.reasoning-bar-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.reasoning-bar-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.reasoning-arrow {
  font-size: 12px;
  color: var(--text-muted);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.reasoning-arrow--open {
  transform: rotate(180deg);
}

/* --- 加载动画点 --- */
.reasoning-dots {
  display: flex;
  gap: 3px;
  flex-shrink: 0;
}

.reasoning-dots .dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  animation: reasoningPulse 1.4s infinite;
}

.reasoning-dots .dot:nth-child(2) { animation-delay: 0.2s; }
.reasoning-dots .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes reasoningPulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

/* --- 推理内容区 --- */
.reasoning-content {
  margin-top: 6px;
  padding: 12px 14px;
  background: rgba(180, 160, 140, 0.03);
  border: 1px solid rgba(180, 160, 140, 0.08);
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 400px;
  overflow-y: auto;
}

.reasoning-cursor {
  animation: blink 1s step-end infinite;
  color: var(--accent);
}

@keyframes blink {
  50% { opacity: 0; }
}
</style>
