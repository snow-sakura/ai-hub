<template>
  <div class="generated-case-table">
    <!-- 批量操作栏 -->
    <n-space v-if="selectedCount > 0" style="margin-bottom: 12px;" :size="8" align="center">
      <n-text>已选 {{ selectedCount }} 条</n-text>
      <n-button size="tiny" type="success" @click="batchAdopt">批量采用</n-button>
      <n-button size="tiny" type="warning" @click="batchDiscard">批量丢弃</n-button>
      <n-button size="tiny" quaternary @click="clearAll">取消选择</n-button>
    </n-space>

    <!-- CSS Grid 表格 -->
    <div class="case-grid">
      <!-- 表头 -->
      <div class="grid-row grid-header">
        <div class="grid-cell cell-check">
          <n-checkbox :checked="isAllSelected" @update:checked="toggleAll" />
        </div>
        <div class="grid-cell cell-id">序号</div>
        <div class="grid-cell cell-title">标题</div>
        <div class="grid-cell cell-priority">优先级</div>
        <div class="grid-cell cell-type">类型</div>
        <div class="grid-cell cell-steps">步骤</div>
        <div class="grid-cell cell-status">状态</div>
        <div class="grid-cell cell-actions">操作</div>
      </div>

      <!-- 数据行 -->
      <div
        v-for="(c, i) in cases"
        :key="String(c.id)"
        class="grid-row grid-data"
        :class="{ selected: isSelected(String(c.id)) }"
      >
        <div class="grid-cell cell-check">
          <n-checkbox :checked="isSelected(String(c.id))" @update:checked="() => toggle(String(c.id))" />
        </div>
        <div class="grid-cell cell-id">{{ (page - 1) * pageSize + i + 1 }}</div>
        <div class="grid-cell cell-title" :title="String(c.title || '')">{{ truncate(String(c.title || ''), 40) }}</div>
        <div class="grid-cell cell-priority">
          <n-tag :type="priorityType(String(c.priority || ''))" size="tiny">{{ c.priority || 'P2' }}</n-tag>
        </div>
        <div class="grid-cell cell-type">
          <n-tag size="tiny">{{ c.case_type || 'functional' }}</n-tag>
        </div>
        <div class="grid-cell cell-steps" :title="String(c.steps || '')">{{ truncate(String(c.steps || ''), 30) }}</div>
        <div class="grid-cell cell-status">
          <n-tag :type="c.status === 'adopted' ? 'success' : 'default'" size="tiny">
            {{ c.status === 'adopted' ? '已采用' : '待定' }}
          </n-tag>
        </div>
        <div class="grid-cell cell-actions">
          <n-space :size="4">
            <n-button size="tiny" quaternary @click="$emit('preview', c)">查看</n-button>
            <n-button size="tiny" quaternary @click="adoptSingle(c)">采用</n-button>
          </n-space>
        </div>
      </div>

      <!-- 空状态 -->
      <n-empty v-if="cases.length === 0" style="grid-column: 1 / -1; padding: 40px 0;" description="暂无生成用例" />

      <!-- 分页 -->
      <div v-if="total > 0" class="grid-pagination">
        <n-space align="center" :size="12">
          <n-text depth="3" style="font-size: 12px;">共 {{ total }} 条</n-text>
          <n-select
            :value="pageSize"
            :options="[{ label: '10条/页', value: 10 }, { label: '20条/页', value: 20 }, { label: '50条/页', value: 50 }]"
            size="tiny"
            style="width: 100px;"
            @update:value="changePageSizeHandle"
          />
          <n-pagination
            :page="page"
            :page-size="pageSize"
            :item-count="total"
            size="small"
            @update:page="changePageHandle"
          />
        </n-space>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  cases: Array<Record<string, unknown>>
  total: number
  page: number
  pageSize: number
  selectedIds: string[]
}>()

const emit = defineEmits<{
  toggle: [id: string]
  toggleAll: []
  clearAll: []
  preview: [caseData: Record<string, unknown>]
  adopt: [caseId: string]
  batchAdopt: [ids: string[]]
  batchDiscard: [ids: string[]]
  changePage: [page: number]
  changePageSize: [size: number]
}>()

const selectedCount = computed(() => props.selectedIds.length)
const isAllSelected = computed(() => props.cases.length > 0 && selectedCount.value === props.cases.length)

function isSelected(id: string): boolean {
  return props.selectedIds.includes(id)
}

function toggle(id: string) {
  emit('toggle', id)
}

function toggleAll() {
  emit('toggleAll')
}

function clearAll() {
  emit('clearAll')
}

function changePageHandle(page: number) {
  emit('changePage', page)
}

function changePageSizeHandle(size: number) {
  emit('changePageSize', size)
}

function adoptSingle(c: Record<string, unknown>) {
  emit('adopt', String(c.id))
}

function batchAdopt() {
  emit('batchAdopt', [...props.selectedIds])
}

function batchDiscard() {
  emit('batchDiscard', [...props.selectedIds])
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max) + '...' : s
}

function priorityType(p: string): 'error' | 'warning' | 'info' | 'success' {
  switch (p) {
    case 'P0': return 'error'
    case 'P1': return 'warning'
    case 'P2': return 'info'
    case 'P3': return 'success'
    default: return 'info'
  }
}
</script>

<style scoped>
.case-grid {
  display: flex;
  flex-direction: column;
  border: 1px solid #e8e4e0;
  border-radius: 6px;
  overflow: hidden;
}

.grid-row {
  display: grid;
  grid-template-columns: 40px 50px 1fr 80px 90px 1fr 80px 100px;
  align-items: center;
  border-bottom: 1px solid #f0eeec;
}

.grid-header {
  background: #faf8f6;
  font-weight: 600;
  font-size: 12px;
  color: #7A6855;
}

.grid-data:hover {
  background: #faf8f6;
}

.grid-data.selected {
  background: #f5f0ec;
}

.grid-cell {
  padding: 8px 6px;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-check {
  display: flex;
  justify-content: center;
}

.cell-title, .cell-steps {
  cursor: default;
}

.grid-pagination {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
  background: #faf8f6;
}

@media (max-width: 900px) {
  .grid-row {
    grid-template-columns: 36px 40px 1fr 70px;
  }
  .cell-type, .cell-steps, .cell-status, .cell-actions {
    display: none;
  }
}
</style>
