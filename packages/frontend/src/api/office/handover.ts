/**
 * 工作交接单API
 */
import request from '@/utils/request'

// 通用列表参数类型
interface ListParams {
  page?: number
  size?: number
  [key: string]: string | number | undefined
}

export interface HandoverApplication {
  id?: string
  jiaojie_bianhao?: string
  jiaojie_ren_id?: string
  jieshou_ren_id: string
  jiaojie_yuanyin: string
  jiaojie_shijian: string
  jiaojie_neirong?: string
  wenjian_qingdan?: string
  shebei_qingdan?: string
  zhanghu_qingdan?: string
  daiban_shixiang?: string
  fujian_lujing?: string
  jiaojie_zhuangtai?: string
  queren_ren_id?: string
  queren_shijian?: string
  beizhu?: string
  created_at?: string
  jiaojie_ren_xingming?: string
  jieshou_ren_xingming?: string
  queren_ren_xingming?: string
}

export function getHandoverList(params: ListParams) {
  return request({
    url: '/office/handover',
    method: 'get',
    params
  })
}

export function getHandoverDetail(id: string) {
  return request({
    url: `/office/handover/${id}`,
    method: 'get'
  })
}

export function createHandover(data: HandoverApplication) {
  return request({
    url: '/office/handover',
    method: 'post',
    data
  })
}

export function updateHandover(id: string, data: Partial<HandoverApplication>) {
  return request({
    url: `/office/handover/${id}`,
    method: 'put',
    data
  })
}

export function deleteHandover(id: string) {
  return request({
    url: `/office/handover/${id}`,
    method: 'delete'
  })
}

/**
 * 提交确认
 */
export function submitHandoverForConfirm(id: string) {
  return request({
    url: `/office/handover/${id}/submit`,
    method: 'post'
  })
}

/**
 * 确认接收
 */
export function confirmHandover(id: string, beizhu?: string) {
  return request({
    url: `/office/handover/${id}/confirm`,
    method: 'post',
    params: { beizhu }
  })
}

/**
 * 拒绝接收
 */
export function rejectHandover(id: string, beizhu: string) {
  return request({
    url: `/office/handover/${id}/reject`,
    method: 'post',
    params: { beizhu }
  })
}

/**
 * 获取用户列表（用于选择接收人）
 */
export function getUserList(params?: ListParams) {
  return request({
    url: '/users',
    method: 'get',
    params
  })
}

