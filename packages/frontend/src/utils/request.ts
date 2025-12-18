/**
 * HTTP 请求工具
 */
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/modules/auth'
import { tokenManager } from '@/utils/tokenManager'
import router from '@/router'

// 创建 axios 实例
const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    Pragma: 'no-cache',
  },
})

// 请求拦截器
instance.interceptors.request.use(
  async (config) => {
    const timestamp = new Date().toISOString()

    // 🔧 修复死锁：检查是否是刷新token或登录请求，避免循环依赖和超时
    const isAuthRequest =
      config.url?.includes('/auth/refresh') || config.url?.includes('/auth/login')

    if (isAuthRequest) {
      // 认证相关请求不需要等待初始化，直接放行
      return config
    }

    // 等待认证初始化完成

    const initStart = Date.now()
    await tokenManager.waitForAuthInit()
    const initDuration = Date.now() - initStart

    // 🔧 优化：只在特定条件下执行预防性刷新，避免过度刷新
    // 1. 不是登录请求
    // 2. 不是已经在刷新中
    // 3. 确实需要刷新
    if (!tokenManager.isTokenRefreshing) {
      const refreshStart = Date.now()
      await tokenManager.preventiveRefresh()
      const refreshDuration = Date.now() - refreshStart
    }

    const authStore = useAuthStore()
    const token = authStore.accessToken || localStorage.getItem('access_token')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    } else {
    }

    return config
  },
  (error) => {
    console.error('❌ 请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  async (error) => {
    const authStore = useAuthStore()

    if (error.response) {
      const { status, data, config } = error.response

      switch (status) {
        case 401:
          // 🔧 修复：登录和刷新token请求返回401是正常的，不应该尝试刷新token
          const isAuthRequest =
            config.url?.includes('/auth/login') || config.url?.includes('/auth/refresh')

          if (isAuthRequest) {
            // 登录失败或刷新token失败，直接返回错误，不尝试刷新
            return Promise.reject(error)
          }

          // 其他请求返回401，尝试刷新token

          try {
            // 如果已经在刷新中，将请求加入队列
            if (tokenManager.isTokenRefreshing) {
              const retryConfig = await tokenManager.addPendingRequest(error.config)
              return instance(retryConfig)
            }

            // 尝试刷新token
            const refreshSuccess = await tokenManager.refreshToken()
            if (refreshSuccess) {
              // 更新请求头
              const newToken = localStorage.getItem('access_token')
              if (newToken) {
                error.config.headers.Authorization = `Bearer ${newToken}`
              }
              return instance(error.config)
            } else {
              // 不要继续重试，避免无限循环
              ElMessage.error('登录已过期，请重新登录')
              // 跳转到登录页
              if (window.location.pathname !== '/login') {
                window.location.href = '/login'
              }
              return Promise.reject(new Error('Token刷新失败，请重新登录'))
            }
          } catch (refreshError) {
            console.error('❌ Token刷新过程出错:', refreshError)
            ElMessage.error('认证失败，请重新登录')
            // 跳转到登录页
            if (window.location.pathname !== '/login') {
              window.location.href = '/login'
            }
            return Promise.reject(new Error('认证失败，请重新登录'))
          }
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.detail || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

// 导出请求方法
export const request = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.get(url, config)
  },

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.post(url, data, config)
  },

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.put(url, data, config)
  },

  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.delete(url, config)
  },

  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.patch(url, data, config)
  },
}

export default instance
