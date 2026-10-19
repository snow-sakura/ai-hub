<template>
  <n-layout-content content-style="padding: 24px;">
    <n-space vertical :size="16" style="max-width: 1200px; margin: 0 auto;" v-if="seq">

      <!-- 页头 -->
      <n-page-header :title="seq.title" @back="$router.push('/ai-testing/generate/sequences')">
        <template #subtitle>
          <n-space align="center" :size="8">
            <n-tag :type="seq.model_tier === 'free' ? 'success' : 'warning'" size="small" round>
              {{ seq.model_tier === 'free' ? '🆓 免费模型' : '💎 付费模型' }}
            </n-tag>
            <n-tag :type="seq.strategy === 'parallel' ? 'info' : 'default'" size="small">
              {{ seq.strategy === 'parallel' ? `并行调度 ×${seq.max_parallel}` : '串行调度（单任务序列）' }}
            </n-tag>
            <n-tag :type="statusMeta(seq.status).type" size="small">
              {{ statusMeta(seq.status).label }}
            </n-tag>
            <n-text depth="3" style="font-size: 12px;">模型 {{ seq.model }}</n-text>
          </n-space>
        </template>
        <template #extra>
          <n-space>
            <n-popconfirm v-if="canCancel" @positive-click="cancel">
              <template #trigger><n-button size="small" type="warning" ghost>取消序列</n-button></template>
              取消后运行中的子任务将在当前阶段结束时停止？
            </n-popconfirm>
            <n-button v-if="canRetry" size="small" type="primary" ghost @click="retry">重跑失败子任务</n-button>
            <n-button size="small" tertiary @click="openTask(latestTaskId)" :disabled="!latestTaskId">
              查看最新用例
            </n-button>
          </n-space>
        </template>
      </n-page-header>

      <!-- 总进度 -->
      <n-card size="small">
        <n-space vertical :size="10">
          <n-space justify="space-between" align="center">
            <n-text depth="3" style="font-size: 13px;">
              完成 {{ seq.success_count }} · 失败 {{ seq.failed_count }} · 执行中 {{ seq.running_count }} · 共 {{ seq.total }}
            </n-text>
            <n-text depth="3" style="font-size: 12px;">
              {{ connected ? '🟢 实时连接' : '⚪ 轮询模式' }}
            </n-text>
          </n-space>
          <n-progress
            type="line" :percentage="percentage" :status="progressStatus"
            :height="12" :border-radius="6" :fill-border-radius="6" processing
          />
          <!-- 并行槽位指示（付费并行时展示泳道） -->
          <n-space v-if="seq.strategy === 'parallel'" :size="8" align="center">
            <n-text depth="3" style="font-size: 12px;">执行槽位：</n-text>
            <n-tag
              v-for="slot in slotList" :key="slot.index"
              :type="slot.busy ? 'info' : 'default'" size="small" :bordered="!slot.busy"
            >
              槽 {{ slot.index + 1 }}<template v-if="slot.busy"> ▶ #{{ slot.seqIndex }}</template>
            </n-tag>
          </n-space>
        </n-space>
      </n-card>

      <!-- 错误信息 -->
      <n-alert v-if="seq.error_message" type="error" :bordered="false" title="序列错误">
        {{ seq.error_message }}
      </n-alert>

      <!-- ▸ 子任务卡片：严格按 seq_index 排序循环渲染 -->
      <n-card size="small" :bordered="false" title="子任务序列（按序执行）">
        <n-empty v-if="!subtasks.length" description="暂无子任务" />
        <n-space v-else vertical :size="12">
          <div
            v-for="task in subtasks" :key="task.id"
            class="subtask-card" :class="{ 'is-running': task.status === 'running' }"
          >
            <n-space align="center" justify="space-between">
              <n-space align="center" :size="10">
                <n-tag :type="task.status === 'completed' ? 'success' : task.status === 'running' ? 'info' : task.status === 'pending' ? 'default' : 'error'" size="small" round>
                  #{{ task.seq_index + 1 }}
                </n-tag>
                <n-text strong>{{ task.seq_title || `子任务 ${task.seq_index + 1}` }}</n-text>
                <n-tag :type="statusMeta(task.status).type" size="tiny">{{ statusMeta(task.status).label }}</n-tag>
                <n-tag v-if="task.slot !== null && task.slot !== undefined && task.status === 'running' && seq.strategy === 'parallel'" size="tiny" type="info">
                  槽位 {{ task.slot + 1 }}
                </n-tag>
                <n-tag v-if="task.generated_count > 0" size="tiny" type="success">{{ task.generated_count }} 条用例</n-tag>
              </n-space>
              <n-button text size="tiny" type="primary" @click="openTask(task.id)">详情</n-button>
            </n-space>

            <!-- 步骤条：卡片内部按 4 步工作流循环节流推进 -->
            <n-steps
              size="small" :current="stepIndex(task)" :status="stepStatus(task)"
              style="margin-top: 10px;"
            >
              <n-step v-for="s in SEQ_STAGES" :key="s.key" :title="s.label" />
            </n-steps>

            <n-text v-if="task.error_message" depth="3" style="font-size: 12px; color: #d03050;">
              {{ task.error_message }}
            </n-text>
          </div>
        </n-space>
      </n-card>
    </n-space>

    <n-spin v-else :show="true" style="margin: 80px auto; display: block;" />
  </n-layout-content>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  cancelGenerationSequence,
  getGenerationSequence,
  retryFailedSequence,
} from '@/modules/ai_testing/api/generation'
import {
  SEQ_STAGES,
  SEQ_STATUS_META,
  type GenerationSequence,
  type SequenceSubtask,
  type SequenceSubtaskEvent,
  type SequenceProgressEvent,
} from '@/modules/ai_testing/types/sequence'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const seqId = String(route.params.id)
const seq = ref<GenerationSequence | null>(null)
const subtasks = ref<SequenceSubtask[]>([])
const connected = ref(false)

let eventSource: EventSource | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null

const TERMINAL = ['completed', 'partial_failed', 'cancelled', 'interrupted']

const canCancel = computed(() =>
  seq.value ? ['running', 'pending'].includes(seq.value.status) : false)
const canRetry = computed(() =>
  seq.value ? (seq.value.failed_count > 0 || seq.value.status === 'cancelled' || seq.value.status === 'interrupted') : false)

const percentage = computed(() => {
  const s = seq.value
  if (!s || !s.total) return 0
  return Math.round(((s.success_count + s.failed_count + s.running_count) / s.total) * 100)
})

const progressStatus = computed((): 'default' | 'success' | 'error' | 'warning' | 'info' => {
  const st = seq.value?.status
  if (st === 'completed') return 'success'
  if (st === 'partial_failed' || st === 'cancelled' || st === 'interrupted') return 'warning'
  if (st === 'running') return 'info'
  return 'default'
})

/** 并行槽位泳道：来自运行中子任务的 slot 事件 */
const slotList = computed(() => {
  const max = seq.value?.max_parallel || 1
  const slots = Array.from({ length: max }, (_, i) => ({ index: i, busy: false, seqIndex: -1 }))
  for (const t of subtasks.value) {
    if (t.status === 'running' && t.slot !== null && t.slot !== undefined && t.slot < max) {
      slots[t.slot].busy = true
      slots[t.slot].seqIndex = t.seq_index
    }
  }
  return slots
})

const latestTaskId = computed(() => {
  const done = subtasks.value.filter(t => t.status === 'completed')
  return done.length ? done[done.length - 1].id : (subtasks.value[0]?.id || '')
})

function statusMeta(status: string) {
  return SEQ_STATUS_META[status] || { label: status, type: 'default' as const }
}

/** 卡片步骤条：analyze→write→review→revise 循环推进 */
function stepIndex(task: SequenceSubtask): number {
  if (task.status === 'completed') return SEQ_STAGES.length + 1
  if (task.status === 'pending') return 0
  const idx = SEQ_STAGES.findIndex(s => s.key === task.seq_stage)
  return idx >= 0 ? idx + 1 : 1
}

function stepStatus(task: SequenceSubtask): 'process' | 'finish' | 'error' | 'wait' {
  if (task.status === 'completed') return 'finish'
  if (task.status === 'failed') return 'error'
  if (task.status === 'running') return 'process'
  return 'wait'
}

function openTask(taskId: string) {
  if (taskId) router.push(`/ai-testing/generate/tasks/${taskId}`)
}

async function loadDetail() {
  try {
    const res = await getGenerationSequence(seqId)
    seq.value = res.data
    // 严格按 seq_index 排序 — 循环按序列渲染
    subtasks.value = [...(res.data.subtasks || [])].sort((a, b) => a.seq_index - b.seq_index)
  } catch {
    message.error('加载序列详情失败')
  }
}

function applySubtaskEvent(ev: SequenceSubtaskEvent) {
  const t = subtasks.value.find(x => x.id === ev.task_id)
  if (!t) return
  t.status = ev.status
  if (ev.stage !== undefined) t.seq_stage = ev.stage
  if (ev.generated_count !== undefined) t.generated_count = ev.generated_count
  if (ev.slot !== undefined) t.slot = ev.slot
}

function applyProgress(ev: SequenceProgressEvent) {
  if (!seq.value) return
  const s = seq.value
  s.total = ev.total ?? s.total
  s.success_count = ev.success_count ?? s.success_count
  s.failed_count = ev.failed_count ?? s.failed_count
  s.running_count = ev.running_count ?? s.running_count
  if (ev.status) s.status = ev.status
  if (ev.strategy === 'parallel' || ev.strategy === 'sequential') s.strategy = ev.strategy
  if (ev.tier === 'free' || ev.tier === 'paid') s.model_tier = ev.tier
  if (ev.max_parallel) s.max_parallel = ev.max_parallel
}

function connectSse() {
  const url = `/api/v1/testing/sequences/${seqId}/stream`
  eventSource = new EventSource(url)

  eventSource.addEventListener('sequence_subtask', (e: MessageEvent) => {
    applySubtaskEvent(JSON.parse(e.data) as SequenceSubtaskEvent)
  })
  eventSource.addEventListener('sequence_progress', (e: MessageEvent) => {
    applyProgress(JSON.parse(e.data) as SequenceProgressEvent)
  })
  eventSource.addEventListener('sequence_done', async (e: MessageEvent) => {
    applyProgress(JSON.parse(e.data) as SequenceProgressEvent)
    await loadDetail()
    connected.value = false
    eventSource?.close()
    eventSource = null
  })
  eventSource.onopen = () => { connected.value = true }
  eventSource.onerror = () => {
    connected.value = false
    // EventSource 自动重连；期间由轮询兜底
  }
}

function startPolling() {
  pollTimer = setInterval(() => {
    if (seq.value && !TERMINAL.includes(seq.value.status)) loadDetail()
  }, 6000)
}

async function cancel() {
  try {
    await cancelGenerationSequence(seqId)
    message.success('取消指令已下达')
    loadDetail()
  } catch {
    message.error('取消失败')
  }
}

async function retry() {
  try {
    const res = await retryFailedSequence(seqId)
    if (res.data.retried > 0) message.success(`已重新调度 ${res.data.retried} 个子任务`)
    else message.info(res.data.message || '没有可重跑的子任务')
    await loadDetail()
    if (!eventSource && seq.value && !TERMINAL.includes(seq.value.status)) connectSse()
  } catch {
    message.error('重跑失败')
  }
}

onMounted(async () => {
  await loadDetail()
  if (seq.value && !TERMINAL.includes(seq.value.status)) connectSse()
  startPolling()
})

onBeforeUnmount(() => {
  eventSource?.close()
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.subtask-card {
  padding: 14px 16px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  transition: box-shadow 0.25s, border-color 0.25s;
}
.subtask-card.is-running {
  border-color: rgba(32, 128, 240, 0.55);
  box-shadow: 0 0 0 2px rgba(32, 128, 240, 0.12);
  animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 2px rgba(32, 128, 240, 0.10); }
  50% { box-shadow: 0 0 0 4px rgba(32, 128, 240, 0.22); }
}
</style>
