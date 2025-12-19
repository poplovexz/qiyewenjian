/**
 * 角色管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Role,
  RoleListRequest,
  RoleCreateRequest,
  RoleUpdateRequest,
  RoleStatusRequest,
  RolePermissionRequest,
} from '@/api/modules/role'
import { roleAPI } from '@/api/modules/role'
import { ElMessage } from 'element-plus'

export const useRoleStore = defineStore('role', () => {
  // 状态
  const roles = ref<Role[]>([])
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 计算属性
  const activeRoles = computed(
    () => roles.value.filter((role) => role.zhuangtai === 'active').length
  )

  const inactiveRoles = computed(
    () => roles.value.filter((role) => role.zhuangtai === 'inactive').length
  )

  const totalUsers = computed(() =>
    roles.value.reduce((sum, role) => sum + (role.users?.length || 0), 0)
  )

  // 获取角色列表
  const getRoleList = async (params: RoleListRequest = {}) => {
    try {
      loading.value = true

      const response = await roleAPI.getRoleList({
        page: currentPage.value,
        size: pageSize.value,
        ...params,
      })

      roles.value = response.items
      total.value = response.total
      currentPage.value = response.page

      return response
    } catch (error) {
      ElMessage.error('获取角色列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取角色详情
  const getRoleById = async (id: string) => {
    try {
      loading.value = true
      const role = await roleAPI.getRoleById(id)
      return role
    } catch (error) {
      ElMessage.error('获取角色详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建角色
  const createRole = async (data: RoleCreateRequest) => {
    try {
      loading.value = true
      const role = await roleAPI.createRole(data)
      ElMessage.success('角色创建成功')
      await getRoleList() // 刷新列表
      return role
    } catch (error) {
      ElMessage.error('创建角色失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新角色
  const updateRole = async (id: string, data: RoleUpdateRequest) => {
    try {
      loading.value = true
      const role = await roleAPI.updateRole(id, data)
      ElMessage.success('角色更新成功')
      await getRoleList() // 刷新列表
      return role
    } catch (error) {
      ElMessage.error('更新角色失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除角色
  const deleteRole = async (id: string) => {
    try {
      loading.value = true
      await roleAPI.deleteRole(id)
      ElMessage.success('角色删除成功')
      await getRoleList() // 刷新列表
    } catch (error) {
      ElMessage.error('删除角色失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新角色状态
  const updateRoleStatus = async (id: string, data: RoleStatusRequest) => {
    try {
      loading.value = true
      const role = await roleAPI.updateRoleStatus(id, data)
      ElMessage.success('角色状态更新成功')
      await getRoleList() // 刷新列表
      return role
    } catch (error) {
      ElMessage.error('更新角色状态失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取角色权限
  const getRolePermissions = async (id: string) => {
    try {
      const response = await roleAPI.getRolePermissions(id)
      return response.permissions
    } catch (error) {
      ElMessage.error('获取角色权限失败')
      throw error
    }
  }

  // 更新角色权限
  const updateRolePermissions = async (id: string, data: RolePermissionRequest) => {
    try {
      loading.value = true
      await roleAPI.updateRolePermissions(id, data)
      ElMessage.success('角色权限更新成功')
    } catch (error) {
      ElMessage.error('更新角色权限失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 重置状态
  const resetState = () => {
    roles.value = []
    total.value = 0
    currentPage.value = 1
    loading.value = false
  }

  return {
    // 状态
    roles,
    loading,
    total,
    currentPage,
    pageSize,

    // 计算属性
    activeRoles,
    inactiveRoles,
    totalUsers,

    // 方法
    getRoleList,
    getRoleById,
    createRole,
    updateRole,
    deleteRole,
    updateRoleStatus,
    getRolePermissions,
    updateRolePermissions,
    resetState,

    // 分页方法
    updateCurrentPage: (page: number) => {
      currentPage.value = page
    },
    updatePageSize: (size: number) => {
      pageSize.value = size
    },
  }
})
