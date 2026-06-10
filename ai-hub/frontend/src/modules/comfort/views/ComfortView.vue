<template>
  <div class="comfort-view">
    <!-- 顶部导航 -->
    <header class="comfort-header">
      <button class="back-btn" @click="goHome">← 返回</button>
      <div class="header-center">
        <span class="header-icon">🎭</span>
        <h2 class="header-title">哄哄模拟器</h2>
        <span v-if="comfortStore.selectedScene" class="header-scene-pill">
          {{ comfortStore.selectedScene.icon }} {{ comfortStore.selectedScene.name }}
        </span>
      </div>
      <div class="header-actions">
        <button
          v-if="comfortStore.conversationId"
          class="restart-btn"
          @click="restart"
        >重新开始</button>
        <button class="icon-btn" title="情绪仪表盘" @click="goDashboard">📊</button>
      </div>
    </header>

    <!-- 未开始：场景设置 -->
    <div v-if="!comfortStore.conversationId" class="setup-area">
      <div class="setup-hero">
        <span class="hero-emoji">💕</span>
        <h3 class="hero-title">学习如何安慰别人</h3>
        <p class="hero-desc">选择场景和角色，开始你的安慰之旅。AI 会模拟真实情绪反应，并实时分析你的安慰效果。</p>
      </div>
      <ComfortSetupModal @start="handleStart" />
    </div>

    <!-- 已开始：对话界面 -->
    <div v-else class="chat-area">
      <!-- 整合状态面板 -->
      <EmotionPanel
        :forgiveness="comfortStore.forgivenessValue"
        :forgiveness-data="comfortStore.currentForgiveness"
        :emotion="comfortStore.currentEmotion"
        :character="comfortStore.selectedCharacter"
      />

      <!-- comfort 专属消息列表 -->
      <ComfortMessageList />

      <!-- 输入区域 -->
      <div class="comfort-input-area">
        <div class="composer">
          <n-input
            v-model:value="inputText"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 6 }"
            :placeholder="inputPlaceholder"
            class="composer-input"
            @keydown="handleKeydown"
          />
          <n-button
            circle
            size="small"
            class="send-btn"
            :disabled="!canSend"
            :type="canSend ? 'primary' : 'default'"
            @click="send"
          >
            <template #icon>
              <span v-if="!comfortStore.isStreaming" class="send-icon">↑</span>
              <span v-else class="stop-icon">■</span>
            </template>
          </n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useComfortStore } from '@/modules/comfort/stores/comfort'
import { useSettingsStore } from '@/shared/stores/settings'
import { useSseStream } from '@/shared/composables/useSseStream'
import ComfortSetupModal from '@/modules/comfort/components/ComfortSetupModal.vue'
import EmotionPanel from '@/modules/comfort/components/EmotionPanel.vue'
import ComfortMessageList from '@/modules/comfort/components/ComfortMessageList.vue'

const router = useRouter()
const comfortStore = useComfortStore()
const settingsStore = useSettingsStore()
const { sendChat, abort } = useSseStream()

const inputText = ref('')
const canSend = computed(() => inputText.value.trim() && !comfortStore.isStreaming)

const inputPlaceholder = computed(() => {
  const name = comfortStore.selectedCharacter?.name
  return name ? `说点什么来安慰${name}吧... Enter 发送` : '说点什么来安慰对方... Enter 发送'
})

onMounted(async () => {
  await settingsStore.fetchModels()
  await comfortStore.fetchScenes()
})

onUnmounted(() => {
  // 离开页面不清理状态（保持对话）
})

function goHome() {
  router.push('/')
}

function goDashboard() {
  const params: Record<string, string> = {}
  if (comfortStore.conversationId) {
    params.convId = comfortStore.conversationId
  }
  router.push({ name: 'emotion-dashboard', query: params })
}

function restart() {
  if (comfortStore.conversationId) {
    abort(comfortStore.conversationId)
  }
  comfortStore.reset()
}

async function handleStart() {
  await comfortStore.startSession()
}

async function send() {
  if (!canSend.value || !comfortStore.conversationId) return

  const text = inputText.value.trim()
  comfortStore.addUserMessage(text)
  inputText.value = ''

  await sendChat(
    text,
    comfortStore.conversationId,
    settingsStore.currentModel.provider,
    settingsStore.currentModel.model,
    undefined,
    undefined,
    true, // comfort mode
  )
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}
</script>

<style scoped>
.comfort-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

/* 顶部导航 */
.comfort-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: var(--bg-card);
  border-bottom: 1px solid rgba(180, 150, 120, 0.08);
  box-shadow: 0 1px 4px rgba(60, 40, 20, 0.03);
  flex-shrink: 0;
}

.back-btn {
  background: none;
  border: none;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.15s;
}

.back-btn:hover {
  background: var(--hover-color);
}

.header-center {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 18px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-scene-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  background: var(--accent-bg);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  color: var(--accent);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.restart-btn {
  background: none;
  border: 1px solid rgba(180, 150, 120, 0.2);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 999px;
  transition: all 0.15s;
}

.restart-btn:hover {
  background: var(--hover-color);
  border-color: rgba(180, 150, 120, 0.35);
  color: var(--text-primary);
}

.icon-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.15s;
}

.icon-btn:hover {
  background: var(--hover-color);
}

/* 设置区域 */
.setup-area {
  flex: 1;
  overflow-y: auto;
  padding: 32px 24px;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
}

.setup-hero {
  text-align: center;
  padding: 28px 24px;
  margin-bottom: 28px;
  background: linear-gradient(
    135deg,
    rgba(198, 123, 92, 0.05),
    rgba(212, 165, 116, 0.05)
  );
  border: 1px solid rgba(180, 150, 120, 0.10);
  border-radius: 16px;
}

.hero-emoji {
  font-size: 56px;
  display: block;
  margin-bottom: 12px;
  animation: floatEmoji 3s ease-in-out infinite;
}

@keyframes floatEmoji {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.hero-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.hero-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* 对话区域 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* 输入区域 */
.comfort-input-area {
  padding: 0 20px 16px;
  flex-shrink: 0;
}

.composer {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: 8px;
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.15);
  border-radius: 20px;
  padding: 12px 16px;
  box-shadow: 0 2px 12px rgba(60, 40, 20, 0.06);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.composer:focus-within {
  border-color: rgba(198, 123, 92, 0.35);
  box-shadow: 0 2px 16px rgba(198, 123, 92, 0.08);
}

.composer-input {
  flex: 1;
  min-width: 0;
}

.composer-input :deep(.n-input__textarea) {
  padding: 0 !important;
}

.composer-input :deep(.n-input__border),
.composer-input :deep(.n-input__state-border) {
  display: none !important;
}

.composer-input :deep(.n-input__textarea-el) {
  font-size: 15px;
  line-height: 1.6;
  resize: none;
  padding-top: 6px !important;
  padding-bottom: 6px !important;
}

.composer-input :deep(.n-input__placeholder) span {
  padding-top: 6px !important;
  padding-bottom: 6px !important;
  line-height: 1.6;
}

.send-btn {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  margin-bottom: 6px;
  border: 1px solid rgba(180, 150, 120, 0.25) !important;
  transition: all 0.2s ease, transform 0.15s ease;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.08);
  box-shadow: 0 2px 8px rgba(198, 123, 92, 0.3);
}

.send-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.send-icon {
  font-size: 15px;
  font-weight: 700;
}

.stop-icon {
  font-size: 11px;
  font-weight: 700;
  color: var(--danger);
}

@media (max-width: 768px) {
  .setup-area {
    padding: 20px 16px;
  }

  .comfort-input-area {
    padding: 0 12px 12px;
  }

  .comfort-header {
    padding: 10px 14px;
  }

  .header-scene-pill {
    display: none;
  }
}
</style>
