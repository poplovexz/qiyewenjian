// 用户相关类型
export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'accountant' | 'customer_service' | 'customer'
  createdAt?: string
  updatedAt?: string
}

// 客户相关类型
export interface Customer {
  id: string
  companyName: string
  socialCreditCode: string
  legalPerson: string
  contactPhone: string
  address: string
  status: 'active' | 'renewing' | 'terminated'
  createdAt: string
  updatedAt: string
}

// 合同相关类型
export interface Contract {
  id: string
  customerId: string
  templateType: string
  content: string
  status: 'draft' | 'pending' | 'signed' | 'expired'
  signedAt?: string
  expiresAt: string
  createdAt: string
  updatedAt: string
}

// 订单相关类型
export interface Order {
  id: string
  customerId: string
  packageType: string
  amount: number
  status: 'pending' | 'paid' | 'cancelled'
  paymentMethod?: string
  paidAt?: string
  createdAt: string
  updatedAt: string
}

// 任务相关类型
export interface Task {
  id: string
  customerId: string
  assigneeId?: string
  title: string
  description: string
  type: 'accounting' | 'tax_filing' | 'consultation'
  priority: 'low' | 'medium' | 'high'
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  dueDate: string
  createdAt: string
  updatedAt: string
}

// API 响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 分页类型
export interface Pagination {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: Pagination
}
