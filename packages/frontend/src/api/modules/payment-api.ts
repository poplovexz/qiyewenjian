/**
 * 第三方支付API模块
 */
import request from '@/utils/request'

export interface CreatePaymentRequest {
  dingdan_id: string
  zhifu_pingtai: 'weixin' | 'zhifubao'
  zhifu_fangshi: 'jsapi' | 'app' | 'h5' | 'native' | 'page' | 'wap'
  openid?: string
  return_url?: string
  quit_url?: string
}

// 微信支付数据
export interface WeixinPaymentData {
  prepay_id?: string
  code_url?: string
  h5_url?: string
  app_params?: Record<string, string>
}

// 支付宝支付数据
export interface AlipayPaymentData {
  form_html?: string
  pay_url?: string
}

export interface CreatePaymentResponse {
  dingdan_id: string
  dingdan_bianhao: string
  zhifu_pingtai: string
  zhifu_fangshi: string
  payment_data: WeixinPaymentData | AlipayPaymentData
}

// 查询结果类型
export interface PaymentQueryResult {
  trade_state?: string
  trade_state_desc?: string
  transaction_id?: string
  time_end?: string
}

export interface QueryPaymentResponse {
  dingdan_id: string
  dingdan_bianhao: string
  zhifu_zhuangtai: string
  zhifu_pingtai?: string
  disanfang_dingdan_hao?: string
  disanfang_liushui_hao?: string
  query_result: PaymentQueryResult
}

/**
 * 创建第三方支付
 */
export function createPayment(data: CreatePaymentRequest) {
  return request<CreatePaymentResponse>({
    url: '/payment-api/create',
    method: 'post',
    data,
  })
}

/**
 * 查询支付订单状态
 */
export function queryPayment(dingdanId: string) {
  return request<QueryPaymentResponse>({
    url: `/payment-api/query/${dingdanId}`,
    method: 'get',
  })
}

/**
 * 关闭支付订单
 */
export function closePayment(dingdanId: string) {
  return request<{ message: string }>({
    url: `/payment-api/close/${dingdanId}`,
    method: 'post',
  })
}
