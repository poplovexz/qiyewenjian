/**
 * 客户详情组件测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ElMessage } from 'element-plus'
import CustomerDetail from '@/views/customer/CustomerDetail.vue'
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

const mockRoute = {
  params: { id: 'test-customer-id' }
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  useRoute: () => mockRoute
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

describe('CustomerDetail', () => {
  let wrapper: ReturnType<typeof mount>
  let customerStore: ReturnType<typeof useCustomerStore>

  const mockCustomer = {
    id: 'test-customer-id',
    gongsi_mingcheng: '测试科技有限公司',
    tongyi_shehui_xinyong_daima: '91110000123456789X',
    chengli_riqi: '2020-01-01T00:00:00',
    zhuce_dizhi: '北京市朝阳区测试路123号',
    faren_xingming: '张三',
    faren_shenfenzheng: '110101199001011234',
    faren_lianxi: '13800138000',
    lianxi_dianhua: '010-12345678',
    lianxi_youxiang: 'test@example.com',
    lianxi_dizhi: '北京市朝阳区联系地址456号',
    kehu_zhuangtai: 'active',
    fuwu_kaishi_riqi: '2024-01-01T00:00:00',
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
    created_by: 'user1'
  }

  const mockServiceRecords = [
    {
      id: '1',
      kehu_id: 'test-customer-id',
      goutong_fangshi: 'phone',
      goutong_neirong: '客户咨询发票问题',
      goutong_shijian: '2024-01-15 10:30:00',
      chuli_zhuangtai: 'completed',
      created_at: '2024-01-15T10:30:00',
      updated_at: '2024-01-15T11:00:00',
      created_by: 'user1'
    },
    {
      id: '2',
      kehu_id: 'test-customer-id',
      goutong_fangshi: 'email',
      goutong_neirong: '月度财务报表咨询',
      goutong_shijian: '2024-01-20 14:00:00',
      chuli_zhuangtai: 'pending',
      created_at: '2024-01-20T14:00:00',
      updated_at: '2024-01-20T14:00:00',
      created_by: 'user1'
    }
  ]

  beforeEach(() => {
    setActivePinia(createPinia())
    customerStore = useCustomerStore()
    
    // Mock store methods
    customerStore.fetchCustomerDetail = vi.fn().mockResolvedValue(mockCustomer)
    customerStore.fetchServiceRecords = vi.fn().mockResolvedValue({
      total: mockServiceRecords.length,
      items: mockServiceRecords,
      page: 1,
      size: 20
    })
    customerStore.updateCustomerStatus = vi.fn().mockResolvedValue(mockCustomer)
    customerStore.deleteCustomer = vi.fn().mockResolvedValue(true)
    
    // Mock store state
    customerStore.currentCustomer = mockCustomer
    customerStore.serviceRecords = mockServiceRecords
    customerStore.loading = false

    wrapper = mount(CustomerDetail, {
      global: {
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
  })

  it('应该正确渲染客户详情页面', () => {
    expect(wrapper.find('.customer-detail').exists()).toBe(true)
    expect(wrapper.find('.page-header h2').text()).toBe('客户详情')
  })

  it('应该在组件挂载时获取客户详情', () => {
    expect(customerStore.fetchCustomerDetail).toHaveBeenCalledWith('test-customer-id')
  })

  it('应该在组件挂载时获取服务记录', () => {
    expect(customerStore.fetchServiceRecords).toHaveBeenCalledWith({
      kehu_id: 'test-customer-id'
    })
  })

  it('应该正确显示客户基本信息', () => {
    expect(wrapper.text()).toContain('测试科技有限公司')
    expect(wrapper.text()).toContain('91110000123456789X')
    expect(wrapper.text()).toContain('张三')
    expect(wrapper.text()).toContain('13800138000')
  })

  it('应该正确格式化客户状态', () => {
    expect(wrapper.vm.getStatusText('active')).toBe('活跃')
    expect(wrapper.vm.getStatusText('renewing')).toBe('续约中')
    expect(wrapper.vm.getStatusText('terminated')).toBe('已终止')
    
    expect(wrapper.vm.getStatusType('active')).toBe('success')
    expect(wrapper.vm.getStatusType('renewing')).toBe('warning')
    expect(wrapper.vm.getStatusType('terminated')).toBe('danger')
  })

  it('应该正确格式化沟通方式', () => {
    expect(wrapper.vm.getCommunicationText('phone')).toBe('电话')
    expect(wrapper.vm.getCommunicationText('email')).toBe('邮件')
    expect(wrapper.vm.getCommunicationText('online')).toBe('在线聊天')
    expect(wrapper.vm.getCommunicationText('meeting')).toBe('会议')
  })

  it('应该正确格式化处理状态', () => {
    expect(wrapper.vm.getProcessStatusText('pending')).toBe('待处理')
    expect(wrapper.vm.getProcessStatusText('processing')).toBe('处理中')
    expect(wrapper.vm.getProcessStatusText('completed')).toBe('已完成')
    expect(wrapper.vm.getProcessStatusText('cancelled')).toBe('已取消')
    
    expect(wrapper.vm.getProcessStatusType('pending')).toBe('warning')
    expect(wrapper.vm.getProcessStatusType('processing')).toBe('primary')
    expect(wrapper.vm.getProcessStatusType('completed')).toBe('success')
    expect(wrapper.vm.getProcessStatusType('cancelled')).toBe('danger')
  })

  it('应该正确格式化日期', () => {
    const dateString = '2024-01-01T00:00:00'
    const formatted = wrapper.vm.formatDate(dateString)
    expect(formatted).toBe('2024/1/1')
  })

  it('应该正确处理返回操作', () => {
    wrapper.vm.handleBack()
    expect(mockRouter.back).toHaveBeenCalled()
  })

  it('应该正确处理编辑客户', () => {
    wrapper.vm.handleEdit()
    expect(wrapper.vm.formVisible).toBe(true)
    expect(wrapper.vm.formMode).toBe('edit')
  })

  it('应该正确处理状态管理', () => {
    wrapper.vm.handleStatusManage()
    expect(wrapper.vm.statusDialogVisible).toBe(true)
  })

  it('应该正确处理客户删除', async () => {
    // Mock ElMessageBox.confirm
    const { ElMessageBox } = await import('element-plus')
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm')
    
    await wrapper.vm.handleDelete()
    
    expect(customerStore.deleteCustomer).toHaveBeenCalledWith('test-customer-id')
    expect(mockRouter.push).toHaveBeenCalledWith('/customers')
  })

  it('应该正确处理表单成功回调', async () => {
    await wrapper.vm.handleFormSuccess()
    expect(wrapper.vm.formVisible).toBe(false)
    expect(customerStore.fetchCustomerDetail).toHaveBeenCalledWith('test-customer-id')
  })

  it('应该正确处理状态变更成功回调', async () => {
    await wrapper.vm.handleStatusSuccess()
    expect(wrapper.vm.statusDialogVisible).toBe(false)
    expect(customerStore.fetchCustomerDetail).toHaveBeenCalledWith('test-customer-id')
  })

  it('应该正确处理服务记录分页', async () => {
    await wrapper.vm.handleServiceRecordPageChange(2)
    expect(customerStore.fetchServiceRecords).toHaveBeenCalledWith({
      kehu_id: 'test-customer-id',
      page: 2
    })
  })

  it('应该正确处理新增服务记录', () => {
    wrapper.vm.handleAddServiceRecord()
    expect(wrapper.vm.serviceRecordFormVisible).toBe(true)
    expect(wrapper.vm.serviceRecordFormMode).toBe('create')
    expect(wrapper.vm.currentServiceRecord).toBe(null)
  })

  it('应该正确处理编辑服务记录', () => {
    const record = mockServiceRecords[0]
    wrapper.vm.handleEditServiceRecord(record)
    
    expect(wrapper.vm.currentServiceRecord).toBe(record)
    expect(wrapper.vm.serviceRecordFormMode).toBe('edit')
    expect(wrapper.vm.serviceRecordFormVisible).toBe(true)
  })

  it('应该正确处理服务记录表单成功回调', async () => {
    await wrapper.vm.handleServiceRecordFormSuccess()
    expect(wrapper.vm.serviceRecordFormVisible).toBe(false)
    expect(customerStore.fetchServiceRecords).toHaveBeenCalledWith({
      kehu_id: 'test-customer-id'
    })
  })
})
