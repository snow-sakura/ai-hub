<template>
  <div class="app-auto">
    <div class="app-page-header app-fade-in">
      <div>
        <h1 class="app-page-title">APP 元素管理</h1>
        <p class="app-page-subtitle">管理移动端页面元素定位器 · 共 {{ elements.length }} 个元素</p>
      </div>
      <div class="header-actions">
        <button class="app-btn app-btn-primary" @click="showAddModal = true">+ 新建元素</button>
      </div>
    </div>

    <div class="app-card app-fade-in">
      <div class="app-card-body" style="padding:0">
        <div style="padding:14px 16px;border-bottom:var(--app-border)">
          <div class="filter-bar">
            <select v-model="filters.page" class="app-input" style="width:130px">
              <option value="">全部页面</option>
              <option v-for="p in pages" :key="p" :value="p">{{ p }}</option>
            </select>
            <select v-model="filters.locatorType" class="app-input" style="width:130px">
              <option value="">全部类型</option>
              <option value="id">ID</option>
              <option value="xpath">XPath</option>
              <option value="a11y">Accessibility ID</option>
              <option value="class">Class Name</option>
              <option value="ios-pred">iOS Predicate</option>
            </select>
            <select v-model="filters.platform" class="app-input" style="width:110px">
              <option value="">全部平台</option>
              <option value="android">Android</option>
              <option value="ios">iOS</option>
              <option value="both">双平台</option>
            </select>
            <input v-model="filters.search" class="app-input" style="flex:1;min-width:150px" placeholder="搜索元素名称或表达式...">
          </div>
        </div>
        <div style="overflow-x:auto">
          <table class="app-data-table">
            <thead>
              <tr><th>元素名称</th><th>所属页面</th><th>定位类型</th><th>定位表达式</th><th>平台</th><th>操作</th></tr>
            </thead>
            <tbody>
              <tr v-for="(el, i) in filteredElements" :key="i">
                <td style="font-weight:600">{{ el.name }}</td>
                <td>{{ el.page }}</td>
                <td><span :class="['app-tag', getLocatorClass(el.type)]">{{ getLocatorLabel(el.type) }}</span></td>
                <td style="font-family:var(--app-font-mono);font-size:12px">{{ el.expression }}</td>
                <td>
                  <span :class="['app-tag', el.platform === 'both' ? 'app-tag-both' : el.platform === 'android' ? 'app-tag-android' : 'app-tag-ios']">
                    {{ el.platform === 'both' ? '双平台' : el.platform === 'android' ? 'Android' : 'iOS' }}
                  </span>
                </td>
                <td>
                  <button class="app-btn app-btn-ghost app-btn-xs" @click="copyElement(el)">📋</button>
                  <button class="app-btn app-btn-ghost app-btn-xs" @click="editElement(el)">✏️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 新建元素弹窗 -->
    <div class="app-modal-overlay" :class="{ active: showAddModal }" @click.self="showAddModal = false">
      <div class="app-modal-box">
        <div class="app-modal-head">
          <h3>📱 新建元素</h3>
          <button class="app-modal-close" @click="showAddModal = false">✕</button>
        </div>
        <div class="app-modal-body">
          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">元素名称</label>
          <input v-model="formData.name" class="app-input" style="margin-bottom:12px" placeholder="例如：登录按钮">

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">所属页面</label>
          <select v-model="formData.page" class="app-input" style="margin-bottom:12px">
            <option v-for="p in pages" :key="p" :value="p">{{ p }}</option>
          </select>

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">定位类型</label>
          <select v-model="formData.type" class="app-input" style="margin-bottom:12px">
            <option value="a11y">Accessibility ID</option>
            <option value="id">ID</option>
            <option value="xpath">XPath</option>
            <option value="class">Class Name</option>
            <option value="ios-pred">iOS Predicate String</option>
            <option value="android-ui">Android UIAutomator</option>
          </select>

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">定位表达式</label>
          <input v-model="formData.expression" class="app-input app-input-mono" style="margin-bottom:12px" placeholder="例如：username_input">

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">平台</label>
          <select v-model="formData.platform" class="app-input" style="margin-bottom:12px">
            <option value="android">Android</option>
            <option value="ios">iOS</option>
            <option value="both">双平台</option>
          </select>

          <label style="font-size:13px;color:var(--app-text-secondary);margin-bottom:4px;display:block">元素描述</label>
          <input v-model="formData.description" class="app-input" placeholder="可选">
        </div>
        <div class="app-modal-footer">
          <button class="app-btn app-btn-secondary" @click="showAddModal = false">取消</button>
          <button class="app-btn app-btn-primary" @click="createElement">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

const showAddModal = ref(false)

const filters = reactive({ page: '', locatorType: '', platform: '', search: '' })
const pages = ['登录页', '首页', '商品页', '支付页', '个人中心']

const formData = reactive({
  name: '', page: '登录页', type: 'a11y', expression: '', platform: 'android', description: ''
})

const elements = ref([
  { name: '用户名输入框', page: '登录页', type: 'a11y', expression: 'username_input', platform: 'android' },
  { name: '密码输入框', page: '登录页', type: 'a11y', expression: 'password_input', platform: 'ios' },
  { name: '登录按钮', page: '登录页', type: 'id', expression: 'btn_login', platform: 'android' },
  { name: '搜索栏', page: '首页', type: 'xpath', expression: '//android.widget.EditText[@content-desc="search"]', platform: 'both' },
  { name: '购物车图标', page: '首页', type: 'class', expression: 'android.widget.ImageButton', platform: 'android' },
  { name: '商品列表', page: '商品页', type: 'xpath', expression: '//XCUIElementTypeStaticText[@name="product_name"]', platform: 'ios' },
  { name: '确认支付按钮', page: '支付页', type: 'ios-pred', expression: 'label == "确认支付" AND type == "XCUIElementTypeButton"', platform: 'ios' },
  { name: '个人头像', page: '个人中心', type: 'a11y', expression: 'user_avatar', platform: 'both' }
])

const filteredElements = computed(() => {
  return elements.value.filter(el => {
    if (filters.page && el.page !== filters.page) return false
    if (filters.locatorType && el.type !== filters.locatorType) return false
    if (filters.platform && el.platform !== filters.platform) return false
    if (filters.search) {
      const q = filters.search.toLowerCase()
      if (!el.name.toLowerCase().includes(q) && !el.expression.toLowerCase().includes(q)) return false
    }
    return true
  })
})

function getLocatorClass(type) {
  const map = { id: 'app-tag-id', xpath: 'app-tag-xpath', a11y: 'app-tag-a11y', class: 'app-tag-class', 'ios-pred': 'app-tag-ios-pred' }
  return map[type] || 'app-tag-id'
}

function getLocatorLabel(type) {
  const map = { id: 'ID', xpath: 'XPath', a11y: 'Accessibility ID', class: 'Class Name', 'ios-pred': 'iOS Predicate' }
  return map[type] || type
}

function copyElement(el) {
  ElMessage.info('已复制')
}

function editElement(el) {
  ElMessage.info(`编辑元素: ${el.name}`)
}

function createElement() {
  if (!formData.name) {
    ElMessage.warning('请输入元素名称')
    return
  }
  elements.value.push({
    name: formData.name,
    page: formData.page,
    type: formData.type,
    expression: formData.expression,
    platform: formData.platform
  })
  showAddModal.value = false
  ElMessage.success('元素已创建')
  Object.assign(formData, { name: '', type: 'a11y', expression: '', platform: 'android', description: '' })
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.app-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.app-data-table th {
  text-align: left;
  padding: 10px 12px;
  font-weight: 600;
  color: var(--app-text-secondary);
  border-bottom: var(--app-border);
  white-space: nowrap;
  background: var(--app-sidebar-bg);
  font-size: 12px;
}

.app-data-table td {
  padding: 10px 12px;
  border-bottom: var(--app-border);
  color: var(--app-text);
}

.app-data-table tr:nth-child(even) td {
  background: rgba(180, 150, 120, 0.03);
}

.app-data-table tr:hover td {
  background: var(--app-primary-bg);
}
</style>
