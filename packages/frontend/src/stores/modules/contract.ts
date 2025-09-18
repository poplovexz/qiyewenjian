/**
 * 合同模板管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  contractTemplateApi,
  contractApi,
  contractPartyApi,
  paymentMethodApi,
  type ContractTemplate,
  type ContractTemplateCreate,
  type ContractTemplateUpdate,
  type ContractTemplateListParams,
  type ContractTemplateStatistics,
  type Contract,
  type ContractCreate,
  type ContractUpdate,
  type ContractListParams,
  type ContractPreview,
  type ContractSignature,
  type ContractParty,
  type ContractPartyCreate,
  type ContractPartyUpdate,
  type ContractPartyListParams,
  type PaymentMethod,
  type PaymentMethodCreate,
  type PaymentMethodUpdate,
  type PaymentMethodListParams
} from '@/api/modules/contract'

export const useContractStore = defineStore('contract', () => {
  // 合同模板状态
  const templates = ref<ContractTemplate[]>([])
  const currentTemplate = ref<ContractTemplate | null>(null)
  const templateLoading = ref(false)
  const templateTotal = ref(0)
  const templatePage = ref(1)
  const templateSize = ref(20)
  const statistics = ref<ContractTemplateStatistics | null>(null)

  // 合同状态
  const contracts = ref<Contract[]>([])
  const currentContract = ref<Contract | null>(null)
  const contractLoading = ref(false)
  const contractTotal = ref(0)
  const contractPage = ref(1)
  const contractSize = ref(20)

  // 乙方主体状态
  const parties = ref<ContractParty[]>([])
  const currentParty = ref<ContractParty | null>(null)
  const partyLoading = ref(false)
  const partyTotal = ref(0)
  const partyPage = ref(1)
  const partySize = ref(20)

  // 支付方式状态
  const paymentMethods = ref<PaymentMethod[]>([])
  const currentPaymentMethod = ref<PaymentMethod | null>(null)
  const paymentLoading = ref(false)
  const paymentTotal = ref(0)
  const paymentPage = ref(1)
  const paymentSize = ref(20)

  // 通用loading状态
  const loading = ref(false)

  // 计算属性
  const hasTemplates = computed(() => templates.value.length > 0)
  const templateTotalPages = computed(() => Math.ceil(templateTotal.value / templateSize.value))

  const hasContracts = computed(() => contracts.value.length > 0)
  const contractTotalPages = computed(() => Math.ceil(contractTotal.value / contractSize.value))

  const hasParties = computed(() => parties.value.length > 0)
  const partyTotalPages = computed(() => Math.ceil(partyTotal.value / partySize.value))

  const hasPaymentMethods = computed(() => paymentMethods.value.length > 0)
  const paymentTotalPages = computed(() => Math.ceil(paymentTotal.value / paymentSize.value))

  // ==================== 合同模板相关方法 ====================

  // 获取合同模板列表
  const fetchTemplates = async (params: ContractTemplateListParams = {}) => {
    try {
      templateLoading.value = true
      const response = await contractTemplateApi.getList({
        page: templatePage.value,
        size: templateSize.value,
        ...params
      })

      templates.value = response.items
      templateTotal.value = response.total
      templatePage.value = response.page
      templateSize.value = response.size

      return response
    } catch (error) {
      console.error('获取合同模板列表失败:', error)
      ElMessage.error('获取合同模板列表失败')
      throw error
    } finally {
      templateLoading.value = false
    }
  }

  // 获取合同模板详情
  const fetchTemplateDetail = async (id: string) => {
    try {
      templateLoading.value = true
      const response = await contractTemplateApi.getDetail(id)
      currentTemplate.value = response
      return response
    } catch (error) {
      console.error('获取合同模板详情失败:', error)
      ElMessage.error('获取合同模板详情失败')
      throw error
    } finally {
      templateLoading.value = false
    }
  }

  // 创建合同模板
  const createTemplate = async (data: ContractTemplateCreate) => {
    try {
      templateLoading.value = true
      const response = await contractTemplateApi.create(data)

      // 添加到列表开头
      templates.value.unshift(response)
      templateTotal.value += 1

      ElMessage.success('合同模板创建成功')
      return response
    } catch (error) {
      console.error('创建合同模板失败:', error)
      ElMessage.error('创建合同模板失败')
      throw error
    } finally {
      templateLoading.value = false
    }
  }

  // 更新合同模板
  const updateTemplate = async (id: string, data: ContractTemplateUpdate) => {
    try {
      loading.value = true
      const response = await contractTemplateApi.update(id, data)
      
      // 更新列表中的数据
      const index = templates.value.findIndex(item => item.id === id)
      if (index !== -1) {
        templates.value[index] = response
      }
      
      // 更新当前模板
      if (currentTemplate.value?.id === id) {
        currentTemplate.value = response
      }
      
      ElMessage.success('合同模板更新成功')
      return response
    } catch (error) {
      console.error('更新合同模板失败:', error)
      ElMessage.error('更新合同模板失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除合同模板
  const deleteTemplate = async (id: string) => {
    try {
      loading.value = true
      await contractTemplateApi.delete(id)
      
      // 从列表中移除
      const index = templates.value.findIndex(item => item.id === id)
      if (index !== -1) {
        templates.value.splice(index, 1)
        templateTotal.value -= 1
      }
      
      // 清空当前模板
      if (currentTemplate.value?.id === id) {
        currentTemplate.value = null
      }
      
      ElMessage.success('合同模板删除成功')
    } catch (error) {
      console.error('删除合同模板失败:', error)
      ElMessage.error('删除合同模板失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新模板状态
  const updateTemplateStatus = async (id: string, status: string) => {
    try {
      loading.value = true
      const response = await contractTemplateApi.updateStatus(id, status)
      
      // 更新列表中的数据
      const index = templates.value.findIndex(item => item.id === id)
      if (index !== -1) {
        templates.value[index] = response
      }
      
      // 更新当前模板
      if (currentTemplate.value?.id === id) {
        currentTemplate.value = response
      }
      
      ElMessage.success('模板状态更新成功')
      return response
    } catch (error) {
      console.error('更新模板状态失败:', error)
      ElMessage.error('更新模板状态失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 预览合同模板
  const previewTemplate = async (id: string, variables: Record<string, any>) => {
    try {
      loading.value = true
      const response = await contractTemplateApi.preview(id, variables)
      return response.content
    } catch (error) {
      console.error('预览合同模板失败:', error)
      ElMessage.error('预览合同模板失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取模板变量配置
  const getTemplateVariables = async (id: string) => {
    try {
      const response = await contractTemplateApi.getVariables(id)
      return response.variables
    } catch (error) {
      console.error('获取模板变量失败:', error)
      ElMessage.error('获取模板变量失败')
      throw error
    }
  }

  // 获取统计信息
  const fetchStatistics = async () => {
    try {
      const response = await contractTemplateApi.getStatistics()
      statistics.value = response
      return response
    } catch (error) {
      console.error('获取统计信息失败:', error)
      ElMessage.error('获取统计信息失败')
      throw error
    }
  }

  // 批量删除
  const batchDeleteTemplates = async (ids: string[]) => {
    try {
      loading.value = true
      await contractTemplateApi.batchDelete(ids)
      
      // 从列表中移除
      templates.value = templates.value.filter(item => !ids.includes(item.id))
      templateTotal.value -= ids.length
      
      ElMessage.success(`成功删除 ${ids.length} 个合同模板`)
    } catch (error) {
      console.error('批量删除合同模板失败:', error)
      ElMessage.error('批量删除合同模板失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 批量更新状态
  const batchUpdateStatus = async (ids: string[], status: string) => {
    try {
      loading.value = true
      await contractTemplateApi.batchUpdateStatus(ids, status)
      
      // 更新列表中的数据
      templates.value.forEach(item => {
        if (ids.includes(item.id)) {
          item.moban_zhuangtai = status
        }
      })
      
      ElMessage.success(`成功更新 ${ids.length} 个合同模板状态`)
    } catch (error) {
      console.error('批量更新状态失败:', error)
      ElMessage.error('批量更新状态失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 设置分页参数
  const setPage = (newPage: number) => {
    templatePage.value = newPage
  }

  const setSize = (newSize: number) => {
    templateSize.value = newSize
    templatePage.value = 1 // 重置到第一页
  }

  // 重置状态
  const resetState = () => {
    templates.value = []
    currentTemplate.value = null
    templateLoading.value = false
    templateTotal.value = 0
    templatePage.value = 1
    templateSize.value = 20
    statistics.value = null
  }

  return {
    // 状态
    templates,
    currentTemplate,
    templateLoading,
    templateTotal,
    templatePage,
    templateSize,
    statistics,

    // 计算属性
    hasTemplates,
    templateTotalPages,
    
    // 方法
    fetchTemplates,
    fetchTemplateDetail,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    updateTemplateStatus,
    previewTemplate,
    getTemplateVariables,
    fetchStatistics,
    batchDeleteTemplates,
    batchUpdateStatus,
    setPage,
    setSize,
    resetState
  }
})
