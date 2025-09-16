/**
 * 认证相关 API 接口
 */
import { request } from '@/utils/request'

// 认证相关类型定义
export interface LoginRequest {
  yonghu_ming: string
  mima: string
}

export interface LoginResponse {
  message: string
  user: UserInfo
  token: TokenResponse
}

export interface UserInfo {
  id: string
  yonghu_ming: string
  xingming: string
  youxiang: string
  shouji: string
  zhuangtai: string
  zuihou_denglu: string
  denglu_cishu: number
  roles: string[]
  permissions: string[]
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface ChangePasswordRequest {
  jiu_mima: string
  xin_mima: string
  queren_mima: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

// 认证 API 接口
export const authApi = {
  /**
   * 用户登录
   */
  login(data: LoginRequest): Promise<LoginResponse> {
    return request.post('/api/v1/auth/login', data)
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser(): Promise<UserInfo> {
    return request.get('/api/v1/auth/me')
  },

  /**
   * 刷新访问令牌
   */
  refreshToken(data: RefreshTokenRequest): Promise<TokenResponse> {
    return request.post('/api/v1/auth/refresh', data)
  },

  /**
   * 修改密码
   */
  changePassword(data: ChangePasswordRequest): Promise<{ message: string }> {
    return request.post('/api/v1/auth/change-password', data)
  },

  /**
   * 用户登出
   */
  logout(): Promise<{ message: string }> {
    return request.post('/api/v1/auth/logout')
  }
}
