/**
 * 报销申请API
 */
import request from '@/utils/request'

export interface ReimbursementApplication {
  id?: string
  shenqing_bianhao?: string
  shenqing_ren_id?: string
  baoxiao_leixing: string
  baoxiao_jine: number
  baoxiao_shijian: string
  baoxiao_yuanyin: string
  fujian_lujing?: string
  shenhe_zhuangtai?: string
  shenhe_liucheng_id?: string
  beizhu?: string
  created_at?: string
  updated_at?: string
  shenqing_ren_xingming?: string
}

export interface ReimbursementListParams {
  page?: number
  size?: number
  shenhe_zhuangtai?: string
  baoxiao_leixing?: string
  shenqing_ren_id?: string
  search?: string
}

export interface ReimbursementListResponse {
  items: ReimbursementApplication[]
  total: number
  page: number
  size: number
  pages: number
}

/**
 * 获取报销申请列表
 */
export function getReimbursementList(params: ReimbursementListParams) {
  return request<ReimbursementListResponse>({
    url: '/office/reimbursement',
    method: 'get',
    params
  })
}

/**
 * 获取我的报销申请列表
 */
export function getMyReimbursementList(params: ReimbursementListParams) {
  return request<ReimbursementListResponse>({
    url: '/office/reimbursement/my',
    method: 'get',
    params
  })
}

/**
 * 获取报销申请详情
 */
export function getReimbursementDetail(id: string) {
  return request<ReimbursementApplication>({
    url: `/office/reimbursement/${id}`,
    method: 'get'
  })
}

/**
 * 创建报销申请
 */
export function createReimbursement(data: ReimbursementApplication) {
  return request<ReimbursementApplication>({
    url: '/office/reimbursement',
    method: 'post',
    data
  })
}

/**
 * 更新报销申请
 */
export function updateReimbursement(id: string, data: Partial<ReimbursementApplication>) {
  return request<ReimbursementApplication>({
    url: `/office/reimbursement/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除报销申请
 */
export function deleteReimbursement(id: string) {
  return request({
    url: `/office/reimbursement/${id}`,
    method: 'delete'
  })
}

/**
 * 提交审批
 */
export function submitReimbursementForApproval(id: string) {
  return request({
    url: `/office/reimbursement/${id}/submit`,
    method: 'post'
  })
}

/**
 * 审批通过
 */
export function approveReimbursement(id: string, shenhe_yijian?: string) {
  return request({
    url: `/office/reimbursement/${id}/approve`,
    method: 'post',
    params: { shenhe_yijian }
  })
}

/**
 * 审批拒绝
 */
export function rejectReimbursement(id: string, shenhe_yijian: string) {
  return request({
    url: `/office/reimbursement/${id}/reject`,
    method: 'post',
    params: { shenhe_yijian }
  })
}
