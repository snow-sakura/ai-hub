<template>
  <div class="filter-bar">
    <n-input
      v-model:value="searchText"
      placeholder="搜索..."
      clearable
      :style="{ width: '240px' }"
      @update:value="$emit('search', $event)"
    >
      <template #prefix>
        <span style="color: #7A6855">🔍</span>
      </template>
    </n-input>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { NInput } from 'naive-ui'

const searchText = ref('')

defineEmits<{
  search: [value: string]
}>()
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
