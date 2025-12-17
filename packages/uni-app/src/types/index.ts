/**
 * 全局类型定义
 */

// API 响应结构
export interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
  timestamp?: number
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// 分页请求参数
export interface PaginationParams {
  page?: number
  pageSize?: number
}

// 用户信息
export interface UserInfo {
  id: number
  username: string
  name: string
  phone?: string
  email?: string
  avatar?: string
  role: string
  permissions: string[]
  createdAt?: string
}

// 任务项
export interface TaskItem {
  id: number
  title: string
  description?: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  assigneeId: number
  assigneeName?: string
  projectId?: number
  projectName?: string
  dueDate?: string
  startedAt?: string
  completedAt?: string
  createdAt: string
  updatedAt: string
}

// 任务统计
export interface TaskStatistics {
  total: number
  pending: number
  inProgress: number
  completed: number
  overdue: number
}

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应
export interface LoginResponse {
  token: string
  user: UserInfo
}

