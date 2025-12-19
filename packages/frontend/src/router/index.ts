import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { tokenManager } from '@/utils/tokenManager'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
    },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '工作台',
        },
      },
      // 功能演示页面
      {
        path: 'feature-demo',
        name: 'FeatureDemo',
        component: () => import('@/views/FeatureDemo.vue'),
        meta: {
          title: '功能演示',
        },
      },
      // 组件测试页面
      {
        path: 'test-components',
        name: 'TestComponents',
        component: () => import('@/views/TestComponents.vue'),
        meta: {
          title: '组件测试',
        },
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/user/UserList.vue'),
        meta: {
          title: '用户管理',
          permissions: ['user:read'],
        },
      },
      {
        path: 'roles',
        name: 'RoleList',
        component: () => import('@/views/user/RoleListSimple.vue'),
        meta: {
          title: '角色管理',
          permissions: ['role:read'],
        },
      },
      {
        path: 'permissions',
        name: 'PermissionList',
        component: () => import('@/views/user/PermissionList.vue'),
        meta: {
          title: '权限管理',
          permissions: ['permission:read'],
        },
      },
      {
        path: 'permission-auto-import',
        name: 'PermissionAutoImport',
        component: () => import('@/views/user/PermissionAutoImport.vue'),
        meta: {
          title: '权限自动导入',
          permissions: ['permission:create'],
        },
      },
      {
        path: 'customers',
        name: 'CustomerList',
        component: () => import('@/views/customer/CustomerList.vue'),
        meta: {
          title: '客户管理',
          permissions: ['customer:read'],
        },
      },
      {
        path: 'customers/:id',
        name: 'CustomerDetail',
        component: () => import('@/views/customer/CustomerDetail.vue'),
        meta: {
          title: '客户详情',
          permissions: ['customer:read'],
        },
      },
      {
        path: 'customer-services',
        name: 'ServiceRecordList',
        component: () => import('@/views/customer/ServiceRecordList.vue'),
        meta: {
          title: '服务记录',
          permissions: ['service_record:read'],
        },
      },
      // 产品管理路由
      {
        path: 'product-management',
        name: 'ProductManagement',
        component: () => import('@/views/product/ProductManagement.vue'),
        meta: {
          title: '产品管理',
          permissions: ['product_category:read', 'product:read'],
        },
      },
      {
        path: 'leads',
        name: 'XiansuoList',
        component: () => import('@/views/xiansuo/XiansuoList.vue'),
        meta: {
          title: '线索管理',
          permissions: ['xiansuo:read'],
        },
      },
      {
        path: 'lead-sources',
        name: 'XiansuoLaiyuanList',
        component: () => import('@/views/xiansuo/XiansuoLaiyuanList.vue'),
        meta: {
          title: '线索来源管理',
          permissions: ['xiansuo:source_read'],
        },
      },
      {
        path: 'lead-statuses',
        name: 'XiansuoZhuangtaiList',
        component: () => import('@/views/xiansuo/XiansuoZhuangtaiList.vue'),
        meta: {
          title: '线索状态管理',
          permissions: ['xiansuo:status_read'],
        },
      },
      // 代理记账套餐管理
      {
        path: 'bookkeeping-packages',
        name: 'BookkeepingPackages',
        component: () => import('@/views/product/BookkeepingPackages.vue'),
        meta: {
          title: '代理记账套餐管理',
          permissions: ['product:read'],
        },
      },
      // 合同列表
      {
        path: 'contracts',
        name: 'ContractList',
        component: () => import('@/views/contract/ContractList.vue'),
        meta: {
          title: '合同列表',
          permissions: ['contract_manage'],
        },
      },
      // 合同模板管理重定向（兼容单数形式）
      {
        path: 'contract-template',
        redirect: 'contract-templates',
      },
      // 合同模板管理
      {
        path: 'contract-templates',
        name: 'ContractTemplateList',
        component: () => import('@/views/contract/ContractTemplateList.vue'),
        meta: {
          title: '合同模板管理',
          permissions: ['contract_template_manage'],
        },
      },
      // 合同预览
      {
        path: 'contracts/:id',
        name: 'ContractPreview',
        component: () => import('@/views/contract/ContractPreview.vue'),
        meta: {
          title: '合同预览',
          permissions: ['contract_manage'],
        },
      },
      // 合同创建
      {
        path: 'contracts/create',
        name: 'ContractCreate',
        component: () => import('@/views/contract/ContractForm.vue'),
        meta: {
          title: '新建合同',
          permissions: ['contract_manage'],
        },
      },
      // 合同生成
      {
        path: 'contracts/generate',
        name: 'ContractGenerate',
        component: () => import('@/views/contract/ContractGenerate.vue'),
        meta: {
          title: '合同生成',
          permissions: ['contract_manage'],
        },
      },
      // 合同编辑
      {
        path: 'contracts/:id/edit',
        name: 'ContractEdit',
        component: () => import('@/views/contract/ContractForm.vue'),
        meta: {
          title: '编辑合同',
          permissions: ['contract_manage'],
        },
      },
      // 乙方主体管理（合同模块快捷入口）
      {
        path: 'contract-parties',
        name: 'ContractPartyListRoot',
        component: () => import('@/views/contract/ContractPartyList.vue'),
        meta: {
          title: '乙方主体管理',
          permissions: ['contract_manage'],
        },
      },
      {
        path: 'contract-parties/create',
        name: 'ContractPartyCreateRoot',
        component: () => import('@/views/contract/ContractPartyForm.vue'),
        meta: {
          title: '新建乙方主体',
          permissions: ['contract_manage'],
        },
      },
      {
        path: 'contract-parties/:id/edit',
        name: 'ContractPartyEditRoot',
        component: () => import('@/views/contract/ContractPartyForm.vue'),
        meta: {
          title: '编辑乙方主体',
          permissions: ['contract_manage'],
        },
      },
      // 支付方式管理（合同模块快捷入口）
      {
        path: 'payment-methods',
        name: 'PaymentMethodListRoot',
        component: () => import('@/views/contract/PaymentMethodList.vue'),
        meta: {
          title: '支付方式管理',
          permissions: ['contract_manage'],
        },
      },
      {
        path: 'payment-methods/create',
        name: 'PaymentMethodCreateRoot',
        component: () => import('@/views/contract/PaymentMethodForm.vue'),
        meta: {
          title: '新建支付方式',
          permissions: ['contract_manage'],
        },
      },
      {
        path: 'payment-methods/:id/edit',
        name: 'PaymentMethodEditRoot',
        component: () => import('@/views/contract/PaymentMethodForm.vue'),
        meta: {
          title: '编辑支付方式',
          permissions: ['contract_manage'],
        },
      },
      // 审核任务列表
      {
        path: 'audit/tasks',
        name: 'AuditTaskList',
        component: () => import('@/views/audit/AuditTaskList.vue'),
        meta: {
          title: '审核任务',
          permissions: ['audit:read'], // 修复：与接口权限保持一致
        },
      },
      // 审核流程配置
      {
        path: 'audit/workflow-config',
        name: 'AuditWorkflowConfig',
        component: () => import('@/views/audit/AuditWorkflowConfig.vue'),
        meta: {
          title: '审核流程配置',
          permissions: ['audit_config'],
        },
      },

      // 审核规则配置
      {
        path: 'audit/rule-config',
        name: 'AuditRuleConfig',
        component: () => import('@/views/audit/AuditRuleConfig.vue'),
        meta: {
          title: '审核规则配置',
          permissions: ['audit_config'],
        },
      },
      // 支付审核
      {
        path: 'audit/payment-audit',
        name: 'PaymentAudit',
        component: () => import('@/views/audit/PaymentAudit.vue'),
        meta: {
          title: '支付审核',
          permissions: ['audit_record:read'],
        },
      },
      // 审批权责矩阵
      {
        path: 'audit/approval-matrix',
        name: 'ApprovalMatrix',
        component: () => import('@/views/audit/ApprovalMatrix.vue'),
        meta: {
          title: '审批权责矩阵',
          permissions: ['audit_config'],
        },
      },
    ],
  },
  // 财务管理模块
  {
    path: '/finance',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/finance/dashboard',
    meta: {
      title: '财务管理',
      icon: 'Money',
      requiresAuth: true,
    },
    children: [
      // 财务管理首页
      {
        path: 'dashboard',
        name: 'FinanceDashboard',
        component: () => import('@/views/finance/FinanceDashboard.vue'),
        meta: {
          title: '财务概览',
          permissions: ['finance_manage'],
        },
      },
      // 支付订单管理
      {
        path: 'payment-orders',
        name: 'PaymentOrderList',
        component: () => import('@/views/finance/PaymentOrderList.vue'),
        meta: {
          title: '支付订单',
          permissions: ['finance_manage'],
        },
      },
      // 支付流水管理
      {
        path: 'payment-records',
        name: 'PaymentRecordList',
        component: () => import('@/views/finance/PaymentRecordList.vue'),
        meta: {
          title: '支付流水',
          permissions: ['finance_manage'],
        },
      },
      // 支付配置管理
      {
        path: 'payment-configs',
        name: 'PaymentConfigManage',
        component: () => import('@/views/payment/PaymentConfigManage.vue'),
        meta: {
          title: '支付配置管理',
          permissions: ['payment_config:read'],
        },
      },
      // 退款管理
      {
        path: 'refunds',
        name: 'RefundManage',
        component: () => import('@/views/payment/RefundManage.vue'),
        meta: {
          title: '退款管理',
          permissions: ['zhifu:tuikuan:list'],
        },
      },
      // 银行汇款管理
      {
        path: 'bank-transfers',
        name: 'BankTransferManage',
        component: () => import('@/views/payment/BankTransferManage.vue'),
        meta: {
          title: '银行汇款管理',
          permissions: ['finance_manage'],
        },
      },
      // 乙方主体管理
      {
        path: 'contract-parties',
        name: 'ContractPartyList',
        component: () => import('@/views/contract/ContractPartyList.vue'),
        meta: {
          title: '乙方主体管理',
          permissions: ['finance_manage'],
        },
      },
      // 乙方主体创建
      {
        path: 'contract-parties/create',
        name: 'ContractPartyCreate',
        component: () => import('@/views/contract/ContractPartyForm.vue'),
        meta: {
          title: '新建乙方主体',
          permissions: ['finance_manage'],
        },
      },
      // 乙方主体编辑
      {
        path: 'contract-parties/:id/edit',
        name: 'ContractPartyEdit',
        component: () => import('@/views/contract/ContractPartyForm.vue'),
        meta: {
          title: '编辑乙方主体',
          permissions: ['finance_manage'],
        },
      },
      // 支付方式管理
      {
        path: 'payment-methods',
        name: 'PaymentMethodList',
        component: () => import('@/views/contract/PaymentMethodList.vue'),
        meta: {
          title: '支付方式管理',
          permissions: ['finance_manage'],
        },
      },
      // 支付方式创建
      {
        path: 'payment-methods/create',
        name: 'PaymentMethodCreate',
        component: () => import('@/views/contract/PaymentMethodForm.vue'),
        meta: {
          title: '新建支付方式',
          permissions: ['finance_manage'],
        },
      },
      // 支付方式编辑
      {
        path: 'payment-methods/:id/edit',
        name: 'PaymentMethodEdit',
        component: () => import('@/views/contract/PaymentMethodForm.vue'),
        meta: {
          title: '编辑支付方式',
          permissions: ['finance_manage'],
        },
      },
      // 开票申请管理
      {
        path: 'invoices',
        name: 'InvoiceList',
        component: () => import('@/views/finance/InvoiceList.vue'),
        meta: {
          title: '开票申请',
          permissions: ['invoice:read'],
        },
      },
      // 开票申请创建
      {
        path: 'invoices/create',
        name: 'InvoiceCreate',
        component: () => import('@/views/finance/InvoiceForm.vue'),
        meta: {
          title: '新建开票申请',
          permissions: ['invoice:create'],
        },
      },
      // 开票申请编辑
      {
        path: 'invoices/:id/edit',
        name: 'InvoiceEdit',
        component: () => import('@/views/finance/InvoiceForm.vue'),
        meta: {
          title: '编辑开票申请',
          permissions: ['invoice:update'],
        },
      },
      // 成本记录管理
      {
        path: 'costs',
        name: 'CostList',
        component: () => import('@/views/finance/CostList.vue'),
        meta: {
          title: '成本记录',
          permissions: ['cost:read'],
        },
      },
      // 成本记录创建
      {
        path: 'costs/create',
        name: 'CostCreate',
        component: () => import('@/views/finance/CostForm.vue'),
        meta: {
          title: '新建成本记录',
          permissions: ['cost:create'],
        },
      },
      // 成本记录编辑
      {
        path: 'costs/:id/edit',
        name: 'CostEdit',
        component: () => import('@/views/finance/CostForm.vue'),
        meta: {
          title: '编辑成本记录',
          permissions: ['cost:update'],
        },
      },
    ],
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: {
      title: '关于',
      requiresAuth: false,
    },
  },
  {
    path: '/test/api',
    name: 'ApiTest',
    component: () => import('@/views/test/ApiTest.vue'),
    meta: {
      title: 'API测试',
      requiresAuth: true,
    },
  },

  // 服务工单管理
  {
    path: '/service-orders',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/service-orders',
    meta: {
      title: '服务工单',
      icon: 'Document',
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        name: 'ServiceOrderList',
        component: () => import('@/views/service-orders/ServiceOrderList.vue'),
        meta: {
          title: '服务工单列表',
          permissions: ['service_order:read'],
        },
      },
      {
        path: ':id',
        name: 'ServiceOrderDetail',
        component: () => import('@/views/service-orders/ServiceOrderDetail.vue'),
        meta: {
          title: '服务工单详情',
          permissions: ['service_order:read'],
        },
      },
      {
        path: ':id/edit',
        name: 'ServiceOrderEdit',
        component: () => import('@/views/service-orders/components/ServiceOrderForm.vue'),
        meta: {
          title: '编辑服务工单',
          permissions: ['service_order:write'],
        },
      },
    ],
  },

  // 合规管理
  {
    path: '/compliance',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/compliance/calendar',
    meta: {
      title: '合规管理',
      icon: 'Calendar',
      requiresAuth: true,
    },
    children: [
      {
        path: 'calendar',
        name: 'ComplianceCalendar',
        component: () => import('@/views/compliance/ComplianceCalendar.vue'),
        meta: {
          title: '合规日历',
          permissions: ['compliance:read'],
        },
      },
      {
        path: 'templates',
        name: 'ComplianceTemplates',
        component: () => import('@/views/compliance/ComplianceTemplates.vue'),
        meta: {
          title: '合规模板',
          permissions: ['compliance:manage'],
        },
      },
    ],
  },

  {
    path: '/quote-preview/:id',
    name: 'QuotePreview',
    component: () => import('@/views/xiansuo/QuotePreview.vue'),
    meta: {
      title: '报价预览',
      requiresAuth: false,
    },
  },

  // 公共页面（无需登录）
  {
    path: '/public',
    name: 'Public',
    children: [
      // 合同确认页面
      {
        path: 'contract-confirm/:token',
        name: 'ContractConfirm',
        component: () => import('@/views/public/ContractConfirm.vue'),
        meta: {
          title: '合同确认',
          requiresAuth: false,
        },
      },
      // 合同支付页面
      {
        path: 'contract-payment/:contractId',
        name: 'ContractPayment',
        component: () => import('@/views/public/ContractPayment.vue'),
        meta: {
          title: '合同支付',
          requiresAuth: false,
        },
      },
    ],
  },
  // 客户签署页面（无需登录）
  {
    path: '/contract-sign/:token',
    name: 'CustomerSign',
    component: () => import('@/views/contract/CustomerSign.vue'),
    meta: {
      title: '合同签署',
      requiresAuth: false,
    },
  },
  // 办公管理模块
  {
    path: '/office',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/office/reimbursement',
    meta: {
      title: '办公管理',
      icon: 'OfficeBuilding',
      requiresAuth: true,
    },
    children: [
      // 申请报销
      {
        path: 'reimbursement',
        name: 'ReimbursementList',
        component: () => import('@/views/office/ReimbursementList.vue'),
        meta: {
          title: '申请报销',
          permissions: ['office:baoxiao:read'],
        },
      },
      {
        path: 'reimbursement/create',
        name: 'ReimbursementCreate',
        component: () => import('@/views/office/ReimbursementForm.vue'),
        meta: {
          title: '新建报销申请',
          permissions: ['office:baoxiao:create'],
        },
      },
      {
        path: 'reimbursement/edit/:id',
        name: 'ReimbursementEdit',
        component: () => import('@/views/office/ReimbursementForm.vue'),
        meta: {
          title: '编辑报销申请',
          permissions: ['office:baoxiao:update'],
        },
      },
      {
        path: 'reimbursement/detail/:id',
        name: 'ReimbursementDetail',
        component: () => import('@/views/office/ReimbursementDetail.vue'),
        meta: {
          title: '报销申请详情',
          permissions: ['office:baoxiao:read'],
        },
      },
      // 请假
      {
        path: 'leave',
        name: 'LeaveList',
        component: () => import('@/views/office/LeaveList.vue'),
        meta: {
          title: '请假',
          permissions: ['office:qingjia:read'],
        },
      },
      {
        path: 'leave/create',
        name: 'LeaveCreate',
        component: () => import('@/views/office/LeaveForm.vue'),
        meta: {
          title: '新建请假申请',
          permissions: ['office:qingjia:create'],
        },
      },
      {
        path: 'leave/edit/:id',
        name: 'LeaveEdit',
        component: () => import('@/views/office/LeaveForm.vue'),
        meta: {
          title: '编辑请假申请',
          permissions: ['office:qingjia:update'],
        },
      },
      {
        path: 'leave/detail/:id',
        name: 'LeaveDetail',
        component: () => import('@/views/office/LeaveDetail.vue'),
        meta: {
          title: '请假申请详情',
          permissions: ['office:qingjia:read'],
        },
      },
      // 申请对外付款
      {
        path: 'payment',
        name: 'PaymentApplicationList',
        component: () => import('@/views/office/PaymentApplicationList.vue'),
        meta: {
          title: '申请对外付款',
          permissions: ['office:fukuan:read'],
        },
      },
      {
        path: 'payment/create',
        name: 'PaymentApplicationCreate',
        component: () => import('@/views/office/PaymentApplicationForm.vue'),
        meta: {
          title: '新建对外付款申请',
          permissions: ['office:fukuan:create'],
        },
      },
      {
        path: 'payment/edit/:id',
        name: 'PaymentApplicationEdit',
        component: () => import('@/views/office/PaymentApplicationForm.vue'),
        meta: {
          title: '编辑对外付款申请',
          permissions: ['office:fukuan:update'],
        },
      },
      {
        path: 'payment/detail/:id',
        name: 'PaymentApplicationDetail',
        component: () => import('@/views/office/PaymentApplicationDetail.vue'),
        meta: {
          title: '对外付款申请详情',
          permissions: ['office:fukuan:read'],
        },
      },
      // 申请采购
      {
        path: 'procurement',
        name: 'ProcurementList',
        component: () => import('@/views/office/ProcurementList.vue'),
        meta: {
          title: '申请采购',
          permissions: ['office:caigou:read'],
        },
      },
      {
        path: 'procurement/create',
        name: 'ProcurementCreate',
        component: () => import('@/views/office/ProcurementForm.vue'),
        meta: {
          title: '新建采购申请',
          permissions: ['office:caigou:create'],
        },
      },
      {
        path: 'procurement/edit/:id',
        name: 'ProcurementEdit',
        component: () => import('@/views/office/ProcurementForm.vue'),
        meta: {
          title: '编辑采购申请',
          permissions: ['office:caigou:update'],
        },
      },
      {
        path: 'procurement/detail/:id',
        name: 'ProcurementDetail',
        component: () => import('@/views/office/ProcurementDetail.vue'),
        meta: {
          title: '采购申请详情',
          permissions: ['office:caigou:read'],
        },
      },
      // 交接单
      {
        path: 'handover',
        name: 'HandoverList',
        component: () => import('@/views/office/HandoverList.vue'),
        meta: {
          title: '交接单',
          permissions: ['office:jiaojie:read'],
        },
      },
      {
        path: 'handover/create',
        name: 'HandoverCreate',
        component: () => import('@/views/office/HandoverForm.vue'),
        meta: {
          title: '新建工作交接单',
          permissions: ['office:jiaojie:create'],
        },
      },
      {
        path: 'handover/edit/:id',
        name: 'HandoverEdit',
        component: () => import('@/views/office/HandoverForm.vue'),
        meta: {
          title: '编辑工作交接单',
          permissions: ['office:jiaojie:update'],
        },
      },
      {
        path: 'handover/detail/:id',
        name: 'HandoverDetail',
        component: () => import('@/views/office/HandoverDetail.vue'),
        meta: {
          title: '工作交接单详情',
          permissions: ['office:jiaojie:read'],
        },
      },
    ],
  },
  // 设置
  {
    path: '/settings',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/settings/profile',
    meta: {
      title: '设置',
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        name: 'Settings',
        component: () => import('@/views/settings/SettingsLayout.vue'),
        redirect: '/settings/profile',
        children: [
          {
            path: 'profile',
            name: 'ProfileSettings',
            component: () => import('@/views/settings/ProfileSettings.vue'),
            meta: {
              title: '个人信息',
            },
          },
          {
            path: 'password',
            name: 'PasswordSettings',
            component: () => import('@/views/settings/PasswordSettings.vue'),
            meta: {
              title: '修改密码',
            },
          },
          {
            path: 'notifications',
            name: 'NotificationSettings',
            component: () => import('@/views/settings/NotificationSettings.vue'),
            meta: {
              title: '通知偏好',
            },
          },
          // 系统设置
          {
            path: 'system/basic',
            name: 'SystemBasicInfo',
            component: () => import('@/views/settings/system/BasicInfo.vue'),
            meta: {
              title: '系统基础信息',
            },
          },
          {
            path: 'system/security',
            name: 'SystemSecurityConfig',
            component: () => import('@/views/settings/system/SecurityConfig.vue'),
            meta: {
              title: '安全配置',
            },
          },
          {
            path: 'system/cache',
            name: 'SystemCacheConfig',
            component: () => import('@/views/settings/system/CacheConfig.vue'),
            meta: {
              title: '缓存配置',
            },
          },
          {
            path: 'system/business',
            name: 'SystemBusinessParams',
            component: () => import('@/views/settings/system/BusinessParams.vue'),
            meta: {
              title: '业务参数',
            },
          },
          // 基础数据管理
          {
            path: 'data',
            name: 'DataManagement',
            component: () => import('@/views/settings/data/DataManagement.vue'),
            meta: {
              title: '基础数据管理',
            },
          },
          // 财务设置
          {
            path: 'finance',
            name: 'FinanceSettings',
            component: () => import('@/views/settings/data/FinanceSettings.vue'),
            meta: {
              title: '财务设置',
            },
          },
          // 部署管理
          {
            path: 'deploy',
            name: 'DeployManagement',
            component: () => import('@/views/settings/deploy/DeployManagement.vue'),
            meta: {
              title: '部署管理',
            },
          },
        ],
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面不存在',
    },
  },
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
    const { useAuthStore } = await import('@/stores/modules/auth')
    const authStore = useAuthStore()

    if (!authStore.isAuthenticated) {
      // 未登录，跳转到登录页
      ElMessage.warning('请先登录')
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      })
      return
    }

    // 已登录但用户信息为空，尝试获取用户信息
    if (!authStore.userInfo) {
      try {
        const success = await authStore.getCurrentUser()
        if (!success) {
          // 暂时不强制退出，允许继续导航
        }
      } catch (error) {
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
    const { useAuthStore } = await import('@/stores/modules/auth')
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
