/**
 * 审核管理状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  auditRuleApi,
  auditWorkflowApi,
  auditRecordApi,
  type AuditRuleListParams,
  type AuditRuleCreate,
  type AuditRuleUpdate,
  type AuditWorkflowListParams,
  type AuditRecordListParams,
  type AuditStatisticsParams,
  type AuditActionData
} from '@/api/modules/audit'

// 审核规则类型
interface AuditRule {
  id: string
  guize_mingcheng: string
  guize_leixing: string
  zhuangtai: string
}

// 审核流程类型
interface AuditWorkflow {
  id: string
  liucheng_mingcheng: string
  liucheng_leixing: string
  zhuangtai: string
}

// 审核记录类型
interface AuditRecord {
  id: string
  workflow_id: string
  status: string
  created_at?: string
}

// 待审核任务类型
interface PendingAudit {
  id: string
  workflow_id: string
  record_id: string
  status: string
}

// 审核统计类型
interface AuditStatistics {
  pending_count?: number
  approved_count?: number
  rejected_count?: number
  total_count?: number
}

export const useAuditManagementStore = defineStore('auditManagement', () => {
  // 状态
  const loading = ref(false)

  // 审核规则
  const auditRules = ref<AuditRule[]>([])
  const auditRulesTotal = ref(0)
  const currentAuditRule = ref<AuditRule | null>(null)

  // 审核流程
  const auditWorkflows = ref<AuditWorkflow[]>([])
  const auditWorkflowsTotal = ref(0)
  const currentAuditWorkflow = ref<AuditWorkflow | null>(null)

  // 审核记录
  const auditRecords = ref<AuditRecord[]>([])
  const auditRecordsTotal = ref(0)

  // 待审核任务
  const pendingAudits = ref<PendingAudit[]>([])

  // 审核统计
  const auditStatistics = ref<AuditStatistics>({})

  // 计算属性
  const pendingAuditsCount = computed(() => pendingAudits.value.length)

  // 审核规则管理
  const fetchAuditRules = async (params: AuditRuleListParams = {}) => {
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

  const createAuditRule = async (data: AuditRuleCreate) => {
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

  const updateAuditRule = async (id: string, data: AuditRuleUpdate) => {
    try {
      loading.value = true
      const response = await auditRuleApi.update(id, data)
      const index = auditRules.value.findIndex((rule) => rule.id === id)
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
      const index = auditRules.value.findIndex((rule) => rule.id === id)
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
  const fetchAuditWorkflows = async (params: AuditWorkflowListParams = {}) => {
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
      const responseData = response as { items?: PendingAudit[] } | PendingAudit[]
      pendingAudits.value = Array.isArray(responseData) ? responseData : responseData.items || []
      return response
    } catch (error) {
      console.error('获取待审核任务失败:', error)
      ElMessage.error('获取待审核任务失败')
      throw error
    }
  }

  const processAuditAction = async (taskId: string, action: string, data: AuditActionData) => {
    try {
      loading.value = true

      // 使用axios实例（包含认证token）
      let result
      if (action === 'approve') {
        result = await auditRecordApi.approve(taskId, data)
      } else if (action === 'reject') {
        result = await auditRecordApi.reject(taskId, data)
      }

      // 更新待审核任务列表
      await fetchMyPendingAudits()

      ElMessage.success('审核操作处理成功')
      return result
    } catch (error: unknown) {
      console.error('处理审核操作失败:', error)
      const axiosError = error as { response?: { data?: { detail?: string } } }
      console.error('错误详情:', axiosError.response?.data)
      ElMessage.error(axiosError.response?.data?.detail || '处理审核操作失败')
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
      const index = auditWorkflows.value.findIndex((workflow) => workflow.id === workflowId)
      if (index !== -1) {
        const workflow = auditWorkflows.value[index] as AuditWorkflow & { shenhe_zhuangtai?: string }
        workflow.shenhe_zhuangtai = 'chexiao'
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
  const fetchAuditRecords = async (params: AuditRecordListParams = {}) => {
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

  const fetchMyAuditStatistics = async (params?: AuditStatisticsParams) => {
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
    clearState,
  }
})
