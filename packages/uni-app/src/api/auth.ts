/**
 * 认证相关 API
 */
import { post, get } from '@/utils/request'

// 登录
export const login = (username: string, password: string) => {
  return post('/auth/login', { username, password })
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return get('/users/me')
}

// 退出登录
export const logout = () => {
  return post('/auth/logout')
}

