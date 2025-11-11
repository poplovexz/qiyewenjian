import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API || '/api/v1',
  timeout: 120000, // 增加到120秒，因为后端Redis连接可能较慢
  headers: {
    'Content-Type': 'application/json;charset=UTF-8'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config: any) => {
    const userStore = useUserStore()
    
    // 添加Token
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }

    return config
  },
  (error: AxiosError) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data

    // 如果返回的状态码不是200，则认为是错误
    if (response.status !== 200) {
      showToast({
        message: res.message || 'Error',
        type: 'fail'
      })
      return Promise.reject(new Error(res.message || 'Error'))
    }

    return res
  },
  (error: AxiosError) => {
    console.error('Response error:', error)

    if (error.response) {
      const status = error.response.status
      const data: any = error.response.data

      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          const userStore = useUserStore()
          userStore.clearUserInfo()
          router.push('/login')
          showToast({
            message: '登录已过期，请重新登录',
            type: 'fail'
          })
          break
        case 403:
          showToast({
            message: '没有权限访问',
            type: 'fail'
          })
          break
        case 404:
          showToast({
            message: '请求的资源不存在',
            type: 'fail'
          })
          break
        case 500:
          showToast({
            message: data.detail || '服务器错误',
            type: 'fail'
          })
          break
        default:
          showToast({
            message: data.detail || data.message || '请求失败',
            type: 'fail'
          })
      }
    } else if (error.request) {
      showToast({
        message: '网络错误，请检查网络连接',
        type: 'fail'
      })
    } else {
      showToast({
        message: error.message || '请求失败',
        type: 'fail'
      })
    }

    return Promise.reject(error)
  }
)

export default service

