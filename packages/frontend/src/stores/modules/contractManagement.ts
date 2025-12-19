/**
 * 合同管理 Store - 阶段2功能
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  contractApi,
  contractPartyApi,
  paymentMethodApi,
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

export const useContractManagementStore = defineStore('contractManagement', () => {
  // ==================== 合同状态 ====================
  const contracts = ref<Contract[]>([])
  const currentContract = ref<Contract | null>(null)
  const contractLoading = ref(false)
  const contractTotal = ref(0)
  const contractPage = ref(1)
  const contractSize = ref(20)

  // ==================== 乙方主体状态 ====================
  const parties = ref<ContractParty[]>([])
  const currentParty = ref<ContractParty | null>(null)
  const partyLoading = ref(false)
  const partyTotal = ref(0)
  const partyPage = ref(1)
  const partySize = ref(20)

  // ==================== 支付方式状态 ====================
  const paymentMethods = ref<PaymentMethod[]>([])
  const currentPaymentMethod = ref<PaymentMethod | null>(null)
  const paymentLoading = ref(false)
  const paymentTotal = ref(0)
  const paymentPage = ref(1)
  const paymentSize = ref(20)

  // ==================== 计算属性 ====================
  const hasContracts = computed(() => contracts.value.length > 0)
  const contractTotalPages = computed(() => Math.ceil(contractTotal.value / contractSize.value))
  
  const hasParties = computed(() => parties.value.length > 0)
  const partyTotalPages = computed(() => Math.ceil(partyTotal.value / partySize.value))
  
  const hasPaymentMethods = computed(() => paymentMethods.value.length > 0)
  const paymentTotalPages = computed(() => Math.ceil(paymentTotal.value / paymentSize.value))

  // ==================== 合同管理方法 ====================
  
  // 获取合同列表
  const fetchContracts = async (params: ContractListParams = {}) => {
    try {
      contractLoading.value = true
      const response = await contractApi.getList({
        page: contractPage.value,
        size: contractSize.value,
        ...params
      })
      
      contracts.value = response.items
      contractTotal.value = response.total
      contractPage.value = response.page
      contractSize.value = response.size
      
      return response
    } catch (error) {
      ElMessage.error('获取合同列表失败')
      throw error
    } finally {
      contractLoading.value = false
    }
  }

  // 获取合同详情
  const fetchContractDetail = async (id: string) => {
    try {
      contractLoading.value = true
      const response = await contractApi.getDetail(id)
      currentContract.value = response
      return response
    } catch (error) {
      ElMessage.error('获取合同详情失败')
      throw error
    } finally {
      contractLoading.value = false
    }
  }

  // 创建合同
  const createContract = async (data: ContractCreate) => {
    try {
      contractLoading.value = true
      const response = await contractApi.create(data)
      
      // 添加到列表开头
      contracts.value.unshift(response)
      contractTotal.value += 1
      
      ElMessage.success('合同创建成功')
      return response
    } catch (error) {
      ElMessage.error('创建合同失败')
      throw error
    } finally {
      contractLoading.value = false
    }
  }

  // 基于报价自动生成合同
  const createContractFromQuote = async (
    baojiaId: string,
    options: { customAmount?: number; changeReason?: string } = {}
  ) => {
    try {
      contractLoading.value = true
      let response

      if (options.customAmount !== undefined || options.changeReason) {
        response = await contractApi.createFromQuoteDirect(baojiaId, {
          custom_amount: options.customAmount,
          change_reason: options.changeReason
        })
      } else {
        response = await contractApi.createFromQuote(baojiaId)
      }
      
      // 添加到列表开头
      contracts.value.unshift(response)
      contractTotal.value += 1
      
      ElMessage.success('基于报价生成合同成功')
      return response
    } catch (error: unknown) {
      const axiosError = error as { response?: { status?: number }; message?: string }

      // 检查是否是400错误（重复创建）
      if (axiosError.response?.status === 400) {
        ElMessage.warning('该报价已经生成过合同，请在合同管理页面查看')
      } else {
        ElMessage.error('基于报价生成合同失败: ' + (axiosError.message || '未知错误'))
      }
      throw error
    } finally {
      contractLoading.value = false
    }
  }

  // 检查报价是否已生成合同
  const checkContractByQuote = async (baojiaId: string) => {
    try {
      const response = await contractApi.checkContractByQuote(baojiaId)
      return response.data
    } catch (error) {
      throw error
    }
  }



  // 更新合同
  const updateContract = async (id: string, data: ContractUpdate) => {
    try {
      contractLoading.value = true
      const response = await contractApi.update(id, data)
      
      // 更新列表中的数据
      const index = contracts.value.findIndex(item => item.id === id)
      if (index !== -1) {
        contracts.value[index] = response
      }
      
      // 更新当前合同
      if (currentContract.value?.id === id) {
        currentContract.value = response
      }
      
      ElMessage.success('合同更新成功')
      return response
    } catch (error) {
      ElMessage.error('更新合同失败')
      throw error
    } finally {
      contractLoading.value = false
    }
  }

  // 删除合同
  const deleteContract = async (id: string) => {
    try {
      contractLoading.value = true
      await contractApi.delete(id)
      
      // 从列表中移除
      const index = contracts.value.findIndex(item => item.id === id)
      if (index !== -1) {
        contracts.value.splice(index, 1)
        contractTotal.value -= 1
      }
      
      // 清空当前合同
      if (currentContract.value?.id === id) {
        currentContract.value = null
      }
      
      ElMessage.success('合同删除成功')
    } catch (error) {
      ElMessage.error('删除合同失败')
      throw error
    } finally {
      contractLoading.value = false
    }
  }

  // 预览合同内容
  const previewContract = async (data: ContractPreview) => {
    try {
      contractLoading.value = true
      const response = await contractApi.preview(data)
      return response.content
    } catch (error) {
      ElMessage.error('预览合同失败')
      throw error
    } finally {
      contractLoading.value = false
    }
  }

  // 签署合同
  const signContract = async (id: string, signature: ContractSignature) => {
    try {
      contractLoading.value = true
      const response = await contractApi.sign(id, signature)
      
      // 更新列表中的数据
      const index = contracts.value.findIndex(item => item.id === id)
      if (index !== -1) {
        contracts.value[index] = response
      }
      
      // 更新当前合同
      if (currentContract.value?.id === id) {
        currentContract.value = response
      }
      
      ElMessage.success('合同签署成功')
      return response
    } catch (error) {
      ElMessage.error('签署合同失败')
      throw error
    } finally {
      contractLoading.value = false
    }
  }

  // 更新合同状态
  const updateContractStatus = async (id: string, status: string) => {
    try {
      contractLoading.value = true
      const response = await contractApi.updateStatus(id, status)
      
      // 更新列表中的数据
      const index = contracts.value.findIndex(item => item.id === id)
      if (index !== -1) {
        contracts.value[index] = response
      }
      
      // 更新当前合同
      if (currentContract.value?.id === id) {
        currentContract.value = response
      }
      
      ElMessage.success('合同状态更新成功')
      return response
    } catch (error) {
      ElMessage.error('更新合同状态失败')
      throw error
    } finally {
      contractLoading.value = false
    }
  }

  // 批量删除合同
  const batchDeleteContracts = async (ids: string[]) => {
    try {
      contractLoading.value = true
      await contractApi.batchDelete(ids)
      
      // 从列表中移除
      contracts.value = contracts.value.filter(item => !ids.includes(item.id))
      contractTotal.value -= ids.length
      
      ElMessage.success(`成功删除 ${ids.length} 个合同`)
    } catch (error) {
      ElMessage.error('批量删除合同失败')
      throw error
    } finally {
      contractLoading.value = false
    }
  }

  // ==================== 乙方主体管理方法 ====================

  // 获取乙方主体列表
  const fetchParties = async (params: ContractPartyListParams = {}) => {
    try {
      partyLoading.value = true
      const response = await contractPartyApi.getList({
        page: partyPage.value,
        size: partySize.value,
        ...params
      })

      parties.value = response.items
      partyTotal.value = response.total
      partyPage.value = response.page
      partySize.value = response.size

      return response
    } catch (error) {
      ElMessage.error('获取乙方主体列表失败')
      throw error
    } finally {
      partyLoading.value = false
    }
  }

  // 获取乙方主体详情
  const fetchPartyDetail = async (id: string) => {
    try {
      partyLoading.value = true
      const response = await contractPartyApi.getDetail(id)
      currentParty.value = response
      return response
    } catch (error) {
      ElMessage.error('获取乙方主体详情失败')
      throw error
    } finally {
      partyLoading.value = false
    }
  }

  // 创建乙方主体
  const createParty = async (data: ContractPartyCreate) => {
    try {
      partyLoading.value = true
      const response = await contractPartyApi.create(data)

      // 添加到列表开头
      parties.value.unshift(response)
      partyTotal.value += 1

      ElMessage.success('乙方主体创建成功')
      return response
    } catch (error) {
      ElMessage.error('创建乙方主体失败')
      throw error
    } finally {
      partyLoading.value = false
    }
  }

  // 更新乙方主体
  const updateParty = async (id: string, data: ContractPartyUpdate) => {
    try {
      partyLoading.value = true
      const response = await contractPartyApi.update(id, data)

      // 更新列表中的数据
      const index = parties.value.findIndex(item => item.id === id)
      if (index !== -1) {
        parties.value[index] = response
      }

      // 更新当前乙方主体
      if (currentParty.value?.id === id) {
        currentParty.value = response
      }

      ElMessage.success('乙方主体更新成功')
      return response
    } catch (error) {
      ElMessage.error('更新乙方主体失败')
      throw error
    } finally {
      partyLoading.value = false
    }
  }

  // 删除乙方主体
  const deleteParty = async (id: string) => {
    try {
      partyLoading.value = true
      await contractPartyApi.delete(id)

      // 从列表中移除
      const index = parties.value.findIndex(item => item.id === id)
      if (index !== -1) {
        parties.value.splice(index, 1)
        partyTotal.value -= 1
      }

      // 清空当前乙方主体
      if (currentParty.value?.id === id) {
        currentParty.value = null
      }

      ElMessage.success('乙方主体删除成功')
    } catch (error) {
      ElMessage.error('删除乙方主体失败')
      throw error
    } finally {
      partyLoading.value = false
    }
  }

  // 批量删除乙方主体
  const batchDeleteParties = async (ids: string[]) => {
    try {
      partyLoading.value = true
      await contractPartyApi.batchDelete(ids)

      // 从列表中移除
      parties.value = parties.value.filter(item => !ids.includes(item.id))
      partyTotal.value -= ids.length

      ElMessage.success(`成功删除 ${ids.length} 个乙方主体`)
    } catch (error) {
      ElMessage.error('批量删除乙方主体失败')
      throw error
    } finally {
      partyLoading.value = false
    }
  }



  // ==================== 支付方式管理方法 ====================

  // 获取支付方式列表
  const fetchPaymentMethods = async (params: PaymentMethodListParams = {}) => {
    try {
      paymentLoading.value = true

      // 使用传入的参数，如果没有则使用store中的默认值
      const requestParams = {
        page: params.page || paymentPage.value,
        size: params.size || paymentSize.value,
        search: params.search,
        yifang_zhuti_id: params.yifang_zhuti_id,
        zhifu_leixing: params.zhifu_leixing,
        zhifu_zhuangtai: params.zhifu_zhuangtai
      }

      const response = await paymentMethodApi.getList(requestParams)

      paymentMethods.value = response.items
      paymentTotal.value = response.total

      // 只有当参数中有page/size时才更新store中的值
      if (params.page !== undefined) {
        paymentPage.value = params.page
      }
      if (params.size !== undefined) {
        paymentSize.value = params.size
      }

      return response
    } catch (error) {
      ElMessage.error('获取支付方式列表失败')
      throw error
    } finally {
      paymentLoading.value = false
    }
  }

  // 获取支付方式详情
  const fetchPaymentMethodDetail = async (id: string) => {
    try {
      paymentLoading.value = true
      const response = await paymentMethodApi.getDetail(id)
      currentPaymentMethod.value = response
      return response
    } catch (error) {
      ElMessage.error('获取支付方式详情失败')
      throw error
    } finally {
      paymentLoading.value = false
    }
  }

  // 创建支付方式
  const createPaymentMethod = async (data: PaymentMethodCreate) => {
    try {
      paymentLoading.value = true
      const response = await paymentMethodApi.create(data)

      // 添加到列表开头
      paymentMethods.value.unshift(response)
      paymentTotal.value += 1

      ElMessage.success('支付方式创建成功')
      return response
    } catch (error) {
      ElMessage.error('创建支付方式失败')
      throw error
    } finally {
      paymentLoading.value = false
    }
  }

  // 更新支付方式
  const updatePaymentMethod = async (id: string, data: PaymentMethodUpdate) => {
    try {
      paymentLoading.value = true
      const response = await paymentMethodApi.update(id, data)

      // 更新列表中的数据
      const index = paymentMethods.value.findIndex(item => item.id === id)
      if (index !== -1) {
        paymentMethods.value[index] = response
      }

      // 更新当前支付方式
      if (currentPaymentMethod.value?.id === id) {
        currentPaymentMethod.value = response
      }

      ElMessage.success('支付方式更新成功')
      return response
    } catch (error) {
      ElMessage.error('更新支付方式失败')
      throw error
    } finally {
      paymentLoading.value = false
    }
  }

  // 删除支付方式
  const deletePaymentMethod = async (id: string) => {
    try {
      paymentLoading.value = true
      await paymentMethodApi.delete(id)

      // 从列表中移除
      const index = paymentMethods.value.findIndex(item => item.id === id)
      if (index !== -1) {
        paymentMethods.value.splice(index, 1)
        paymentTotal.value -= 1
      }

      // 清空当前支付方式
      if (currentPaymentMethod.value?.id === id) {
        currentPaymentMethod.value = null
      }

      ElMessage.success('支付方式删除成功')
    } catch (error) {
      ElMessage.error('删除支付方式失败')
      throw error
    } finally {
      paymentLoading.value = false
    }
  }

  // 设置默认支付方式
  const setDefaultPaymentMethod = async (id: string) => {
    try {
      paymentLoading.value = true
      const response = await paymentMethodApi.setDefault(id)

      // 更新列表中的数据
      paymentMethods.value = paymentMethods.value.map(item => {
        if (item.id === id) {
          return response
        }
        return { ...item, shi_moren: false }
      })

      // 更新当前支付方式
      if (currentPaymentMethod.value?.id === id) {
        currentPaymentMethod.value = response
      }

      ElMessage.success('默认支付方式设置成功')
      return response
    } catch (error) {
      ElMessage.error('设置默认支付方式失败')
      throw error
    } finally {
      paymentLoading.value = false
    }
  }

  // 批量删除支付方式
  const batchDeletePaymentMethods = async (ids: string[]) => {
    try {
      paymentLoading.value = true
      await paymentMethodApi.batchDelete(ids)

      // 从列表中移除
      paymentMethods.value = paymentMethods.value.filter(item => !ids.includes(item.id))
      paymentTotal.value -= ids.length

      ElMessage.success(`成功删除 ${ids.length} 个支付方式`)
    } catch (error) {
      ElMessage.error('批量删除支付方式失败')
      throw error
    } finally {
      paymentLoading.value = false
    }
  }

  // ==================== 分页和重置方法 ====================

  // 设置合同分页参数
  const setContractPage = (newPage: number) => {
    contractPage.value = newPage
  }

  const setContractSize = (newSize: number) => {
    contractSize.value = newSize
    contractPage.value = 1 // 重置到第一页
  }

  // 设置乙方主体分页参数
  const setPartyPage = (newPage: number) => {
    partyPage.value = newPage
  }

  const setPartySize = (newSize: number) => {
    partySize.value = newSize
    partyPage.value = 1 // 重置到第一页
  }

  // 设置支付方式分页参数
  const setPaymentPage = (newPage: number) => {
    paymentPage.value = newPage
  }

  const setPaymentSize = (newSize: number) => {
    paymentSize.value = newSize
    paymentPage.value = 1 // 重置到第一页
  }

  // 重置状态
  const resetState = () => {
    // 重置合同状态
    contracts.value = []
    currentContract.value = null
    contractLoading.value = false
    contractTotal.value = 0
    contractPage.value = 1
    contractSize.value = 20

    // 重置乙方主体状态
    parties.value = []
    currentParty.value = null
    partyLoading.value = false
    partyTotal.value = 0
    partyPage.value = 1
    partySize.value = 20

    // 重置支付方式状态
    paymentMethods.value = []
    currentPaymentMethod.value = null
    paymentLoading.value = false
    paymentTotal.value = 0
    paymentPage.value = 1
    paymentSize.value = 20
  }

  return {
    // 合同状态
    contracts,
    currentContract,
    contractLoading,
    contractTotal,
    contractPage,
    contractSize,

    // 乙方主体状态
    parties,
    currentParty,
    partyLoading,
    partyTotal,
    partyPage,
    partySize,

    // 支付方式状态
    paymentMethods,
    currentPaymentMethod,
    paymentLoading,
    paymentTotal,
    paymentPage,
    paymentSize,

    // 计算属性
    hasContracts,
    contractTotalPages,
    hasParties,
    partyTotalPages,
    hasPaymentMethods,
    paymentTotalPages,

    // 合同方法
    fetchContracts,
    fetchContractDetail,
    createContract,
    createContractFromQuote,
    checkContractByQuote,
    updateContract,
    deleteContract,
    previewContract,
    signContract,
    updateContractStatus,
    batchDeleteContracts,

    // 乙方主体方法
    fetchParties,
    fetchPartyDetail,
    createParty,
    updateParty,
    deleteParty,
    batchDeleteParties,

    // 支付方式方法
    fetchPaymentMethods,
    fetchPaymentMethodDetail,
    createPaymentMethod,
    updatePaymentMethod,
    deletePaymentMethod,
    setDefaultPaymentMethod,
    batchDeletePaymentMethods,

    // 分页和重置方法
    setContractPage,
    setContractSize,
    setPartyPage,
    setPartySize,
    setPaymentPage,
    setPaymentSize,
    resetState
  }
})
