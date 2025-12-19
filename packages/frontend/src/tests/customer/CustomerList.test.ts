/**
 * 客户列表组件测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ElMessage } from 'element-plus'
import CustomerList from '@/views/customer/CustomerList.vue'
import { useCustomerStore } from '@/stores/modules/customer'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn()
  }
}))

// Mock Vue Router
const mockRouter = {
  push: vi.fn(),
  back: vi.fn()
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  useRoute: () => ({
    params: { id: 'test-id' }
  })
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

describe('CustomerList', () => {
  let wrapper: ReturnType<typeof mount>
  let customerStore: ReturnType<typeof useCustomerStore>

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

  beforeEach(() => {
    setActivePinia(createPinia())
    customerStore = useCustomerStore()
    
    // Mock store methods
    customerStore.fetchCustomers = vi.fn().mockResolvedValue({
      total: mockCustomers.length,
      items: mockCustomers,
      page: 1,
      size: 20
    })
    customerStore.deleteCustomer = vi.fn().mockResolvedValue(true)
    customerStore.updateCustomerStatus = vi.fn().mockResolvedValue(mockCustomers[0])
    
    // Mock store state
    customerStore.customers = mockCustomers
    customerStore.loading = false
    customerStore.total = mockCustomers.length
    customerStore.currentPage = 1
    customerStore.pageSize = 20
    customerStore.activeCustomers = mockCustomers.filter(c => c.kehu_zhuangtai === 'active')
    customerStore.renewingCustomers = mockCustomers.filter(c => c.kehu_zhuangtai === 'renewing')
    customerStore.terminatedCustomers = mockCustomers.filter(c => c.kehu_zhuangtai === 'terminated')

    wrapper = mount(CustomerList, {
      global: {
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
  })

  it('应该正确渲染客户列表', () => {
    expect(wrapper.find('.customer-list').exists()).toBe(true)
    expect(wrapper.find('.page-header h2').text()).toBe('客户管理')
  })

  it('应该显示统计卡片', () => {
    const statsCards = wrapper.findAll('.stat-card')
    expect(statsCards).toHaveLength(4)
    
    // 验证统计数据
    expect(wrapper.text()).toContain('活跃客户')
    expect(wrapper.text()).toContain('续约中')
    expect(wrapper.text()).toContain('已终止')
    expect(wrapper.text()).toContain('总客户数')
  })

  it('应该在组件挂载时获取客户列表', () => {
    expect(customerStore.fetchCustomers).toHaveBeenCalled()
  })

  it('应该正确处理搜索功能', async () => {
    const searchInput = wrapper.find('input[placeholder*="搜索"]')
    await searchInput.setValue('测试公司A')
    
    const searchButton = wrapper.find('.search-left .el-button')
    await searchButton.trigger('click')
    
    expect(customerStore.fetchCustomers).toHaveBeenCalledWith({
      search: '测试公司A',
      kehu_zhuangtai: ''
    })
  })

  it('应该正确处理重置功能', async () => {
    // 先设置搜索条件
    const searchInput = wrapper.find('input[placeholder*="搜索"]')
    await searchInput.setValue('测试')
    
    // 点击重置按钮
    const resetButton = wrapper.find('.search-left .el-button:nth-child(4)')
    await resetButton.trigger('click')
    
    expect(customerStore.fetchCustomers).toHaveBeenCalledWith()
  })

  it('应该正确处理新增客户', async () => {
    const createButton = wrapper.find('.search-right .el-button')
    await createButton.trigger('click')
    
    expect(wrapper.vm.formVisible).toBe(true)
    expect(wrapper.vm.formMode).toBe('create')
    expect(wrapper.vm.currentCustomer).toBe(null)
  })

  it('应该正确格式化客户状态', () => {
    expect(wrapper.vm.getStatusText('active')).toBe('活跃')
    expect(wrapper.vm.getStatusText('renewing')).toBe('续约中')
    expect(wrapper.vm.getStatusText('terminated')).toBe('已终止')
    
    expect(wrapper.vm.getStatusType('active')).toBe('success')
    expect(wrapper.vm.getStatusType('renewing')).toBe('warning')
    expect(wrapper.vm.getStatusType('terminated')).toBe('danger')
  })

  it('应该正确格式化日期', () => {
    const dateString = '2024-01-01T00:00:00'
    const formatted = wrapper.vm.formatDate(dateString)
    expect(formatted).toBe('2024/1/1')
  })

  it('应该正确处理分页变化', async () => {
    await wrapper.vm.handleSizeChange(50)
    expect(customerStore.pageSize).toBe(50)
    expect(customerStore.fetchCustomers).toHaveBeenCalled()
    
    await wrapper.vm.handleCurrentChange(2)
    expect(customerStore.currentPage).toBe(2)
    expect(customerStore.fetchCustomers).toHaveBeenCalled()
  })

  it('应该正确处理表单成功回调', async () => {
    await wrapper.vm.handleFormSuccess()
    expect(wrapper.vm.formVisible).toBe(false)
    expect(customerStore.fetchCustomers).toHaveBeenCalled()
  })

  it('应该正确处理状态变更成功回调', async () => {
    await wrapper.vm.handleStatusSuccess()
    expect(wrapper.vm.statusDialogVisible).toBe(false)
    expect(customerStore.fetchCustomers).toHaveBeenCalled()
  })

  it('应该正确处理查看客户', () => {
    const customer = mockCustomers[0]
    wrapper.vm.handleView(customer)
    expect(mockRouter.push).toHaveBeenCalledWith(`/customers/${customer.id}`)
  })

  it('应该正确处理编辑客户', () => {
    const customer = mockCustomers[0]
    wrapper.vm.handleEdit(customer)
    
    expect(wrapper.vm.currentCustomer).toBe(customer)
    expect(wrapper.vm.formMode).toBe('edit')
    expect(wrapper.vm.formVisible).toBe(true)
  })

  it('应该正确处理下拉菜单命令', () => {
    const customer = mockCustomers[0]
    
    // 测试状态管理
    wrapper.vm.handleDropdownCommand('status', customer)
    expect(wrapper.vm.currentCustomer).toBe(customer)
    expect(wrapper.vm.statusDialogVisible).toBe(true)
    
    // 测试服务记录
    wrapper.vm.handleDropdownCommand('records', customer)
    expect(mockRouter.push).toHaveBeenCalledWith(`/customers/${customer.id}/records`)
  })

  it('应该正确处理客户删除', async () => {
    const customer = mockCustomers[0]
    
    // Mock ElMessageBox.confirm
    const { ElMessageBox } = await import('element-plus')
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm')
    
    await wrapper.vm.handleDelete(customer)
    
    expect(customerStore.deleteCustomer).toHaveBeenCalledWith(customer.id)
    expect(customerStore.fetchCustomers).toHaveBeenCalled()
  })

  it('应该正确处理选择变化', () => {
    const selection = [mockCustomers[0]]
    wrapper.vm.handleSelectionChange(selection)
    expect(wrapper.vm.selectedCustomers).toEqual(selection)
  })
})
