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

// API函数类型定义
export interface RoleAPI {
  getRoleList(params: RoleListRequest): Promise<RoleListResponse>
  getRoleById(id: string): Promise<Role>
  createRole(data: RoleCreateRequest): Promise<Role>
  updateRole(id: string, data: RoleUpdateRequest): Promise<Role>
  deleteRole(id: string): Promise<void>
  updateRoleStatus(id: string, data: RoleStatusRequest): Promise<Role>
  getRolePermissions(id: string): Promise<Permission[]>
  updateRolePermissions(id: string, data: RolePermissionRequest): Promise<void>
  getRoleUsers(id: string): Promise<User[]>
}
