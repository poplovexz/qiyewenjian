/**
 * 设置相关API
 */
import request from '../request'

// ==================== 类型定义 ====================

/** 用户个人信息 */
export interface UserProfile {
  id: string
  yonghu_ming: string
  xingming: string
  shouji?: string
  youxiang?: string
  zhuangtai: string
  created_at: string
}

/** 更新个人信息 */
export interface UserProfileUpdate {
  xingming?: string
  shouji?: string
  youxiang?: string
}

/** 修改密码 */
export interface PasswordChange {
  old_password: string
  new_password: string
}

/** 用户偏好设置 */
export interface UserPreferences {
  email_notification: boolean
  sms_notification: boolean
  system_notification: boolean
}

/** 更新用户偏好 */
export interface UserPreferencesUpdate {
  email_notification?: boolean
  sms_notification?: boolean
  system_notification?: boolean
}

// ==================== API 函数 ====================

/**
 * 获取个人信息
 */
export function getUserProfile() {
  return request<UserProfile>({
    url: '/users/me/profile',
    method: 'get'
  })
}

/**
 * 更新个人信息
 */
export function updateUserProfile(data: UserProfileUpdate) {
  return request<UserProfile>({
    url: '/users/me/profile',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 */
export function changePassword(data: PasswordChange) {
  return request<{ message: string }>({
    url: '/users/me/password',
    method: 'put',
    data
  })
}

/**
 * 获取用户偏好设置
 */
export function getUserPreferences() {
  return request<UserPreferences>({
    url: '/users/me/preferences',
    method: 'get'
  })
}

/**
 * 更新用户偏好设置
 */
export function updateUserPreferences(data: UserPreferencesUpdate) {
  return request<UserPreferences>({
    url: '/users/me/preferences',
    method: 'put',
    data
  })
}

