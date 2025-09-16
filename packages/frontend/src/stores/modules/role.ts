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
  RolePermissionRequest
} from '@/api/modules/role'

export const useRoleStore = defineStore('role', () => {
  // 状态
  const roles = ref<Role[]>([])
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 计算属性
  const activeRoles = computed(() => 
    roles.value.filter(role => role.zhuangtai === 'active').length
  )

  const inactiveRoles = computed(() => 
    roles.value.filter(role => role.zhuangtai === 'inactive').length
  )

  const totalUsers = computed(() => 
    roles.value.reduce((sum, role) => sum + (role.users?.length || 0), 0)
  )

  // 获取角色列表
  const getRoleList = async (params: RoleListRequest = {}) => {
    try {
      loading.value = true
      
      // TODO: 调用实际API
      // const response = await roleApi.getRoleList({
      //   page: currentPage.value,
      //   size: pageSize.value,
      //   ...params
      // })
      
      // 模拟数据
      const mockRoles: Role[] = [
        {
          id: '1',
          jiaose_ming: '系统管理员',
          jiaose_bianma: 'admin',
          miaoshu: '系统最高权限管理员',
          zhuangtai: 'active',
          permissions: [],
          users: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          created_by: 'system'
        },
        {
          id: '2',
          jiaose_ming: '会计',
          jiaose_bianma: 'accountant',
          miaoshu: '负责财务处理和账务管理',
          zhuangtai: 'active',
          permissions: [],
          users: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          created_by: 'system'
        },
        {
          id: '3',
          jiaose_ming: '客服',
          jiaose_bianma: 'customer_service',
          miaoshu: '负责客户服务和沟通',
          zhuangtai: 'active',
          permissions: [],
          users: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          created_by: 'system'
        }
      ]
      
      roles.value = mockRoles
      total.value = mockRoles.length
      
      return {
        items: mockRoles,
        total: mockRoles.length,
        page: currentPage.value,
        size: pageSize.value,
        pages: Math.ceil(mockRoles.length / pageSize.value)
      }
    } catch (error) {
      console.error('获取角色列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取角色详情
  const getRoleById = async (id: string): Promise<Role | null> => {
    try {
      // TODO: 调用实际API
      // return await roleApi.getRoleById(id)
      
      // 模拟数据
      const role = roles.value.find(r => r.id === id)
      return role || null
    } catch (error) {
      console.error('获取角色详情失败:', error)
      throw error
    }
  }

  // 创建角色
  const createRole = async (data: RoleCreateRequest): Promise<Role> => {
    try {
      // TODO: 调用实际API
      // const newRole = await roleApi.createRole(data)
      
      // 模拟数据
      const newRole: Role = {
        id: Date.now().toString(),
        jiaose_ming: data.jiaose_ming,
        jiaose_bianma: data.jiaose_bianma,
        miaoshu: data.miaoshu,
        zhuangtai: data.zhuangtai,
        permissions: [],
        users: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        created_by: 'current_user'
      }
      
      roles.value.unshift(newRole)
      total.value += 1
      
      return newRole
    } catch (error) {
      console.error('创建角色失败:', error)
      throw error
    }
  }

  // 更新角色
  const updateRole = async (id: string, data: RoleUpdateRequest): Promise<Role> => {
    try {
      // TODO: 调用实际API
      // const updatedRole = await roleApi.updateRole(id, data)
      
      // 模拟数据
      const index = roles.value.findIndex(r => r.id === id)
      if (index !== -1) {
        roles.value[index] = {
          ...roles.value[index],
          ...data,
          updated_at: new Date().toISOString()
        }
        return roles.value[index]
      }
      
      throw new Error('角色不存在')
    } catch (error) {
      console.error('更新角色失败:', error)
      throw error
    }
  }

  // 删除角色
  const deleteRole = async (id: string): Promise<void> => {
    try {
      // TODO: 调用实际API
      // await roleApi.deleteRole(id)
      
      // 模拟数据
      const index = roles.value.findIndex(r => r.id === id)
      if (index !== -1) {
        roles.value.splice(index, 1)
        total.value -= 1
      }
    } catch (error) {
      console.error('删除角色失败:', error)
      throw error
    }
  }

  // 更新角色状态
  const updateRoleStatus = async (id: string, data: RoleStatusRequest): Promise<Role> => {
    try {
      // TODO: 调用实际API
      // const updatedRole = await roleApi.updateRoleStatus(id, data)
      
      // 模拟数据
      const index = roles.value.findIndex(r => r.id === id)
      if (index !== -1) {
        roles.value[index] = {
          ...roles.value[index],
          zhuangtai: data.zhuangtai,
          updated_at: new Date().toISOString()
        }
        return roles.value[index]
      }
      
      throw new Error('角色不存在')
    } catch (error) {
      console.error('更新角色状态失败:', error)
      throw error
    }
  }

  // 更新角色权限
  const updateRolePermissions = async (id: string, data: RolePermissionRequest): Promise<void> => {
    try {
      // TODO: 调用实际API
      // await roleApi.updateRolePermissions(id, data)
      
      console.log('更新角色权限:', id, data)
    } catch (error) {
      console.error('更新角色权限失败:', error)
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
    roles.value = []
    loading.value = false
    total.value = 0
    currentPage.value = 1
    pageSize.value = 20
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
    updateRolePermissions,
    updateCurrentPage,
    updatePageSize,
    resetState
  }
})
