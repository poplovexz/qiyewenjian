/**
 * Token管理器 - 解决并发刷新和认证状态管理问题
 */
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

interface PendingRequest {
  resolve: (value: any) => void
  reject: (reason: any) => void
  config: any
}

class TokenManager {
  private _isRefreshing = false
  private pendingRequests: PendingRequest[] = []
  private refreshPromise: Promise<boolean> | null = null
  private authInitialized = false
  private initPromise: Promise<void> | null = null

  /**
   * 检查是否正在刷新
   */
  get isTokenRefreshing(): boolean {
    return this._isRefreshing
  }

  /**
   * 初始化认证状态
   */
  async initializeAuth(): Promise<void> {
    if (this.authInitialized) {
      return
    }

    if (this.initPromise) {
      return this.initPromise
    }

    this.initPromise = this._doInitialize()
    await this.initPromise
  }

  private async _doInitialize(): Promise<void> {
    console.log('🔄 开始初始化认证状态...')

    const storedAccessToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUserInfo = localStorage.getItem('user_info')

    // 如果没有任何认证信息，直接完成初始化
    if (!storedAccessToken && !storedRefreshToken && !storedUserInfo) {
      console.log('ℹ️ 无存储的认证信息，跳过验证')
      this.authInitialized = true
      return
    }

    // 如果没有access token，直接完成初始化
    if (!storedAccessToken) {
      console.log('ℹ️ 无access token，跳过验证')
      this.authInitialized = true
      return
    }

    // 检查token是否明显过期（避免不必要的API调用）
    if (this._isTokenExpired(storedAccessToken)) {
      console.log('⚠️ Token已过期，尝试刷新...')
      try {
        const refreshSuccess = await this._refreshTokenInternal(storedRefreshToken)
        if (!refreshSuccess) {
          console.log('❌ Token刷新失败，清除认证状态')
          this._clearAuth(true) // 静默清除
        }
      } catch (error) {
        console.log('❌ Token刷新异常，清除认证状态')
        this._clearAuth(true) // 静默清除
      }
      this.authInitialized = true
      return
    }

    // 如果token看起来有效，延迟验证到实际需要时
    console.log('✅ Token格式有效，延迟验证到首次API调用')
    this.authInitialized = true
  }

  /**
   * 检查token是否已过期
   */
  private _isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp * 1000 // 转换为毫秒
      const now = Date.now()
      return now >= exp
    } catch (error) {
      console.error('解析token失败:', error)
      return true // 解析失败视为过期
    }
  }

  /**
   * 检查认证是否已初始化
   */
  isAuthInitialized(): boolean {
    return this.authInitialized
  }

  /**
   * 等待认证初始化完成
   */
  async waitForAuthInit(): Promise<void> {
    if (this.authInitialized) {
      return
    }
    await this.initializeAuth()
  }

  /**
   * 刷新Token（带并发控制）
   */
  async refreshToken(): Promise<boolean> {
    // 如果已经在刷新中，返回现有的Promise
    if (this._isRefreshing && this.refreshPromise) {
      return this.refreshPromise
    }

    this._isRefreshing = true
    this.refreshPromise = this._doRefresh()

    try {
      const result = await this.refreshPromise
      return result
    } finally {
      this._isRefreshing = false
      this.refreshPromise = null
    }
  }

  private async _doRefresh(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      this._failAllPendingRequests('No refresh token available')
      return false
    }

    try {
      const success = await this._refreshTokenInternal(refreshToken)
      if (success) {
        this._retryAllPendingRequests()
        return true
      } else {
        this._failAllPendingRequests('Token refresh failed')
        return false
      }
    } catch (error) {
      this._failAllPendingRequests(error)
      return false
    }
  }

  private async _refreshTokenInternal(refreshToken: string): Promise<boolean> {
    try {
      // 🔧 修复死锁：使用不带拦截器的原生fetch避免循环依赖
      const response = await this._refreshTokenWithFetch(refreshToken)
      
      // 更新localStorage
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      
      console.log('✅ Token刷新成功')
      return true
    } catch (error) {
      console.error('❌ Token刷新失败:', error)
      this._clearAuth()
      return false
    }
  }

  /**
   * 使用原生fetch刷新token，避免axios拦截器的循环依赖
   */
  private async _refreshTokenWithFetch(refreshToken: string): Promise<any> {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const url = `${baseURL}/api/v1/auth/refresh`

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: refreshToken
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  }

  /**
   * 添加待处理的请求
   */
  addPendingRequest(config: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.pendingRequests.push({ resolve, reject, config })
    })
  }

  /**
   * 重试所有待处理的请求
   */
  private _retryAllPendingRequests() {
    const requests = this.pendingRequests.splice(0)
    console.log(`🔄 重试 ${requests.length} 个待处理请求`)
    
    requests.forEach(({ resolve, config }) => {
      // 更新Authorization头
      const newToken = localStorage.getItem('access_token')
      if (newToken) {
        config.headers.Authorization = `Bearer ${newToken}`
      }
      resolve(config)
    })
  }

  /**
   * 失败所有待处理的请求
   */
  private _failAllPendingRequests(error: any) {
    const requests = this.pendingRequests.splice(0)
    console.log(`❌ 失败 ${requests.length} 个待处理请求`)
    
    requests.forEach(({ reject }) => {
      reject(error)
    })
  }

  /**
   * 清除认证状态
   */
  private _clearAuth(silent: boolean = false) {
    console.log('🧹 清除认证状态')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')

    // 如果是静默清除（如初始化时），不跳转和显示消息
    if (silent) {
      return
    }

    // 只有在不是登录页面时才跳转和显示消息
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    }
  }

  /**
   * 检查token是否即将过期（提前5分钟刷新）
   */
  shouldRefreshToken(): boolean {
    const token = localStorage.getItem('access_token')
    if (!token) return false

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp * 1000 // 转换为毫秒
      const now = Date.now()
      const fiveMinutes = 5 * 60 * 1000

      return (exp - now) < fiveMinutes
    } catch (error) {
      console.error('解析token失败:', error)
      return true // 解析失败时也尝试刷新
    }
  }

  /**
   * 预防性刷新token
   */
  async preventiveRefresh(): Promise<void> {
    if (this.shouldRefreshToken() && !this._isRefreshing) {
      console.log('🔄 执行预防性token刷新')
      await this.refreshToken()
    }
  }
}

// 导出单例实例
export const tokenManager = new TokenManager()
