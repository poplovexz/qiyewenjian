/**
 * 线索管理 API
 */
import { request } from '@/utils/request'
import type {
  Xiansuo,
  XiansuoCreate,
  XiansuoUpdate,
  XiansuoDetail,
  XiansuoListResponse,
  XiansuoListParams,
  XiansuoStatusUpdate,
  XiansuoAssignUpdate,
  XiansuoStatistics,
  XiansuoLaiyuan,
  XiansuoLaiyuanCreate,
  XiansuoLaiyuanUpdate,
  XiansuoLaiyuanListResponse,
  XiansuoLaiyuanListParams,
  XiansuoZhuangtai,
  XiansuoZhuangtaiCreate,
  XiansuoZhuangtaiListResponse,
  XiansuoGenjin,
  XiansuoGenjinCreate,
  XiansuoGenjinUpdate,
  XiansuoGenjinListResponse,
  XiansuoGenjinListParams,
  XiansuoBaojia,
  XiansuoBaojiaCreate,
  XiansuoBaojiaUpdate,
  XiansuoBaojiaListParams,
  XiansuoBaojiaListResponse,
  XiansuoBaojiaDetail,
  ChanpinDataForBaojia
} from '@/types/xiansuo'

// 线索管理 API
export const xiansuoApi = {
  // 创建线索
  create: (data: XiansuoCreate) => {
    return request.post<Xiansuo>('/leads/', data)
  },

  // 获取线索列表
  getList: (params: XiansuoListParams = {}) => {
    return request.get<XiansuoListResponse>('/leads/', { params })
  },

  // 获取线索详情
  getDetail: (id: string) => {
    return request.get<XiansuoDetail>(`/leads/${id}`)
  },

  // 更新线索信息
  update: (id: string, data: XiansuoUpdate) => {
    return request.put<Xiansuo>(`/leads/${id}`, data)
  },

  // 删除线索
  delete: (id: string) => {
    return request.delete(`/leads/${id}`)
  },

  // 更新线索状态
  updateStatus: (id: string, data: XiansuoStatusUpdate) => {
    return request.patch<Xiansuo>(`/leads/${id}/status`, data)
  },

  // 分配线索
  assign: (id: string, data: XiansuoAssignUpdate) => {
    return request.patch<Xiansuo>(`/leads/${id}/assign`, data)
  },

  // 获取线索统计
  getStatistics: (params: { start_date?: string; end_date?: string; fenpei_ren_id?: string } = {}) => {
    return request.get<XiansuoStatistics>('/leads/statistics', { params })
  },

  // 获取线索的合同状态
  getContractStatus: (id: string) => {
    return request.get<{
      contract_status: string | null
      contract_id: string | null
      audit_status: string | null
      audit_workflow_id: string | null
      audit_details: {
        workflow_id: string
        workflow_number: string
        current_step: number
        total_steps: number
        steps: Array<{
          step_number: number
          step_name: string
          auditor_name: string
          auditor_id: string
          status: string
          comment: string | null
          audit_time: string | null
        }>
        created_at: string | null
        completed_at: string | null
      } | null
    }>(`/leads/${id}/contract-status`)
  }
}

// 线索来源管理 API
export const xiansuoLaiyuanApi = {
  // 创建线索来源
  create: (data: XiansuoLaiyuanCreate) => {
    return request.post<XiansuoLaiyuan>('/lead-sources/', data)
  },

  // 获取线索来源列表
  getList: (params: XiansuoLaiyuanListParams = {}) => {
    return request.get<XiansuoLaiyuanListResponse>('/lead-sources/', { params })
  },

  // 获取启用的线索来源
  getActiveList: () => {
    return request.get<XiansuoLaiyuan[]>('/lead-sources/active')
  },

  // 获取线索来源详情
  getDetail: (id: string) => {
    return request.get<XiansuoLaiyuan>(`/lead-sources/${id}`)
  },

  // 更新线索来源
  update: (id: string, data: XiansuoLaiyuanUpdate) => {
    return request.put<XiansuoLaiyuan>(`/lead-sources/${id}`, data)
  },

  // 删除线索来源
  delete: (id: string) => {
    return request.delete(`/lead-sources/${id}`)
  }
}

// 线索状态管理 API
export const xiansuoZhuangtaiApi = {
  // 创建线索状态
  create: (data: XiansuoZhuangtaiCreate) => {
    return request.post<XiansuoZhuangtai>('/lead-statuses/', data)
  },

  // 获取线索状态列表
  getList: (params: { page?: number; size?: number; search?: string; zhuangtai_leixing?: string; zhuangtai?: string } = {}) => {
    return request.get<XiansuoZhuangtaiListResponse>('/lead-statuses/', { params })
  },

  // 获取启用的线索状态
  getActiveList: () => {
    return request.get<XiansuoZhuangtai[]>('/lead-statuses/active')
  },

  // 获取线索状态详情
  getDetail: (id: string) => {
    return request.get<XiansuoZhuangtai>(`/lead-statuses/${id}`)
  },

  // 更新线索状态
  update: (id: string, data: Partial<XiansuoZhuangtaiCreate>) => {
    return request.put<XiansuoZhuangtai>(`/lead-statuses/${id}`, data)
  },

  // 删除线索状态
  delete: (id: string) => {
    return request.delete(`/lead-statuses/${id}`)
  }
}

// 线索跟进记录管理 API
export const xiansuoGenjinApi = {
  // 创建跟进记录
  create: (data: XiansuoGenjinCreate) => {
    return request.post<XiansuoGenjin>('/lead-followups/', data)
  },

  // 获取跟进记录列表
  getList: (params: XiansuoGenjinListParams = {}) => {
    return request.get<XiansuoGenjinListResponse>('/lead-followups/', { params })
  },

  // 获取指定线索的跟进记录
  getByXiansuo: (xiansuoId: string) => {
    return request.get<XiansuoGenjin[]>(`/lead-followups/xiansuo/${xiansuoId}`)
  },

  // 获取跟进记录详情
  getDetail: (id: string) => {
    return request.get<XiansuoGenjin>(`/lead-followups/${id}`)
  },

  // 更新跟进记录
  update: (id: string, data: XiansuoGenjinUpdate) => {
    return request.put<XiansuoGenjin>(`/lead-followups/${id}`, data)
  },

  // 删除跟进记录
  delete: (id: string) => {
    return request.delete(`/lead-followups/${id}`)
  }
}

// 线索报价管理 API
export const xiansuoBaojiaApi = {
  // 创建报价
  create: (data: XiansuoBaojiaCreate) => {
    return request.post<XiansuoBaojia>('/lead-quotes/', data)
  },

  // 获取指定线索的报价列表
  getByXiansuo: (xiansuoId: string) => {
    return request.get<XiansuoBaojia[]>(`/lead-quotes/xiansuo/${xiansuoId}`)
  },

  // 获取报价详情
  getDetail: (id: string) => {
    return request.get<XiansuoBaojia>(`/lead-quotes/${id}`)
  },

  // 获取包含线索信息的报价详情
  getDetailWithXiansuo: (id: string) => {
    return request.get<XiansuoBaojiaDetail>(`/lead-quotes/${id}/detail`)
  },

  // 更新报价
  update: (id: string, data: XiansuoBaojiaUpdate) => {
    return request.put<XiansuoBaojia>(`/lead-quotes/${id}`, data)
  },

  // 删除报价
  delete: (id: string) => {
    return request.delete(`/lead-quotes/${id}`)
  },

  // 获取产品数据用于报价
  getProductData: () => {
    return request.get<ChanpinDataForBaojia>('/lead-quotes/product-data')
  },

  // 确认报价
  confirm: (id: string) => {
    return request.post<XiansuoBaojia>(`/lead-quotes/${id}/confirm`)
  },

  // 拒绝报价
  reject: (id: string) => {
    return request.post<XiansuoBaojia>(`/lead-quotes/${id}/reject`)
  }
}
