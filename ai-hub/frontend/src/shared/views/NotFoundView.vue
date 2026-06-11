<template>
  <div class="not-found">
    <div class="nf-content">
      <div class="nf-code">404</div>
      <h2 class="nf-title">页面未找到</h2>
      <p class="nf-desc">你访问的页面不存在或已被移除</p>
      <n-button type="primary" @click="router.push('/')">返回首页</n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--bg-primary);
}

.nf-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.nf-code {
  font-size: 80px;
  font-weight: 700;
  color: var(--accent);
  opacity: 0.6;
  line-height: 1;
}

.nf-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
}

.nf-desc {
  font-size: 14px;
  color: var(--text-muted);
}
</style>
