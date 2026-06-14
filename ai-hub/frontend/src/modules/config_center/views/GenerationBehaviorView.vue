<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">生成行为配置</h1>
        <span class="page-count">{{ items.length }} 项配置</span>
      </div>
      <n-button type="primary" @click="showAddModal = true">添加配置项</n-button>
    </header>

    <p class="page-desc">配置 AI 生成测试用例的行为参数，修改后自动保存</p>

    <n-spin :show="loading">
      <div class="card-list">
        <n-card v-for="item in items" :key="item.key" hoverable>
          <div class="behavior-header"><span class="behavior-key">{{ item.key }}</span><n-button text type="error" size="tiny" @click="handleDelete(item.key)">删除</n-button></div>
          <p class="behavior-desc">{{ item.description }}</p>
          <div style="margin-top:10px">
            <n-input v-if="item.key.includes('prompt') || item.key.includes('template') || item.key.includes('format')" v-model:value="item.value" type="textarea" :rows="3" placeholder="输入配置值" @blur="handleSave(item)" />
            <n-switch v-else-if="item.value === 'true' || item.value === 'false'" :value="item.value === 'true'" @update:value="(v) => { item.value = String(v); handleSave(item) }" />
            <n-input-number v-else-if="!isNaN(Number(item.value))" :value="Number(item.value)" style="width:200px" @update:value="(v) => { item.value = String(v); handleSave(item) }" />
            <n-input v-else v-model:value="item.value" placeholder="输入配置值" @blur="handleSave(item)" />
          </div>
        </n-card>
      </div>
    </n-spin>

    <n-empty v-if="!loading && items.length === 0" description="暂无配置项" style="margin-top:60px" />

    <n-modal v-model:show="showAddModal" preset="card" style="width:480px" title="新增配置项">
      <n-form label-placement="top">
        <n-form-item label="配置键名"><n-input v-model:value="newItem.key" placeholder="如: max_cases_per_task" /></n-form-item>
        <n-form-item label="配置值"><n-input v-model:value="newItem.value" placeholder="配置值" /></n-form-item>
        <n-form-item label="描述"><n-input v-model:value="newItem.description" placeholder="配置项说明" /></n-form-item>
      </n-form>
      <template #footer><n-space justify="end"><n-button @click="showAddModal = false">取消</n-button><n-button type="primary" :loading="adding" @click="handleAddItem">添加</n-button></n-space></template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { listBehaviors, upsertBehavior, deleteBehavior, type BehaviorConfigItem } from '../api/config'

const message = useMessage()
const loading = ref(false)
const showAddModal = ref(false)
const adding = ref(false)
const items = ref<BehaviorConfigItem[]>([])
const newItem = ref({ key: '', value: '', description: '' })

async function loadData() { loading.value = true; try { const res: any = await listBehaviors(); items.value = res.data || [] } catch { /* ignore */ } finally { loading.value = false } }
async function handleSave(item: BehaviorConfigItem) { try { await upsertBehavior(item.key, item.value, item.description); message.success('已保存', { duration: 1500 }) } catch { message.error('保存失败') } }
async function handleDelete(key: string) { try { await deleteBehavior(key); items.value = items.value.filter(i => i.key !== key); message.success('已删除') } catch { message.error('删除失败') } }
async function handleAddItem() {
  if (!newItem.value.key) { message.warning('请输入配置键名'); return }
  adding.value = true
  try { await upsertBehavior(newItem.value.key, newItem.value.value, newItem.value.description); items.value.push({ ...newItem.value, updated_at: new Date().toISOString() }); showAddModal.value = false; newItem.value = { key: '', value: '', description: '' }; message.success('添加成功') }
  catch { message.error('添加失败') }
  finally { adding.value = false }
}
onMounted(loadData)
</script>

<style scoped>
.page-wrap { max-width: 900px; margin: 0 auto; padding: 32px 24px 64px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.header-left { display: flex; align-items: baseline; gap: 12px; }
.page-title { font-size: 24px; font-weight: 700; color: #3D2E1F; letter-spacing: -0.02em; margin: 0; }
.page-count { font-size: 13px; color: #7A6855; }
.page-desc { font-size: 13px; color: #7A6855; margin-bottom: 20px; }
.card-list { display: flex; flex-direction: column; gap: 12px; }
.behavior-header { display: flex; align-items: center; justify-content: space-between; }
.behavior-key { font-size: 14px; font-weight: 600; color: #5C4A38; font-family: 'SF Mono', 'Fira Code', monospace; }
.behavior-desc { font-size: 12px; color: #7A6855; margin: 4px 0 0; }
</style>
