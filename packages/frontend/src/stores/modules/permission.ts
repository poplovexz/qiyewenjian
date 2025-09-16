/**
 * 权限管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  Permission, 
  PermissionListRequest, 
  PermissionCreateRequest, 
  PermissionUpdateRequest
} from '@/api/modules/permission'

export const usePermissionStore = defineStore('permission', () => {
  // 状态
  const permissions = ref<Permission[]>([])
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
      
      // TODO: 调用实际API
      // const response = await permissionApi.getPermissionList({
      //   page: currentPage.value,
      //   size: pageSize.value,
      //   ...params
      // })
      
      // 模拟数据
      const mockPermissions: Permission[] = [
        {
          id: '1',
          quanxian_ming: '用户管理菜单',
          quanxian_bianma: 'user:menu',
          miaoshu: '访问用户管理菜单的权限',
          ziyuan_leixing: 'menu',
          ziyuan_lujing: '/users',
          zhuangtai: 'active',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          created_by: 'system'
        },
        {
          id: '2',
          quanxian_ming: '查看用户',
          quanxian_bianma: 'user:read',
          miaoshu: '查看用户信息的权限',
          ziyuan_leixing: 'api',
          ziyuan_lujing: '/api/v1/users/*',
          zhuangtai: 'active',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          created_by: 'system'
        },
        {
          id: '3',
          quanxian_ming: '新增用户按钮',
          quanxian_bianma: 'user:create_button',
          miaoshu: '显示新增用户按钮的权限',
          ziyuan_leixing: 'button',
          ziyuan_lujing: 'user-create-btn',
          zhuangtai: 'active',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          created_by: 'system'
        },
        {
          id: '4',
          quanxian_ming: '客户管理菜单',
          quanxian_bianma: 'customer:menu',
          miaoshu: '访问客户管理菜单的权限',
          ziyuan_leixing: 'menu',
          ziyuan_lujing: '/customers',
          zhuangtai: 'active',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          created_by: 'system'
        },
        {
          id: '5',
          quanxian_ming: '查看客户',
          quanxian_bianma: 'customer:read',
          miaoshu: '查看客户信息的权限',
          ziyuan_leixing: 'api',
          ziyuan_lujing: '/api/v1/customers/*',
          zhuangtai: 'active',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          created_by: 'system'
        }
      ]
      
      // 根据搜索条件过滤
      let filteredPermissions = mockPermissions
      
      if (params.search) {
        const searchLower = params.search.toLowerCase()
        filteredPermissions = filteredPermissions.filter(perm => 
          perm.quanxian_ming.toLowerCase().includes(searchLower) ||
          perm.quanxian_bianma.toLowerCase().includes(searchLower)
        )
      }
      
      if (params.ziyuan_leixing) {
        filteredPermissions = filteredPermissions.filter(perm => 
          perm.ziyuan_leixing === params.ziyuan_leixing
        )
      }
      
      if (params.zhuangtai) {
        filteredPermissions = filteredPermissions.filter(perm => 
          perm.zhuangtai === params.zhuangtai
        )
      }
      
      permissions.value = filteredPermissions
      total.value = filteredPermissions.length
      
      return {
        items: filteredPermissions,
        total: filteredPermissions.length,
        page: currentPage.value,
        size: pageSize.value,
        pages: Math.ceil(filteredPermissions.length / pageSize.value)
      }
    } catch (error) {
      console.error('获取权限列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取权限详情
  const getPermissionById = async (id: string): Promise<Permission | null> => {
    try {
      // TODO: 调用实际API
      // return await permissionApi.getPermissionById(id)
      
      // 模拟数据
      const permission = permissions.value.find(p => p.id === id)
      return permission || null
    } catch (error) {
      console.error('获取权限详情失败:', error)
      throw error
    }
  }

  // 创建权限
  const createPermission = async (data: PermissionCreateRequest): Promise<Permission> => {
    try {
      // TODO: 调用实际API
      // const newPermission = await permissionApi.createPermission(data)
      
      // 模拟数据
      const newPermission: Permission = {
        id: Date.now().toString(),
        quanxian_ming: data.quanxian_ming,
        quanxian_bianma: data.quanxian_bianma,
        miaoshu: data.miaoshu,
        ziyuan_leixing: data.ziyuan_leixing,
        ziyuan_lujing: data.ziyuan_lujing,
        zhuangtai: data.zhuangtai,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        created_by: 'current_user'
      }
      
      permissions.value.unshift(newPermission)
      total.value += 1
      
      return newPermission
    } catch (error) {
      console.error('创建权限失败:', error)
      throw error
    }
  }

  // 更新权限
  const updatePermission = async (id: string, data: PermissionUpdateRequest): Promise<Permission> => {
    try {
      // TODO: 调用实际API
      // const updatedPermission = await permissionApi.updatePermission(id, data)
      
      // 模拟数据
      const index = permissions.value.findIndex(p => p.id === id)
      if (index !== -1) {
        permissions.value[index] = {
          ...permissions.value[index],
          ...data,
          updated_at: new Date().toISOString()
        }
        return permissions.value[index]
      }
      
      throw new Error('权限不存在')
    } catch (error) {
      console.error('更新权限失败:', error)
      throw error
    }
  }

  // 删除权限
  const deletePermission = async (id: string): Promise<void> => {
    try {
      // TODO: 调用实际API
      // await permissionApi.deletePermission(id)
      
      // 模拟数据
      const index = permissions.value.findIndex(p => p.id === id)
      if (index !== -1) {
        permissions.value.splice(index, 1)
        total.value -= 1
      }
    } catch (error) {
      console.error('删除权限失败:', error)
      throw error
    }
  }

  // 更新分页参数
  const updateCurrentPage = (page: number) => {
    currentPage.value = page
  }

  const updatePageSize = (size: number) => {
    pageSize.value = size
  }

  // 重置状态
  const resetState = () => {
    permissions.value = []
    loading.value = false
    total.value = 0
    currentPage.value = 1
    pageSize.value = 20
  }

  return {
    // 状态
    permissions,
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
    getPermissionById,
    createPermission,
    updatePermission,
    deletePermission,
    updateCurrentPage,
    updatePageSize,
    resetState
  }
})
