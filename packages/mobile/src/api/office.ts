/**
 * 办公管理API - 移动端
 * 包含请假申请和报销申请的API接口
 */
import request from '@/utils/request'

// ==================== 请假申请 ====================

export interface LeaveApplication {
  id?: string
  shenqing_bianhao?: string
  shenqing_ren_id?: string
  shenqing_ren_xingming?: string
  qingjia_leixing: string
  kaishi_shijian: string
  jieshu_shijian: string
  qingjia_tianshu: number
  qingjia_yuanyin: string
  fujian_lujing?: string
  shenhe_zhuangtai?: string
  shenhe_liucheng_id?: string
  beizhu?: string
  created_at?: string
  updated_at?: string
}

export interface LeaveListParams {
  page?: number
  size?: number
  shenhe_zhuangtai?: string
  qingjia_leixing?: string
  search?: string
}

export interface LeaveListResponse {
  items: LeaveApplication[]
  total: number
  page: number
  size: number
  pages: number
}

/**
 * 获取请假申请列表
 */
export function getLeaveList(params: LeaveListParams): Promise<LeaveListResponse> {
  return request({
    url: '/office/leave',
    method: 'get',
    params
  })
}

/**
 * 获取请假申请详情
 */
export function getLeaveDetail(id: string): Promise<LeaveApplication> {
  return request({
    url: `/office/leave/${id}`,
    method: 'get'
  })
}

/**
 * 创建请假申请
 */
export function createLeave(data: LeaveApplication): Promise<LeaveApplication> {
  return request({
    url: '/office/leave',
    method: 'post',
    data
  })
}

/**
 * 更新请假申请
 */
export function updateLeave(id: string, data: Partial<LeaveApplication>): Promise<LeaveApplication> {
  return request({
    url: `/office/leave/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除请假申请
 */
export function deleteLeave(id: string): Promise<void> {
  return request({
    url: `/office/leave/${id}`,
    method: 'delete'
  })
}

/**
 * 提交请假申请审批
 */
export function submitLeave(id: string): Promise<LeaveApplication> {
  return request({
    url: `/office/leave/${id}/submit`,
    method: 'post'
  })
}

/**
 * 审批通过请假申请
 */
export function approveLeave(id: string, opinion?: string): Promise<LeaveApplication> {
  return request({
    url: `/office/leave/${id}/approve`,
    method: 'post',
    data: { shenhe_yijian: opinion }
  })
}

/**
 * 审批拒绝请假申请
 */
export function rejectLeave(id: string, opinion: string): Promise<LeaveApplication> {
  return request({
    url: `/office/leave/${id}/reject`,
    method: 'post',
    data: { shenhe_yijian: opinion }
  })
}

// ==================== 报销申请 ====================

export interface ReimbursementApplication {
  id?: string
  shenqing_bianhao?: string
  shenqing_ren_id?: string
  shenqing_ren_xingming?: string
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
}

export interface ReimbursementListParams {
  page?: number
  size?: number
  shenhe_zhuangtai?: string
  baoxiao_leixing?: string
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
export function getReimbursementList(params: ReimbursementListParams): Promise<ReimbursementListResponse> {
  return request({
    url: '/office/reimbursement',
    method: 'get',
    params
  })
}

/**
 * 获取报销申请详情
 */
export function getReimbursementDetail(id: string): Promise<ReimbursementApplication> {
  return request({
    url: `/office/reimbursement/${id}`,
    method: 'get'
  })
}

/**
 * 创建报销申请
 */
export function createReimbursement(data: ReimbursementApplication): Promise<ReimbursementApplication> {
  return request({
    url: '/office/reimbursement',
    method: 'post',
    data
  })
}

/**
 * 更新报销申请
 */
export function updateReimbursement(id: string, data: Partial<ReimbursementApplication>): Promise<ReimbursementApplication> {
  return request({
    url: `/office/reimbursement/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除报销申请
 */
export function deleteReimbursement(id: string): Promise<void> {
  return request({
    url: `/office/reimbursement/${id}`,
    method: 'delete'
  })
}

/**
 * 提交报销申请审批
 */
export function submitReimbursement(id: string): Promise<ReimbursementApplication> {
  return request({
    url: `/office/reimbursement/${id}/submit`,
    method: 'post'
  })
}

/**
 * 审批通过报销申请
 */
export function approveReimbursement(id: string, opinion?: string): Promise<ReimbursementApplication> {
  return request({
    url: `/office/reimbursement/${id}/approve`,
    method: 'post',
    data: { shenhe_yijian: opinion }
  })
}

/**
 * 审批拒绝报销申请
 */
export function rejectReimbursement(id: string, opinion: string): Promise<ReimbursementApplication> {
  return request({
    url: `/office/reimbursement/${id}/reject`,
    method: 'post',
    data: { shenhe_yijian: opinion }
  })
}

// ==================== 审批记录 ====================

export interface AuditRecord {
  id: string
  shenhe_liucheng_id: string
  shenhe_buzhou_id: string
  buzhou_mingcheng: string
  shenhe_ren_id: string
  shenhe_ren_xingming: string
  shenhe_yijian?: string
  jilu_zhuangtai: string
  fujian_lujing?: string
  created_at: string
  updated_at: string
}

/**
 * 获取审批记录
 */
export function getAuditRecords(workflowId: string): Promise<AuditRecord[]> {
  return request({
    url: `/audit-records/workflow/${workflowId}`,
    method: 'get'
  })
}

