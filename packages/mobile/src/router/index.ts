import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页', requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'TaskList',
    component: () => import('@/views/TaskList.vue'),
    meta: { title: '我的任务', requiresAuth: true }
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: () => import('@/views/TaskDetail.vue'),
    meta: { title: '任务详情', requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'OrderList',
    component: () => import('@/views/OrderList.vue'),
    meta: { title: '工单列表', requiresAuth: true }
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: () => import('@/views/OrderDetail.vue'),
    meta: { title: '工单详情', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  // 办公管理 - 请假申请
  {
    path: '/office/leave',
    name: 'LeaveList',
    component: () => import('@/views/office/LeaveList.vue'),
    meta: { title: '请假申请', requiresAuth: true }
  },
  {
    path: '/office/leave/create',
    name: 'LeaveCreate',
    component: () => import('@/views/office/LeaveForm.vue'),
    meta: { title: '新建请假申请', requiresAuth: true }
  },
  {
    path: '/office/leave/edit/:id',
    name: 'LeaveEdit',
    component: () => import('@/views/office/LeaveForm.vue'),
    meta: { title: '编辑请假申请', requiresAuth: true }
  },
  {
    path: '/office/leave/:id',
    name: 'LeaveDetail',
    component: () => import('@/views/office/LeaveDetail.vue'),
    meta: { title: '请假申请详情', requiresAuth: true }
  },
  // 办公管理 - 报销申请
  {
    path: '/office/reimbursement',
    name: 'ReimbursementList',
    component: () => import('@/views/office/ReimbursementList.vue'),
    meta: { title: '报销申请', requiresAuth: true }
  },
  {
    path: '/office/reimbursement/create',
    name: 'ReimbursementCreate',
    component: () => import('@/views/office/ReimbursementForm.vue'),
    meta: { title: '新建报销申请', requiresAuth: true }
  },
  {
    path: '/office/reimbursement/edit/:id',
    name: 'ReimbursementEdit',
    component: () => import('@/views/office/ReimbursementForm.vue'),
    meta: { title: '编辑报销申请', requiresAuth: true }
  },
  {
    path: '/office/reimbursement/:id',
    name: 'ReimbursementDetail',
    component: () => import('@/views/office/ReimbursementDetail.vue'),
    meta: { title: '报销申请详情', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory('/mobile/'),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const token = userStore.token

  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title as string
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/home')
  } else {
    next()
  }
})

export default router

