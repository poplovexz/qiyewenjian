/**
 * 退款管理 API
 */
import request from '@/utils/request'

/**
 * 退款记录
 */
export interface Refund {
  id: string
  zhifu_dingdan_id: string
  zhifu_peizhi_id?: string
  tuikuan_danhao: string
  yuanshi_dingdan_hao: string
  disanfang_tuikuan_hao?: string
  yuanshi_jine: number
  tuikuan_jine: number
  tuikuan_yuanyin?: string
  tuikuan_zhuangtai: string
  tuikuan_pingtai: string
  shenqing_shijian?: string
  chenggong_shijian?: string
  chuli_jieguo?: string
  cuowu_xinxi?: string
  cuowu_daima?: string
  created_at?: string
  updated_at?: string
  created_by?: string
  updated_by?: string
}

/**
 * 创建退款请求
 */
export interface CreateRefundRequest {
  zhifu_dingdan_id: string
  tuikuan_jine: number
  tuikuan_yuanyin?: string
}

/**
 * 退款列表响应
 */
export interface RefundListResponse {
  total: number
  items: Refund[]
  page: number
  page_size: number
}

/**
 * 退款列表查询参数
 */
export interface RefundListParams {
  page?: number
  page_size?: number
  tuikuan_zhuangtai?: string
  tuikuan_pingtai?: string
  search?: string
}

/**
 * 退款管理 API
 */
export const refundApi = {
  /**
   * 创建退款申请
   */
  create: (data: CreateRefundRequest) => {
    return request.post<Refund>('/payment-refunds/', data)
  },

  /**
   * 获取退款列表
   */
  getList: (params: RefundListParams = {}) => {
    return request.get<RefundListResponse>('/payment-refunds/', { params })
  },

  /**
   * 获取退款详情
   */
  getDetail: (id: string) => {
    return request.get<Refund>(`/payment-refunds/${id}`)
  },
}
