import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/modules/auth'
import { tokenManager } from '@/utils/tokenManager'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '工作台'
        }
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/user/UserList.vue'),
        meta: {
          title: '用户管理',
          permissions: ['user:read']
        }
      },
      {
        path: 'roles',
        name: 'RoleList',
        component: () => import('@/views/user/RoleListSimple.vue'),
        meta: {
          title: '角色管理',
          permissions: ['role:read']
        }
      },
      {
        path: 'permissions',
        name: 'PermissionList',
        component: () => import('@/views/user/PermissionList.vue'),
        meta: {
          title: '权限管理',
          permissions: ['permission:read']
        }
      },
      {
        path: 'customers',
        name: 'CustomerList',
        component: () => import('@/views/customer/CustomerList.vue'),
        meta: {
          title: '客户管理',
          permissions: ['customer:read']
        }
      },
      {
        path: 'customers/:id',
        name: 'CustomerDetail',
        component: () => import('@/views/customer/CustomerDetail.vue'),
        meta: {
          title: '客户详情',
          permissions: ['customer:read']
        }
      },
      {
        path: 'customer-services',
        name: 'ServiceRecordList',
        component: () => import('@/views/customer/ServiceRecordList.vue'),
        meta: {
          title: '服务记录',
          permissions: ['service_record:read']
        }
      },
      // 产品管理路由
      {
        path: 'product-management',
        name: 'ProductManagement',
        component: () => import('@/views/product/ProductManagement.vue'),
        meta: {
          title: '产品管理',
          permissions: ['product_category:read', 'product:read']
        }
      },
      {
        path: 'leads',
        name: 'XiansuoList',
        component: () => import('@/views/xiansuo/XiansuoList.vue'),
        meta: {
          title: '线索管理',
          permissions: ['xiansuo:read']
        }
      },
      {
        path: 'lead-sources',
        name: 'XiansuoLaiyuanList',
        component: () => import('@/views/xiansuo/XiansuoLaiyuanList.vue'),
        meta: {
          title: '线索来源管理',
          permissions: ['xiansuo:source_read']
        }
      },
      {
        path: 'lead-statuses',
        name: 'XiansuoZhuangtaiList',
        component: () => import('@/views/xiansuo/XiansuoZhuangtaiList.vue'),
        meta: {
          title: '线索状态管理',
          permissions: ['xiansuo:status_read']
        }
      },
      // 代理记账套餐管理
      {
        path: 'bookkeeping-packages',
        name: 'BookkeepingPackages',
        component: () => import('@/views/product/BookkeepingPackages.vue'),
        meta: {
          title: '代理记账套餐管理',
          permissions: ['product:read']
        }
      },
      // 合同列表
      {
        path: 'contracts',
        name: 'ContractList',
        component: () => import('@/views/contract/ContractList.vue'),
        meta: {
          title: '合同列表',
          permissions: ['contract_manage']
        }
      },
      // 合同模板管理
      {
        path: 'contract-templates',
        name: 'ContractTemplateList',
        component: () => import('@/views/contract/ContractTemplateList.vue'),
        meta: {
          title: '合同模板管理',
          permissions: ['contract_template_manage']
        }
      },
      // 合同预览
      {
        path: 'contracts/:id',
        name: 'ContractPreview',
        component: () => import('@/views/contract/ContractPreview.vue'),
        meta: {
          title: '合同预览',
          permissions: ['contract_manage']
        }
      },
      // 合同创建
      {
        path: 'contracts/create',
        name: 'ContractCreate',
        component: () => import('@/views/contract/ContractForm.vue'),
        meta: {
          title: '新建合同',
          permissions: ['contract_manage']
        }
      },
      // 合同编辑
      {
        path: 'contracts/:id/edit',
        name: 'ContractEdit',
        component: () => import('@/views/contract/ContractForm.vue'),
        meta: {
          title: '编辑合同',
          permissions: ['contract_manage']
        }
      },

    ]
  },
  // 财务管理模块
  {
    path: '/finance',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/finance/dashboard',
    meta: {
      title: '财务管理',
      icon: 'Money',
      requiresAuth: true
    },
    children: [
      // 财务管理首页
      {
        path: 'dashboard',
        name: 'FinanceDashboard',
        component: () => import('@/views/finance/FinanceDashboard.vue'),
        meta: {
          title: '财务概览',
          permissions: ['finance_manage']
        }
      },
      // 支付订单管理
      {
        path: 'payment-orders',
        name: 'PaymentOrderList',
        component: () => import('@/views/finance/PaymentOrderList.vue'),
        meta: {
          title: '支付订单',
          permissions: ['finance_manage']
        }
      },
      // 支付流水管理
      {
        path: 'payment-records',
        name: 'PaymentRecordList',
        component: () => import('@/views/finance/PaymentRecordList.vue'),
        meta: {
          title: '支付流水',
          permissions: ['finance_manage']
        }
      },
      // 乙方主体管理
      {
        path: 'contract-parties',
        name: 'ContractPartyList',
        component: () => import('@/views/contract/ContractPartyList.vue'),
        meta: {
          title: '乙方主体管理',
          permissions: ['finance_manage']
        }
      },
      // 乙方主体创建
      {
        path: 'contract-parties/create',
        name: 'ContractPartyCreate',
        component: () => import('@/views/contract/ContractPartyForm.vue'),
        meta: {
          title: '新建乙方主体',
          permissions: ['finance_manage']
        }
      },
      // 乙方主体编辑
      {
        path: 'contract-parties/:id/edit',
        name: 'ContractPartyEdit',
        component: () => import('@/views/contract/ContractPartyForm.vue'),
        meta: {
          title: '编辑乙方主体',
          permissions: ['finance_manage']
        }
      },
      // 支付方式管理
      {
        path: 'payment-methods',
        name: 'PaymentMethodList',
        component: () => import('@/views/contract/PaymentMethodList.vue'),
        meta: {
          title: '支付方式管理',
          permissions: ['finance_manage']
        }
      },
      // 支付方式创建
      {
        path: 'payment-methods/create',
        name: 'PaymentMethodCreate',
        component: () => import('@/views/contract/PaymentMethodForm.vue'),
        meta: {
          title: '新建支付方式',
          permissions: ['finance_manage']
        }
      },
      // 支付方式编辑
      {
        path: 'payment-methods/:id/edit',
        name: 'PaymentMethodEdit',
        component: () => import('@/views/contract/PaymentMethodForm.vue'),
        meta: {
          title: '编辑支付方式',
          permissions: ['finance_manage']
        }
      }
    ]
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: {
      title: '关于',
      requiresAuth: false
    }
  },
  {
    path: '/test/api',
    name: 'ApiTest',
    component: () => import('@/views/test/ApiTest.vue'),
    meta: {
      title: 'API测试',
      requiresAuth: true
    }
  },
  {
    path: '/quote-preview/:id',
    name: 'QuotePreview',
    component: () => import('@/views/xiansuo/QuotePreview.vue'),
    meta: {
      title: '报价预览',
      requiresAuth: false
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面不存在'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 代理记账营运内部系统`
  }

  // 等待认证状态初始化完成
  await tokenManager.waitForAuthInit()

  // 检查是否需要认证
  if (to.meta?.requiresAuth) {
    const authStore = useAuthStore()

    if (!authStore.isAuthenticated) {
      // 未登录，跳转到登录页
      ElMessage.warning('请先登录')
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // 已登录但用户信息为空，尝试获取用户信息
    if (!authStore.userInfo) {
      try {
        const success = await authStore.getCurrentUser()
        if (!success) {
          console.warn('获取用户信息失败，但继续导航')
          // 暂时不强制退出，允许继续导航
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 暂时不强制退出，允许继续导航
      }
    }

    // 检查页面权限
    if (to.meta?.permissions && Array.isArray(to.meta.permissions)) {
      const hasPermission = to.meta.permissions.some((permission: string) =>
        authStore.hasPermission(permission)
      )

      if (!hasPermission) {
        ElMessage.error('您没有访问该页面的权限')
        next('/dashboard')
        return
      }
    }
  } else if (to.path === '/login') {
    const authStore = useAuthStore()
    if (authStore.isAuthenticated) {
      // 已登录用户访问登录页，跳转到首页
      next('/')
      return
    }
  }

  next()
})

export default router
