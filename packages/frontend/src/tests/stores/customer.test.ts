/**
 * 客户管理 Store 测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { ElMessage } from 'element-plus'
import { useCustomerStore } from '@/stores/modules/customer'
import { customerApi, serviceRecordApi } from '@/api/modules/customer'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

// Mock API
vi.mock('@/api/modules/customer', () => ({
  customerApi: {
    getList: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    updateStatus: vi.fn(),
    getDetail: vi.fn()
  },
  serviceRecordApi: {
    getList: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    getCustomerRecords: vi.fn(),
    updateStatus: vi.fn()
  }
}))

describe('useCustomerStore', () => {
  let customerStore: ReturnType<typeof useCustomerStore>

  const mockCustomer = {
    id: '1',
    gongsi_mingcheng: '测试公司',
    tongyi_shehui_xinyong_daima: '91110000123456789A',
    faren_xingming: '张三',
    lianxi_dianhua: '13800138000',
    kehu_zhuangtai: 'active' as const,
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
    created_by: 'user1'
  }

  const mockCustomerList = {
    total: 2,
    items: [
      mockCustomer,
      {
        ...mockCustomer,
        id: '2',
        gongsi_mingcheng: '测试公司B',
        kehu_zhuangtai: 'renewing' as const
      }
    ],
    page: 1,
    size: 20
  }

  const mockServiceRecord = {
    id: '1',
    kehu_id: '1',
    goutong_fangshi: 'phone' as const,
    goutong_neirong: '客户咨询',
    goutong_shijian: '2024-01-01 10:00:00',
    chuli_zhuangtai: 'pending' as const,
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
    created_by: 'user1'
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    customerStore = useCustomerStore()
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      expect(customerStore.customers).toEqual([])
      expect(customerStore.currentCustomer).toBe(null)
      expect(customerStore.serviceRecords).toEqual([])
      expect(customerStore.loading).toBe(false)
      expect(customerStore.total).toBe(0)
      expect(customerStore.currentPage).toBe(1)
      expect(customerStore.pageSize).toBe(20)
    })
  })

  describe('计算属性', () => {
    beforeEach(() => {
      customerStore.customers = mockCustomerList.items
    })

    it('应该正确计算活跃客户', () => {
      expect(customerStore.activeCustomers).toHaveLength(1)
      expect(customerStore.activeCustomers[0].kehu_zhuangtai).toBe('active')
    })

    it('应该正确计算续约中客户', () => {
      expect(customerStore.renewingCustomers).toHaveLength(1)
      expect(customerStore.renewingCustomers[0].kehu_zhuangtai).toBe('renewing')
    })

    it('应该正确计算已终止客户', () => {
      expect(customerStore.terminatedCustomers).toHaveLength(0)
    })
  })

  describe('客户管理方法', () => {
    describe('fetchCustomers', () => {
      it('应该成功获取客户列表', async () => {
        vi.mocked(customerApi.getList).mockResolvedValue({
          data: mockCustomerList
        } as any)

        const result = await customerStore.fetchCustomers()

        expect(customerApi.getList).toHaveBeenCalledWith({
          page: 1,
          size: 20
        })
        expect(customerStore.customers).toEqual(mockCustomerList.items)
        expect(customerStore.total).toBe(mockCustomerList.total)
        expect(result).toEqual(mockCustomerList)
      })

      it('应该处理获取客户列表失败', async () => {
        const error = new Error('网络错误')
        vi.mocked(customerApi.getList).mockRejectedValue(error)

        await expect(customerStore.fetchCustomers()).rejects.toThrow(error)
        expect(ElMessage.error).toHaveBeenCalledWith('获取客户列表失败')
      })
    })

    describe('fetchCustomerDetail', () => {
      it('应该成功获取客户详情', async () => {
        vi.mocked(customerApi.getDetail).mockResolvedValue({
          data: mockCustomer
        } as any)

        const result = await customerStore.fetchCustomerDetail('1')

        expect(customerApi.getDetail).toHaveBeenCalledWith('1')
        expect(customerStore.currentCustomer).toEqual(mockCustomer)
        expect(result).toEqual(mockCustomer)
      })

      it('应该处理获取客户详情失败', async () => {
        const error = new Error('客户不存在')
        vi.mocked(customerApi.getDetail).mockRejectedValue(error)

        await expect(customerStore.fetchCustomerDetail('1')).rejects.toThrow(error)
        expect(ElMessage.error).toHaveBeenCalledWith('获取客户详情失败')
      })
    })

    describe('createCustomer', () => {
      it('应该成功创建客户', async () => {
        const customerData = {
          gongsi_mingcheng: '新客户',
          tongyi_shehui_xinyong_daima: '91110000123456789B',
          faren_xingming: '李四',
          kehu_zhuangtai: 'active' as const
        }

        vi.mocked(customerApi.create).mockResolvedValue({
          data: { ...mockCustomer, ...customerData }
        } as any)

        const result = await customerStore.createCustomer(customerData)

        expect(customerApi.create).toHaveBeenCalledWith(customerData)
        expect(customerStore.customers[0]).toEqual(expect.objectContaining(customerData))
        expect(customerStore.total).toBe(1)
        expect(ElMessage.success).toHaveBeenCalledWith('客户创建成功')
        expect(result).toEqual(expect.objectContaining(customerData))
      })

      it('应该处理创建客户失败', async () => {
        const customerData = {
          gongsi_mingcheng: '新客户',
          tongyi_shehui_xinyong_daima: '91110000123456789B',
          faren_xingming: '李四',
          kehu_zhuangtai: 'active' as const
        }
        const error = new Error('信用代码已存在')
        vi.mocked(customerApi.create).mockRejectedValue(error)

        await expect(customerStore.createCustomer(customerData)).rejects.toThrow(error)
        expect(ElMessage.error).toHaveBeenCalledWith('创建客户失败')
      })
    })

    describe('updateCustomer', () => {
      beforeEach(() => {
        customerStore.customers = [mockCustomer]
        customerStore.currentCustomer = mockCustomer
      })

      it('应该成功更新客户', async () => {
        const updateData = { gongsi_mingcheng: '更新后的公司名称' }
        const updatedCustomer = { ...mockCustomer, ...updateData }

        vi.mocked(customerApi.update).mockResolvedValue({
          data: updatedCustomer
        } as any)

        const result = await customerStore.updateCustomer('1', updateData)

        expect(customerApi.update).toHaveBeenCalledWith('1', updateData)
        expect(customerStore.customers[0]).toEqual(updatedCustomer)
        expect(customerStore.currentCustomer).toEqual(updatedCustomer)
        expect(ElMessage.success).toHaveBeenCalledWith('客户信息更新成功')
        expect(result).toEqual(updatedCustomer)
      })
    })

    describe('deleteCustomer', () => {
      beforeEach(() => {
        customerStore.customers = [mockCustomer]
        customerStore.currentCustomer = mockCustomer
        customerStore.total = 1
      })

      it('应该成功删除客户', async () => {
        vi.mocked(customerApi.delete).mockResolvedValue({} as any)

        const result = await customerStore.deleteCustomer('1')

        expect(customerApi.delete).toHaveBeenCalledWith('1')
        expect(customerStore.customers).toHaveLength(0)
        expect(customerStore.currentCustomer).toBe(null)
        expect(customerStore.total).toBe(0)
        expect(ElMessage.success).toHaveBeenCalledWith('客户删除成功')
        expect(result).toBe(true)
      })
    })

    describe('updateCustomerStatus', () => {
      beforeEach(() => {
        customerStore.customers = [mockCustomer]
        customerStore.currentCustomer = mockCustomer
      })

      it('应该成功更新客户状态', async () => {
        const updatedCustomer = { ...mockCustomer, kehu_zhuangtai: 'renewing' as const }

        vi.mocked(customerApi.updateStatus).mockResolvedValue({
          data: updatedCustomer
        } as any)

        const result = await customerStore.updateCustomerStatus('1', 'renewing')

        expect(customerApi.updateStatus).toHaveBeenCalledWith('1', 'renewing')
        expect(customerStore.customers[0].kehu_zhuangtai).toBe('renewing')
        expect(customerStore.currentCustomer?.kehu_zhuangtai).toBe('renewing')
        expect(ElMessage.success).toHaveBeenCalledWith('客户状态更新成功')
        expect(result).toEqual(updatedCustomer)
      })
    })
  })

  describe('服务记录管理方法', () => {
    describe('fetchServiceRecords', () => {
      it('应该成功获取服务记录列表', async () => {
        const mockRecordList = {
          total: 1,
          items: [mockServiceRecord],
          page: 1,
          size: 20
        }

        vi.mocked(serviceRecordApi.getList).mockResolvedValue({
          data: mockRecordList
        } as any)

        const result = await customerStore.fetchServiceRecords()

        expect(serviceRecordApi.getList).toHaveBeenCalledWith({})
        expect(customerStore.serviceRecords).toEqual(mockRecordList.items)
        expect(result).toEqual(mockRecordList)
      })
    })

    describe('createServiceRecord', () => {
      it('应该成功创建服务记录', async () => {
        const recordData = {
          kehu_id: '1',
          goutong_fangshi: 'phone' as const,
          goutong_neirong: '客户咨询',
          goutong_shijian: '2024-01-01 10:00:00',
          chuli_zhuangtai: 'pending' as const
        }

        vi.mocked(serviceRecordApi.create).mockResolvedValue({
          data: mockServiceRecord
        } as any)

        const result = await customerStore.createServiceRecord(recordData)

        expect(serviceRecordApi.create).toHaveBeenCalledWith(recordData)
        expect(customerStore.serviceRecords[0]).toEqual(mockServiceRecord)
        expect(ElMessage.success).toHaveBeenCalledWith('服务记录创建成功')
        expect(result).toEqual(mockServiceRecord)
      })
    })
  })

  describe('工具方法', () => {
    describe('resetState', () => {
      it('应该重置所有状态', () => {
        // 先设置一些状态
        customerStore.customers = [mockCustomer]
        customerStore.currentCustomer = mockCustomer
        customerStore.serviceRecords = [mockServiceRecord]
        customerStore.loading = true
        customerStore.total = 10
        customerStore.currentPage = 2
        customerStore.pageSize = 50

        // 重置状态
        customerStore.resetState()

        // 验证状态已重置
        expect(customerStore.customers).toEqual([])
        expect(customerStore.currentCustomer).toBe(null)
        expect(customerStore.serviceRecords).toEqual([])
        expect(customerStore.loading).toBe(false)
        expect(customerStore.total).toBe(0)
        expect(customerStore.currentPage).toBe(1)
        expect(customerStore.pageSize).toBe(20)
      })
    })
  })
})
