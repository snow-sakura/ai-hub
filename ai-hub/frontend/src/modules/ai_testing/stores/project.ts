import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  TestingProject,
  ProjectMember,
  MemberRole,
  ProjectCreate,
  ProjectUpdate,
  ProjectStatus,
} from '@/modules/ai_testing/types/project'
import * as projectApi from '@/modules/ai_testing/api/project'

export const useProjectStore = defineStore('testing-project', () => {
  const projects = ref<TestingProject[]>([])
  const currentProject = ref<TestingProject | null>(null)
  const members = ref<ProjectMember[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(10)
  const isLoading = ref(false)
  const searchKeyword = ref('')
  const statusFilter = ref<ProjectStatus | null>(null)

  /** 加载项目列表 */
  async function fetchProjects() {
    isLoading.value = true
    try {
      const res = await projectApi.getProjects({
        status: statusFilter.value,
        keyword: searchKeyword.value || null,
        page: page.value,
        page_size: pageSize.value,
      })
      const data = res.data
      projects.value = data.items
      total.value = data.total
    } catch (e) {
      console.error('获取项目列表失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  /** 加载项目详情 */
  async function fetchProject(id: string) {
    isLoading.value = true
    try {
      const res = await projectApi.getProject(id)
      currentProject.value = res.data
    } catch (e) {
      console.error('获取项目详情失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  /** 创建项目 */
  async function createProject(data: ProjectCreate): Promise<TestingProject | null> {
    try {
      const res = await projectApi.createProject(data)
      await fetchProjects()
      return res.data
    } catch (e) {
      console.error('创建项目失败:', e)
      return null
    }
  }

  /** 更新项目 */
  async function updateProject(id: string, data: ProjectUpdate): Promise<boolean> {
    try {
      await projectApi.updateProject(id, data)
      await fetchProjects()
      if (currentProject.value?.id === id) {
        await fetchProject(id)
      }
      return true
    } catch (e) {
      console.error('更新项目失败:', e)
      return false
    }
  }

  /** 删除项目 */
  async function deleteProject(id: string): Promise<boolean> {
    try {
      await projectApi.deleteProject(id)
      await fetchProjects()
      return true
    } catch (e) {
      console.error('删除项目失败:', e)
      return false
    }
  }

  /** 加载项目成员 */
  async function fetchMembers(projectId: string) {
    try {
      const res = await projectApi.getProjectMembers(projectId)
      members.value = res.data || []
    } catch (e) {
      console.error('获取成员列表失败:', e)
    }
  }

  /** 添加成员 */
  async function addMember(projectId: string, name: string, role: MemberRole = 'tester') {
    try {
      await projectApi.addMember(projectId, { name, role })
      await fetchMembers(projectId)
      await fetchProjects()
      return true
    } catch (e) {
      console.error('添加成员失败:', e)
      return false
    }
  }

  /** 从项目中移除成员关联（多对多，仅解绑不删除成员） */
  async function removeMember(memberId: string, projectId: string) {
    try {
      await projectApi.unlinkMemberFromProject(memberId, projectId)
      await fetchMembers(projectId)
      await fetchProjects()
      return true
    } catch (e) {
      console.error('移除成员失败:', e)
      return false
    }
  }

  /** 更新成员角色 */
  async function updateMemberRole(memberId: string, role: string): Promise<boolean> {
    try {
      await projectApi.updateMemberRole(memberId, { role: role as MemberRole })
      const idx = members.value.findIndex(m => m.id === memberId)
      if (idx !== -1) members.value[idx].role = role as MemberRole
      return true
    } catch (e) {
      console.error('更新成员角色失败:', e)
      return false
    }
  }

  return {
    projects,
    currentProject,
    members,
    total,
    page,
    pageSize,
    isLoading,
    searchKeyword,
    statusFilter,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
    fetchMembers,
    addMember,
    removeMember,
    updateMemberRole,
  }
})
