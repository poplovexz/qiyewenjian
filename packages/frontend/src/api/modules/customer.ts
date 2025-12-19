/**
 * 客户管理 API
 */
import { request } from '@/utils/request'

// 客户相关接口类型定义
export interface Customer {
  id: string
  gongsi_mingcheng: string
  tongyi_shehui_xinyong_daima: string
  chengli_riqi?: string
  zhuce_dizhi?: string
  faren_xingming: string
  faren_shenfenzheng?: string
  faren_lianxi?: string
  lianxi_dianhua?: string
  lianxi_youxiang?: string
  lianxi_dizhi?: string
  yingye_zhizhao_lujing?: string
  yingye_zhizhao_youxiao_qi?: string
  kehu_zhuangtai: 'active' | 'renewing' | 'terminated'
  fuwu_kaishi_riqi?: string
  fuwu_jieshu_riqi?: string
  created_at: string
  updated_at: string
  created_by: string
}

export interface CustomerCreate {
  gongsi_mingcheng: string
  tongyi_shehui_xinyong_daima: string
  chengli_riqi?: string
  zhuce_dizhi?: string
  faren_xingming: string
  faren_shenfenzheng?: string
  faren_lianxi?: string
  lianxi_dianhua?: string
  lianxi_youxiang?: string
  lianxi_dizhi?: string
  yingye_zhizhao_lujing?: string
  yingye_zhizhao_youxiao_qi?: string
  kehu_zhuangtai?: 'active' | 'renewing' | 'terminated'
  fuwu_kaishi_riqi?: string
  fuwu_jieshu_riqi?: string
}

export interface CustomerUpdate {
  gongsi_mingcheng?: string
  tongyi_shehui_xinyong_daima?: string
  chengli_riqi?: string
  zhuce_dizhi?: string
  faren_xingming?: string
  faren_shenfenzheng?: string
  faren_lianxi?: string
  lianxi_dianhua?: string
  lianxi_youxiang?: string
  lianxi_dizhi?: string
  yingye_zhizhao_lujing?: string
  yingye_zhizhao_youxiao_qi?: string
  kehu_zhuangtai?: 'active' | 'renewing' | 'terminated'
  fuwu_kaishi_riqi?: string
  fuwu_jieshu_riqi?: string
}

export interface CustomerListParams {
  page?: number
  size?: number
  search?: string
  kehu_zhuangtai?: string
}

export interface CustomerListResponse {
  total: number
  items: Customer[]
  page: number
  size: number
}

// 客户管理 API
export const customerApi = {
  // 创建客户
  create: (data: CustomerCreate) => {
    return request.post<Customer>('/customers/', data)
  },

  // 获取客户列表
  getList: (params: CustomerListParams = {}) => {
    return request.get<CustomerListResponse>('/customers/', { params })
  },

  // 获取客户详情
  getDetail: (id: string) => {
    return request.get<Customer>(`/customers/${id}`)
  },

  // 更新客户信息
  update: (id: string, data: CustomerUpdate) => {
    return request.put<Customer>(`/customers/${id}`, data)
  },

  // 删除客户
  delete: (id: string) => {
    return request.delete(`/customers/${id}`)
  },

  // 更新客户状态
  updateStatus: (id: string, status: string) => {
    return request.patch<Customer>(`/customers/${id}/status`, null, {
      params: { new_status: status }
    })
  },

  // 获取客户统计信息
  getStatistics: () => {
    return request.get<{
      total_customers: number
      active_customers: number
      renewing_customers: number
      terminated_customers: number
      monthly_new_customers: number
      status_distribution: Record<string, number>
    }>('/customers/statistics/overview')
  },

  // 批量更新客户状态
  batchUpdateStatus: (customerIds: string[], status: string) => {
    return request.post<{
      updated_count: number
      total_requested: number
      new_status: string
    }>('/customers/batch/status', customerIds, {
      params: { new_status: status }
    })
  },

  // 批量删除客户
  batchDelete: (customerIds: string[]) => {
    return request.post<{
      deleted_count: number
      total_requested: number
    }>('/customers/batch/delete', customerIds)
  },

  // 高级搜索客户
  advancedSearch: (searchParams: {
    gongsi_mingcheng?: string
    tongyi_shehui_xinyong_daima?: string
    faren_xingming?: string
    kehu_zhuangtai?: string
    fuwu_kaishi_start?: string
    fuwu_kaishi_end?: string
    created_start?: string
    created_end?: string
    page?: number
    size?: number
  }) => {
    return request.post<CustomerListResponse>('/customers/search/advanced', searchParams)
  }
}

// 服务记录相关接口类型定义
export interface ServiceRecord {
  id: string
  kehu_id: string
  goutong_fangshi: 'phone' | 'email' | 'online' | 'meeting'
  goutong_neirong: string
  goutong_shijian: string
  wenti_leixing?: 'zhangwu' | 'shuiwu' | 'zixun' | 'other'
  wenti_miaoshu?: string
  chuli_zhuangtai: 'pending' | 'processing' | 'completed' | 'cancelled'
  chuli_jieguo?: string
  chuli_ren_id?: string
  created_at: string
  updated_at: string
  created_by: string
}

export interface ServiceRecordCreate {
  kehu_id: string
  goutong_fangshi: 'phone' | 'email' | 'online' | 'meeting'
  goutong_neirong: string
  goutong_shijian: string
  wenti_leixing?: 'zhangwu' | 'shuiwu' | 'zixun' | 'other'
  wenti_miaoshu?: string
  chuli_zhuangtai?: 'pending' | 'processing' | 'completed' | 'cancelled'
  chuli_jieguo?: string
  chuli_ren_id?: string
}

export interface ServiceRecordUpdate {
  goutong_fangshi?: 'phone' | 'email' | 'online' | 'meeting'
  goutong_neirong?: string
  goutong_shijian?: string
  wenti_leixing?: 'zhangwu' | 'shuiwu' | 'zixun' | 'other'
  wenti_miaoshu?: string
  chuli_zhuangtai?: 'pending' | 'processing' | 'completed' | 'cancelled'
  chuli_jieguo?: string
  chuli_ren_id?: string
}

export interface ServiceRecordListParams {
  page?: number
  size?: number
  kehu_id?: string
  goutong_fangshi?: string
  wenti_leixing?: string
  chuli_zhuangtai?: string
  search?: string
}

export interface ServiceRecordListResponse {
  total: number
  items: ServiceRecord[]
  page: number
  size: number
}

// 服务记录管理 API
export const serviceRecordApi = {
  // 创建服务记录
  create: (data: ServiceRecordCreate) => {
    return request.post<ServiceRecord>('/service-records/', data)
  },

  // 获取服务记录列表
  getList: (params: ServiceRecordListParams = {}) => {
    return request.get<ServiceRecordListResponse>('/service-records/', { params })
  },

  // 获取服务记录详情
  getDetail: (id: string) => {
    return request.get<ServiceRecord>(`/service-records/${id}`)
  },

  // 更新服务记录
  update: (id: string, data: ServiceRecordUpdate) => {
    return request.put<ServiceRecord>(`/service-records/${id}`, data)
  },

  // 删除服务记录
  delete: (id: string) => {
    return request.delete(`/service-records/${id}`)
  },

  // 获取客户的服务记录
  getCustomerRecords: (customerId: string, params: { page?: number; size?: number } = {}) => {
    return request.get<ServiceRecordListResponse>(`/service-records/kehu/${customerId}/records`, { params })
  },

  // 更新处理状态
  updateStatus: (id: string, status: string, result?: string) => {
    return request.patch<ServiceRecord>(`/service-records/${id}/status`, null, {
      params: { new_status: status, chuli_jieguo: result }
    })
  },

  // 获取服务记录统计信息
  getStatistics: (customerId?: string) => {
    return request.get<{
      total_records: number
      monthly_records: number
      communication_distribution: Record<string, number>
      problem_type_distribution: Record<string, number>
      status_distribution: Record<string, number>
      pending_count: number
      processing_count: number
      completed_count: number
    }>('/service-records/statistics/overview', {
      params: customerId ? { kehu_id: customerId } : {}
    })
  },

  // 批量更新服务记录状态
  batchUpdateStatus: (recordIds: string[], status: string, result?: string) => {
    return request.post<{
      updated_count: number
      total_requested: number
      new_status: string
    }>('/service-records/batch/status', recordIds, {
      params: { new_status: status, chuli_jieguo: result }
    })
  },

  // 批量删除服务记录
  batchDelete: (recordIds: string[]) => {
    return request.post<{
      deleted_count: number
      total_requested: number
    }>('/service-records/batch/delete', recordIds)
  },

  // 获取客户服务记录摘要
  getCustomerSummary: (customerId: string) => {
    return request.get<{
      customer_info: {
        id: string
        gongsi_mingcheng: string
        kehu_zhuangtai: string
      }
      service_statistics: {
        total_records: number
        completed_records: number
        pending_records: number
      }
      recent_records: ServiceRecord[]
      pending_issues: number
    }>(`/service-records/kehu/${customerId}/summary`)
  }
}
