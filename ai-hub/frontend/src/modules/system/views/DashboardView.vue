<template>
  <div class="page-wrap">
    <!-- 页面标题 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统概览</h1>
      </div>
    </header>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card" @click="router.push('/system/users')" style="cursor:pointer">
        <div class="stat-icon" style="background:rgba(198,123,92,0.12);color:#C67B5C">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.user_count }}</div>
          <div class="stat-label">用户总数</div>
        </div>
      </div>
      <div class="stat-card" @click="router.push('/system/roles')" style="cursor:pointer">
        <div class="stat-icon" style="background:rgba(212,165,116,0.12);color:#D4A574">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.role_count }}</div>
          <div class="stat-label">角色总数</div>
        </div>
      </div>
      <div class="stat-card" @click="router.push('/system/audit-logs')" style="cursor:pointer">
        <div class="stat-icon" style="background:rgba(198,123,92,0.12);color:#C67B5C">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.audit_log_count }}</div>
          <div class="stat-label">审计日志</div>
        </div>
      </div>
      <div class="stat-card" @click="router.push('/system/settings')" style="cursor:pointer">
        <div class="stat-icon" style="background:rgba(212,165,116,0.12);color:#D4A574">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.active_sessions }}</div>
          <div class="stat-label">活跃会话</div>
        </div>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="table-card" style="padding:20px">
      <h3 style="font-size:15px;font-weight:600;color:#3D2E1F;margin:0 0 16px">快捷操作</h3>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <n-button @click="router.push('/system/users')">用户管理</n-button>
        <n-button @click="router.push('/system/roles')">角色管理</n-button>
        <n-button @click="router.push('/system/audit-logs')">审计日志</n-button>
        <n-button @click="router.push('/system/operation-logs')">操作日志</n-button>
        <n-button @click="router.push('/system/settings')">系统设置</n-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSystemStats } from '@/modules/system/api/system'
import type { SystemStats } from '@/modules/system/types/system'

const router = useRouter()
const stats = reactive<SystemStats>({
  user_count: 0,
  role_count: 0,
  active_sessions: 0,
  audit_log_count: 0,
})

onMounted(async () => {
  try {
    const res: any = await getSystemStats()
    Object.assign(stats, res.data)
  } catch { /* ignore */ }
})
</script>

<style scoped>
.page-wrap { max-width: 1120px; margin: 0 auto; padding: 32px 24px 64px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.header-left { display: flex; align-items: baseline; gap: 12px; }
.page-title { font-size: 24px; font-weight: 700; color: #3D2E1F; letter-spacing: -0.02em; margin: 0; }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: #FFFDF9; border: 1px solid rgba(198, 123, 92, 0.12); border-radius: 12px; padding: 16px 20px; display: flex; align-items: center; gap: 14px; transition: all 0.2s ease; }
.stat-card:hover { border-color: rgba(198, 123, 92, 0.3); box-shadow: 0 2px 8px rgba(198, 123, 92, 0.08); transform: translateY(-1px); }
.stat-icon { font-size: 24px; width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-body { display: flex; flex-direction: column; gap: 2px; }
.stat-value { font-size: 22px; font-weight: 700; color: #3d2e1f; line-height: 1.2; }
.stat-label { font-size: 12px; color: #7a6855; }
.table-card { background: #FFFDF9; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 12px; overflow: hidden; }
@media (max-width: 768px) { .page-wrap { padding: 16px 12px 48px; } .stats-row { grid-template-columns: repeat(2, 1fr); gap: 10px; } }
</style>
