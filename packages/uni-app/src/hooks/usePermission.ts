/**
 * 权限检查 Hook
 */
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

export const usePermission = () => {
  const userStore = useUserStore()

  // 检查单个权限
  const hasPermission = (permission: string): boolean => {
    return userStore.hasPermission(permission)
  }

  // 检查多个权限（全部满足）
  const hasAllPermissions = (permissions: string[]): boolean => {
    return userStore.hasAllPermissions(permissions)
  }

  // 检查多个权限（满足其一）
  const hasAnyPermission = (permissions: string[]): boolean => {
    return userStore.hasAnyPermission(permissions)
  }

  // 常用权限的计算属性
  const canViewTask = computed(() => hasPermission('task:view'))
  const canEditTask = computed(() => hasPermission('task:edit'))
  const canCreateTask = computed(() => hasPermission('task:create'))
  const canDeleteTask = computed(() => hasPermission('task:delete'))

  return {
    hasPermission,
    hasAllPermissions,
    hasAnyPermission,
    canViewTask,
    canEditTask,
    canCreateTask,
    canDeleteTask
  }
}

