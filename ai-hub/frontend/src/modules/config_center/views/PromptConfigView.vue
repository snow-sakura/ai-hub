<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">提示词配置</h1>
        <span class="page-count">{{ filteredPrompts.length }} 条提示词</span>
      </div>
      <div class="header-actions">
        <n-input v-model:value="searchKeyword" placeholder="搜索提示词..." clearable style="width:200px" />
        <n-select v-model:value="stageFilter" :options="stageOptions" placeholder="全部类型" clearable style="width:130px" />
        <n-button type="primary" @click="openCreateModal">新建提示词</n-button>
      </div>
    </header>

    <!-- 表格卡片 -->
    <div class="table-card">
      <n-data-table :columns="columns" :data="filteredPrompts" :bordered="false" :single-line="false" :loading="loading" size="small" />
    </div>

    <div style="margin-top:16px"><n-button @click="resetDefaults">恢复默认设置</n-button></div>

    <!-- 新建/编辑弹窗 -->
    <n-modal v-model:show="showModal" :mask-closable="false" preset="card" style="width:680px" title="提示词配置">
      <n-form label-placement="top">
        <n-form-item label="提示词名称"><n-input v-model:value="editForm.name" placeholder="输入提示词名称" /></n-form-item>
        <n-form-item label="类型"><n-select v-model:value="editForm.stage" :options="stageOptions" placeholder="选择类型" /></n-form-item>
        <n-form-item label="提示词内容"><n-input v-model:value="editForm.content" type="textarea" :rows="10" placeholder="输入提示词内容..." /></n-form-item>
        <n-form-item label="描述"><n-input v-model:value="editForm.description" placeholder="可选描述" /></n-form-item>
        <n-form-item label="启用"><n-switch v-model:value="editForm.enabled" /></n-form-item>
      </n-form>
      <template #footer><n-space justify="end"><n-button @click="showModal = false">取消</n-button><n-button type="primary" :loading="modalSaving" @click="handleSaveModal">保存</n-button></n-space></template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import type { DataTableColumn } from 'naive-ui'
import { useMessage, NTag, NSwitch, NButton, NSpace } from 'naive-ui'
import { listPrompts, createPrompt, updatePrompt, deletePrompt, type PromptConfigItem } from '../api/config'

const message = useMessage()
const loading = ref(false)
const showModal = ref(false)
const modalSaving = ref(false)
const searchKeyword = ref('')
const stageFilter = ref<string | null>(null)
const editingId = ref<string | null>(null)

const stageOptions = [
  { label: '需求分析', value: 'analyze' }, { label: '用例生成', value: 'write' },
  { label: '用例评审', value: 'review' }, { label: '用例修订', value: 'revise' }, { label: '通用', value: 'general' },
]
const stageLabelMap: Record<string, string> = { analyze: '需求分析', write: '用例生成', review: '用例评审', revise: '用例修订', general: '通用' }
const stageColorMap: Record<string, 'info' | 'success' | 'warning' | 'error' | 'primary'> = { analyze: 'info', write: 'success', review: 'warning', revise: 'error', general: 'info' }

const prompts = ref<PromptConfigItem[]>([])
const editForm = reactive({ name: '', stage: '', content: '', enabled: true, description: '' })

const filteredPrompts = computed(() => {
  let list = prompts.value
  if (searchKeyword.value) { const kw = searchKeyword.value.toLowerCase(); list = list.filter(p => p.name.toLowerCase().includes(kw) || p.content.toLowerCase().includes(kw)) }
  if (stageFilter.value) list = list.filter(p => p.stage === stageFilter.value)
  return list
})

const columns: DataTableColumn<PromptConfigItem>[] = [
  { title: '提示词名称', key: 'name', width: 160, ellipsis: { tooltip: true } },
  { title: '类型', key: 'stage', width: 110, render: (row: PromptConfigItem) => h(NTag, { type: stageColorMap[row.stage] || 'info', size: 'small' }, () => stageLabelMap[row.stage] || row.stage) },
  { title: '内容预览', key: 'content', ellipsis: { tooltip: true }, width: 300 },
  { title: '启用', key: 'enabled', width: 70, render: (row: PromptConfigItem) => h(NSwitch, { value: row.enabled, 'onUpdate:value': async (val: boolean) => { try { await updatePrompt(row.id, { enabled: val }); row.enabled = val; message.success('更新成功') } catch { message.error('更新失败') } } }) },
  { title: '操作', key: 'actions', width: 140, render: (row: PromptConfigItem) => h(NSpace, { size: 'small' }, () => [h(NButton, { size: 'tiny', quaternary: true, onClick: () => openEditModal(row) }, () => '编辑'), h(NButton, { size: 'tiny', quaternary: true, type: 'error', onClick: () => handleDelete(row.id) }, () => '删除')]) },
]

async function loadData() { loading.value = true; try { const res: any = await listPrompts(); prompts.value = res.data || [] } catch { /* ignore */ } finally { loading.value = false } }
function openCreateModal() { editingId.value = null; Object.assign(editForm, { name: '', stage: '', content: '', enabled: true, description: '' }); showModal.value = true }
function openEditModal(row: PromptConfigItem) { editingId.value = row.id; Object.assign(editForm, { name: row.name, stage: row.stage, content: row.content, enabled: row.enabled, description: row.description }); showModal.value = true }
async function handleSaveModal() {
  modalSaving.value = true
  try { if (editingId.value) { await updatePrompt(editingId.value, { ...editForm }); message.success('更新成功') } else { await createPrompt({ ...editForm }); message.success('创建成功') } showModal.value = false; await loadData() }
  catch { message.error('操作失败') } finally { modalSaving.value = false }
}
async function handleDelete(id: string) { try { await deletePrompt(id); message.success('删除成功'); await loadData() } catch { message.error('删除失败') } }
function resetDefaults() { message.info('恢复默认设置功能待实现') }
onMounted(loadData)
</script>

<style scoped>
.page-wrap { max-width: 1120px; margin: 0 auto; padding: 32px 24px 64px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
.header-left { display: flex; align-items: baseline; gap: 12px; }
.page-title { font-size: 24px; font-weight: 700; color: #3D2E1F; letter-spacing: -0.02em; margin: 0; }
.page-count { font-size: 13px; color: #7A6855; }
.header-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.table-card { background: #FFFDF9; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 12px; overflow: hidden; }
@media (max-width: 768px) { .page-wrap { padding: 16px 12px 48px; } .page-header { flex-direction: column; align-items: stretch; } .header-actions { flex-direction: column; } .header-actions > * { width: 100%; } }
</style>
