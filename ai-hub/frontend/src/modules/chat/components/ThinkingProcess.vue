<template>
  <div class="thinking-process" :class="{ 'thinking-process--expanded': isExpanded }">
    <!-- 折叠栏 -->
    <div class="thinking-bar" @click="toggle">
      <span class="thinking-bar-icon">💭</span>
      <span class="thinking-bar-label">
        {{ isStreaming ? '正在思考...' : summaryText }}
      </span>
      <span v-if="!isStreaming && steps.length > 0" class="thinking-bar-count">
        {{ steps.length }} 步
      </span>
      <span v-if="isStreaming" class="thinking-dots">
        <span class="dot" /><span class="dot" /><span class="dot" />
      </span>
      <span v-else :class="['thinking-arrow', { 'thinking-arrow--open': isExpanded }]">▾</span>
    </div>

    <!-- 展开后的时间线内容 -->
    <div v-if="isExpanded && steps.length > 0" class="thinking-detail">
      <div class="timeline">
        <div v-for="(step, i) in steps" :key="i" class="timeline-item">
          <div class="timeline-dot" :class="`dot-${step.step}`" />
          <div v-if="i < steps.length - 1" class="timeline-line" />

          <div class="timeline-content" :class="`step-${step.step}`">
            <div class="step-header">
              <span class="step-label">{{ stepLabel(step.step) }}</span>
              <span class="step-time">{{ formatTime(step.timestamp) }}</span>
            </div>

            <div v-if="step.step === 'thought'" class="step-reasoning">
              {{ step.content }}
            </div>

            <div v-else-if="step.step === 'action'" class="step-action">
              {{ parseActionStep(step.content) }}
              <!-- 内联工具调用状态 -->
              <ToolCallStatus
                v-if="matchedToolCall(step.content)"
                :tool-call="matchedToolCall(step.content)!"
                :compact="true"
              />
            </div>

            <div v-else-if="step.step === 'observation'" class="step-observation">
              {{ step.content }}
            </div>
          </div>
        </div>

        <!-- 多工具进度条 -->
        <div v-if="progress && progress.total > 1" class="timeline-progress">
          <AgentProgressBar :progress="progress" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ThinkingStep, ToolCallStatus as ToolCallStatusType, ProgressInfo } from '@/modules/chat/types/chat'
import ToolCallStatus from '@/modules/chat/components/ToolCallStatus.vue'
import AgentProgressBar from '@/modules/chat/components/AgentProgressBar.vue'

const props = withDefaults(defineProps<{
  steps: ThinkingStep[]
  isStreaming?: boolean
  toolCalls?: ToolCallStatusType[]
  progress?: ProgressInfo | null
}>(), {
  isStreaming: false,
  toolCalls: () => [],
  progress: null,
})

const isExpanded = ref(false)

function toggle() {
  if (!props.isStreaming) {
    isExpanded.value = !isExpanded.value
  }
}

/** 折叠栏摘要：取第一条 thought 步骤的内容或耗时 */
const summaryText = computed(() => {
  if (props.steps.length === 0) return '思考中...'
  const thoughtStep = props.steps.find(s => s.step === 'thought')
  if (thoughtStep) {
    const text = thoughtStep.content
    return text.length > 60 ? text.slice(0, 60) + '...' : text
  }
  return `已思考 ${props.steps.length} 步`
})

function stepLabel(step: string): string {
  const map: Record<string, string> = {
    thought: '推理',
    action: '工具调用',
    observation: '观察',
  }
  return map[step] || step
}

/** 格式化时间戳为 mm:ss */
function formatTime(ts: number): string {
  const d = new Date(ts)
  const m = String(d.getMinutes()).padStart(2, '0')
  const s = String(d.getSeconds()).padStart(2, '0')
  return `${m}:${s}`
}

/** 解析 action 步骤，提取工具名 */
function parseActionStep(content: string): string {
  const match = content.match(/调用 (\w+)\(/)
  if (match) return match[1]
  return content
}

/** 根据 action 步骤内容匹配对应的工具调用状态 */
function matchedToolCall(content: string): ToolCallStatusType | undefined {
  const match = content.match(/调用 (\w+)\(/)
  if (!match || !props.toolCalls) return undefined
  return props.toolCalls.find(tc => tc.toolName === match[1])
}
</script>

<style scoped>
.thinking-process {
  width: 100%;
  margin-bottom: 8px;
}

/* --- 折叠栏 --- */
.thinking-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(198, 123, 92, 0.04);
  border: 1px solid rgba(198, 123, 92, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.thinking-bar:hover {
  background: rgba(198, 123, 92, 0.07);
  border-color: rgba(198, 123, 92, 0.18);
}

.thinking-bar-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.thinking-bar-label {
  font-size: 13px;
  color: var(--accent);
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.thinking-bar-count {
  font-size: 11px;
  color: var(--text-muted);
  padding: 1px 6px;
  background: rgba(180, 150, 120, 0.08);
  border-radius: 8px;
  flex-shrink: 0;
}

.thinking-arrow {
  font-size: 12px;
  color: var(--text-muted);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.thinking-arrow--open {
  transform: rotate(180deg);
}

/* --- 加载动画点 --- */
.thinking-dots {
  display: flex;
  gap: 3px;
  flex-shrink: 0;
}

.dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  animation: thinkingPulse 1.4s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes thinkingPulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

/* --- 时间线区域 --- */
.thinking-detail {
  margin-top: 6px;
  padding: 12px 16px;
  background: rgba(198, 123, 92, 0.03);
  border: 1px solid rgba(198, 123, 92, 0.08);
  border-radius: 10px;
}

.timeline {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0;
}

/* 每个时间线条目 */
.timeline-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  padding-bottom: 14px;
}

/* 时间线圆点 */
.timeline-dot {
  position: absolute;
  left: 0;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  z-index: 1;
  flex-shrink: 0;
}

.dot-thought {
  background: #c67b5c;
  border: 2px solid rgba(198, 123, 92, 0.25);
}

.dot-action {
  background: #5b8dd9;
  border: 2px solid rgba(91, 141, 217, 0.25);
}

.dot-observation {
  background: #10b981;
  border: 2px solid rgba(16, 185, 129, 0.25);
}

/* 时间线竖线（连接圆点） */
.timeline-line {
  position: absolute;
  left: 4px;
  top: 16px;
  width: 2px;
  height: calc(100% - 4px);
  background: rgba(180, 150, 120, 0.12);
}

/* 时间线内容区 */
.timeline-content {
  margin-left: 22px;
  flex: 1;
  min-width: 0;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.step-label {
  font-size: 11px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

.step-thought .step-label {
  background: rgba(198, 123, 92, 0.08);
  color: var(--accent);
}

.step-action .step-label {
  background: rgba(91, 141, 217, 0.1);
  color: #5b8dd9;
}

.step-observation .step-label {
  background: rgba(16, 185, 129, 0.08);
  color: #10b981;
}

.step-time {
  font-size: 10px;
  color: var(--text-muted);
}

.step-reasoning {
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-secondary);
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 300px;
  overflow-y: auto;
}

.step-action {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
  padding: 2px 0;
}

.step-observation {
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-muted);
  white-space: pre-wrap;
  word-break: break-word;
}

/* 进度条 */
.timeline-progress {
  margin-top: 4px;
  margin-left: 22px;
}
</style>
