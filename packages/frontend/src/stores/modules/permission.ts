/**
 * 权限管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Permission,
  PermissionListRequest,
  PermissionCreateRequest,
  PermissionUpdateRequest,
  PermissionTreeNode,
  PermissionStatistics
} from '@/api/modules/permission'
import { permissionAPI } from '@/api/modules/permission'
import { ElMessage } from 'element-plus'

export const usePermissionStore = defineStore('permission', () => {
  // 状态
  const permissions = ref<Permission[]>([])
  const permissionTree = ref<PermissionTreeNode[]>([])
  const statistics = ref<PermissionStatistics | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 计算属性
  const menuPermissions = computed(() => 
    permissions.value.filter(perm => perm.ziyuan_leixing === 'menu').length
  )

  const buttonPermissions = computed(() => 
    permissions.value.filter(perm => perm.ziyuan_leixing === 'button').length
  )

  const apiPermissions = computed(() => 
    permissions.value.filter(perm => perm.ziyuan_leixing === 'api').length
  )

  // 获取权限列表
  const getPermissionList = async (params: PermissionListRequest = {}) => {
    try {
      loading.value = true

      const response = await permissionAPI.getPermissionList({
        page: currentPage.value,
        size: pageSize.value,
        ...params
      })

      permissions.value = response.items
      total.value = response.total
      currentPage.value = response.page

      return response
    } catch (error) {
      console.error('获取权限列表失败:', error)
      ElMessage.error('获取权限列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取权限树形结构
  const getPermissionTree = async (zhuangtai = 'active') => {
    try {
      loading.value = true
      const tree = await permissionAPI.getPermissionTree(zhuangtai)
      permissionTree.value = tree
      return tree
    } catch (error) {
      console.error('获取权限树失败:', error)
      ElMessage.error('获取权限树失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取权限详情
  const getPermissionById = async (id: string) => {
    try {
      loading.value = true
      const permission = await permissionAPI.getPermissionById(id)
      return permission
    } catch (error) {
      console.error('获取权限详情失败:', error)
      ElMessage.error('获取权限详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建权限
  const createPermission = async (data: PermissionCreateRequest) => {
    try {
      loading.value = true
      const permission = await permissionAPI.createPermission(data)
      ElMessage.success('权限创建成功')
      await getPermissionList() // 刷新列表
      return permission
    } catch (error) {
      console.error('创建权限失败:', error)
      ElMessage.error('创建权限失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新权限
  const updatePermission = async (id: string, data: PermissionUpdateRequest) => {
    try {
      loading.value = true
      const permission = await permissionAPI.updatePermission(id, data)
      ElMessage.success('权限更新成功')
      await getPermissionList() // 刷新列表
      return permission
    } catch (error) {
      console.error('更新权限失败:', error)
      ElMessage.error('更新权限失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除权限
  const deletePermission = async (id: string) => {
    try {
      loading.value = true
      await permissionAPI.deletePermission(id)
      ElMessage.success('权限删除成功')
      await getPermissionList() // 刷新列表
    } catch (error) {
      console.error('删除权限失败:', error)
      ElMessage.error('删除权限失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 按资源类型获取权限
  const getPermissionsByResourceType = async (ziyuan_leixing: string, zhuangtai = 'active') => {
    try {
      const permissions = await permissionAPI.getPermissionsByResourceType(ziyuan_leixing, zhuangtai)
      return permissions
    } catch (error) {
      console.error('获取权限失败:', error)
      ElMessage.error('获取权限失败')
      throw error
    }
  }

  // 获取权限统计
  const getPermissionStatistics = async () => {
    try {
      const stats = await permissionAPI.getPermissionStatistics()
      statistics.value = stats
      return stats
    } catch (error) {
      console.error('获取权限统计失败:', error)
      ElMessage.error('获取权限统计失败')
      throw error
    }
  }

  // 重置状态
  const resetState = () => {
    permissions.value = []
    permissionTree.value = []
    statistics.value = null
    total.value = 0
    currentPage.value = 1
    loading.value = false
  }

  return {
    // 状态
    permissions,
    permissionTree,
    statistics,
    loading,
    total,
    currentPage,
    pageSize,

    // 计算属性
    menuPermissions,
    buttonPermissions,
    apiPermissions,

    // 方法
    getPermissionList,
    getPermissionTree,
    getPermissionById,
    createPermission,
    updatePermission,
    deletePermission,
    getPermissionsByResourceType,
    getPermissionStatistics,
    resetState,

    // 分页方法
    updateCurrentPage: (page: number) => {
      currentPage.value = page
    },
    updatePageSize: (size: number) => {
      pageSize.value = size
    }
  }
})
