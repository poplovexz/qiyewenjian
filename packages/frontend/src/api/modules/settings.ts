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

// ==================== 系统配置相关 ====================

/** 系统配置项 */
export interface SystemConfig {
  id: string
  config_key: string
  config_value: string | null
  config_type: string
  config_name: string | null
  config_desc: string | null
  default_value: string | null
  value_type: string | null
  is_editable: string
  sort_order: number
  created_at: string
  updated_at: string
}

/** 系统信息 */
export interface SystemInfo {
  system_name: string
  version: string
  environment: string
  database_status: string
  redis_status: string
  uptime: string
}

/** 缓存清除响应 */
export interface CacheClearResponse {
  message: string
  cleared_keys: number
}

/**
 * 获取系统信息
 */
export function getSystemInfo() {
  return request<SystemInfo>({
    url: '/system/info',
    method: 'get'
  })
}

/**
 * 获取所有配置
 */
export function getAllConfigs(configType?: string) {
  return request<SystemConfig[]>({
    url: '/system/configs',
    method: 'get',
    params: configType ? { config_type: configType } : undefined
  })
}

/**
 * 获取单个配置
 */
export function getConfigByKey(configKey: string) {
  return request<SystemConfig>({
    url: `/system/configs/${configKey}`,
    method: 'get'
  })
}

/**
 * 更新单个配置
 */
export function updateConfig(configKey: string, configValue: string) {
  return request<SystemConfig>({
    url: `/system/configs/${configKey}`,
    method: 'put',
    data: { config_value: configValue }
  })
}

/**
 * 批量更新配置
 */
export function batchUpdateConfigs(configs: Record<string, string>) {
  return request<{ updated: Record<string, string>; errors: Record<string, string> }>({
    url: '/system/configs',
    method: 'put',
    data: { configs }
  })
}

/**
 * 清除缓存
 */
export function clearCache(pattern?: string) {
  return request<CacheClearResponse>({
    url: '/system/cache/clear',
    method: 'post',
    params: pattern ? { pattern } : undefined
  })
}

