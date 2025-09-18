/**
 * 合同模板管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  contractTemplateApi, 
  type ContractTemplate, 
  type ContractTemplateCreate, 
  type ContractTemplateUpdate,
  type ContractTemplateListParams,
  type ContractTemplateStatistics
} from '@/api/modules/contract'

export const useContractStore = defineStore('contract', () => {
  // 状态
  const templates = ref<ContractTemplate[]>([])
  const currentTemplate = ref<ContractTemplate | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const size = ref(20)
  const statistics = ref<ContractTemplateStatistics | null>(null)

  // 计算属性
  const hasTemplates = computed(() => templates.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / size.value))

  // 获取合同模板列表
  const fetchTemplates = async (params: ContractTemplateListParams = {}) => {
    try {
      loading.value = true
      const response = await contractTemplateApi.getList({
        page: page.value,
        size: size.value,
        ...params
      })
      
      templates.value = response.items
      total.value = response.total
      page.value = response.page
      size.value = response.size
      
      return response
    } catch (error) {
      console.error('获取合同模板列表失败:', error)
      ElMessage.error('获取合同模板列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取合同模板详情
  const fetchTemplateDetail = async (id: string) => {
    try {
      loading.value = true
      const response = await contractTemplateApi.getDetail(id)
      currentTemplate.value = response
      return response
    } catch (error) {
      console.error('获取合同模板详情失败:', error)
      ElMessage.error('获取合同模板详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建合同模板
  const createTemplate = async (data: ContractTemplateCreate) => {
    try {
      loading.value = true
      const response = await contractTemplateApi.create(data)
      
      // 添加到列表开头
      templates.value.unshift(response)
      total.value += 1
      
      ElMessage.success('合同模板创建成功')
      return response
    } catch (error) {
      console.error('创建合同模板失败:', error)
      ElMessage.error('创建合同模板失败')
      throw error
    } finally {
      loading.value = false
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
        total.value -= 1
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
      total.value -= ids.length
      
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
    page.value = newPage
  }

  const setSize = (newSize: number) => {
    size.value = newSize
    page.value = 1 // 重置到第一页
  }

  // 重置状态
  const resetState = () => {
    templates.value = []
    currentTemplate.value = null
    loading.value = false
    total.value = 0
    page.value = 1
    size.value = 20
    statistics.value = null
  }

  return {
    // 状态
    templates,
    currentTemplate,
    loading,
    total,
    page,
    size,
    statistics,
    
    // 计算属性
    hasTemplates,
    totalPages,
    
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
