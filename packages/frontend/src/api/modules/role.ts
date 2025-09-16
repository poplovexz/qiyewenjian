/**
 * 角色管理相关API类型定义
 */

export interface Role {
  id: string
  jiaose_ming: string
  jiaose_bianma: string
  miaoshu?: string
  zhuangtai: 'active' | 'inactive'
  permissions?: Permission[]
  users?: User[]
  created_at: string
  updated_at: string
  created_by: string
  updated_by?: string
}

export interface Permission {
  id: string
  quanxian_ming: string
  quanxian_bianma: string
  miaoshu?: string
  ziyuan_leixing: 'menu' | 'button' | 'api'
  ziyuan_lujing: string
  zhuangtai: 'active' | 'inactive'
  created_at: string
  updated_at: string
}

export interface User {
  id: string
  yonghu_ming: string
  xing_ming: string
  youxiang?: string
  shouji?: string
  zhuangtai: 'active' | 'inactive'
}

export interface RoleCreateRequest {
  jiaose_ming: string
  jiaose_bianma: string
  miaoshu?: string
  zhuangtai: 'active' | 'inactive'
}

export interface RoleUpdateRequest {
  jiaose_ming?: string
  jiaose_bianma?: string
  miaoshu?: string
  zhuangtai?: 'active' | 'inactive'
}

export interface RoleListRequest {
  page?: number
  size?: number
  search?: string
  zhuangtai?: 'active' | 'inactive'
}

export interface RoleListResponse {
  items: Role[]
  total: number
  page: number
  size: number
  pages: number
}

export interface RolePermissionRequest {
  permission_ids: string[]
}

export interface RoleStatusRequest {
  zhuangtai: 'active' | 'inactive'
  reason?: string
}

import { request } from '../request'

// API函数实现
export const roleAPI = {
  // 获取角色列表
  async getRoleList(params: RoleListRequest): Promise<RoleListResponse> {
    const response = await request.get('/user-management/roles', { params })
    return response.data
  },

  // 获取角色详情
  async getRoleById(id: string): Promise<Role> {
    const response = await request.get(`/user-management/roles/${id}`)
    return response.data
  },

  // 创建角色
  async createRole(data: RoleCreateRequest): Promise<Role> {
    const response = await request.post('/user-management/roles', data)
    return response.data
  },

  // 更新角色
  async updateRole(id: string, data: RoleUpdateRequest): Promise<Role> {
    const response = await request.put(`/user-management/roles/${id}`, data)
    return response.data
  },

  // 删除角色
  async deleteRole(id: string): Promise<void> {
    await request.delete(`/user-management/roles/${id}`)
  },

  // 更新角色状态
  async updateRoleStatus(id: string, data: RoleStatusRequest): Promise<Role> {
    const response = await request.patch(`/user-management/roles/${id}/status`, data)
    return response.data
  },

  // 获取角色权限
  async getRolePermissions(id: string): Promise<{ permissions: Permission[] }> {
    const response = await request.get(`/user-management/roles/${id}/permissions`)
    return response.data
  },

  // 更新角色权限
  async updateRolePermissions(id: string, data: RolePermissionRequest): Promise<void> {
    await request.put(`/user-management/roles/${id}/permissions`, data)
  }
}
