/**
 * 客户管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  customerApi, 
  serviceRecordApi,
  type Customer, 
  type CustomerCreate, 
  type CustomerUpdate,
  type CustomerListParams,
  type ServiceRecord,
  type ServiceRecordCreate,
  type ServiceRecordUpdate,
  type ServiceRecordListParams
} from '@/api/modules/customer'

export const useCustomerStore = defineStore('customer', () => {
  // 状态
  const customers = ref<Customer[]>([])
  const currentCustomer = ref<Customer | null>(null)
  const serviceRecords = ref<ServiceRecord[]>([])
  const currentServiceRecord = ref<ServiceRecord | null>(null)
  
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 计算属性
  const activeCustomers = computed(() => 
    customers.value.filter(customer => customer.kehu_zhuangtai === 'active')
  )
  
  const renewingCustomers = computed(() => 
    customers.value.filter(customer => customer.kehu_zhuangtai === 'renewing')
  )
  
  const terminatedCustomers = computed(() => 
    customers.value.filter(customer => customer.kehu_zhuangtai === 'terminated')
  )

  // 客户管理方法
  const fetchCustomers = async (params: CustomerListParams = {}) => {
    try {
      loading.value = true
      const response = await customerApi.getList({
        page: currentPage.value,
        size: pageSize.value,
        ...params
      })

      customers.value = response.items
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.size

      return response
    } catch (error) {
      console.error('获取客户列表失败:', error)
      ElMessage.error('获取客户列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchCustomerDetail = async (id: string) => {
    try {
      loading.value = true
      const response = await customerApi.getDetail(id)
      currentCustomer.value = response.data
      return response.data
    } catch (error) {
      console.error('获取客户详情失败:', error)
      ElMessage.error('获取客户详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const createCustomer = async (customerData: CustomerCreate) => {
    try {
      loading.value = true
      const response = await customerApi.create(customerData)
      
      // 添加到列表中
      customers.value.unshift(response.data)
      total.value += 1
      
      ElMessage.success('客户创建成功')
      return response.data
    } catch (error) {
      console.error('创建客户失败:', error)
      ElMessage.error('创建客户失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateCustomer = async (id: string, customerData: CustomerUpdate) => {
    try {
      loading.value = true
      const response = await customerApi.update(id, customerData)
      
      // 更新列表中的数据
      const index = customers.value.findIndex(customer => customer.id === id)
      if (index !== -1) {
        customers.value[index] = response.data
      }
      
      // 更新当前客户
      if (currentCustomer.value?.id === id) {
        currentCustomer.value = response.data
      }
      
      ElMessage.success('客户信息更新成功')
      return response.data
    } catch (error) {
      console.error('更新客户失败:', error)
      ElMessage.error('更新客户失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteCustomer = async (id: string) => {
    try {
      loading.value = true
      await customerApi.delete(id)
      
      // 从列表中移除
      const index = customers.value.findIndex(customer => customer.id === id)
      if (index !== -1) {
        customers.value.splice(index, 1)
        total.value -= 1
      }
      
      // 清除当前客户
      if (currentCustomer.value?.id === id) {
        currentCustomer.value = null
      }
      
      ElMessage.success('客户删除成功')
      return true
    } catch (error) {
      console.error('删除客户失败:', error)
      ElMessage.error('删除客户失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateCustomerStatus = async (id: string, status: string) => {
    try {
      loading.value = true
      const response = await customerApi.updateStatus(id, status)
      
      // 更新列表中的数据
      const index = customers.value.findIndex(customer => customer.id === id)
      if (index !== -1) {
        customers.value[index] = response.data
      }
      
      // 更新当前客户
      if (currentCustomer.value?.id === id) {
        currentCustomer.value = response.data
      }
      
      ElMessage.success('客户状态更新成功')
      return response.data
    } catch (error) {
      console.error('更新客户状态失败:', error)
      ElMessage.error('更新客户状态失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 服务记录管理方法
  const fetchServiceRecords = async (params: ServiceRecordListParams = {}) => {
    try {
      loading.value = true
      const response = await serviceRecordApi.getList(params)
      serviceRecords.value = response.items
      return response
    } catch (error) {
      console.error('获取服务记录失败:', error)
      ElMessage.error('获取服务记录失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchCustomerServiceRecords = async (customerId: string, params: { page?: number; size?: number } = {}) => {
    try {
      loading.value = true
      const response = await serviceRecordApi.getCustomerRecords(customerId, params)
      serviceRecords.value = response.items
      return response
    } catch (error) {
      console.error('获取客户服务记录失败:', error)
      ElMessage.error('获取客户服务记录失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const createServiceRecord = async (recordData: ServiceRecordCreate) => {
    try {
      loading.value = true
      const response = await serviceRecordApi.create(recordData)
      
      // 添加到列表中
      serviceRecords.value.unshift(response.data)
      
      ElMessage.success('服务记录创建成功')
      return response.data
    } catch (error) {
      console.error('创建服务记录失败:', error)
      ElMessage.error('创建服务记录失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateServiceRecord = async (id: string, recordData: ServiceRecordUpdate) => {
    try {
      loading.value = true
      const response = await serviceRecordApi.update(id, recordData)
      
      // 更新列表中的数据
      const index = serviceRecords.value.findIndex(record => record.id === id)
      if (index !== -1) {
        serviceRecords.value[index] = response.data
      }
      
      ElMessage.success('服务记录更新成功')
      return response.data
    } catch (error) {
      console.error('更新服务记录失败:', error)
      ElMessage.error('更新服务记录失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateServiceRecordStatus = async (id: string, status: string, result?: string) => {
    try {
      loading.value = true
      const response = await serviceRecordApi.updateStatus(id, status, result)
      
      // 更新列表中的数据
      const index = serviceRecords.value.findIndex(record => record.id === id)
      if (index !== -1) {
        serviceRecords.value[index] = response.data
      }
      
      ElMessage.success('处理状态更新成功')
      return response.data
    } catch (error) {
      console.error('更新处理状态失败:', error)
      ElMessage.error('更新处理状态失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 重置状态
  const resetState = () => {
    customers.value = []
    currentCustomer.value = null
    serviceRecords.value = []
    currentServiceRecord.value = null
    loading.value = false
    total.value = 0
    currentPage.value = 1
    pageSize.value = 20
  }

  return {
    // 状态
    customers,
    currentCustomer,
    serviceRecords,
    currentServiceRecord,
    loading,
    total,
    currentPage,
    pageSize,
    
    // 计算属性
    activeCustomers,
    renewingCustomers,
    terminatedCustomers,
    
    // 客户管理方法
    fetchCustomers,
    fetchCustomerDetail,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    updateCustomerStatus,
    
    // 服务记录管理方法
    fetchServiceRecords,
    fetchCustomerServiceRecords,
    createServiceRecord,
    updateServiceRecord,
    updateServiceRecordStatus,
    
    // 工具方法
    resetState
  }
})
