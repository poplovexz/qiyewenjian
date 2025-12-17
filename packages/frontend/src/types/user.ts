/**
 * 用户相关类型定义
 */

// 基础分页参数
export interface BaseListParams {
  page: number
  size: number
}

// 基础分页响应
export interface BaseListResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages?: number
}

// 权限
export interface Permission {
  id: string
  quanxian_ming: string
  quanxian_bianma?: string
  miaoshu?: string
  ziyuan_leixing: 'menu' | 'button' | 'api'
  ziyuan_lujing?: string
  zhuangtai: 'active' | 'inactive'
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 角色
export interface Role {
  id: string
  jiaose_ming: string
  jiaose_bianma?: string
  miaoshu?: string
  zhuangtai: 'active' | 'inactive'
  permissions?: Permission[]
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
  permission_count?: number
  user_count?: number
}

// 用户
export interface User {
  id: string
  yonghu_ming: string
  youxiang: string
  xingming: string
  shouji: string
  zhuangtai: 'active' | 'inactive'
  denglu_cishu: string
  zuihou_denglu?: string
  roles?: Role[]
  permissions?: Permission[]
  created_at: string
  updated_at: string
}

// 用户创建参数
export interface UserCreate {
  yonghu_ming: string
  mima: string
  youxiang: string
  xingming: string
  shouji: string
  zhuangtai: 'active' | 'inactive'
}

// 用户更新参数
export interface UserUpdate {
  youxiang?: string
  xingming?: string
  shouji?: string
  zhuangtai?: 'active' | 'inactive'
}

// 用户列表查询参数
export interface UserListParams extends BaseListParams {
  yonghu_ming?: string
  xingming?: string
  youxiang?: string
  zhuangtai?: 'active' | 'inactive' | ''
}

// 用户列表响应
export interface UserListResponse extends BaseListResponse<User> {}

// 角色创建参数
export interface RoleCreate {
  jiaose_bianma?: string
  jiaose_ming: string
  miaoshu?: string
  zhuangtai: 'active' | 'inactive'
}

// 角色更新参数
export interface RoleUpdate {
  jiaose_ming?: string
  miaoshu?: string
  zhuangtai?: 'active' | 'inactive'
}

// 角色列表查询参数
export interface RoleListParams extends BaseListParams {
  jiaose_ming?: string
  zhuangtai?: 'active' | 'inactive' | ''
}

// 角色列表响应
export interface RoleListResponse extends BaseListResponse<Role> {}

// 权限创建参数
export interface PermissionCreate {
  quanxian_ming: string
  quanxian_bianma?: string
  miaoshu?: string
  ziyuan_leixing: 'menu' | 'button' | 'api'
  ziyuan_lujing?: string
  zhuangtai: 'active' | 'inactive'
}

// 权限更新参数
export interface PermissionUpdate {
  quanxian_ming?: string
  quanxian_bianma?: string
  miaoshu?: string
  ziyuan_leixing?: 'menu' | 'button' | 'api'
  ziyuan_lujing?: string
  zhuangtai?: 'active' | 'inactive'
}

// 权限列表查询参数
export interface PermissionListParams extends BaseListParams {
  quanxian_ming?: string
  ziyuan_leixing?: 'menu' | 'button' | 'api'
  zhuangtai?: 'active' | 'inactive'
}

// 权限列表响应
export interface PermissionListResponse extends BaseListResponse<Permission> {}
