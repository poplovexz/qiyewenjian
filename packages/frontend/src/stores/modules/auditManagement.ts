/**
 * 审核管理状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { auditRuleApi, auditWorkflowApi, auditRecordApi } from '@/api/modules/audit'

export const useAuditManagementStore = defineStore('auditManagement', () => {
  // 状态
  const loading = ref(false)
  
  // 审核规则
  const auditRules = ref<any[]>([])
  const auditRulesTotal = ref(0)
  const currentAuditRule = ref<any>(null)
  
  // 审核流程
  const auditWorkflows = ref<any[]>([])
  const auditWorkflowsTotal = ref(0)
  const currentAuditWorkflow = ref<any>(null)
  
  // 审核记录
  const auditRecords = ref<any[]>([])
  const auditRecordsTotal = ref(0)
  
  // 待审核任务
  const pendingAudits = ref<any[]>([])
  
  // 审核统计
  const auditStatistics = ref<any>({})
  
  // 计算属性
  const pendingAuditsCount = computed(() => pendingAudits.value.length)
  
  // 审核规则管理
  const fetchAuditRules = async (params: any = {}) => {
    try {
      loading.value = true
      const response = await auditRuleApi.getList(params)
      auditRules.value = response.items
      auditRulesTotal.value = response.total
    } catch (error) {
      console.error('获取审核规则列表失败:', error)
      ElMessage.error('获取审核规则列表失败')
    } finally {
      loading.value = false
    }
  }
  
  const createAuditRule = async (data: any) => {
    try {
      loading.value = true
      const response = await auditRuleApi.create(data)
      auditRules.value.unshift(response)
      auditRulesTotal.value += 1
      ElMessage.success('审核规则创建成功')
      return response
    } catch (error) {
      console.error('创建审核规则失败:', error)
      ElMessage.error('创建审核规则失败')
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const updateAuditRule = async (id: string, data: any) => {
    try {
      loading.value = true
      const response = await auditRuleApi.update(id, data)
      const index = auditRules.value.findIndex(rule => rule.id === id)
      if (index !== -1) {
        auditRules.value[index] = response
      }
      ElMessage.success('审核规则更新成功')
      return response
    } catch (error) {
      console.error('更新审核规则失败:', error)
      ElMessage.error('更新审核规则失败')
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const deleteAuditRule = async (id: string) => {
    try {
      loading.value = true
      await auditRuleApi.delete(id)
      const index = auditRules.value.findIndex(rule => rule.id === id)
      if (index !== -1) {
        auditRules.value.splice(index, 1)
        auditRulesTotal.value -= 1
      }
      ElMessage.success('审核规则删除成功')
    } catch (error) {
      console.error('删除审核规则失败:', error)
      ElMessage.error('删除审核规则失败')
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 审核流程管理
  const fetchAuditWorkflows = async (params: any = {}) => {
    try {
      loading.value = true
      const response = await auditWorkflowApi.getList(params)
      auditWorkflows.value = response.items
      auditWorkflowsTotal.value = response.total
    } catch (error) {
      console.error('获取审核流程列表失败:', error)
      ElMessage.error('获取审核流程列表失败')
    } finally {
      loading.value = false
    }
  }
  
  const fetchAuditWorkflowById = async (id: string) => {
    try {
      loading.value = true
      // 修复：使用 getInstanceById 获取审核流程实例详情，而不是工作流模板详情
      const response = await auditWorkflowApi.getInstanceById(id)
      currentAuditWorkflow.value = response
      return response
    } catch (error) {
      console.error('获取审核流程详情失败:', error)
      ElMessage.error('获取审核流程详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const fetchMyPendingAudits = async () => {
    try {
      const response = await auditWorkflowApi.getMyPendingAudits()
      // 修复：后端返回的是纯数组，不是分页对象
      // 兼容两种格式：纯数组或分页对象 { items, total }
      pendingAudits.value = Array.isArray(response) ? response : (response.items || [])
      return response
    } catch (error) {
      console.error('获取待审核任务失败:', error)
      ElMessage.error('获取待审核任务失败')
      throw error
    }
  }
  
  const processAuditAction = async (taskId: string, action: string, data: any) => {
    try {
      loading.value = true

      console.log('审核操作参数:', { taskId, action, data })

      // 使用axios实例（包含认证token）
      let result
      if (action === 'approve') {
        console.log('发送审核通过请求:', `/audit-records/${taskId}/approve`)
        result = await auditRecordApi.approve(taskId, data)
      } else if (action === 'reject') {
        console.log('发送审核拒绝请求:', `/audit-records/${taskId}/reject`)
        result = await auditRecordApi.reject(taskId, data)
      }

      console.log('审核操作响应:', result)

      // 更新待审核任务列表
      await fetchMyPendingAudits()

      ElMessage.success('审核操作处理成功')
      return result
    } catch (error: any) {
      console.error('处理审核操作失败:', error)
      console.error('错误详情:', error.response?.data)
      ElMessage.error(error.response?.data?.detail || '处理审核操作失败')
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const cancelAuditWorkflow = async (workflowId: string, reason: string) => {
    try {
      loading.value = true
      await auditWorkflowApi.cancel(workflowId, reason)
      
      // 更新流程列表
      const index = auditWorkflows.value.findIndex(workflow => workflow.id === workflowId)
      if (index !== -1) {
        auditWorkflows.value[index].shenhe_zhuangtai = 'chexiao'
      }
      
      ElMessage.success('审核流程取消成功')
    } catch (error) {
      console.error('取消审核流程失败:', error)
      ElMessage.error('取消审核流程失败')
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 审核记录管理
  const fetchAuditRecords = async (params: any = {}) => {
    try {
      loading.value = true
      const response = await auditRecordApi.getList(params)
      auditRecords.value = response.items
      auditRecordsTotal.value = response.total
    } catch (error) {
      console.error('获取审核记录列表失败:', error)
      ElMessage.error('获取审核记录列表失败')
    } finally {
      loading.value = false
    }
  }
  
  const fetchAuditRecordsByWorkflow = async (workflowId: string) => {
    try {
      // 修复：使用正确的API路径，通过workflow_id参数查询
      const response = await auditRecordApi.getList({ workflow_id: workflowId })
      return response
    } catch (error) {
      console.error('获取审核记录失败:', error)
      ElMessage.error('获取审核记录失败')
      throw error
    }
  }
  
  // 审核统计
  const fetchAuditStatistics = async () => {
    try {
      const response = await auditRecordApi.getMyStatistics()
      auditStatistics.value = response
      return response
    } catch (error) {
      console.error('获取审核统计失败:', error)
      ElMessage.error('获取审核统计失败')
      throw error
    }
  }
  
  const fetchMyAuditStatistics = async (params?: any) => {
    try {
      const response = await auditRecordApi.getMyStatistics(params)
      return response
    } catch (error) {
      console.error('获取我的审核统计失败:', error)
      ElMessage.error('获取我的审核统计失败')
      throw error
    }
  }
  
  // 获取审核历史
  const fetchAuditHistory = async (auditType: string, relatedId: string) => {
    try {
      const response = await auditWorkflowApi.getHistory(auditType, relatedId)
      return response
    } catch (error) {
      console.error('获取审核历史失败:', error)
      ElMessage.error('获取审核历史失败')
      throw error
    }
  }
  
  // 清理状态
  const clearState = () => {
    auditRules.value = []
    auditRulesTotal.value = 0
    currentAuditRule.value = null
    auditWorkflows.value = []
    auditWorkflowsTotal.value = 0
    currentAuditWorkflow.value = null
    auditRecords.value = []
    auditRecordsTotal.value = 0
    pendingAudits.value = []
    auditStatistics.value = {}
  }
  
  return {
    // 状态
    loading,
    auditRules,
    auditRulesTotal,
    currentAuditRule,
    auditWorkflows,
    auditWorkflowsTotal,
    currentAuditWorkflow,
    auditRecords,
    auditRecordsTotal,
    pendingAudits,
    auditStatistics,
    
    // 计算属性
    pendingAuditsCount,
    
    // 方法
    fetchAuditRules,
    createAuditRule,
    updateAuditRule,
    deleteAuditRule,
    fetchAuditWorkflows,
    fetchAuditWorkflowById,
    fetchMyPendingAudits,
    processAuditAction,
    cancelAuditWorkflow,
    fetchAuditRecords,
    fetchAuditRecordsByWorkflow,
    fetchAuditStatistics,
    fetchMyAuditStatistics,
    fetchAuditHistory,
    clearState
  }
})
