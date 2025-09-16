import { request } from '@/utils/request'
import type { 
  User, 
  UserCreate, 
  UserUpdate, 
  UserListParams, 
  UserListResponse,
  Role,
  RoleListParams,
  RoleListResponse
} from '@/types/user'

/**
 * 用户管理 API
 */
export const userApi = {
  /**
   * 获取用户列表
   */
  getUserList(params: UserListParams): Promise<UserListResponse> {
    return request.get('/api/v1/users/', { params })
  },

  /**
   * 根据ID获取用户详情
   */
  getUserById(id: string): Promise<User> {
    return request.get(`/api/v1/users/${id}`)
  },

  /**
   * 创建用户
   */
  createUser(data: UserCreate): Promise<User> {
    return request.post('/api/v1/users/', data)
  },

  /**
   * 更新用户
   */
  updateUser(id: string, data: UserUpdate): Promise<User> {
    return request.put(`/api/v1/users/${id}`, data)
  },

  /**
   * 删除用户
   */
  deleteUser(id: string): Promise<void> {
    return request.delete(`/api/v1/users/${id}`)
  },

  /**
   * 分配角色给用户
   */
  assignRoles(userId: string, roleIds: string[]): Promise<boolean> {
    return request.post(`/api/v1/users/${userId}/roles`, { jiaose_ids: roleIds })
  },

  /**
   * 获取用户的角色列表
   */
  getUserRoles(userId: string): Promise<Role[]> {
    return request.get(`/api/v1/users/${userId}/roles`)
  },

  /**
   * 获取用户的权限列表
   */
  getUserPermissions(userId: string): Promise<string[]> {
    return request.get(`/api/v1/users/${userId}/permissions`)
  }
}

/**
 * 角色管理 API
 */
export const roleApi = {
  /**
   * 获取角色列表
   */
  getRoleList(params: RoleListParams): Promise<RoleListResponse> {
    return request.get('/api/v1/roles/', { params })
  },

  /**
   * 根据ID获取角色详情
   */
  getRoleById(id: string): Promise<Role> {
    return request.get(`/api/v1/roles/${id}`)
  },

  /**
   * 创建角色
   */
  createRole(data: any): Promise<Role> {
    return request.post('/api/v1/roles/', data)
  },

  /**
   * 更新角色
   */
  updateRole(id: string, data: any): Promise<Role> {
    return request.put(`/api/v1/roles/${id}`, data)
  },

  /**
   * 删除角色
   */
  deleteRole(id: string): Promise<void> {
    return request.delete(`/api/v1/roles/${id}`)
  },

  /**
   * 分配权限给角色
   */
  assignPermissions(roleId: string, permissionIds: string[]): Promise<boolean> {
    return request.post(`/api/v1/roles/${roleId}/permissions`, { quanxian_ids: permissionIds })
  }
}
