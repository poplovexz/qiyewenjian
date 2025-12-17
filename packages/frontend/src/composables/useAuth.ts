/**
 * 认证相关组合式函数
 */
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/modules/auth'
import type { LoginRequest, ChangePasswordRequest } from '@/api/auth'

export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()

  // 计算属性
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const userInfo = computed(() => authStore.userInfo)
  const isLoading = computed(() => authStore.isLoading)
  const userRoles = computed(() => authStore.userRoles)
  const userPermissions = computed(() => authStore.userPermissions)

  // 登录
  const login = async (loginData: LoginRequest): Promise<boolean> => {
    const success = await authStore.login(loginData)
    if (success) {
      // 登录成功后跳转到首页或之前访问的页面
      const redirect = router.currentRoute.value.query.redirect as string
      await router.push(redirect || '/')
    }
    return success
  }

  // 登出
  const logout = async () => {
    await authStore.logout()
    await router.push('/login')
  }

  // 修改密码
  const changePassword = async (passwordData: ChangePasswordRequest): Promise<boolean> => {
    return await authStore.changePassword(passwordData)
  }

  // 检查权限
  const hasPermission = (permission: string): boolean => {
    return authStore.hasPermission(permission)
  }

  // 检查角色
  const hasRole = (role: string): boolean => {
    return authStore.hasRole(role)
  }

  // 检查多个权限（需要全部拥有）
  const hasAllPermissions = (permissions: string[]): boolean => {
    return permissions.every(permission => hasPermission(permission))
  }

  // 检查多个权限（拥有其中一个即可）
  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some(permission => hasPermission(permission))
  }

  // 检查多个角色（需要全部拥有）
  const hasAllRoles = (roles: string[]): boolean => {
    return roles.every(role => hasRole(role))
  }

  // 检查多个角色（拥有其中一个即可）
  const hasAnyRole = (roles: string[]): boolean => {
    return roles.some(role => hasRole(role))
  }

  // 刷新用户信息
  const refreshUserInfo = async (): Promise<boolean> => {
    return await authStore.getCurrentUser()
  }

  return {
    // 状态
    isAuthenticated,
    userInfo,
    isLoading,
    userRoles,
    userPermissions,

    // 方法
    login,
    logout,
    changePassword,
    hasPermission,
    hasRole,
    hasAllPermissions,
    hasAnyPermission,
    hasAllRoles,
    hasAnyRole,
    refreshUserInfo
  }
}
