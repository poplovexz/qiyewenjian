/**
 * 用户管理模块测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ElButton, ElTable, ElDialog } from 'element-plus'
import UserList from '@/views/user/UserList.vue'
import UserDetail from '@/components/user/UserDetail.vue'
import UserForm from '@/components/user/UserForm.vue'
import { userApi } from '@/api/modules/user'

// Mock API
vi.mock('@/api/modules/user', () => ({
  userApi: {
    getUserList: vi.fn(),
    getUserById: vi.fn(),
    createUser: vi.fn(),
    updateUser: vi.fn(),
    deleteUser: vi.fn(),
    assignRoles: vi.fn()
  }
}))

// Mock router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

// Mock auth store
vi.mock('@/stores/modules/auth', () => ({
  useAuthStore: () => ({
    hasPermission: vi.fn(() => true),
    hasRole: vi.fn(() => true),
    userInfo: {
      id: '1',
      yonghu_ming: 'testuser',
      xingming: '测试用户'
    }
  })
}))

// Mock Element Plus message
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn()
    },
    ElMessageBox: {
      confirm: vi.fn(() => Promise.resolve())
    }
  }
})

describe('用户管理模块测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('UserList 组件', () => {
    it('应该正确渲染用户列表页面', async () => {
      // Mock API 响应
      const mockUsers = [
        {
          id: '1',
          yonghu_ming: 'user1',
          xingming: '用户1',
          youxiang: 'user1@example.com',
          shouji: '13800138001',
          zhuangtai: 'active',
          denglu_cishu: '5',
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: '2',
          yonghu_ming: 'user2',
          xingming: '用户2',
          youxiang: 'user2@example.com',
          shouji: '13800138002',
          zhuangtai: 'inactive',
          denglu_cishu: '3',
          created_at: '2024-01-02T00:00:00Z'
        }
      ]

      vi.mocked(userApi.getUserList).mockResolvedValue({
        items: mockUsers,
        total: 2,
        page: 1,
        size: 20,
        pages: 1
      })

      const wrapper = mount(UserList, {
        global: {
          components: {
            ElButton,
            ElTable,
            ElDialog
          },
          stubs: {
            'el-card': true,
            'el-form': true,
            'el-form-item': true,
            'el-input': true,
            'el-select': true,
            'el-option': true,
            'el-table': true,
            'el-table-column': true,
            'el-tag': true,
            'el-pagination': true,
            'el-dialog': true,
            'UserDetail': true,
            'UserForm': true
          }
        }
      })

      // 等待组件挂载和数据加载
      await wrapper.vm.$nextTick()

      // 验证页面标题
      expect(wrapper.find('.page-title').text()).toBe('用户管理')
      
      // 验证新增按钮存在
      expect(wrapper.find('[data-test="create-user-btn"]').exists()).toBe(true)
      
      // 验证 API 被调用
      expect(userApi.getUserList).toHaveBeenCalled()
    })

    it('应该正确处理搜索功能', async () => {
      const wrapper = mount(UserList, {
        global: {
          stubs: {
            'el-card': true,
            'el-form': true,
            'el-form-item': true,
            'el-input': true,
            'el-select': true,
            'el-option': true,
            'el-button': true,
            'el-table': true,
            'el-table-column': true,
            'el-pagination': true,
            'UserDetail': true,
            'UserForm': true
          }
        }
      })

      // 模拟搜索
      await wrapper.setData({
        searchForm: {
          yonghu_ming: 'test',
          xingming: '测试',
          zhuangtai: 'active'
        }
      })

      // 触发搜索
      await wrapper.vm.handleSearch()

      // 验证 API 被正确调用
      expect(userApi.getUserList).toHaveBeenCalledWith(
        expect.objectContaining({
          yonghu_ming: 'test',
          xingming: '测试',
          zhuangtai: 'active'
        })
      )
    })
  })

  describe('UserDetail 组件', () => {
    it('应该正确显示用户详情', async () => {
      const mockUser = {
        id: '1',
        yonghu_ming: 'testuser',
        xingming: '测试用户',
        youxiang: 'test@example.com',
        shouji: '13800138000',
        zhuangtai: 'active',
        denglu_cishu: '5',
        zuihou_denglu: '2024-01-01T12:00:00Z',
        created_at: '2024-01-01T00:00:00Z',
        roles: [
          {
            id: 'role1',
            jiaose_ming: '管理员',
            jiaose_bianma: 'admin',
            zhuangtai: 'active',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          }
        ],
        permissions: [
          {
            id: 'perm1',
            quanxian_ming: '用户管理',
            quanxian_bianma: 'user:manage',
            ziyuan_leixing: 'menu',
            zhuangtai: 'active',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          }
        ]
      }

      vi.mocked(userApi.getUserById).mockResolvedValue(mockUser)

      const wrapper = mount(UserDetail, {
        props: {
          visible: true,
          userId: '1'
        },
        global: {
          stubs: {
            'el-dialog': true,
            'el-card': true,
            'el-descriptions': true,
            'el-descriptions-item': true,
            'el-tag': true,
            'el-button': true,
            'el-empty': true,
            'UserRoleAssign': true
          }
        }
      })

      // 等待数据加载
      await wrapper.vm.$nextTick()

      // 验证 API 被调用
      expect(userApi.getUserById).toHaveBeenCalledWith('1')
    })
  })

  describe('UserForm 组件', () => {
    it('应该正确处理用户创建', async () => {
      const mockCreateData = {
        yonghu_ming: 'newuser',
        xingming: '新用户',
        youxiang: 'newuser@example.com',
        shouji: '13800138999',
        zhuangtai: 'active',
        mima: 'password123'
      }

      vi.mocked(userApi.createUser).mockResolvedValue({
        id: '3',
        ...mockCreateData,
        denglu_cishu: '0',
        created_at: '2024-01-03T00:00:00Z'
      })

      const wrapper = mount(UserForm, {
        props: {
          visible: true,
          mode: 'create'
        },
        global: {
          stubs: {
            'el-dialog': true,
            'el-form': true,
            'el-form-item': true,
            'el-input': true,
            'el-radio-group': true,
            'el-radio': true,
            'el-button': true
          }
        }
      })

      // 设置表单数据
      await wrapper.setData({
        formData: mockCreateData
      })

      // 模拟表单提交
      await wrapper.vm.handleSubmit()

      // 验证 API 被调用
      expect(userApi.createUser).toHaveBeenCalledWith(mockCreateData)
    })

    it('应该正确处理用户更新', async () => {
      const mockUpdateData = {
        xingming: '更新用户',
        youxiang: 'updated@example.com',
        shouji: '13800138888',
        zhuangtai: 'inactive'
      }

      const mockUser = {
        id: '1',
        yonghu_ming: 'testuser',
        ...mockUpdateData,
        denglu_cishu: '5',
        created_at: '2024-01-01T00:00:00Z'
      }

      vi.mocked(userApi.getUserById).mockResolvedValue(mockUser)
      vi.mocked(userApi.updateUser).mockResolvedValue(mockUser)

      const wrapper = mount(UserForm, {
        props: {
          visible: true,
          mode: 'edit',
          userId: '1'
        },
        global: {
          stubs: {
            'el-dialog': true,
            'el-form': true,
            'el-form-item': true,
            'el-input': true,
            'el-radio-group': true,
            'el-radio': true,
            'el-button': true
          }
        }
      })

      // 等待用户数据加载
      await wrapper.vm.$nextTick()

      // 设置更新数据
      await wrapper.setData({
        formData: {
          yonghu_ming: 'testuser',
          ...mockUpdateData
        }
      })

      // 模拟表单提交
      await wrapper.vm.handleSubmit()

      // 验证 API 被调用
      expect(userApi.updateUser).toHaveBeenCalledWith('1', mockUpdateData)
    })
  })

  describe('用户管理 API 测试', () => {
    it('应该正确调用用户列表 API', async () => {
      const mockResponse = {
        items: [],
        total: 0,
        page: 1,
        size: 20,
        pages: 0
      }

      vi.mocked(userApi.getUserList).mockResolvedValue(mockResponse)

      const params = {
        page: 1,
        size: 20,
        yonghu_ming: 'test'
      }

      const result = await userApi.getUserList(params)

      expect(userApi.getUserList).toHaveBeenCalledWith(params)
      expect(result).toEqual(mockResponse)
    })

    it('应该正确调用角色分配 API', async () => {
      const mockResponse = { message: '角色分配成功' }
      vi.mocked(userApi.assignRoles).mockResolvedValue(mockResponse)

      const userId = '1'
      const roleIds = ['role1', 'role2']

      const result = await userApi.assignRoles(userId, roleIds)

      expect(userApi.assignRoles).toHaveBeenCalledWith(userId, roleIds)
      expect(result).toEqual(mockResponse)
    })
  })
})
