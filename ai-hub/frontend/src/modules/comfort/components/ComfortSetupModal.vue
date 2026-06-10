<template>
  <div class="setup-modal">
    <!-- 步骤 1：选择场景 -->
    <div class="step">
      <h3 class="step-title">
        <span class="step-number">1</span>
        选择场景
      </h3>
      <div class="scene-grid">
        <div
          v-for="scene in scenes"
          :key="scene.id"
          class="scene-card"
          :class="{ selected: selectedScene?.id === scene.id }"
          @click="onSelectScene(scene)"
        >
          <span class="scene-icon">{{ scene.icon }}</span>
          <div class="scene-info">
            <span class="scene-name">{{ scene.name }}</span>
            <span class="scene-desc">{{ scene.description }}</span>
          </div>
          <div class="scene-difficulty">
            <span v-for="s in 5" :key="s" class="star" :class="{ active: s <= scene.difficulty_default }">★</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 步骤 2：选择角色 -->
    <div v-if="selectedScene" class="step animate-in">
      <h3 class="step-title">
        <span class="step-number">2</span>
        选择角色
      </h3>
      <div class="character-grid">
        <div
          v-for="char in characters"
          :key="char.id"
          class="character-card"
          :class="{ selected: selectedCharacter?.id === char.id }"
          @click="onSelectCharacter(char)"
        >
          <span class="char-avatar">{{ char.avatar_emoji }}</span>
          <div class="char-info">
            <span class="char-name">{{ char.name }}</span>
            <span class="char-identity">{{ char.identity }}</span>
            <div class="char-tags">
              <span v-for="tag in char.personality_tags.slice(0, 3)" :key="tag" class="char-tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 步骤 3：难度调节 -->
    <div v-if="selectedCharacter" class="step animate-in">
      <h3 class="step-title">
        <span class="step-number">3</span>
        难度等级
      </h3>
      <div class="difficulty-row">
        <span v-for="d in 5" :key="d" class="diff-star" :class="{ active: d <= difficulty }" @click="difficulty = d">★</span>
        <span class="diff-label">{{ diffLabels[difficulty - 1] }}</span>
      </div>
    </div>

    <!-- 开始按钮 -->
    <div class="actions">
      <button
        class="start-btn"
        :class="{ disabled: !canStart }"
        :disabled="!canStart"
        @click="$emit('start')"
      >
        开始哄哄 💕
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useComfortStore } from '@/modules/comfort/stores/comfort'
import type { ComfortScene, ComfortCharacter } from '@/modules/comfort/types/comfort'

const emit = defineEmits<{ start: [] }>()

const comfortStore = useComfortStore()
const scenes = computed(() => comfortStore.scenes)
const characters = computed(() => comfortStore.characters)
const selectedScene = computed(() => comfortStore.selectedScene)
const selectedCharacter = computed(() => comfortStore.selectedCharacter)
const difficulty = computed({
  get: () => comfortStore.difficulty,
  set: (v) => { comfortStore.difficulty = v },
})

const diffLabels = ['很简单', '简单', '普通', '困难', '地狱']

const canStart = computed(() => !!selectedScene.value && !!selectedCharacter.value)

function onSelectScene(scene: ComfortScene) {
  comfortStore.selectScene(scene)
}

function onSelectCharacter(char: ComfortCharacter) {
  comfortStore.selectCharacter(char)
}

onMounted(() => {
  if (scenes.value.length === 0) {
    comfortStore.fetchScenes()
  }
})
</script>

<style scoped>
.setup-modal {
  padding: 8px 0;
}

.step {
  margin-bottom: 28px;
}

.animate-in {
  animation: fadeSlideIn 0.35s ease-out;
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 步骤标题 */
.step-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 14px;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

/* 场景卡片 */
.scene-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.scene-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--bg-card);
}

.scene-card:hover {
  border-color: rgba(198, 123, 92, 0.25);
  background: rgba(198, 123, 92, 0.03);
  box-shadow: 0 2px 8px rgba(60, 40, 20, 0.04);
}

.scene-card.selected {
  border-color: var(--accent);
  border-left: 3px solid var(--accent);
  background: rgba(198, 123, 92, 0.06);
  transform: translateY(-1px);
  box-shadow: 0 3px 12px rgba(198, 123, 92, 0.08);
}

.scene-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.scene-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.scene-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.scene-desc {
  font-size: 11px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.scene-difficulty {
  flex-shrink: 0;
}

.star {
  font-size: 12px;
  color: rgba(180, 150, 120, 0.2);
}

.star.active {
  color: #D4A574;
}

/* 角色卡片 */
.character-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.character-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border: 1px solid rgba(180, 150, 120, 0.12);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--bg-card);
}

.character-card:hover {
  border-color: rgba(198, 123, 92, 0.25);
  box-shadow: 0 2px 8px rgba(60, 40, 20, 0.04);
}

.character-card.selected {
  border-color: var(--accent);
  border-left: 3px solid var(--accent);
  background: rgba(198, 123, 92, 0.06);
  transform: scale(1.01);
  box-shadow: 0 3px 12px rgba(198, 123, 92, 0.08);
}

.char-avatar {
  font-size: 36px;
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    rgba(198, 123, 92, 0.08),
    rgba(212, 165, 116, 0.08)
  );
  border-radius: 50%;
  border: 2px solid rgba(180, 150, 120, 0.12);
}

.char-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.char-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.char-identity {
  font-size: 12px;
  color: var(--text-secondary);
}

.char-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.char-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(198, 123, 92, 0.08);
  color: var(--accent);
  font-weight: 500;
}

/* 难度选择 */
.difficulty-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.diff-star {
  font-size: 28px;
  color: rgba(180, 150, 120, 0.2);
  cursor: pointer;
  transition: all 0.15s ease;
  padding: 4px;
  line-height: 1;
}

.diff-star:hover {
  transform: scale(1.15);
}

.diff-star.active {
  color: #D4A574;
  text-shadow: 0 0 8px rgba(212, 165, 116, 0.3);
}

.diff-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-left: 8px;
  font-weight: 500;
}

/* 开始按钮 */
.actions {
  display: flex;
  padding-top: 12px;
}

.start-btn {
  width: 100%;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  background: var(--accent);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(198, 123, 92, 0.2);
}

.start-btn:hover:not(.disabled) {
  background: var(--primaryColorHover, #D49472);
  box-shadow: 0 4px 16px rgba(198, 123, 92, 0.3);
  transform: translateY(-1px);
}

.start-btn:active:not(.disabled) {
  transform: translateY(0);
}

.start-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}
</style>
