/**
 * 支付配置API模块
 */
import request from '@/utils/request'

export interface ZhifuPeizhiCreate {
  peizhi_mingcheng: string
  peizhi_leixing: 'weixin' | 'zhifubao' | 'yinhang' | 'xianjin'
  zhuangtai?: 'qiyong' | 'tingyong'
  huanjing?: 'shachang' | 'shengchan' | 'wuxu'

  // 微信支付配置
  weixin_appid?: string
  weixin_shanghu_hao?: string
  weixin_shanghu_siyao?: string
  weixin_zhengshu_xuliehao?: string
  weixin_api_v3_miyao?: string

  // 支付宝配置
  zhifubao_appid?: string
  zhifubao_shanghu_siyao?: string
  zhifubao_zhifubao_gongyao?: string

  // 银行汇款配置
  yinhang_mingcheng?: string
  yinhang_zhanghu_mingcheng?: string
  yinhang_zhanghu_haoma?: string
  kaihuhang_mingcheng?: string
  kaihuhang_lianhanghao?: string

  // 通用配置
  tongzhi_url?: string
  beizhu?: string
}

export interface ZhifuPeizhiUpdate {
  peizhi_mingcheng?: string
  zhuangtai?: 'qiyong' | 'tingyong'
  huanjing?: 'shachang' | 'shengchan' | 'wuxu'

  // 微信支付配置
  weixin_appid?: string
  weixin_shanghu_hao?: string
  weixin_shanghu_siyao?: string
  weixin_zhengshu_xuliehao?: string
  weixin_api_v3_miyao?: string

  // 支付宝配置
  zhifubao_appid?: string
  zhifubao_shanghu_siyao?: string
  zhifubao_zhifubao_gongyao?: string

  // 银行汇款配置
  yinhang_mingcheng?: string
  yinhang_zhanghu_mingcheng?: string
  yinhang_zhanghu_haoma?: string
  kaihuhang_mingcheng?: string
  kaihuhang_lianhanghao?: string

  // 通用配置
  tongzhi_url?: string
  beizhu?: string
}

export interface ZhifuPeizhiResponse {
  id: string
  peizhi_mingcheng: string
  peizhi_leixing: 'weixin' | 'zhifubao' | 'yinhang' | 'xianjin'
  zhuangtai: 'qiyong' | 'tingyong'
  huanjing: 'shachang' | 'shengchan' | 'wuxu'

  // 微信支付配置（脱敏）
  weixin_appid?: string
  weixin_shanghu_hao?: string
  weixin_shanghu_siyao_masked?: string
  weixin_zhengshu_xuliehao?: string
  weixin_api_v3_miyao_masked?: string

  // 支付宝配置（脱敏）
  zhifubao_appid?: string
  zhifubao_shanghu_siyao_masked?: string
  zhifubao_zhifubao_gongyao_masked?: string

  // 银行汇款配置
  yinhang_mingcheng?: string
  yinhang_zhanghu_mingcheng?: string
  yinhang_zhanghu_haoma?: string
  kaihuhang_mingcheng?: string
  kaihuhang_lianhanghao?: string

  // 通用配置
  tongzhi_url?: string
  beizhu?: string

  // 审计字段
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

export interface ZhifuPeizhiListResponse {
  total: number
  items: ZhifuPeizhiResponse[]
  page?: number
  page_size?: number
}

export interface ZhifuPeizhiListParams {
  page?: number
  page_size?: number
  peizhi_leixing?: 'weixin' | 'zhifubao' | 'yinhang' | 'xianjin'
  zhuangtai?: 'qiyong' | 'tingyong'
  search?: string
}

/**
 * 创建支付配置
 */
export function createZhifuPeizhi(data: ZhifuPeizhiCreate) {
  return request<ZhifuPeizhiResponse>({
    url: '/payment-configs/',
    method: 'post',
    data
  })
}

/**
 * 获取支付配置列表
 */
export function getZhifuPeizhiList(params?: ZhifuPeizhiListParams) {
  return request<ZhifuPeizhiListResponse>({
    url: '/payment-configs/',
    method: 'get',
    params
  })
}

/**
 * 获取支付配置详情
 */
export function getZhifuPeizhi(id: string) {
  return request<ZhifuPeizhiResponse>({
    url: `/payment-configs/${id}`,
    method: 'get'
  })
}

/**
 * 更新支付配置
 */
export function updateZhifuPeizhi(id: string, data: ZhifuPeizhiUpdate) {
  return request<ZhifuPeizhiResponse>({
    url: `/payment-configs/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除支付配置
 */
export function deleteZhifuPeizhi(id: string) {
  return request<{ message: string }>({
    url: `/payment-configs/${id}`,
    method: 'delete'
  })
}

/**
 * 切换配置状态
 */
export function toggleZhifuPeizhiStatus(id: string) {
  return request<ZhifuPeizhiResponse>({
    url: `/payment-configs/${id}/toggle-status`,
    method: 'post'
  })
}

