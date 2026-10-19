<template>
  <n-layout-content content-style="padding: 24px;">
    <n-space vertical :size="16" style="max-width: 1080px; margin: 0 auto;">

      <n-page-header title="序列生成" subtitle="需求自动拆分为子任务序列 — 免费模型串行执行，付费模型并行执行">
        <template #extra>
          <n-button tertiary size="small" @click="load">刷新</n-button>
        </template>
      </n-page-header>

      <!-- 策略说明 -->
      <n-alert :bordered="false" type="info">
        <template #header>调度策略</template>
        <n-space :size="20" inline>
          <n-text>🆓 <b>免费模型</b> → 单任务序列（并发 1，严格按序逐个执行）</n-text>
          <n-text>💎 <b>付费模型</b> → 并行序列（最多 {{ maxPaid }} 个子任务同时执行）</n-text>
        </n-space>
      </n-alert>

      <!-- 创建序列 -->
      <n-card size="small" title="➕ 新建生成序列" :collapsed="!!sequences.length" :collapsible="true">
        <n-form label-placement="top">
          <n-grid :cols="3" :x-gap="16">
            <n-gi>
              <n-form-item label="序列名称">
                <n-input v-model:value="form.title" placeholder="如：登录与订单模块用例序列" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="所属项目（可选）">
                <n-select v-model:value="form.project_id" :options="projectOptions" clearable placeholder="不关联项目" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="子任务数（可选，默认按章节自动拆分）">
                <n-input-number v-model:value="form.subtask_count" :min="1" :max="20" clearable style="width: 100%;" />
              </n-form-item>
            </n-gi>
          </n-grid>

          <n-form-item label="AI 模型（决定调度策略）">
            <n-space align="center" :size="12" style="width: 100%;">
              <n-select
                v-model:value="form.model"
                :options="modelOptions"
                filterable
                style="width: 320px;"
                placeholder="选择模型"
              />
              <n-tag v-if="selectedTier" :type="selectedTier === 'free' ? 'success' : 'warning'" size="small" round>
                {{ selectedTier === 'free' ? '免费 · 串行（单任务）' : `付费 · 并行（≤${maxPaid} 任务）` }}
              </n-tag>
              <n-text v-if="selectedHint" depth="3" style="font-size: 12px;">{{ selectedHint }}</n-text>
            </n-space>
          </n-form-item>

          <n-form-item label="需求全文（Markdown 标题 #/## 将自动拆分为子任务）">
            <n-input
              v-model:value="form.requirement_text"
              type="textarea"
              :autosize="{ minRows: 6, maxRows: 16 }"
              placeholder="## 模块A&#10;……&#10;## 模块B&#10;……"
            />
          </n-form-item>

          <n-space>
            <n-button type="primary" :loading="creating" :disabled="!canCreate" @click="create">
              🚀 创建并开始调度
            </n-button>
            <n-button :disabled="creating" @click="loadDemoText">填入示例需求</n-button>
          </n-space>
        </n-form>
      </n-card>

      <!-- 序列列表 -->
      <n-card size="small" title="序列列表" :bordered="false">
        <n-empty v-if="!loading && sequences.length === 0" description="还没有序列，创建第一个吧" />
        <n-list v-else bordered>
          <n-list-item v-for="seq in sequences" :key="seq.id" class="seq-row" @click="goDetail(seq.id)">
            <n-space vertical :size="6" style="width: 100%;">
              <n-space align="center" justify="space-between" style="width: 100%;">
                <n-space align="center" :size="8">
                  <n-text strong style="font-size: 15px;">{{ seq.title }}</n-text>
                  <n-tag :type="seq.model_tier === 'free' ? 'success' : 'warning'" size="tiny" round>
                    {{ seq.model_tier === 'free' ? '免费' : '付费' }}
                  </n-tag>
                  <n-tag :type="seq.strategy === 'parallel' ? 'info' : 'default'" size="tiny">
                    {{ seq.strategy === 'parallel' ? `并行 ×${seq.max_parallel}` : '串行 ×1' }}
                  </n-tag>
                  <n-tag :type="statusMeta(seq.status).type" size="tiny">{{ statusMeta(seq.status).label }}</n-tag>
                </n-space>
                <n-space align="center" :size="8">
                  <n-text depth="3" style="font-size: 12px;">{{ formatTime(seq.created_at) }}</n-text>
                  <n-popconfirm @positive-click="remove(seq.id)">
                    <template #trigger>
                      <n-button size="tiny" quaternary type="error" @click.stop>删除</n-button>
                    </template>
                    删除序列及其子任务？
                  </n-popconfirm>
                </n-space>
              </n-space>
              <n-progress
                type="line"
                :percentage="percentage(seq)"
                :status="progressStatus(seq)"
                :height="8"
                :border-radius="4"
                :fill-border-radius="4"
              >
                <n-text depth="3" style="font-size: 12px;">
                  {{ seq.success_count + seq.failed_count }}/{{ seq.total }}
                  <template v-if="seq.running_count">（执行中 {{ seq.running_count }}）</template>
                  <template v-if="seq.failed_count">· 失败 {{ seq.failed_count }}</template>
                </n-text>
              </n-progress>
              <n-text depth="3" style="font-size: 12px;">模型：{{ seq.model }}</n-text>
            </n-space>
          </n-list-item>
        </n-list>
      </n-card>
    </n-space>
  </n-layout-content>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useGenerationStore } from '@/modules/ai_testing/stores/generation'
import { useProjectStore } from '@/modules/ai_testing/stores/project'
import {
  createGenerationSequence,
  deleteGenerationSequence,
  listGenerationSequences,
} from '@/modules/ai_testing/api/generation'
import {
  SEQ_STATUS_META,
  type GenerationSequence,
} from '@/modules/ai_testing/types/sequence'

const router = useRouter()
const message = useMessage()
const store = useGenerationStore()
const projectStore = useProjectStore()

const sequences = ref<GenerationSequence[]>([])
const loading = ref(false)
const creating = ref(false)
let pollTimer: ReturnType<typeof setInterval> | null = null

const form = reactive({
  title: '',
  project_id: null as string | null,
  model: '',
  requirement_text: '',
  subtask_count: null as number | null,
})

const maxPaid = computed(() => {
  const hints = store.configDefaults?.models
    ?.filter(m => m.tier === 'paid' && m.sequence_hint)
    .map(m => m.sequence_hint as string) || []
  const match = hints[0]?.match(/(\d+)/)
  return match ? Number(match[1]) : 3
})

const projectOptions = computed(() =>
  projectStore.projects.map(p => ({ label: p.name, value: p.id })),
)

const modelOptions = computed(() => {
  const models = store.configDefaults?.models || []
  const groups: Record<string, Array<{ label: string; value: string }>> = {}
  for (const m of models) {
    const key = m.provider
    if (!groups[key]) groups[key] = []
    const badge = m.tier === 'free' ? ' · 免费' : ' · 付费'
    groups[key].push({ label: m.display_name + badge, value: `${m.provider}:${m.model}` })
  }
  return Object.entries(groups).map(([provider, children]) => ({
    type: 'group', label: provider, children,
  }))
})

const selectedModelInfo = computed(() =>
  (store.configDefaults?.models || [])
    .find(m => `${m.provider}:${m.model}` === form.model),
)
const selectedTier = computed(() => selectedModelInfo.value?.tier || '')
const selectedHint = computed(() => selectedModelInfo.value?.sequence_hint || '')

const canCreate = computed(() =>
  Boolean(form.model && form.requirement_text.trim().length >= 10 && !creating.value),
)

function statusMeta(status: string) {
  return SEQ_STATUS_META[status] || { label: status, type: 'default' as const }
}

function percentage(seq: GenerationSequence) {
  if (!seq.total) return 0
  return Math.round(((seq.success_count + seq.failed_count) / seq.total) * 100)
}

function progressStatus(seq: GenerationSequence): 'default' | 'success' | 'error' | 'warning' | 'info' {
  if (seq.status === 'completed') return 'success'
  if (seq.status === 'partial_failed' || seq.status === 'cancelled' || seq.status === 'interrupted') return 'warning'
  if (seq.status === 'running') return 'info'
  return 'default'
}

function formatTime(t: string | null) {
  if (!t) return ''
  return String(t).replace('T', ' ').slice(0, 16)
}

function goDetail(id: string) {
  router.push(`/ai-testing/generate/sequences/${id}`)
}

async function load() {
  loading.value = true
  try {
    const res = await listGenerationSequences({ page: 1, page_size: 50 })
    sequences.value = res.data.items
  } catch {
    message.error('加载序列列表失败')
  } finally {
    loading.value = false
  }
}

async function create() {
  creating.value = true
  try {
    const res = await createGenerationSequence({ ...form })
    message.success(`序列已创建：${res.data.total} 个子任务（${res.data.strategy === 'parallel' ? '并行' : '串行'}）`)
    router.push(`/ai-testing/generate/sequences/${res.data.id}`)
  } catch (e: unknown) {
    const err = e as { message?: string }
    message.error(err?.message || '创建序列失败')
  } finally {
    creating.value = false
  }
}

async function remove(id: string) {
  try {
    await deleteGenerationSequence(id)
    message.success('已删除')
    load()
  } catch {
    message.error('删除失败')
  }
}

function loadDemoText() {
  form.title = '电商核心模块用例序列（演示）'
  if (!form.model) form.model = 'mock:mock-pro'
  form.requirement_text = [
    '## 用户注册与登录',
    '支持手机号+密码注册，密码强度校验；手机号+验证码登录，验证码 60 秒过期；连续 5 次登录失败锁定账号 10 分钟。',
    '',
    '## 商品与库存',
    '商品上架/下架，库存扣减采用预扣+确认两阶段，超卖必须拦截；商品价格变更不影响已生成订单。',
    '',
    '## 订单与支付',
    '创建订单锁定库存，30 分钟未支付自动取消并回滚库存；支持支付宝/微信支付，回调需幂等；部分退款按比例分摊优惠券。',
    '',
    '## 物流与售后',
    '对接第三方物流查询接口，签收状态自动同步；7 天无理由退货，退货入库后库存回补并触发退款。',
  ].join('\n')
}

onMounted(async () => {
  await Promise.all([
    store.configDefaults ? Promise.resolve() : store.fetchConfigDefaults(),
    projectStore.projects.length ? Promise.resolve() : projectStore.fetchProjects(),
    load(),
  ])
  if (!form.model) {
    const paid = store.configDefaults?.models?.find(m => m.tier === 'paid')
    form.model = paid ? `${paid.provider}:${paid.model}` : ''
  }
  // 有运行中的序列时轮询列表
  pollTimer = setInterval(() => {
    if (sequences.value.some(s => s.status === 'running' || s.status === 'pending')) load()
  }, 5000)
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.seq-row {
  cursor: pointer;
  transition: background 0.2s;
}
.seq-row:hover {
  background: rgba(198, 123, 92, 0.06);
}
</style>
