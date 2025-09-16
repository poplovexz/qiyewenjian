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
  created_by: string
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

// API函数类型定义
export interface PermissionAPI {
  getPermissionList(params: PermissionListRequest): Promise<PermissionListResponse>
  getPermissionById(id: string): Promise<Permission>
  createPermission(data: PermissionCreateRequest): Promise<Permission>
  updatePermission(id: string, data: PermissionUpdateRequest): Promise<Permission>
  deletePermission(id: string): Promise<void>
}
