/**
 * 审核管理 Store
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { auditRuleApi, auditWorkflowApi } from '@/api/modules/audit'

// 审核规则数据类型
interface AuditRuleData {
  guize_mingcheng: string
  guize_leixing: string
  chufa_tiaojian?: Record<string, unknown>
  shenhe_liucheng?: Record<string, unknown>
  shifou_qiyong?: boolean
}

// 审核操作数据类型
interface AuditActionData {
  shenhe_jieguo: string
  shenhe_yijian?: string
}

// 触发数据类型
interface TriggerData {
  amount_change?: string | number
  [key: string]: unknown
}

// 触发条件类型
interface TriggerConditions {
  amount_threshold?: string | number
  [key: string]: unknown
}

export const useAuditStore = defineStore('audit', () => {
  // 状态
  const auditRules = ref([])
  const auditWorkflows = ref([])
  const currentWorkflow = ref(null)
  const loading = ref(false)

  // 获取审核规则列表
  const fetchAuditRules = async (params = {}) => {
    try {
      loading.value = true
      const response = await auditRuleApi.getList(params)
      auditRules.value = response.data.items
      return response.data
    } catch (error) {
      console.error('获取审核规则失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 根据类型获取启用的审核规则
  const fetchActiveRulesByType = async (type: string) => {
    try {
      const response = await auditRuleApi.getActiveByType(type)
      return response.data
    } catch (error) {
      console.error('获取审核规则失败:', error)
      throw error
    }
  }

  // 创建审核规则
  const createAuditRule = async (ruleData: AuditRuleData) => {
    try {
      loading.value = true
      const response = await auditRuleApi.create(ruleData)
      await fetchAuditRules() // 刷新列表
      return response.data
    } catch (error) {
      console.error('创建审核规则失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新审核规则
  const updateAuditRule = async (id: string, ruleData: Partial<AuditRuleData>) => {
    try {
      loading.value = true
      const response = await auditRuleApi.update(id, ruleData)
      await fetchAuditRules() // 刷新列表
      return response.data
    } catch (error) {
      console.error('更新审核规则失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除审核规则
  const deleteAuditRule = async (id: string) => {
    try {
      loading.value = true
      await auditRuleApi.delete(id)
      await fetchAuditRules() // 刷新列表
    } catch (error) {
      console.error('删除审核规则失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取审核工作流列表
  const fetchAuditWorkflows = async (params = {}) => {
    try {
      loading.value = true
      const response = await auditWorkflowApi.getList(params)
      auditWorkflows.value = response.data.items
      return response.data
    } catch (error) {
      console.error('获取审核工作流失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取我的待审核任务
  const fetchMyPendingTasks = async (params = {}) => {
    try {
      const response = await auditWorkflowApi.getMyPendingTasks(params)
      return response.data
    } catch (error) {
      console.error('获取待审核任务失败:', error)
      throw error
    }
  }

  // 获取审核工作流详情
  const fetchWorkflowDetail = async (workflowId: string) => {
    try {
      const response = await auditWorkflowApi.getDetail(workflowId)
      currentWorkflow.value = response.data
      return response.data
    } catch (error) {
      console.error('获取审核工作流详情失败:', error)
      throw error
    }
  }

  // 提交审核申请
  const submitAudit = async (auditData: Record<string, unknown>) => {
    try {
      loading.value = true
      const response = await auditWorkflowApi.create(auditData)
      return response.data
    } catch (error) {
      console.error('提交审核申请失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 处理审核操作
  const processAuditAction = async (workflowId: string, stepId: string, actionData: AuditActionData) => {
    try {
      loading.value = true
      const response = await auditWorkflowApi.processAction(workflowId, stepId, actionData)

      // 刷新当前工作流详情
      if (currentWorkflow.value?.id === workflowId) {
        await fetchWorkflowDetail(workflowId)
      }

      return response.data
    } catch (error) {
      console.error('处理审核操作失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取审核历史
  const fetchAuditHistory = async (auditType: string, relatedId: string) => {
    try {
      const response = await auditWorkflowApi.getHistory(auditType, relatedId)
      return response.data
    } catch (error) {
      console.error('获取审核历史失败:', error)
      throw error
    }
  }

  // 取消审核流程
  const cancelAuditWorkflow = async (workflowId: string, reason: string) => {
    try {
      loading.value = true
      const response = await auditWorkflowApi.cancel(workflowId, reason)
      
      // 刷新当前工作流详情
      if (currentWorkflow.value?.id === workflowId) {
        await fetchWorkflowDetail(workflowId)
      }
      
      return response.data
    } catch (error) {
      console.error('取消审核流程失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取审核统计概览
  const fetchStatisticsOverview = async () => {
    try {
      const response = await auditWorkflowApi.getStatisticsOverview()
      return response.data
    } catch (error) {
      console.error('获取审核统计失败:', error)
      throw error
    }
  }

  // 批量审核操作
  const batchProcessAudit = async (actions: Array<{
    workflowId: string
    stepId: string
    actionData: AuditActionData
  }>) => {
    try {
      loading.value = true
      const results: Array<{ success: boolean; data?: unknown; error?: string }> = []

      for (const action of actions) {
        try {
          const result = await auditWorkflowApi.processAction(
            action.workflowId,
            action.stepId,
            action.actionData
          )
          results.push({ success: true, data: result.data })
        } catch (error: unknown) {
          const err = error as Error
          results.push({ success: false, error: err.message })
        }
      }

      return results
    } catch (error) {
      console.error('批量审核操作失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取审核规则配置
  const fetchRuleConfig = async (ruleType: string) => {
    try {
      const response = await auditRuleApi.getActiveByType(ruleType)
      return response.data
    } catch (error) {
      console.error('获取审核规则配置失败:', error)
      throw error
    }
  }

  // 检查是否需要审核
  const checkNeedsAudit = async (auditType: string, triggerData: TriggerData) => {
    try {
      // 这里可以调用后端API检查是否需要审核
      // 暂时使用前端逻辑判断
      const rules = await fetchActiveRulesByType(auditType)

      for (const rule of rules) {
        const conditions = JSON.parse(rule.chufa_tiaojian)

        // 检查触发条件
        if (checkTriggerConditions(conditions, triggerData)) {
          return {
            needsAudit: true,
            rule: rule,
            reason: rule.guize_miaoshu
          }
        }
      }

      return { needsAudit: false }
    } catch (error) {
      console.error('检查审核需求失败:', error)
      throw error
    }
  }

  // 检查触发条件
  const checkTriggerConditions = (conditions: TriggerConditions, triggerData: TriggerData): boolean => {
    try {
      // 金额阈值检查
      if (conditions.amount_threshold && triggerData.amount_change) {
        const threshold = parseFloat(conditions.amount_threshold)
        const change = Math.abs(parseFloat(triggerData.amount_change))
        if (change > threshold) {
          return true
        }
      }
      
      // 百分比阈值检查
      if (conditions.percentage_threshold && triggerData.percentage_change) {
        const threshold = parseFloat(conditions.percentage_threshold)
        const change = Math.abs(parseFloat(triggerData.percentage_change))
        if (change > threshold) {
          return true
        }
      }
      
      // 其他条件检查...
      
      return false
    } catch (error) {
      console.error('检查触发条件失败:', error)
      return false
    }
  }

  // 重置状态
  const resetState = () => {
    auditRules.value = []
    auditWorkflows.value = []
    currentWorkflow.value = null
    loading.value = false
  }

  return {
    // 状态
    auditRules,
    auditWorkflows,
    currentWorkflow,
    loading,

    // 审核规则相关
    fetchAuditRules,
    fetchActiveRulesByType,
    createAuditRule,
    updateAuditRule,
    deleteAuditRule,

    // 审核工作流相关
    fetchAuditWorkflows,
    fetchMyPendingTasks,
    fetchWorkflowDetail,
    submitAudit,
    processAuditAction,
    fetchAuditHistory,
    cancelAuditWorkflow,
    fetchStatisticsOverview,
    batchProcessAudit,

    // 工具方法
    fetchRuleConfig,
    checkNeedsAudit,
    checkTriggerConditions,
    resetState
  }
})
