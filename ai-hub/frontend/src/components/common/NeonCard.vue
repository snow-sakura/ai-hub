<template>
  <div class="neon-card" :class="{ 'card-glow': hovered }"
    @mouseenter="hovered = true"
    @mouseleave="hovered = false"
  >
    <div class="card-glow-bg" />
    <div class="card-icon" :class="{ 'icon-bounce': hovered }">{{ icon }}</div>
    <h3 class="card-title">{{ title }}</h3>
    <p class="card-desc">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  icon: string
  title: string
  description: string
}>()

const hovered = ref(false)
</script>

<style scoped>
.neon-card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.1);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.card-glow-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
    rgba(198, 123, 92, 0.03),
    transparent 40%
  );
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.neon-card:hover .card-glow-bg {
  opacity: 1;
}

.neon-card:hover {
  border-color: rgba(198, 123, 92, 0.2);
  box-shadow:
    0 0 20px rgba(198, 123, 92, 0.06),
    var(--shadow-md);
  transform: translateY(-4px);
}

.card-icon {
  font-size: 32px;
  margin-bottom: 12px;
  transition: transform 0.3s ease;
}

.icon-bounce {
  transform: scale(1.15) rotate(-5deg);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.card-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}
</style>
