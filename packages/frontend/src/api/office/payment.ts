/**
 * 对外付款申请API
 */
import request from '@/utils/request'

// 通用列表参数类型
interface ListParams {
  page?: number
  size?: number
  [key: string]: string | number | undefined
}

export interface PaymentApplication {
  id?: string
  shenqing_bianhao?: string
  shenqing_ren_id?: string
  fukuan_duixiang: string
  fukuan_jine: number
  fukuan_yuanyin: string
  fukuan_fangshi: string
  shoukuan_zhanghu: string
  shoukuan_yinhang?: string
  yaoqiu_fukuan_shijian?: string
  fujian_lujing?: string
  shenhe_zhuangtai?: string
  fukuan_zhuangtai?: string
  shiji_fukuan_shijian?: string
  fukuan_liushui_hao?: string
  beizhu?: string
  created_at?: string
  shenqing_ren_xingming?: string
}

export function getPaymentList(params: ListParams) {
  return request({
    url: '/office/payment',
    method: 'get',
    params
  })
}

export function getPaymentDetail(id: string) {
  return request({
    url: `/office/payment/${id}`,
    method: 'get'
  })
}

export function createPayment(data: PaymentApplication) {
  return request({
    url: '/office/payment',
    method: 'post',
    data
  })
}

export function updatePayment(id: string, data: Partial<PaymentApplication>) {
  return request({
    url: `/office/payment/${id}`,
    method: 'put',
    data
  })
}

export function deletePayment(id: string) {
  return request({
    url: `/office/payment/${id}`,
    method: 'delete'
  })
}

/**
 * 提交审批
 */
export function submitPaymentForApproval(id: string) {
  return request({
    url: `/office/payment/${id}/submit`,
    method: 'post'
  })
}

/**
 * 审批通过
 */
export function approvePayment(id: string, shenhe_yijian?: string) {
  return request({
    url: `/office/payment/${id}/approve`,
    method: 'post',
    params: { shenhe_yijian }
  })
}

/**
 * 审批拒绝
 */
export function rejectPayment(id: string, shenhe_yijian: string) {
  return request({
    url: `/office/payment/${id}/reject`,
    method: 'post',
    params: { shenhe_yijian }
  })
}
