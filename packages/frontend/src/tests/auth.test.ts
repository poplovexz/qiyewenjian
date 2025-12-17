/**
 * 认证功能测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/modules/auth'
import { authApi } from '@/api/auth'

// Mock API
vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
    refreshToken: vi.fn(),
    changePassword: vi.fn(),
    logout: vi.fn()
  }
}))

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn()
  }
}))

describe('认证 Store 测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    // 清除 localStorage
    localStorage.clear()
    // 重置所有 mock
    vi.clearAllMocks()
  })

  it('应该正确初始化状态', () => {
    const authStore = useAuthStore()
    
    expect(authStore.accessToken).toBe('')
    expect(authStore.refreshToken).toBe('')
    expect(authStore.userInfo).toBeNull()
    expect(authStore.isLoading).toBe(false)
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('应该正确处理登录成功', async () => {
    const authStore = useAuthStore()
    const mockResponse = {
      message: '登录成功',
      user: {
        id: '1',
        yonghu_ming: 'testuser',
        xingming: '测试用户',
        youxiang: 'test@example.com',
        shouji: '13800138000',
        zhuangtai: '正常',
        zuihou_denglu: '2024-01-01T00:00:00Z',
        denglu_cishu: '1',
        roles: ['user'],
        permissions: ['read']
      },
      token: {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_123',
        token_type: 'bearer',
        expires_in: 3600
      }
    }

    vi.mocked(authApi.login).mockResolvedValue(mockResponse)

    const result = await authStore.login({
      yonghu_ming: 'testuser',
      mima: 'password'
    })

    expect(result).toBe(true)
    expect(authStore.accessToken).toBe('access_token_123')
    expect(authStore.refreshToken).toBe('refresh_token_123')
    expect(authStore.userInfo).toEqual(mockResponse.user)
    expect(authStore.isAuthenticated).toBe(true)
    
    // 检查本地存储
    expect(localStorage.getItem('access_token')).toBe('access_token_123')
    expect(localStorage.getItem('refresh_token')).toBe('refresh_token_123')
    expect(localStorage.getItem('user_info')).toBe(JSON.stringify(mockResponse.user))
  })

  it('应该正确处理登录失败', async () => {
    const authStore = useAuthStore()
    
    vi.mocked(authApi.login).mockRejectedValue(new Error('登录失败'))

    const result = await authStore.login({
      yonghu_ming: 'testuser',
      mima: 'wrongpassword'
    })

    expect(result).toBe(false)
    expect(authStore.accessToken).toBe('')
    expect(authStore.refreshToken).toBe('')
    expect(authStore.userInfo).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('应该正确处理登出', async () => {
    const authStore = useAuthStore()
    
    // 先设置一些状态
    authStore.accessToken = 'test_token'
    authStore.refreshToken = 'test_refresh'
    authStore.userInfo = {
      id: '1',
      yonghu_ming: 'testuser',
      xingming: '测试用户',
      youxiang: 'test@example.com',
      shouji: '13800138000',
      zhuangtai: '正常',
      zuihou_denglu: '2024-01-01T00:00:00Z',
      denglu_cishu: '1',
      roles: ['user'],
      permissions: ['read']
    }
    localStorage.setItem('access_token', 'test_token')
    localStorage.setItem('refresh_token', 'test_refresh')
    localStorage.setItem('user_info', JSON.stringify(authStore.userInfo))

    vi.mocked(authApi.logout).mockResolvedValue({ message: '登出成功' })

    await authStore.logout()

    expect(authStore.accessToken).toBe('')
    expect(authStore.refreshToken).toBe('')
    expect(authStore.userInfo).toBeNull()
    expect(authStore.isAuthenticated).toBe(false)
    
    // 检查本地存储已清除
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
    expect(localStorage.getItem('user_info')).toBeNull()
  })

  it('应该正确检查权限', () => {
    const authStore = useAuthStore()
    
    authStore.userInfo = {
      id: '1',
      yonghu_ming: 'testuser',
      xingming: '测试用户',
      youxiang: 'test@example.com',
      shouji: '13800138000',
      zhuangtai: '正常',
      zuihou_denglu: '2024-01-01T00:00:00Z',
      denglu_cishu: '1',
      roles: ['admin', 'user'],
      permissions: ['read', 'write', 'delete']
    }

    expect(authStore.hasPermission('read')).toBe(true)
    expect(authStore.hasPermission('write')).toBe(true)
    expect(authStore.hasPermission('admin')).toBe(false)
    
    expect(authStore.hasRole('admin')).toBe(true)
    expect(authStore.hasRole('user')).toBe(true)
    expect(authStore.hasRole('guest')).toBe(false)
  })

  it('应该正确从本地存储恢复状态', () => {
    const userInfo = {
      id: '1',
      yonghu_ming: 'testuser',
      xingming: '测试用户',
      youxiang: 'test@example.com',
      shouji: '13800138000',
      zhuangtai: '正常',
      zuihou_denglu: '2024-01-01T00:00:00Z',
      denglu_cishu: '1',
      roles: ['user'],
      permissions: ['read']
    }

    localStorage.setItem('access_token', 'stored_token')
    localStorage.setItem('refresh_token', 'stored_refresh')
    localStorage.setItem('user_info', JSON.stringify(userInfo))

    const authStore = useAuthStore()
    authStore.restoreFromStorage()

    expect(authStore.accessToken).toBe('stored_token')
    expect(authStore.refreshToken).toBe('stored_refresh')
    expect(authStore.userInfo).toEqual(userInfo)
    expect(authStore.isAuthenticated).toBe(true)
  })
})
