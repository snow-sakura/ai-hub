<template>
  <div class="markdown-field">
    <label v-if="label" class="field-label">{{ label }}</label>
    <MdEditor
      v-model="content"
      :language="'zh-CN'"
      :preview="preview"
      :height="height + 'px'"
      :toolbars="toolbars"
      @on-save="$emit('save', content)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MdEditor } from 'md-editor-v3'
import type { ToolbarNames } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

const props = withDefaults(defineProps<{
  modelValue: string
  label?: string
  height?: number
  preview?: boolean
}>(), {
  modelValue: '',
  height: 280,
  preview: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  save: [value: string]
}>()

const content = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const toolbars: ToolbarNames[] = [
  'bold', 'underline', 'italic', 'strikeThrough', '-',
  'title', 'unorderedList', 'orderedList', '-',
  'codeRow', 'code', 'link', 'image', 'table', '-',
  'revoke', 'next', '=',
  'preview', 'catalog',
]
</script>

<style scoped>
.markdown-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #1a1a2e);
}
</style>
