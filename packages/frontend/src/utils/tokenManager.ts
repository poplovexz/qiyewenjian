/**
 * Token管理器 - 解决并发刷新和认证状态管理问题
 */
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'
import router from '@/router'
import type { InternalAxiosRequestConfig } from 'axios'

interface PendingRequest {
  resolve: (value: unknown) => void
  reject: (reason: unknown) => void
  config: InternalAxiosRequestConfig
}

class TokenManager {
  private _isRefreshing = false
  private pendingRequests: PendingRequest[] = []
  private refreshPromise: Promise<boolean> | null = null
  private authInitialized = false
  private initPromise: Promise<void> | null = null
  private lastRefreshTime = 0 // 上次刷新时间，用于防抖

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
    const storedAccessToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUserInfo = localStorage.getItem('user_info')

    // 如果没有任何认证信息，直接完成初始化
    if (!storedAccessToken && !storedRefreshToken && !storedUserInfo) {
      this.authInitialized = true
      return
    }

    // 如果没有access token，直接完成初始化
    if (!storedAccessToken) {
      this.authInitialized = true
      return
    }

    // 检查token是否明显过期（避免不必要的API调用）
    if (this._isTokenExpired(storedAccessToken)) {
      try {
        const refreshSuccess = await this._refreshTokenInternal(storedRefreshToken)
        if (!refreshSuccess) {
          this._clearAuth(true) // 静默清除
        }
      } catch (error) {
        this._clearAuth(true) // 静默清除
      }
      this.authInitialized = true
      return
    }

    // 如果token看起来有效，延迟验证到实际需要时

    this.authInitialized = true
  }

  /**
   * 解码JWT载荷，兼容base64url编码
   */
  private _decodeTokenPayload(token: string): Record<string, any> {
    const parts = token.split('.')
    if (parts.length < 2) {
      throw new Error('Invalid token format')
    }

    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const paddingLength = (4 - (base64.length % 4)) % 4
    const padded = base64 + '='.repeat(paddingLength)

    const decoded = atob(padded)
    return JSON.parse(decoded)
  }

  /**
   * 检查token是否已过期
   */
  private _isTokenExpired(token: string): boolean {
    try {
      const payload = this._decodeTokenPayload(token)
      const exp = payload.exp * 1000 // 转换为毫秒
      const now = Date.now()
      return now >= exp
    } catch (error) {
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

      return true
    } catch (error) {
      // 清除认证状态，但不立即跳转（由request拦截器处理）
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      return false
    }
  }

  /**
   * 使用原生fetch刷新token，避免axios拦截器的循环依赖
   */
  private async _refreshTokenWithFetch(refreshToken: string): Promise<{ access_token: string; refresh_token?: string }> {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
    const url = `${baseURL}/auth/refresh`

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  }

  /**
   * 添加待处理的请求
   */
  addPendingRequest(config: InternalAxiosRequestConfig): Promise<unknown> {
    return new Promise((resolve, reject) => {
      this.pendingRequests.push({ resolve, reject, config })
    })
  }

  /**
   * 重试所有待处理的请求
   */
  private _retryAllPendingRequests() {
    const requests = this.pendingRequests.splice(0)

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
  private _failAllPendingRequests(error: unknown) {
    const requests = this.pendingRequests.splice(0)

    requests.forEach(({ reject }) => {
      reject(error)
    })
  }

  /**
   * 清除认证状态
   */
  private _clearAuth(silent = false) {
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
   * 检查token是否即将过期（提前30分钟刷新，适合8小时token）
   */
  shouldRefreshToken(): boolean {
    const token = localStorage.getItem('access_token')
    if (!token) return false

    try {
      const payload = this._decodeTokenPayload(token)
      const exp = payload.exp * 1000 // 转换为毫秒
      const now = Date.now()
      const thirtyMinutes = 30 * 60 * 1000 // 30分钟缓冲时间

      const remaining = exp - now
      const shouldRefresh = remaining < thirtyMinutes

      if (shouldRefresh) {
      }

      return shouldRefresh
    } catch (error) {
      return true // 解析失败时也尝试刷新
    }
  }

  /**
   * 预防性刷新token（增加防抖逻辑）
   */
  async preventiveRefresh(): Promise<void> {
    // 如果已经在刷新中，跳过
    if (this._isRefreshing) {
      return
    }

    // 防抖：如果距离上次刷新不到1分钟，跳过
    const now = Date.now()
    const oneMinute = 60 * 1000
    if (now - this.lastRefreshTime < oneMinute) {
      return
    }

    // 检查是否需要刷新
    if (this.shouldRefreshToken()) {
      this.lastRefreshTime = now
      await this.refreshToken()
    }
  }
}

// 导出单例实例
export const tokenManager = new TokenManager()
