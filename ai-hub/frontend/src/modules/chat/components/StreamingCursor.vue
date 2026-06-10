<template>
  <span class="streaming-cursor">▊</span>
</template>

<style scoped>
.streaming-cursor {
  color: var(--accent);
  animation: blink 1s step-end infinite;
  font-size: 14px;
}

@keyframes blink {
  50% { opacity: 0 }
}
</style>
