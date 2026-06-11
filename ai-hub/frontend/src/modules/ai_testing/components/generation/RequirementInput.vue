<template>
  <div class="requirement-input">
    <!-- 需求标题 -->
    <n-input
      v-model:value="title"
      placeholder="需求标题（可选）"
      :maxlength="200"
      show-count
      :disabled="disabled"
      style="margin-bottom: 12px;"
    />

    <!-- 双列并排输入 -->
    <div class="dual-pane">
      <!-- 左侧：手动输入 -->
      <div class="pane">
        <div class="pane-label">手动输入需求</div>
        <n-input
          v-model:value="text"
          type="textarea"
          :rows="10"
          :placeholder="`在此粘贴需求文档内容...

支持 Markdown 格式：
- **功能点描述**
- 边界条件
- 异常场景`
"
          show-count
          :maxlength="8000"
          :disabled="disabled"
        />
      </div>

      <!-- 中间分隔 -->
      <div class="pane-divider">
        <span class="divider-label">或</span>
      </div>

      <!-- 右侧：文件上传 -->
      <div class="pane">
        <div class="pane-label">上传需求文档</div>
        <div class="upload-area">
          <DocumentUpload :disabled="disabled" @parsed="onDocumentParsed" />
        </div>
        <div v-if="parsedText" style="margin-top: 8px;">
          <n-input
            v-model:value="text"
            type="textarea"
            :rows="6"
            placeholder="解析结果（可编辑）..."
            show-count
            :maxlength="8000"
            :disabled="disabled"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DocumentUpload from './DocumentUpload.vue'

withDefaults(defineProps<{
  disabled?: boolean
}>(), {
  disabled: false,
})

const title = ref('')
const text = ref('')
const parsedText = ref('')

function onDocumentParsed(result: { text: string; file_name: string }) {
  parsedText.value = result.text
  text.value = result.text
  if (!title.value) {
    title.value = result.file_name.replace(/\.[^.]+$/, '')
  }
}

defineExpose({ title, text })
</script>

<style scoped>
.requirement-input {
  width: 100%;
}

.dual-pane {
  display: flex;
  gap: 0;
  align-items: stretch;
}

.pane {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.pane-label {
  font-size: 12px;
  font-weight: 600;
  color: #7A6855;
  margin-bottom: 8px;
}

.pane-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  flex-shrink: 0;
}

.divider-label {
  font-size: 13px;
  color: #999;
  font-weight: 500;
  background: #f5f5f5;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area {
  flex: 1;
  display: flex;
  align-items: stretch;
}

@media (max-width: 768px) {
  .dual-pane {
    flex-direction: column;
  }
  .pane-divider {
    width: 100%;
    height: 32px;
  }
}
</style>
