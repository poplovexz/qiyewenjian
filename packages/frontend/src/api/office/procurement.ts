/**
 * 采购申请API
 */
import request from '@/utils/request'

export interface ProcurementApplication {
  id?: string
  shenqing_bianhao?: string
  shenqing_ren_id?: string
  caigou_leixing: string
  caigou_mingcheng: string
  caigou_shuliang: number
  danwei: string
  yugu_jine: number
  caigou_yuanyin: string
  yaoqiu_shijian?: string
  gongyingshang_xinxi?: string
  fujian_lujing?: string
  shenhe_zhuangtai?: string
  caigou_zhuangtai?: string
  shiji_jine?: number
  beizhu?: string
  created_at?: string
  shenqing_ren_xingming?: string
}

export function getProcurementList(params: any) {
  return request({
    url: '/office/procurement',
    method: 'get',
    params
  })
}

export function getProcurementDetail(id: string) {
  return request({
    url: `/office/procurement/${id}`,
    method: 'get'
  })
}

export function createProcurement(data: ProcurementApplication) {
  return request({
    url: '/office/procurement',
    method: 'post',
    data
  })
}

export function updateProcurement(id: string, data: Partial<ProcurementApplication>) {
  return request({
    url: `/office/procurement/${id}`,
    method: 'put',
    data
  })
}

export function deleteProcurement(id: string) {
  return request({
    url: `/office/procurement/${id}`,
    method: 'delete'
  })
}

/**
 * 提交审批
 */
export function submitProcurementForApproval(id: string) {
  return request({
    url: `/office/procurement/${id}/submit`,
    method: 'post'
  })
}

/**
 * 审批通过
 */
export function approveProcurement(id: string, shenhe_yijian?: string) {
  return request({
    url: `/office/procurement/${id}/approve`,
    method: 'post',
    params: { shenhe_yijian }
  })
}

/**
 * 审批拒绝
 */
export function rejectProcurement(id: string, shenhe_yijian: string) {
  return request({
    url: `/office/procurement/${id}/reject`,
    method: 'post',
    params: { shenhe_yijian }
  })
}

