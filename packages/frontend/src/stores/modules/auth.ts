/**
 * 认证状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type LoginRequest, type UserInfo, type TokenResponse, type ChangePasswordRequest } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const accessToken = ref<string>('')
  const refreshToken = ref<string>('')
  const userInfo = ref<UserInfo | null>(null)
  const isLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!accessToken.value && !!userInfo.value)
  const userRoles = computed(() => userInfo.value?.roles || [])
  const userPermissions = computed(() => userInfo.value?.permissions || [])

  // 从本地存储恢复状态
  const restoreFromStorage = () => {
    const storedAccessToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUserInfo = localStorage.getItem('user_info')

    if (storedAccessToken) {
      accessToken.value = storedAccessToken
    }
    if (storedRefreshToken) {
      refreshToken.value = storedRefreshToken
    }
    if (storedUserInfo) {
      try {
        userInfo.value = JSON.parse(storedUserInfo)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        clearStorage()
      }
    }
  }

  // 保存到本地存储
  const saveToStorage = (tokens: TokenResponse, user: UserInfo) => {
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    localStorage.setItem('user_info', JSON.stringify(user))
  }

  // 清除本地存储
  const clearStorage = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  }

  // 用户登录
  const login = async (loginData: LoginRequest): Promise<boolean> => {
    try {
      isLoading.value = true
      const response = await authApi.login(loginData)
      
      // 保存令牌和用户信息
      accessToken.value = response.token.access_token
      refreshToken.value = response.token.refresh_token
      userInfo.value = response.user
      
      // 保存到本地存储
      saveToStorage(response.token, response.user)
      
      ElMessage.success(response.message || '登录成功')
      return true
    } catch (error: any) {
      console.error('登录失败:', error)
      ElMessage.error(error.response?.data?.detail || '登录失败')
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 刷新访问令牌
  const refreshAccessToken = async (): Promise<boolean> => {
    if (!refreshToken.value) {
      return false
    }

    try {
      const response = await authApi.refreshToken({
        refresh_token: refreshToken.value
      })
      
      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token
      
      // 更新本地存储
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      
      return true
    } catch (error) {
      console.error('刷新令牌失败:', error)
      logout()
      return false
    }
  }

  // 获取当前用户信息
  const getCurrentUser = async (): Promise<boolean> => {
    if (!accessToken.value) {
      return false
    }

    try {
      const user = await authApi.getCurrentUser()
      userInfo.value = user
      localStorage.setItem('user_info', JSON.stringify(user))
      return true
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return false
    }
  }

  // 修改密码
  const changePassword = async (passwordData: ChangePasswordRequest): Promise<boolean> => {
    try {
      isLoading.value = true
      const response = await authApi.changePassword(passwordData)
      ElMessage.success(response.message || '密码修改成功')
      return true
    } catch (error: any) {
      console.error('修改密码失败:', error)
      ElMessage.error(error.response?.data?.detail || '修改密码失败')
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 用户登出
  const logout = async () => {
    try {
      if (accessToken.value) {
        await authApi.logout()
      }
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      // 清除状态和本地存储
      accessToken.value = ''
      refreshToken.value = ''
      userInfo.value = null
      clearStorage()
      ElMessage.success('已退出登录')
    }
  }

  // 检查权限
  const hasPermission = (permission: string): boolean => {
    return userPermissions.value.includes(permission)
  }

  // 检查角色
  const hasRole = (role: string): boolean => {
    return userRoles.value.includes(role)
  }

  // 初始化时恢复状态
  restoreFromStorage()

  return {
    // 状态
    accessToken,
    refreshToken,
    userInfo,
    isLoading,
    
    // 计算属性
    isAuthenticated,
    userRoles,
    userPermissions,
    
    // 方法
    login,
    logout,
    refreshAccessToken,
    getCurrentUser,
    changePassword,
    hasPermission,
    hasRole,
    restoreFromStorage
  }
})
