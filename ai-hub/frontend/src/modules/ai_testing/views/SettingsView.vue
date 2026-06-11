<template>
  <n-layout-content content-style="padding: 24px;">
    <n-space vertical :size="20" style="max-width: 1000px; margin: 0 auto;">

      <!-- 页头 -->
      <n-page-header title="⚙️ 配置管理" @back="$router.back()">
        <template #subtitle>
          <n-text depth="3">管理 AI 模型、提示词模板和生成行为参数</n-text>
        </template>
        <template #extra>
          <n-button size="small" quaternary @click="handleRefresh">
            刷新状态
          </n-button>
        </template>
      </n-page-header>

      <!-- 配置状态概览 -->
      <n-card title="配置状态" size="small">
        <n-space v-if="configStatus" :size="12" wrap>
          <n-tag
            v-for="item in configStatus.items"
            :key="item.key"
            :type="item.status === 'ok' ? 'success' : 'warning'"
            size="medium"
            round
          >
            {{ item.label }}: {{ item.status === 'ok' ? '✅ 已配置' : '⚠️ 未配置' }}
          </n-tag>
        </n-space>
        <n-empty v-else description="正在检查配置..." />
      </n-card>

      <!-- 配置分类卡片网格 -->
      <div class="config-grid">
        <n-card
          v-for="card in configCards"
          :key="card.path"
          class="config-card"
          size="medium"
          hoverable
          @click="navigateTo(card.path)"
        >
          <div class="card-icon">{{ card.icon }}</div>
          <div class="card-title">{{ card.title }}</div>
          <div class="card-desc">{{ card.desc }}</div>
          <div class="card-extra">
            <n-tag
              :type="card.status === 'all_ok' ? 'success' : card.status === 'partial' ? 'warning' : 'default'"
              size="small"
            >
              {{ card.statusLabel }}
            </n-tag>
          </div>
        </n-card>
      </div>

    </n-space>
  </n-layout-content>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { checkConfig } from '@/modules/ai_testing/api/generation'
import type { ConfigCheckResponse } from '@/modules/ai_testing/types/generation'

const router = useRouter()
const message = useMessage()

const configStatus = ref<ConfigCheckResponse | null>(null)

const configCards = computed(() => [
  {
    icon: '🤖',
    title: 'AI 模型配置',
    desc: '管理 AI 提供商、模型选择、API Key 等',
    path: '/ai-testing/config/model',
    status: getCategoryStatus('model'),
    statusLabel: getCategoryStatusLabel('model'),
  },
  {
    icon: '📝',
    title: '提示词模板',
    desc: '自定义分析、编写、评审、修订各阶段提示词',
    path: '/ai-testing/config/prompt',
    status: getCategoryStatus('prompt'),
    statusLabel: getCategoryStatusLabel('prompt'),
  },
  {
    icon: '🎛️',
    title: '生成行为',
    desc: '输出模式、最大用例数、评审阈值、超时设置',
    path: '/ai-testing/config/generation',
    status: getCategoryStatus('behavior'),
    statusLabel: getCategoryStatusLabel('behavior'),
  },
  {
    icon: '📋',
    title: '项目与用例',
    desc: '管理测试项目、版本、成员和测试用例',
    path: '/ai-testing/projects',
    status: 'all_ok',
    statusLabel: '可访问',
  },
])

function getCategoryStatus(category: string): 'all_ok' | 'partial' | 'unknown' {
  if (!configStatus.value) return 'unknown'
  const items = configStatus.value.items.filter(i => i.category === category)
  if (items.length === 0) return 'unknown'
  return items.every(i => i.status === 'ok') ? 'all_ok' : 'partial'
}

function getCategoryStatusLabel(category: string): string {
  const status = getCategoryStatus(category)
  if (status === 'all_ok') return '全部就绪'
  if (status === 'partial') return '部分未配置'
  return '待检查'
}

function navigateTo(path: string) {
  router.push(path)
}

async function loadStatus() {
  try {
    const res = await checkConfig()
    configStatus.value = res.data || null
  } catch {
    configStatus.value = null
  }
}

function handleRefresh() {
  message.info('正在刷新配置状态...')
  loadStatus()
}

onMounted(() => loadStatus())
</script>

<style scoped>
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.config-card {
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.config-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-icon {
  font-size: 32px;
  margin-bottom: 8px;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #5C4A38;
  margin-bottom: 4px;
}
.card-desc {
  font-size: 13px;
  color: #7A6855;
  line-height: 1.5;
  margin-bottom: 12px;
}
.card-extra {
  display: flex;
  justify-content: flex-end;
}
</style>
