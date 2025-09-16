import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials: { email: string; password: string }) => {
    try {
      // 这里将来会调用 API
      console.log('登录凭据:', credentials)
      
      // 模拟登录成功
      const mockToken = 'mock-jwt-token'
      const mockUser: User = {
        id: '1',
        email: credentials.email,
        name: '测试用户',
        role: 'admin',
      }

      token.value = mockToken
      user.value = mockUser
      localStorage.setItem('token', mockToken)
      
      return { success: true }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: '登录失败' }
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  const checkAuth = () => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      token.value = storedToken
      // 这里将来会验证 token 并获取用户信息
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    checkAuth,
  }
})
