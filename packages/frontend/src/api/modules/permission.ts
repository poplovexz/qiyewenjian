/**
 * 权限管理相关API类型定义
 */

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
  created_by?: string
  updated_by?: string
}

export interface PermissionCreateRequest {
  quanxian_ming: string
  quanxian_bianma: string
  miaoshu?: string
  ziyuan_leixing: 'menu' | 'button' | 'api'
  ziyuan_lujing: string
  zhuangtai: 'active' | 'inactive'
}

export interface PermissionUpdateRequest {
  quanxian_ming?: string
  quanxian_bianma?: string
  miaoshu?: string
  ziyuan_leixing?: 'menu' | 'button' | 'api'
  ziyuan_lujing?: string
  zhuangtai?: 'active' | 'inactive'
}

export interface PermissionListRequest {
  page?: number
  size?: number
  search?: string
  ziyuan_leixing?: 'menu' | 'button' | 'api'
  zhuangtai?: 'active' | 'inactive'
}

export interface PermissionListResponse {
  items: Permission[]
  total: number
  page: number
  size: number
  pages: number
}

export interface PermissionTreeNode {
  id: string
  label: string
  quanxian_bianma?: string
  ziyuan_leixing?: string
  children?: PermissionTreeNode[]
  is_permission: boolean
}

export interface PermissionStatistics {
  total_permissions: number
  menu_permissions: number
  button_permissions: number
  api_permissions: number
  active_permissions: number
  inactive_permissions: number
  permissions_with_roles: number
}

import { request } from '@/utils/request'

// API函数实现
export const permissionAPI = {
  // 获取权限列表
  async getPermissionList(params: PermissionListRequest): Promise<PermissionListResponse> {
    const response = await request.get('/user-management/permissions/', { params })
    return response
  },

  // 获取权限树形结构
  async getPermissionTree(zhuangtai = 'active'): Promise<PermissionTreeNode[]> {
    const response = await request.get('/user-management/permissions/tree', {
      params: { zhuangtai },
    })
    return response
  },

  // 获取权限详情
  async getPermissionById(id: string): Promise<Permission> {
    const response = await request.get(`/user-management/permissions/${id}`)
    return response
  },

  // 创建权限
  async createPermission(data: PermissionCreateRequest): Promise<Permission> {
    const response = await request.post('/user-management/permissions/', data)
    return response
  },

  // 更新权限
  async updatePermission(id: string, data: PermissionUpdateRequest): Promise<Permission> {
    const response = await request.put(`/user-management/permissions/${id}`, data)
    return response
  },

  // 删除权限
  async deletePermission(id: string): Promise<void> {
    await request.delete(`/user-management/permissions/${id}`)
  },

  // 按资源类型获取权限
  async getPermissionsByResourceType(
    ziyuan_leixing: string,
    zhuangtai = 'active'
  ): Promise<Permission[]> {
    const response = await request.get(
      `/user-management/permissions/by-resource-type/${ziyuan_leixing}`,
      {
        params: { zhuangtai },
      }
    )
    return response
  },

  // 获取权限统计信息
  async getPermissionStatistics(): Promise<PermissionStatistics> {
    const response = await request.get('/user-management/permissions/statistics/summary')
    return response
  },
}
