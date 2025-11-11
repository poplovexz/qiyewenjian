/**
 * 服务工单管理 API
 */
import { request } from '@/utils/request'

/**
 * 服务工单 API
 */
export const serviceOrderApi = {
  /**
   * 基于合同创建服务工单
   */
  createFromContract(hetongId: string) {
    return request.post(`/service-orders/from-contract/${hetongId}`)
  },

  /**
   * 获取合同关联的工单列表
   */
  getByContract(hetongId: string) {
    return request.get('/service-orders/', {
      params: { hetong_id: hetongId }
    })
  },

  /**
   * 获取工单详情
   */
  getDetail(id: string) {
    return request.get(`/service-orders/${id}`)
  },

  /**
   * 获取工单列表
   */
  getList(params: any = {}) {
    return request.get('/service-orders/', { params })
  }
}

