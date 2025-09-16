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
  if (authStore.user?.yonghu_ming === 'admin') {
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
    showServiceRecordButton: () => hasPermission(SERVICE_RECORD_PERMISSIONS.MANAGE_BUTTON)
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
