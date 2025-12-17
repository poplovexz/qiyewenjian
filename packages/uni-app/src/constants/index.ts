/**
 * 全局常量配置
 */

// 存储 Key
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER_INFO: 'userInfo',
  PERMISSIONS: 'permissions',
  DEVICE_ID: 'deviceId',
  THEME: 'theme',
  LANGUAGE: 'language'
} as const

// API 状态码
export const API_CODE = {
  SUCCESS: 0,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  SERVER_ERROR: 500
} as const

// 任务状态
export const TASK_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  SKIPPED: 'skipped',
  CANCELLED: 'cancelled'
} as const

export const TASK_STATUS_MAP: Record<string, { label: string; color: string; bgColor: string }> = {
  [TASK_STATUS.PENDING]: { label: '待处理', color: '#fa8c16', bgColor: '#fff7e6' },
  [TASK_STATUS.IN_PROGRESS]: { label: '进行中', color: '#1989fa', bgColor: '#e6f7ff' },
  [TASK_STATUS.COMPLETED]: { label: '已完成', color: '#07c160', bgColor: '#f6ffed' },
  [TASK_STATUS.SKIPPED]: { label: '已跳过', color: '#999999', bgColor: '#f5f5f5' },
  [TASK_STATUS.CANCELLED]: { label: '已取消', color: '#999999', bgColor: '#f5f5f5' }
}

// 分页默认配置
export const PAGINATION = {
  PAGE: 1,
  PAGE_SIZE: 20
} as const

// 请求超时时间（毫秒）
export const REQUEST_TIMEOUT = 30000

// 重试次数
export const RETRY_COUNT = 3

