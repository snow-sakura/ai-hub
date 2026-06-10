<template>
  <div class="dashboard-view">
    <header class="dash-header">
      <button class="back-btn" @click="router.push('/comfort')">← 返回</button>
      <h2>📊 情绪仪表盘</h2>
      <div class="date-range">
        <n-date-picker v-model:value="startDate" type="date" size="small" clearable />
        <span class="date-sep">至</span>
        <n-date-picker v-model:value="endDate" type="date" size="small" clearable />
      </div>
    </header>

    <div class="dash-content">
      <!-- 加载错误 -->
      <n-result v-if="fetchError" status="error" title="加载失败" :description="fetchError" />

      <!-- 加载中 -->
      <n-spin v-else-if="isLoading" style="margin: 48px auto" />

      <!-- 情绪分布 -->
      <div class="dash-card">
        <h3 class="card-title">情绪分布</h3>
        <div v-if="emotionCounts.length" class="emotion-chart">
          <div
            v-for="item in emotionCounts"
            :key="item.label"
            class="emotion-bar-row"
          >
            <span class="emotion-label">{{ item.emoji }} {{ emotionNames[item.label] }}</span>
            <div class="emotion-bar-track">
              <div
                class="emotion-bar-fill"
                :style="{ width: `${item.percent}%`, background: emotionColors[item.label] }"
              />
            </div>
            <span class="emotion-count">{{ item.count }} 次</span>
          </div>
        </div>
        <div v-else class="empty-state">暂无情绪数据，开始一段哄哄对话后这里会显示统计</div>
      </div>

      <!-- 原谅值趋势 -->
      <div class="dash-card">
        <h3 class="card-title">原谅值趋势</h3>
        <div v-if="forgivenessHistory.length" class="forgiveness-chart">
          <div class="chart-bars">
            <div
              v-for="(item, i) in forgivenessHistory"
              :key="i"
              class="chart-bar-wrap"
            >
              <div
                class="chart-bar"
                :style="{ height: `${item.score}%`, background: barColor(item.score) }"
                :title="`${item.date}: ${item.score}`"
              />
              <span class="bar-date">{{ formatDate(item.date) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">暂无数据</div>
      </div>

      <!-- 哄人能力雷达（简化版） -->
      <div class="dash-card">
        <h3 class="card-title">哄人能力分析</h3>
        <div class="ability-grid">
          <div v-for="ability in abilities" :key="ability.name" class="ability-item">
            <span class="ability-name">{{ ability.name }}</span>
            <div class="ability-bar-track">
              <div
                class="ability-bar-fill"
                :style="{ width: `${ability.score}%` }"
              />
            </div>
            <span class="ability-score">{{ ability.score }}%</span>
          </div>
        </div>
      </div>

      <!-- 记忆管理 -->
      <div v-if="comfortStore.conversationId" class="dash-card">
        <h3 class="card-title">记忆管理</h3>
        <MemoryManager :conversation-id="comfortStore.conversationId" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useComfortStore } from '@/modules/comfort/stores/comfort'
import { getEmotionStats } from '@/modules/comfort/api/comfort'
import MemoryManager from '@/modules/comfort/components/MemoryManager.vue'
import type { EmotionStat } from '@/modules/comfort/types/comfort'

const router = useRouter()
const route = useRoute()
const comfortStore = useComfortStore()

const startDate = ref<number>(Date.now() - 7 * 86400000)
const endDate = ref<number>(Date.now())

const stats = ref<EmotionStat[]>([])
const fetchError = ref<string | null>(null)
const isLoading = ref(false)

const emotionNames: Record<string, string> = {
  anger: '愤怒', sadness: '悲伤', anxiety: '焦虑',
  fatigue: '疲惫', calm: '平静', joy: '喜悦', fear: '恐惧',
}

const emotionColors: Record<string, string> = {
  anger: '#D4745C', sadness: '#7B9FD4', anxiety: '#D4A574',
  fatigue: '#B5A590', calm: '#7BA87D', joy: '#D4A574', fear: '#9B8EC4',
}

async function fetchStats() {
  if (!startDate.value || !endDate.value) return
  const start = new Date(startDate.value).toISOString().split('T')[0]
  const end = new Date(endDate.value).toISOString().split('T')[0]
  isLoading.value = true
  fetchError.value = null
  try {
    const res = await getEmotionStats(start, end)
    stats.value = res.data || []
  } catch (e) {
    fetchError.value = '获取统计数据失败，请稍后重试'
    console.error('获取情绪统计失败:', e)
  } finally {
    isLoading.value = false
  }
}

watch([startDate, endDate], fetchStats)
onMounted(async () => {
  const convId = route.query.convId as string | undefined
  if (convId) {
    await comfortStore.loadSessionInfo(convId)
  }
  await fetchStats()
})

/** 情绪分布聚合 */
const emotionCounts = computed(() => {
  const map: Record<string, { count: number; totalIntensity: number }> = {}
  for (const s of stats.value) {
    if (!map[s.emotion_label]) map[s.emotion_label] = { count: 0, totalIntensity: 0 }
    map[s.emotion_label].count += s.count
    map[s.emotion_label].totalIntensity += s.avg_intensity * s.count
  }
  const total = Object.values(map).reduce((sum, v) => sum + v.count, 0)
  if (!total) return []
  return Object.entries(map)
    .map(([label, v]) => ({
      label,
      count: v.count,
      emoji: emotionEmoji[label] || '😐',
      percent: Math.round((v.count / total) * 100),
    }))
    .sort((a, b) => b.count - a.count)
})

const emotionEmoji: Record<string, string> = {
  anger: '😡', sadness: '😢', anxiety: '😰',
  fatigue: '😩', calm: '😌', joy: '😊', fear: '😨',
}

/** 原谅值趋势（按日期聚合） */
const forgivenessHistory = computed(() => {
  const dateMap: Record<string, number[]> = {}
  for (const s of stats.value) {
    if (s.comfort_score != null) {
      if (!dateMap[s.user_date]) dateMap[s.user_date] = []
      dateMap[s.user_date].push(s.comfort_score)
    }
  }
  return Object.entries(dateMap)
    .map(([date, scores]) => ({
      date,
      score: Math.round(scores.reduce((a, b) => a + b, 0) / scores.length),
    }))
    .sort((a, b) => a.date.localeCompare(b.date))
})

/** 哄人能力分析（基于历史数据简化计算） */
const abilities = computed(() => {
  const total = stats.value.reduce((sum, s) => sum + s.count, 0)
  const calmCount = stats.value.filter(s => s.emotion_label === 'calm' || s.emotion_label === 'joy')
    .reduce((sum, s) => sum + s.count, 0)
  const avgComfort = forgivenessHistory.value.length
    ? forgivenessHistory.value[forgivenessHistory.value.length - 1].score
    : 50

  return [
    { name: '共情能力', score: Math.min(100, Math.round((calmCount / Math.max(total, 1)) * 100)) },
    { name: '安抚技巧', score: Math.min(100, avgComfort) },
    { name: '耐心程度', score: Math.min(100, Math.round(total * 2)) },
    { name: '话术丰富度', score: Math.min(100, Math.round(stats.value.length * 5)) },
    { name: '情绪感知', score: Math.min(100, Math.round(70 + total * 0.5)) },
  ]
})

function barColor(score: number): string {
  if (score >= 70) return '#7BA87D'
  if (score >= 40) return '#D4A574'
  return '#D4745C'
}

function formatDate(date: string): string {
  return date.slice(5) // MM-DD
}
</script>

<style scoped>
.dashboard-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.dash-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: var(--bg-card);
  border-bottom: 1px solid rgba(180, 150, 120, 0.1);
  flex-shrink: 0;
}

.dash-header h2 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  flex: 1;
}

.back-btn {
  background: none;
  border: none;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
}

.back-btn:hover { background: var(--hover-color); }

.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-sep {
  font-size: 13px;
  color: var(--text-muted);
}

.dash-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dash-card {
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 12px;
  padding: 20px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px;
}

/* 情绪分布图表 */
.emotion-bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.emotion-label {
  font-size: 15px;
  font-weight: 500;
  width: 90px;
  flex-shrink: 0;
  color: var(--text-primary);
}

.emotion-bar-track {
  flex: 1;
  height: 26px;
  background: rgba(180, 150, 120, 0.08);
  border-radius: 6px;
  overflow: hidden;
}

.emotion-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.emotion-count {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  width: 56px;
  text-align: right;
  flex-shrink: 0;
}

/* 原谅值趋势 */
.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 160px;
  padding-top: 8px;
}

.chart-bar-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
  justify-content: flex-end;
}

.chart-bar {
  width: 100%;
  max-width: 40px;
  min-height: 4px;
  border-radius: 4px 4px 0 0;
  transition: height 0.5s ease;
}

.bar-date {
  font-size: 10px;
  color: var(--text-muted);
}

/* 能力分析 */
.ability-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ability-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ability-name {
  font-size: 13px;
  width: 80px;
  flex-shrink: 0;
  color: var(--text-secondary);
}

.ability-bar-track {
  flex: 1;
  height: 18px;
  background: rgba(180, 150, 120, 0.08);
  border-radius: 9px;
  overflow: hidden;
}

.ability-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #C67B5C, #D4A574);
  border-radius: 6px;
  transition: width 0.5s ease;
}

.ability-score {
  font-size: 12px;
  color: var(--text-muted);
  width: 36px;
  text-align: right;
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
  font-size: 13px;
}
</style>
