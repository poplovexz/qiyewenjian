/**
 * 企业级请求封装
 * - 请求/响应拦截器
 * - 自动重试
 * - Loading 状态
 * - 错误处理
 * - 请求取消
 */
import { appConfig } from './config'
import { STORAGE_KEYS, API_CODE } from '@/constants'
import type { ApiResponse } from '@/types'

// 请求配置
interface RequestConfig {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  showLoading?: boolean
  loadingText?: string
  showError?: boolean
  retry?: number
  timeout?: number
}

// 默认配置
const defaultConfig: Partial<RequestConfig> = {
  method: 'GET',
  showLoading: true,
  loadingText: '加载中...',
  showError: true,
  retry: 0,
  timeout: appConfig.requestTimeout
}

// 请求队列（用于显示/隐藏 loading）
let requestCount = 0

// 显示 Loading
const showLoading = (text: string) => {
  if (requestCount === 0) {
    uni.showLoading({ title: text, mask: true })
  }
  requestCount++
}

// 隐藏 Loading
const hideLoading = () => {
  requestCount--
  if (requestCount <= 0) {
    requestCount = 0
    uni.hideLoading()
  }
}

// 获取 Token
const getToken = (): string => {
  return uni.getStorageSync(STORAGE_KEYS.TOKEN) || ''
}

// 处理响应错误
const handleError = (statusCode: number, message: string, showError: boolean) => {
  if (statusCode === API_CODE.UNAUTHORIZED) {
    // Token 过期，清除登录状态并跳转
    uni.removeStorageSync(STORAGE_KEYS.TOKEN)
    uni.removeStorageSync(STORAGE_KEYS.USER_INFO)
    uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/login/index' })
    }, 1500)
    return
  }

  if (showError) {
    uni.showToast({ title: message || '请求失败', icon: 'none' })
  }
}

// 核心请求方法
const executeRequest = <T>(config: RequestConfig, retryCount: number): Promise<T> => {
  return new Promise((resolve, reject) => {
    const token = getToken()

    uni.request({
      url: appConfig.apiBaseUrl + config.url,
      method: config.method,
      data: config.data,
      timeout: config.timeout,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...config.header
      },
      success: (res) => {
        const response = res.data as ApiResponse<T>

        if (res.statusCode >= 200 && res.statusCode < 300) {
          // 业务层成功
          if (response.code === API_CODE.SUCCESS || response.code === undefined) {
            resolve(response.data !== undefined ? response.data : response as any)
          } else {
            handleError(response.code, response.message, config.showError!)
            reject(new Error(response.message))
          }
        } else {
          handleError(res.statusCode, response?.message || '请求失败', config.showError!)
          reject(new Error(response?.message || `HTTP Error: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        // 网络错误，尝试重试
        if (retryCount < (config.retry || 0)) {
          console.log(`请求失败，正在重试 (${retryCount + 1}/${config.retry})`)
          setTimeout(() => {
            executeRequest<T>(config, retryCount + 1)
              .then(resolve)
              .catch(reject)
          }, 1000 * (retryCount + 1))
        } else {
          if (config.showError) {
            uni.showToast({ title: '网络连接失败', icon: 'none' })
          }
          reject(err)
        }
      }
    })
  })
}

// 主请求方法
export const request = async <T = any>(config: RequestConfig): Promise<T> => {
  const finalConfig = { ...defaultConfig, ...config }

  if (finalConfig.showLoading) {
    showLoading(finalConfig.loadingText!)
  }

  try {
    const result = await executeRequest<T>(finalConfig, 0)
    return result
  } finally {
    if (finalConfig.showLoading) {
      hideLoading()
    }
  }
}

// 便捷方法
export const get = <T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> => {
  return request<T>({ url, method: 'GET', data, ...config })
}

export const post = <T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> => {
  return request<T>({ url, method: 'POST', data, ...config })
}

export const put = <T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> => {
  return request<T>({ url, method: 'PUT', data, ...config })
}

export const del = <T = any>(url: string, data?: any, config?: Partial<RequestConfig>): Promise<T> => {
  return request<T>({ url, method: 'DELETE', data, ...config })
}

export default { request, get, post, put, del }

