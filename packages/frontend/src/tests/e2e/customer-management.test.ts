/**
 * 客户管理端到端测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import CustomerList from '@/views/customer/CustomerList.vue'
import CustomerDetail from '@/views/customer/CustomerDetail.vue'
import { useCustomerStore } from '@/stores/modules/customer'
import { useAuthStore } from '@/stores/modules/auth'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn().mockResolvedValue('confirm')
  }
}))

// Mock API
const mockCustomerApi = {
  getList: vi.fn(),
  create: vi.fn(),
  update: vi.fn(),
  delete: vi.fn(),
  updateStatus: vi.fn(),
  getDetail: vi.fn()
}

const mockServiceRecordApi = {
  getList: vi.fn(),
  create: vi.fn(),
  update: vi.fn(),
  delete: vi.fn(),
  getCustomerRecords: vi.fn(),
  updateStatus: vi.fn()
}

vi.mock('@/api/modules/customer', () => ({
  customerApi: mockCustomerApi,
  serviceRecordApi: mockServiceRecordApi
}))

describe('客户管理端到端测试', () => {
  let router: ReturnType<typeof createRouter>
  let customerStore: ReturnType<typeof useCustomerStore>
  let authStore: ReturnType<typeof useAuthStore>

  const mockUser = {
    id: 'user1',
    yonghu_ming: 'testuser',
    xingming: '测试用户',
    youxiang: 'test@example.com',
    jiaose_liebiao: [
      {
        jiaose_bianma: 'admin',
        jiaose_ming: '管理员',
        quanxian_liebiao: [
          { quanxian_bianma: 'customer:read' },
          { quanxian_bianma: 'customer:write' },
          { quanxian_bianma: 'customer:delete' },
          { quanxian_bianma: 'customer:status_manage' }
        ]
      }
    ]
  }

  const mockCustomers = [
    {
      id: '1',
      gongsi_mingcheng: '测试公司A',
      tongyi_shehui_xinyong_daima: '91110000123456789A',
      faren_xingming: '张三',
      lianxi_dianhua: '13800138000',
      kehu_zhuangtai: 'active',
      fuwu_kaishi_riqi: '2024-01-01T00:00:00',
      created_at: '2024-01-01T00:00:00',
      updated_at: '2024-01-01T00:00:00',
      created_by: 'user1'
    },
    {
      id: '2',
      gongsi_mingcheng: '测试公司B',
      tongyi_shehui_xinyong_daima: '91110000123456789B',
      faren_xingming: '李四',
      lianxi_dianhua: '13800138001',
      kehu_zhuangtai: 'renewing',
      fuwu_kaishi_riqi: '2024-02-01T00:00:00',
      created_at: '2024-02-01T00:00:00',
      updated_at: '2024-02-01T00:00:00',
      created_by: 'user1'
    }
  ]

  const mockServiceRecords = [
    {
      id: '1',
      kehu_id: '1',
      goutong_fangshi: 'phone',
      goutong_neirong: '客户咨询发票问题',
      goutong_shijian: '2024-01-15 10:30:00',
      chuli_zhuangtai: 'completed',
      created_at: '2024-01-15T10:30:00',
      updated_at: '2024-01-15T11:00:00',
      created_by: 'user1'
    }
  ]

  beforeEach(() => {
    setActivePinia(createPinia())
    
    // 创建路由
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/customers', component: CustomerList },
        { path: '/customers/:id', component: CustomerDetail }
      ]
    })

    // 初始化 stores
    customerStore = useCustomerStore()
    authStore = useAuthStore()
    
    // Mock auth store
    authStore.user = mockUser
    authStore.isAuthenticated = true
    authStore.hasPermission = vi.fn((permission: string) => {
      const permissions = ['customer:read', 'customer:write', 'customer:delete', 'customer:status_manage']
      return permissions.includes(permission)
    })

    // Mock API responses
    mockCustomerApi.getList.mockResolvedValue({
      data: {
        total: mockCustomers.length,
        items: mockCustomers,
        page: 1,
        size: 20
      }
    })

    mockCustomerApi.getDetail.mockResolvedValue({
      data: mockCustomers[0]
    })

    mockCustomerApi.create.mockResolvedValue({
      data: {
        ...mockCustomers[0],
        id: 'new-customer-id',
        gongsi_mingcheng: '新创建的公司'
      }
    })

    mockCustomerApi.update.mockResolvedValue({
      data: {
        ...mockCustomers[0],
        gongsi_mingcheng: '更新后的公司名称'
      }
    })

    mockCustomerApi.updateStatus.mockResolvedValue({
      data: {
        ...mockCustomers[0],
        kehu_zhuangtai: 'terminated'
      }
    })

    mockCustomerApi.delete.mockResolvedValue({})

    mockServiceRecordApi.getCustomerRecords.mockResolvedValue({
      data: {
        total: mockServiceRecords.length,
        items: mockServiceRecords,
        page: 1,
        size: 20
      }
    })

    mockServiceRecordApi.create.mockResolvedValue({
      data: {
        ...mockServiceRecords[0],
        id: 'new-record-id',
        goutong_neirong: '新的服务记录'
      }
    })

    vi.clearAllMocks()
  })

  describe('客户列表页面完整流程', () => {
    it('应该完成客户列表的完整操作流程', async () => {
      const wrapper = mount(CustomerList, {
        global: {
          plugins: [router],
          stubs: {
            'el-input': true,
            'el-select': true,
            'el-option': true,
            'el-button': true,
            'el-card': true,
            'el-table': true,
            'el-table-column': true,
            'el-tag': true,
            'el-dropdown': true,
            'el-dropdown-menu': true,
            'el-dropdown-item': true,
            'el-pagination': true,
            'el-icon': true,
            'CustomerForm': true,
            'CustomerStatusDialog': true
          }
        }
      })

      // 1. 验证页面初始化
      expect(wrapper.find('.customer-list').exists()).toBe(true)
      expect(customerStore.fetchCustomers).toHaveBeenCalled()

      // 2. 测试搜索功能
      await wrapper.vm.handleSearch('测试公司A')
      expect(customerStore.fetchCustomers).toHaveBeenCalledWith({
        search: '测试公司A',
        kehu_zhuangtai: ''
      })

      // 3. 测试筛选功能
      await wrapper.vm.handleFilter('active')
      expect(customerStore.fetchCustomers).toHaveBeenCalledWith({
        search: '',
        kehu_zhuangtai: 'active'
      })

      // 4. 测试新增客户
      wrapper.vm.handleCreate()
      expect(wrapper.vm.formVisible).toBe(true)
      expect(wrapper.vm.formMode).toBe('create')

      // 5. 测试编辑客户
      wrapper.vm.handleEdit(mockCustomers[0])
      expect(wrapper.vm.currentCustomer).toBe(mockCustomers[0])
      expect(wrapper.vm.formMode).toBe('edit')

      // 6. 测试状态管理
      wrapper.vm.handleDropdownCommand('status', mockCustomers[0])
      expect(wrapper.vm.statusDialogVisible).toBe(true)

      // 7. 测试删除客户
      await wrapper.vm.handleDelete(mockCustomers[0])
      expect(customerStore.deleteCustomer).toHaveBeenCalledWith(mockCustomers[0].id)

      // 8. 测试分页
      await wrapper.vm.handleCurrentChange(2)
      expect(customerStore.currentPage).toBe(2)
      expect(customerStore.fetchCustomers).toHaveBeenCalled()
    })
  })

  describe('客户详情页面完整流程', () => {
    it('应该完成客户详情的完整操作流程', async () => {
      // 设置路由参数
      router.push('/customers/1')
      await router.isReady()

      const wrapper = mount(CustomerDetail, {
        global: {
          plugins: [router],
          stubs: {
            'el-card': true,
            'el-descriptions': true,
            'el-descriptions-item': true,
            'el-button': true,
            'el-tag': true,
            'el-table': true,
            'el-table-column': true,
            'el-pagination': true,
            'el-tabs': true,
            'el-tab-pane': true,
            'el-icon': true,
            'CustomerForm': true,
            'CustomerStatusDialog': true
          }
        }
      })

      // 1. 验证页面初始化
      expect(wrapper.find('.customer-detail').exists()).toBe(true)
      expect(customerStore.fetchCustomerDetail).toHaveBeenCalledWith('1')
      expect(customerStore.fetchServiceRecords).toHaveBeenCalledWith({
        kehu_id: '1'
      })

      // 2. 测试编辑客户
      wrapper.vm.handleEdit()
      expect(wrapper.vm.formVisible).toBe(true)
      expect(wrapper.vm.formMode).toBe('edit')

      // 3. 测试状态管理
      wrapper.vm.handleStatusManage()
      expect(wrapper.vm.statusDialogVisible).toBe(true)

      // 4. 测试删除客户
      await wrapper.vm.handleDelete()
      expect(customerStore.deleteCustomer).toHaveBeenCalledWith('1')

      // 5. 测试新增服务记录
      wrapper.vm.handleAddServiceRecord()
      expect(wrapper.vm.serviceRecordFormVisible).toBe(true)
      expect(wrapper.vm.serviceRecordFormMode).toBe('create')

      // 6. 测试编辑服务记录
      wrapper.vm.handleEditServiceRecord(mockServiceRecords[0])
      expect(wrapper.vm.currentServiceRecord).toBe(mockServiceRecords[0])
      expect(wrapper.vm.serviceRecordFormMode).toBe('edit')

      // 7. 测试服务记录分页
      await wrapper.vm.handleServiceRecordPageChange(2)
      expect(customerStore.fetchServiceRecords).toHaveBeenCalledWith({
        kehu_id: '1',
        page: 2
      })
    })
  })

  describe('权限控制测试', () => {
    it('应该根据用户权限显示/隐藏操作按钮', async () => {
      // 测试有权限的用户
      const wrapper = mount(CustomerList, {
        global: {
          plugins: [router],
          stubs: {
            'el-input': true,
            'el-select': true,
            'el-option': true,
            'el-button': true,
            'el-card': true,
            'el-table': true,
            'el-table-column': true,
            'el-tag': true,
            'el-dropdown': true,
            'el-dropdown-menu': true,
            'el-dropdown-item': true,
            'el-pagination': true,
            'el-icon': true,
            'CustomerForm': true,
            'CustomerStatusDialog': true
          }
        }
      })

      // 验证有权限时显示操作按钮
      expect(wrapper.vm.canWrite).toBe(true)
      expect(wrapper.vm.canDelete).toBe(true)
      expect(wrapper.vm.canManageStatus).toBe(true)

      // 测试无权限的用户
      authStore.hasPermission = vi.fn(() => false)
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.canWrite).toBe(false)
      expect(wrapper.vm.canDelete).toBe(false)
      expect(wrapper.vm.canManageStatus).toBe(false)
    })
  })

  describe('错误处理测试', () => {
    it('应该正确处理API错误', async () => {
      // Mock API 错误
      mockCustomerApi.getList.mockRejectedValue(new Error('网络错误'))
      
      const wrapper = mount(CustomerList, {
        global: {
          plugins: [router],
          stubs: {
            'el-input': true,
            'el-select': true,
            'el-option': true,
            'el-button': true,
            'el-card': true,
            'el-table': true,
            'el-table-column': true,
            'el-tag': true,
            'el-dropdown': true,
            'el-dropdown-menu': true,
            'el-dropdown-item': true,
            'el-pagination': true,
            'el-icon': true,
            'CustomerForm': true,
            'CustomerStatusDialog': true
          }
        }
      })

      // 等待错误处理
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // 验证错误消息显示
      expect(ElMessage.error).toHaveBeenCalledWith('获取客户列表失败')
    })
  })
})
