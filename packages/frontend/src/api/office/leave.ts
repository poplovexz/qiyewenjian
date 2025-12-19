/**
 * 请假申请API
 */
import request from '@/utils/request'

// 通用列表参数类型
interface ListParams {
  page?: number
  size?: number
  [key: string]: string | number | undefined
}

export interface LeaveApplication {
  id?: string
  shenqing_bianhao?: string
  shenqing_ren_id?: string
  qingjia_leixing: string
  kaishi_shijian: string
  jieshu_shijian: string
  qingjia_tianshu: number
  qingjia_yuanyin: string
  fujian_lujing?: string
  shenhe_zhuangtai?: string
  beizhu?: string
  created_at?: string
  shenqing_ren_xingming?: string
}

export function getLeaveList(params: ListParams) {
  return request({
    url: '/office/leave',
    method: 'get',
    params,
  })
}

export function getLeaveDetail(id: string) {
  return request({
    url: `/office/leave/${id}`,
    method: 'get',
  })
}

export function createLeave(data: LeaveApplication) {
  return request({
    url: '/office/leave',
    method: 'post',
    data,
  })
}

export function updateLeave(id: string, data: Partial<LeaveApplication>) {
  return request({
    url: `/office/leave/${id}`,
    method: 'put',
    data,
  })
}

export function deleteLeave(id: string) {
  return request({
    url: `/office/leave/${id}`,
    method: 'delete',
  })
}

/**
 * 提交审批
 */
export function submitLeaveForApproval(id: string) {
  return request({
    url: `/office/leave/${id}/submit`,
    method: 'post',
  })
}

/**
 * 审批通过
 */
export function approveLeave(id: string, shenhe_yijian?: string) {
  return request({
    url: `/office/leave/${id}/approve`,
    method: 'post',
    params: { shenhe_yijian },
  })
}

/**
 * 审批拒绝
 */
export function rejectLeave(id: string, shenhe_yijian: string) {
  return request({
    url: `/office/leave/${id}/reject`,
    method: 'post',
    params: { shenhe_yijian },
  })
}
