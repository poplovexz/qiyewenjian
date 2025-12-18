/**
 * 用户状态管理 - 企业级
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { STORAGE_KEYS } from '@/constants'
import { post, get } from '@/utils/request'
import type { UserInfo, LoginResponse } from '@/types'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string>('')
  const userInfo = ref<UserInfo | null>(null)
  const permissions = ref<string[]>([])

  // 计算属性
  const isLoggedIn = computed(() => Boolean(token.value))
  const userName = computed(() => userInfo.value?.name || '')
  const userRole = computed(() => userInfo.value?.role || '')

  // 设置 Token
  const setToken = (newToken: string) => {
    token.value = newToken
    uni.setStorageSync(STORAGE_KEYS.TOKEN, newToken)
  }

  // 获取 Token
  const getToken = (): string => {
    if (!token.value) {
      token.value = uni.getStorageSync(STORAGE_KEYS.TOKEN) || ''
    }
    return token.value
  }

  // 设置用户信息
  const setUserInfo = (info: UserInfo) => {
    userInfo.value = info
    permissions.value = info.permissions || []
    uni.setStorageSync(STORAGE_KEYS.USER_INFO, JSON.stringify(info))
    uni.setStorageSync(STORAGE_KEYS.PERMISSIONS, JSON.stringify(info.permissions || []))
  }

  // 登录
  const login = async (username: string, password: string) => {
    try {
      const res = await post<LoginResponse>('/auth/login', { username, password }, {
        showLoading: true,
        loadingText: '登录中...'
      })

      setToken(res.token)
      setUserInfo(res.user)

      return { success: true }
    } catch (error: any) {
      // 开发环境 Mock 登录
      if (import.meta.env.DEV) {
        const mockToken = 'dev_token_' + Date.now()
        const mockUser: UserInfo = {
          id: 1,
          username,
          name: '测试用户',
          role: '服务人员',
          permissions: ['task:view', 'task:edit', 'task:create']
        }
        setToken(mockToken)
        setUserInfo(mockUser)
        return { success: true }
      }
      throw error
    }
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      const res = await get<UserInfo>('/users/me', {}, { showLoading: false })
      setUserInfo(res)
      return res
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }

  // 退出登录
  const logout = () => {
    token.value = ''
    userInfo.value = null
    permissions.value = []
    uni.removeStorageSync(STORAGE_KEYS.TOKEN)
    uni.removeStorageSync(STORAGE_KEYS.USER_INFO)
    uni.removeStorageSync(STORAGE_KEYS.PERMISSIONS)
  }

  // 恢复登录状态
  const restoreLogin = () => {
    const savedToken = uni.getStorageSync(STORAGE_KEYS.TOKEN)
    const savedUserInfo = uni.getStorageSync(STORAGE_KEYS.USER_INFO)
    const savedPermissions = uni.getStorageSync(STORAGE_KEYS.PERMISSIONS)

    if (savedToken) {
      token.value = savedToken
      try {
        if (savedUserInfo) userInfo.value = JSON.parse(savedUserInfo)
        if (savedPermissions) permissions.value = JSON.parse(savedPermissions)
      } catch (e) {
        logout()
      }
    }
  }

  // 检查权限
  const hasPermission = (permission: string): boolean => {
    return permissions.value.includes(permission)
  }

  // 检查多个权限（AND）
  const hasAllPermissions = (perms: string[]): boolean => {
    return perms.every(p => permissions.value.includes(p))
  }

  // 检查多个权限（OR）
  const hasAnyPermission = (perms: string[]): boolean => {
    return perms.some(p => permissions.value.includes(p))
  }

  return {
    // 状态
    token,
    userInfo,
    permissions,
    // 计算属性
    isLoggedIn,
    userName,
    userRole,
    // 方法
    setToken,
    getToken,
    setUserInfo,
    login,
    fetchUserInfo,
    logout,
    restoreLogin,
    hasPermission,
    hasAllPermissions,
    hasAnyPermission
  }
})

