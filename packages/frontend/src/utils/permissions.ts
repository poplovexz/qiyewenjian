/**
 * 权限检查工具
 */
import { useAuthStore } from '@/stores/modules/auth'

/**
 * 检查用户是否具有指定权限
 * @param permission 权限编码
 * @returns 是否具有权限
 */
export function hasPermission(permission: string): boolean {
  const authStore = useAuthStore()
  const userPermissions = authStore.userPermissions || []

  // 超级管理员拥有所有权限
  if (authStore.userInfo?.yonghu_ming === 'admin') {
    return true
  }

  // 拥有全量权限标记
  if (userPermissions.includes('all')) {
    return true
  }

  return userPermissions.includes(permission)
}

/**
 * 检查用户是否具有任意一个权限
 * @param permissions 权限编码数组
 * @returns 是否具有任意权限
 */
export function hasAnyPermission(permissions: string[]): boolean {
  return permissions.some(permission => hasPermission(permission))
}

/**
 * 检查用户是否具有所有权限
 * @param permissions 权限编码数组
 * @returns 是否具有所有权限
 */
export function hasAllPermissions(permissions: string[]): boolean {
  return permissions.every(permission => hasPermission(permission))
}

/**
 * 客户管理相关权限常量
 */
export const CUSTOMER_PERMISSIONS = {
  // 菜单权限
  MENU: 'customer:menu',
  
  // 基础权限
  READ: 'customer:read',
  CREATE: 'customer:create',
  UPDATE: 'customer:update',
  DELETE: 'customer:delete',
  
  // 状态管理
  STATUS_MANAGE: 'customer:status_manage',
  
  // 按钮权限
  CREATE_BUTTON: 'customer:create_button',
  EDIT_BUTTON: 'customer:edit_button',
  DELETE_BUTTON: 'customer:delete_button',
  STATUS_BUTTON: 'customer:status_button'
} as const

/**
 * 服务记录相关权限常量
 */
export const SERVICE_RECORD_PERMISSIONS = {
  READ: 'service_record:read',
  CREATE: 'service_record:create',
  UPDATE: 'service_record:update',
  DELETE: 'service_record:delete',
  MANAGE_BUTTON: 'service_record:manage_button'
} as const

/**
 * 用户管理相关权限常量
 */
export const USER_PERMISSIONS = {
  // 菜单权限
  MENU: 'user:menu',

  // 基础权限
  READ: 'user:read',
  CREATE: 'user:create',
  UPDATE: 'user:update',
  DELETE: 'user:delete',

  // 特殊权限
  RESET_PASSWORD: 'user:reset_password',
  STATUS_MANAGE: 'user:status_manage',

  // 按钮权限
  CREATE_BUTTON: 'user:create_button',
  EDIT_BUTTON: 'user:edit_button',
  DELETE_BUTTON: 'user:delete_button',
  RESET_PASSWORD_BUTTON: 'user:reset_password_button'
} as const

/**
 * 角色管理相关权限常量
 */
export const ROLE_PERMISSIONS = {
  // 菜单权限
  MENU: 'role:menu',

  // 基础权限
  READ: 'role:read',
  CREATE: 'role:create',
  UPDATE: 'role:update',
  DELETE: 'role:delete',

  // 特殊权限
  PERMISSION_MANAGE: 'role:permission_manage',

  // 按钮权限
  CREATE_BUTTON: 'role:create_button',
  EDIT_BUTTON: 'role:edit_button',
  DELETE_BUTTON: 'role:delete_button',
  PERMISSION_MANAGE_BUTTON: 'role:permission_manage_button'
} as const

/**
 * 权限管理相关权限常量
 */
export const PERMISSION_PERMISSIONS = {
  // 菜单权限
  MENU: 'permission:menu',

  // 基础权限
  READ: 'permission:read',
  CREATE: 'permission:create',
  UPDATE: 'permission:update',
  DELETE: 'permission:delete',

  // 按钮权限
  CREATE_BUTTON: 'permission:create_button',
  EDIT_BUTTON: 'permission:edit_button',
  DELETE_BUTTON: 'permission:delete_button'
} as const

/**
 * 权限检查指令 - Vue 3 Composition API
 */
export function usePermission() {
  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    
    // 客户管理权限检查
    canViewCustomers: () => hasPermission(CUSTOMER_PERMISSIONS.READ),
    canCreateCustomer: () => hasPermission(CUSTOMER_PERMISSIONS.CREATE),
    canEditCustomer: () => hasPermission(CUSTOMER_PERMISSIONS.UPDATE),
    canDeleteCustomer: () => hasPermission(CUSTOMER_PERMISSIONS.DELETE),
    canManageCustomerStatus: () => hasPermission(CUSTOMER_PERMISSIONS.STATUS_MANAGE),
    
    // 服务记录权限检查
    canViewServiceRecords: () => hasPermission(SERVICE_RECORD_PERMISSIONS.READ),
    canCreateServiceRecord: () => hasPermission(SERVICE_RECORD_PERMISSIONS.CREATE),
    canEditServiceRecord: () => hasPermission(SERVICE_RECORD_PERMISSIONS.UPDATE),
    canDeleteServiceRecord: () => hasPermission(SERVICE_RECORD_PERMISSIONS.DELETE),
    
    // 按钮显示权限
    showCreateCustomerButton: () => hasPermission(CUSTOMER_PERMISSIONS.CREATE_BUTTON),
    showEditCustomerButton: () => hasPermission(CUSTOMER_PERMISSIONS.EDIT_BUTTON),
    showDeleteCustomerButton: () => hasPermission(CUSTOMER_PERMISSIONS.DELETE_BUTTON),
    showStatusManageButton: () => hasPermission(CUSTOMER_PERMISSIONS.STATUS_BUTTON),
    showServiceRecordButton: () => hasPermission(SERVICE_RECORD_PERMISSIONS.MANAGE_BUTTON),

    // 用户管理权限检查
    canViewUsers: () => hasPermission(USER_PERMISSIONS.READ),
    canCreateUser: () => hasPermission(USER_PERMISSIONS.CREATE),
    canEditUser: () => hasPermission(USER_PERMISSIONS.UPDATE),
    canDeleteUser: () => hasPermission(USER_PERMISSIONS.DELETE),
    canResetPassword: () => hasPermission(USER_PERMISSIONS.RESET_PASSWORD),
    canManageUserStatus: () => hasPermission(USER_PERMISSIONS.STATUS_MANAGE),

    // 用户管理按钮权限
    showCreateUserButton: () => hasPermission(USER_PERMISSIONS.CREATE_BUTTON),
    showEditUserButton: () => hasPermission(USER_PERMISSIONS.EDIT_BUTTON),
    showDeleteUserButton: () => hasPermission(USER_PERMISSIONS.DELETE_BUTTON),
    showResetPasswordButton: () => hasPermission(USER_PERMISSIONS.RESET_PASSWORD_BUTTON),

    // 角色管理权限检查
    canViewRoles: () => hasPermission(ROLE_PERMISSIONS.READ),
    canCreateRole: () => hasPermission(ROLE_PERMISSIONS.CREATE),
    canEditRole: () => hasPermission(ROLE_PERMISSIONS.UPDATE),
    canDeleteRole: () => hasPermission(ROLE_PERMISSIONS.DELETE),
    canManageRolePermissions: () => hasPermission(ROLE_PERMISSIONS.PERMISSION_MANAGE),

    // 角色管理按钮权限
    showCreateRoleButton: () => hasPermission(ROLE_PERMISSIONS.CREATE_BUTTON),
    showEditRoleButton: () => hasPermission(ROLE_PERMISSIONS.EDIT_BUTTON),
    showDeleteRoleButton: () => hasPermission(ROLE_PERMISSIONS.DELETE_BUTTON),
    showPermissionManageButton: () => hasPermission(ROLE_PERMISSIONS.PERMISSION_MANAGE_BUTTON),

    // 权限管理权限检查
    canViewPermissions: () => hasPermission(PERMISSION_PERMISSIONS.READ),
    canCreatePermission: () => hasPermission(PERMISSION_PERMISSIONS.CREATE),
    canEditPermission: () => hasPermission(PERMISSION_PERMISSIONS.UPDATE),
    canDeletePermission: () => hasPermission(PERMISSION_PERMISSIONS.DELETE),

    // 权限管理按钮权限
    showCreatePermissionButton: () => hasPermission(PERMISSION_PERMISSIONS.CREATE_BUTTON),
    showEditPermissionButton: () => hasPermission(PERMISSION_PERMISSIONS.EDIT_BUTTON),
    showDeletePermissionButton: () => hasPermission(PERMISSION_PERMISSIONS.DELETE_BUTTON)
  }
}

/**
 * 权限检查装饰器（用于路由守卫）
 */
export function requirePermission(permission: string) {
  return () => {
    if (!hasPermission(permission)) {
      throw new Error(`权限不足：需要 ${permission} 权限`)
    }
    return true
  }
}

/**
 * 权限检查装饰器（用于路由守卫，需要任意权限）
 */
export function requireAnyPermission(permissions: string[]) {
  return () => {
    if (!hasAnyPermission(permissions)) {
      throw new Error(`权限不足：需要以下任意权限之一：${permissions.join(', ')}`)
    }
    return true
  }
}
