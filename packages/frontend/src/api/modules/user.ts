import { request } from '@/utils/request'
import type {
  User,
  UserCreate,
  UserUpdate,
  UserListParams,
  UserListResponse,
  Role,
  RoleListParams,
  RoleListResponse,
  Permission
} from '@/types/user'

/**
 * 用户管理 API
 */
export const userApi = {
  /**
   * 获取用户列表
   */
  getUserList(params: UserListParams): Promise<UserListResponse> {
    return request.get('/users/', { params })
  },

  /**
   * 根据ID获取用户详情
   */
  getUserById(id: string): Promise<User> {
    return request.get(`/users/${id}`)
  },

  /**
   * 创建用户
   */
  createUser(data: UserCreate): Promise<User> {
    return request.post('/users/', data)
  },

  /**
   * 更新用户
   */
  updateUser(id: string, data: UserUpdate): Promise<User> {
    return request.put(`/users/${id}`, data)
  },

  /**
   * 删除用户
   */
  deleteUser(id: string): Promise<void> {
    return request.delete(`/users/${id}`)
  },

  /**
   * 分配角色给用户
   */
  assignRoles(userId: string, roleIds: string[]): Promise<{ message: string }> {
    return request.post(`/users/${userId}/roles`, roleIds)
  },

  /**
   * 获取用户的角色列表
   */
  getUserRoles(userId: string): Promise<Role[]> {
    return request.get(`/users/${userId}/roles`)
  },

  /**
   * 获取用户的权限列表
   */
  getUserPermissions(userId: string): Promise<Permission[]> {
    return request.get(`/users/${userId}/permissions`)
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
    return request.get('/user-management/roles/', { params })
  },

  /**
   * 根据ID获取角色详情
   */
  getRoleById(id: string): Promise<Role> {
    return request.get(`/user-management/roles/${id}`)
  },

  /**
   * 创建角色
   */
  createRole(data: any): Promise<Role> {
    return request.post('/user-management/roles/', data)
  },

  /**
   * 更新角色
   */
  updateRole(id: string, data: any): Promise<Role> {
    return request.put(`/user-management/roles/${id}`, data)
  },

  /**
   * 删除角色
   */
  deleteRole(id: string): Promise<void> {
    return request.delete(`/user-management/roles/${id}`)
  },

  /**
   * 分配权限给角色
   */
  assignPermissions(roleId: string, permissionIds: string[]): Promise<{ message: string }> {
    return request.put(`/user-management/roles/${roleId}/permissions`, { permission_ids: permissionIds })
  }
}
