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
  const isAuthenticated = computed(() => Boolean(accessToken.value) && Boolean(userInfo.value))
  const userRoles = computed(() => userInfo.value?.roles || [])
  const userPermissions = computed(() => userInfo.value?.permissions || [])

  // 从本地存储恢复状态
  const restoreFromStorage = async () => {
    const storedAccessToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUserInfo = localStorage.getItem('user_info')

    console.log('恢复认证状态:', {
      hasAccessToken: Boolean(storedAccessToken),
      hasRefreshToken: Boolean(storedRefreshToken),
      hasUserInfo: Boolean(storedUserInfo)
    })

    // 如果没有任何存储的认证信息，直接返回
    if (!storedAccessToken && !storedRefreshToken && !storedUserInfo) {
      console.log('ℹ️ 无存储的认证信息，跳过恢复')
      return
    }

    // 恢复token信息
    if (storedAccessToken) {
      accessToken.value = storedAccessToken
    }
    if (storedRefreshToken) {
      refreshToken.value = storedRefreshToken
    }

    // 恢复用户信息
    if (storedUserInfo) {
      try {
        userInfo.value = JSON.parse(storedUserInfo)
        console.log('✅ 认证状态恢复成功')
      } catch (error) {
        console.error('解析用户信息失败:', error)
        // 只清除用户信息，保留token
        localStorage.removeItem('user_info')
        userInfo.value = null
      }
    }

    // 如果有token但没有用户信息，静默处理（不进行API调用）
    if (storedAccessToken && !storedUserInfo) {
      console.log('ℹ️ 有token但无用户信息，将在首次API调用时验证')
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

      // 兼容后端不同的响应结构
      const tokenInfo = response.token ?? {
        access_token: response.access_token || '',
        refresh_token: response.refresh_token || '',
        token_type: response.token_type || 'bearer',
        expires_in: response.expires_in ?? 0
      }

      // 验证必须有access_token，refresh_token可选（兼容旧版本）
      if (!tokenInfo.access_token) {
        throw new Error('登录响应缺少access_token')
      }

      // 保存令牌和用户信息
      accessToken.value = tokenInfo.access_token
      refreshToken.value = tokenInfo.refresh_token || tokenInfo.access_token // 如果没有refresh_token，使用access_token
      userInfo.value = response.user

      // 保存到本地存储
      saveToStorage(tokenInfo, response.user)

      ElMessage.success(response.message || '登录成功')
      return true
    } catch (error: any) {
      console.error('登录失败:', error)
      ElMessage.error(error.response?.data?.detail || error.message || '登录失败')
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
    // admin用户拥有所有权限
    if (userInfo.value?.yonghu_ming === 'admin') {
      return true
    }
    return userPermissions.value.includes(permission)
  }

  // 检查角色
  const hasRole = (role: string): boolean => {
    return userRoles.value.includes(role)
  }

  // 注意：不在这里自动调用 restoreFromStorage()，而是在 main.ts 中显式调用

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
