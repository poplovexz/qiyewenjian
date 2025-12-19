/**
 * 审核管理API
 */
import { request } from '@/utils/request'

// 审核规则类型定义
export interface AuditRuleListParams {
  page?: number
  size?: number
  search?: string
  guize_leixing?: string
  shi_qiyong?: string
}

export interface AuditRuleCreate {
  guize_mingcheng: string
  guize_leixing: string
  chufa_tiaojian: Record<string, string | number | boolean>
  shenhe_liucheng_peizhi: Record<string, unknown>
  shi_qiyong?: string
  paixu?: number
  guize_miaoshu?: string
}

export interface AuditRuleUpdate {
  guize_mingcheng?: string
  guize_leixing?: string
  chufa_tiaojian?: Record<string, string | number | boolean>
  shenhe_liucheng_peizhi?: Record<string, unknown>
  shi_qiyong?: string
  paixu?: number
  guize_miaoshu?: string
}

// 审核流程类型定义
export interface AuditWorkflowListParams {
  page?: number
  size?: number
  search?: string
  workflow_status?: string
}

export interface AuditWorkflowCreate {
  workflow_name: string
  workflow_type: string
  related_id: string
  steps: AuditWorkflowStep[]
}

export interface AuditWorkflowStep {
  step_name: string
  approver_id?: string
  approver_role?: string
  required: boolean
}

export interface AuditWorkflowUpdate {
  workflow_name?: string
  workflow_status?: string
}

export interface AuditActionData {
  action: 'approve' | 'reject' | 'return'
  comment?: string
}

// 审核记录类型定义
export interface AuditRecordListParams {
  page?: number
  size?: number
  workflow_id?: string
  approver_id?: string
  status?: string
}

export interface AuditRecordUpdate {
  status?: string
  comment?: string
}

export interface AuditStatisticsParams {
  start_date?: string
  end_date?: string
}

export interface AuditApproveData {
  comment?: string
}

export interface AuditRejectData {
  comment: string
  reason?: string
}

// 合同支付类型定义
export interface ContractPaymentListParams {
  page?: number
  size?: number
  contract_id?: string
  payment_status?: string
}

export interface ContractPaymentCreate {
  contract_id: string
  payment_amount: number
  payment_method: string
}

export interface ContractPaymentUpdate {
  payment_status?: string
  payment_amount?: number
}

// 银行汇款类型定义
export interface BankTransferListParams {
  page?: number
  size?: number
  payment_id?: string
  status?: string
}

export interface BankTransferCreate {
  payment_id: string
  transfer_amount: number
  transfer_date: string
  bank_name: string
  account_number: string
  transfer_reference?: string
}

export interface BankTransferUpdate {
  status?: string
  transfer_reference?: string
}

export interface BankTransferAuditData {
  action: 'approve' | 'reject'
  comment?: string
}

// 审核规则相关接口
export const auditRuleApi = {
  // 获取审核规则列表
  getList: (params: AuditRuleListParams) => {
    return request.get('/audit-rules', { params })
  },

  // 根据ID获取审核规则
  getById: (id: string) => {
    return request.get(`/audit-rules/${id}`)
  },

  // 创建审核规则
  create: (data: AuditRuleCreate) => {
    return request.post('/audit-rules', data)
  },

  // 更新审核规则
  update: (id: string, data: AuditRuleUpdate) => {
    return request.put(`/audit-rules/${id}`, data)
  },

  // 删除审核规则
  delete: (id: string) => {
    return request.delete(`/audit-rules/${id}`)
  },

  // 根据类型获取启用的审核规则
  getActiveByType: (type: string) => {
    return request.get(`/audit-rules/type/${type}`)
  }
}

// 审核流程相关接口
export const auditWorkflowApi = {
  // 获取审核流程列表
  getList: (params: AuditWorkflowListParams) => {
    return request.get('/audit-workflows', { params })
  },

  // 根据ID获取工作流模板详情
  getById: (id: string) => {
    return request.get(`/audit-workflows/template/${id}`)
  },

  // 根据ID获取审核流程实例详情
  getInstanceById: (id: string) => {
    return request.get(`/audit-workflows/${id}`)
  },

  // 创建审核流程
  create: (data: AuditWorkflowCreate) => {
    return request.post('/audit-workflows', data)
  },

  // 更新审核流程
  update: (id: string, data: AuditWorkflowUpdate) => {
    return request.put(`/audit-workflows/${id}`, data)
  },

  // 删除审核流程
  delete: (id: string) => {
    return request.delete(`/audit-workflows/${id}`)
  },

  // 获取我的待审核任务
  getMyPendingAudits: () => {
    return request.get('/audit-workflows/pending/my')
  },

  // 处理审核操作
  processAction: (workflowId: string, stepId: string, data: AuditActionData) => {
    return request.post(`/audit-workflows/${workflowId}/steps/${stepId}/action`, data)
  },

  // 获取审核历史
  getHistory: (auditType: string, relatedId: string) => {
    return request.get(`/audit-workflows/history/${auditType}/${relatedId}`)
  },

  // 取消审核流程
  cancel: (workflowId: string, reason: string) => {
    return request.post(`/audit-workflows/${workflowId}/cancel`, { reason })
  },

  // 获取审核统计概览
  getStatisticsOverview: () => {
    return request.get('/audit-workflows/statistics/overview')
  }
}

// 审核记录相关接口
export const auditRecordApi = {
  // 获取审核记录列表
  getList: (params: AuditRecordListParams) => {
    return request.get('/audit-records', { params })
  },

  // 根据流程ID获取审核记录
  getByWorkflow: (workflowId: string) => {
    return request.get(`/audit-records/workflow/${workflowId}`)
  },

  // 根据ID获取审核记录详情
  getById: (id: string) => {
    return request.get(`/audit-records/${id}`)
  },

  // 更新审核记录
  update: (id: string, data: AuditRecordUpdate) => {
    return request.put(`/audit-records/${id}`, data)
  },

  // 获取用户审核统计
  getUserStatistics: (userId: string, params?: AuditStatisticsParams) => {
    return request.get(`/audit-records/statistics/user/${userId}`, { params })
  },

  // 获取我的审核统计
  getMyStatistics: (params?: AuditStatisticsParams) => {
    return request.get('/audit-records/statistics/my', { params })
  },

  // 获取超期审核记录
  getOverdueList: (params?: AuditRecordListParams) => {
    return request.get('/audit-records/overdue/list', { params })
  },

  // 获取我的超期审核记录
  getMyOverdueList: () => {
    return request.get('/audit-records/overdue/my')
  },

  // 审核通过
  approve: (recordId: string, data: AuditApproveData) => {
    return request.post(`/audit-records/${recordId}/approve`, data)
  },

  // 审核拒绝
  reject: (recordId: string, data: AuditRejectData) => {
    return request.post(`/audit-records/${recordId}/reject`, data)
  },

  // 获取我已处理的审核任务
  getMyProcessed: () => {
    return request.get('/audit-records/my-processed')
  }
}

// 合同支付相关接口
export const contractPaymentApi = {
  // 获取合同支付列表
  getList: (params: ContractPaymentListParams) => {
    return request.get('/contract-payments', { params })
  },

  // 根据ID获取合同支付详情
  getById: (id: string) => {
    return request.get(`/contract-payments/${id}`)
  },

  // 创建合同支付
  create: (data: ContractPaymentCreate) => {
    return request.post('/contract-payments', data)
  },

  // 更新合同支付
  update: (id: string, data: ContractPaymentUpdate) => {
    return request.put(`/contract-payments/${id}`, data)
  },

  // 根据合同ID获取支付记录
  getByContract: (contractId: string) => {
    return request.get(`/contract-payments/contract/${contractId}`)
  }
}

// 银行汇款单据相关接口
export const bankTransferApi = {
  // 获取汇款单据列表
  getList: (params: BankTransferListParams) => {
    return request.get('/bank-transfers', { params })
  },

  // 根据ID获取汇款单据详情
  getById: (id: string) => {
    return request.get(`/bank-transfers/${id}`)
  },

  // 创建汇款单据
  create: (data: BankTransferCreate) => {
    return request.post('/bank-transfers', data)
  },

  // 更新汇款单据
  update: (id: string, data: BankTransferUpdate) => {
    return request.put(`/bank-transfers/${id}`, data)
  },

  // 审核汇款单据
  audit: (id: string, data: BankTransferAuditData) => {
    return request.post(`/bank-transfers/${id}/audit`, data)
  },

  // 根据合同支付ID获取汇款单据
  getByPayment: (paymentId: string) => {
    return request.get(`/bank-transfers/payment/${paymentId}`)
  },

  // 获取待审核的汇款单据
  getPendingAudits: () => {
    return request.get('/bank-transfers/pending-audits')
  }
}
