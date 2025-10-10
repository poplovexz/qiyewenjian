/**
 * 审核管理API
 */
import { request } from '@/utils/request'

// 审核规则相关接口
export const auditRuleApi = {
  // 获取审核规则列表
  getList: (params: any) => {
    return request.get('/api/v1/audit-rules', { params })
  },

  // 根据ID获取审核规则
  getById: (id: string) => {
    return request.get(`/api/v1/audit-rules/${id}`)
  },

  // 创建审核规则
  create: (data: any) => {
    return request.post('/api/v1/audit-rules', data)
  },

  // 更新审核规则
  update: (id: string, data: any) => {
    return request.put(`/api/v1/audit-rules/${id}`, data)
  },

  // 删除审核规则
  delete: (id: string) => {
    return request.delete(`/api/v1/audit-rules/${id}`)
  },

  // 根据类型获取启用的审核规则
  getActiveByType: (type: string) => {
    return request.get(`/api/v1/audit-rules/type/${type}`)
  }
}

// 审核流程相关接口
export const auditWorkflowApi = {
  // 获取审核流程列表
  getList: (params: any) => {
    return request.get('/api/v1/audit-workflows', { params })
  },

  // 根据ID获取审核流程详情
  getById: (id: string) => {
    return request.get(`/api/v1/audit-workflows/${id}`)
  },

  // 创建审核流程
  create: (data: any) => {
    return request.post('/api/v1/audit-workflows', data)
  },

  // 更新审核流程
  update: (id: string, data: any) => {
    return request.put(`/api/v1/audit-workflows/${id}`, data)
  },

  // 删除审核流程
  delete: (id: string) => {
    return request.delete(`/api/v1/audit-workflows/${id}`)
  },

  // 获取我的待审核任务
  getMyPendingAudits: () => {
    return request.get('/api/v1/audit-workflows/pending/my')
  },

  // 处理审核操作
  processAction: (workflowId: string, stepId: string, data: any) => {
    return request.post(`/api/v1/audit-workflows/${workflowId}/steps/${stepId}/action`, data)
  },

  // 获取审核历史
  getHistory: (auditType: string, relatedId: string) => {
    return request.get(`/api/v1/audit-workflows/history/${auditType}/${relatedId}`)
  },

  // 取消审核流程
  cancel: (workflowId: string, reason: string) => {
    return request.post(`/api/v1/audit-workflows/${workflowId}/cancel`, { reason })
  },

  // 获取审核统计概览
  getStatisticsOverview: () => {
    return request.get('/api/v1/audit-workflows/statistics/overview')
  }
}

// 审核记录相关接口
export const auditRecordApi = {
  // 获取审核记录列表
  getList: (params: any) => {
    return request.get('/api/v1/audit-records', { params })
  },

  // 根据流程ID获取审核记录
  getByWorkflow: (workflowId: string) => {
    return request.get(`/api/v1/audit-records/workflow/${workflowId}`)
  },

  // 根据ID获取审核记录详情
  getById: (id: string) => {
    return request.get(`/api/v1/audit-records/${id}`)
  },

  // 更新审核记录
  update: (id: string, data: any) => {
    return request.put(`/api/v1/audit-records/${id}`, data)
  },

  // 获取用户审核统计
  getUserStatistics: (userId: string, params?: any) => {
    return request.get(`/api/v1/audit-records/statistics/user/${userId}`, { params })
  },

  // 获取我的审核统计
  getMyStatistics: (params?: any) => {
    return request.get('/api/v1/audit-records/statistics/my', { params })
  },

  // 获取超期审核记录
  getOverdueList: (params?: any) => {
    return request.get('/api/v1/audit-records/overdue/list', { params })
  },

  // 获取我的超期审核记录
  getMyOverdueList: () => {
    return request.get('/api/v1/audit-records/overdue/my')
  }
}

// 合同支付相关接口
export const contractPaymentApi = {
  // 获取合同支付列表
  getList: (params: any) => {
    return request.get('/api/v1/contract-payments', { params })
  },

  // 根据ID获取合同支付详情
  getById: (id: string) => {
    return request.get(`/api/v1/contract-payments/${id}`)
  },

  // 创建合同支付
  create: (data: any) => {
    return request.post('/api/v1/contract-payments', data)
  },

  // 更新合同支付
  update: (id: string, data: any) => {
    return request.put(`/api/v1/contract-payments/${id}`, data)
  },

  // 根据合同ID获取支付记录
  getByContract: (contractId: string) => {
    return request.get(`/api/v1/contract-payments/contract/${contractId}`)
  }
}

// 银行汇款单据相关接口
export const bankTransferApi = {
  // 获取汇款单据列表
  getList: (params: any) => {
    return request.get('/api/v1/bank-transfers', { params })
  },

  // 根据ID获取汇款单据详情
  getById: (id: string) => {
    return request.get(`/api/v1/bank-transfers/${id}`)
  },

  // 创建汇款单据
  create: (data: any) => {
    return request.post('/api/v1/bank-transfers', data)
  },

  // 更新汇款单据
  update: (id: string, data: any) => {
    return request.put(`/api/v1/bank-transfers/${id}`, data)
  },

  // 审核汇款单据
  audit: (id: string, data: any) => {
    return request.post(`/api/v1/bank-transfers/${id}/audit`, data)
  },

  // 根据合同支付ID获取汇款单据
  getByPayment: (paymentId: string) => {
    return request.get(`/api/v1/bank-transfers/payment/${paymentId}`)
  },

  // 获取待审核的汇款单据
  getPendingAudits: () => {
    return request.get('/api/v1/bank-transfers/pending-audits')
  }
}
