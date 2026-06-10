<template>
  <div v-if="hasError" class="error-boundary">
    <n-card title="发生错误" :bordered="false">
      <n-space vertical>
        <n-text type="error">{{ errorMessage }}</n-text>
        <n-space>
          <n-button @click="handleRetry" type="primary">重试</n-button>
          <n-button @click="handleReset">重置</n-button>
        </n-space>
      </n-space>
    </n-card>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
/**
 * ErrorBoundary 组件
 * 捕获子组件渲染错误，显示友好的错误界面（卡片形式），
 * 提供重试和重置两种恢复方式。
 */

import { ref, onErrorCaptured } from 'vue'

const hasError = ref(false)
const errorMessage = ref('')

/** 捕获子组件错误 */
onErrorCaptured((error: Error) => {
  console.error('[ErrorBoundary] 捕获到错误:', error)
  hasError.value = true
  errorMessage.value = error.message || '未知错误'
  // 阻止错误继续传播
  return false
})

/** 重试：重新渲染子组件 */
function handleRetry() {
  hasError.value = false
  errorMessage.value = ''
}

/** 重置：刷新页面 */
function handleReset() {
  window.location.reload()
}
</script>

<style scoped>
.error-boundary {
  padding: 24px;
  max-width: 600px;
  margin: 48px auto;
}
</style>
