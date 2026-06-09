<template>
  <div class="glass-card-wrapper">
    <div class="glass-inner">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.glass-card-wrapper {
  background: var(--bg-card);
  border: 1px solid rgba(180, 150, 120, 0.1);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.glass-inner {
  padding: 20px;
}
</style>
