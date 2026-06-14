import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { ProjectVersion, VersionCreate, VersionUpdate } from '@/modules/ai_testing/types/version'
import * as versionApi from '@/modules/ai_testing/api/version'

export const useVersionStore = defineStore('testingVersion', () => {
  const versions = ref<ProjectVersion[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const res = await versionApi.getAllVersions()
      versions.value = res.data || []
    } finally {
      loading.value = false
    }
  }

  async function fetchVersions(projectId: string) {
    loading.value = true
    try {
      const res = await versionApi.getVersions(projectId)
      versions.value = res.data || []
    } finally {
      loading.value = false
    }
  }

  async function create(data: VersionCreate): Promise<ProjectVersion | null> {
    try {
      const res = await versionApi.createVersionStandalone(data)
      if (res.data) {
        versions.value.unshift(res.data)
        return res.data
      }
    } catch (e) { console.warn('创建版本失败:', e) }
    return null
  }

  async function createWithProject(projectId: string, data: VersionCreate): Promise<boolean> {
    try {
      const res = await versionApi.createVersion(projectId, data)
      if (res.data) {
        versions.value.unshift(res.data)
        return true
      }
    } catch (e) { console.warn('创建项目版本失败:', e) }
    return false
  }

  async function update(versionId: string, data: VersionUpdate): Promise<boolean> {
    try {
      const res = await versionApi.updateVersion(versionId, data)
      if (res.data) {
        const idx = versions.value.findIndex(v => v.id === versionId)
        if (idx !== -1) versions.value[idx] = res.data
        return true
      }
    } catch (e) { console.warn('更新版本失败:', e) }
    return false
  }

  async function remove(versionId: string) {
    try {
      await versionApi.deleteVersion(versionId)
      versions.value = versions.value.filter(v => v.id !== versionId)
    } catch (e) { console.warn('删除版本失败:', e) }
  }

  return { versions, loading, fetchAll, fetchVersions, create, createWithProject, update, remove }
})
