<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="main-header">
      <div class="header-left">
        <div class="logo">
          <div class="logo-icon">S</div>
          <h1>智能管理系统</h1>
        </div>
        
        <button class="sidebar-toggle-btn" @click="toggleSidebar">
          <el-icon v-if="sidebarCollapsed"><Expand /></el-icon>
          <el-icon v-else><Fold /></el-icon>
        </button>
        
        <nav class="breadcrumb">
          <span>首页</span>
          <span>/</span>
          <span>工作台</span>
        </nav>
      </div>
      
      <div class="header-right">
        <div class="header-actions">
          <!-- 通知中心 -->
          <NotificationCenter />

          <button class="action-btn" title="全屏" @click="toggleFullscreen">
            <el-icon><FullScreen /></el-icon>
          </button>

          <button class="action-btn" title="设置">
            <el-icon><Setting /></el-icon>
          </button>
        </div>
        
        <el-dropdown @command="handleCommand" trigger="click">
          <div class="user-dropdown">
            <div class="user-avatar">
              {{ userInfo?.xingming?.charAt(0) || 'U' }}
            </div>
            <div class="user-info">
              <div class="username">{{ userInfo?.xingming || '用户' }}</div>
              <div class="user-role">管理员</div>
            </div>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人资料
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                系统设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主体内容区域 -->
    <div class="main-body">
      <!-- 侧边导航栏 -->
      <aside class="main-sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-content">
          <el-menu
            :default-active="activeMenu"
            class="sidebar-menu"
            :collapse="sidebarCollapsed"
            :router="true"
            background-color="transparent"
            text-color="var(--text-secondary)"
            active-text-color="white"
          >
          <el-menu-item index="/dashboard">
            <el-icon><house /></el-icon>
            <template #title>工作台</template>
          </el-menu-item>

          <el-menu-item index="/feature-demo">
            <el-icon><star /></el-icon>
            <template #title>功能演示</template>
          </el-menu-item>

          <el-sub-menu index="user">
            <template #title>
              <el-icon><user /></el-icon>
              <span>用户管理</span>
            </template>
            <el-menu-item index="/users">用户列表</el-menu-item>
            <el-menu-item index="/roles">角色管理</el-menu-item>
            <el-menu-item index="/permissions">权限管理</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="customer">
            <template #title>
              <el-icon><user-filled /></el-icon>
              <span>客户管理</span>
            </template>
            <el-menu-item index="/customers">客户列表</el-menu-item>
            <el-menu-item index="/customer-services">服务记录</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="leads">
            <template #title>
              <el-icon><phone /></el-icon>
              <span>线索管理</span>
            </template>
            <el-menu-item index="/leads">线索列表</el-menu-item>
            <el-menu-item index="/lead-sources">线索来源</el-menu-item>
            <el-menu-item index="/lead-statuses">线索状态</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="product">
            <template #title>
              <el-icon><goods /></el-icon>
              <span>产品管理</span>
            </template>
            <el-menu-item index="/product-management?type=zengzhi">增值服务</el-menu-item>
            <el-menu-item index="/bookkeeping-packages">代理记账服务</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="contract">
            <template #title>
              <el-icon><document /></el-icon>
              <span>合同管理</span>
            </template>
            <el-menu-item index="/contracts">合同列表</el-menu-item>
            <el-menu-item index="/contract-templates">合同模板</el-menu-item>
            <el-menu-item index="/contract-parties">乙方主体</el-menu-item>
            <el-menu-item index="/payment-methods">支付方式</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="audit">
            <template #title>
              <el-icon><check /></el-icon>
              <span>审核管理</span>
            </template>
            <el-menu-item index="/audit/tasks">我的审核任务</el-menu-item>
            <el-menu-item index="/audit/workflow-config">审核流程配置</el-menu-item>
            <el-menu-item index="/audit/rule-config">审核规则配置</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="order">
            <template #title>
              <el-icon><shopping-cart /></el-icon>
              <span>订单管理</span>
            </template>
            <el-menu-item index="/orders">订单列表</el-menu-item>
            <el-menu-item index="/order-tracking">订单跟踪</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="task">
            <template #title>
              <el-icon><list /></el-icon>
              <span>任务管理</span>
            </template>
            <el-menu-item index="/tasks">任务列表</el-menu-item>
            <el-menu-item index="/task-templates">任务模板</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="finance">
            <template #title>
              <el-icon><money /></el-icon>
              <span>财务管理</span>
            </template>
            <el-menu-item index="/finance/dashboard">财务概览</el-menu-item>
            <el-menu-item index="/finance/payment-orders">支付订单</el-menu-item>
            <el-menu-item index="/finance/payment-records">支付流水</el-menu-item>
            <el-menu-item index="/finance/bank-transfers">银行汇款管理</el-menu-item>
            <el-menu-item index="/finance/contract-parties">乙方主体</el-menu-item>
            <el-menu-item index="/finance/payment-methods">支付方式</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="office">
            <template #title>
              <el-icon><office-building /></el-icon>
              <span>办公管理</span>
            </template>
            <el-menu-item index="/office/reimbursement">申请报销</el-menu-item>
            <el-menu-item index="/office/leave">请假</el-menu-item>
            <el-menu-item index="/office/payment">申请对外付款</el-menu-item>
            <el-menu-item index="/office/procurement">申请采购</el-menu-item>
            <el-menu-item index="/office/handover">交接单</el-menu-item>
          </el-sub-menu>
        </el-menu>
        </div>
      </aside>

      <!-- 主内容区域 -->
      <main class="main-content">
        <div class="content-wrapper">
          <router-view />
        </div>
      </main>
    </div>

    <!-- 认证修复组件 -->
    <AuthFix />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/modules/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import AuthFix from '@/components/AuthFix.vue'
import NotificationCenter from '@/components/notification/NotificationCenter.vue'
import {
  ArrowDown,
  Expand,
  Fold,
  House,
  User,
  UserFilled,
  Phone,
  Document,
  ShoppingCart,
  List,
  Money,
  Goods,
  Check,
  Star,
  Setting,
  Bell,
  FullScreen,
  SwitchButton,
  OfficeBuilding
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const sidebarCollapsed = ref(false)

// 计算属性
const userInfo = computed(() => authStore.userInfo)
const activeMenu = computed(() => route.path)

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 全屏切换
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    }
  }
}

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/settings/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await authStore.logout()
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}
</script>

<style scoped>
.main-layout {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

/* 顶部导航栏 */
.main-header {
  height: 70px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  z-index: 1000;
  position: relative;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: var(--border-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  font-weight: bold;
  box-shadow: var(--shadow-sm);
}

.logo h1 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-toggle-btn {
  width: 44px;
  height: 44px;
  border-radius: var(--border-radius-md);
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-secondary);
}

.sidebar-toggle-btn:hover {
  background: var(--primary-color);
  color: white;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--text-secondary);
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.action-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-md);
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-secondary);
  position: relative;
}

.action-btn:hover {
  background: var(--primary-color);
  color: white;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.notification-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 8px;
  height: 8px;
  background: var(--error-color);
  border-radius: 50%;
  border: 2px solid white;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-lg);
  transition: all var(--transition-fast);
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  gap: var(--spacing-sm);
}

.user-dropdown:hover {
  background: var(--bg-tertiary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.user-role {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
}

/* 主体内容区域 */
.main-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 侧边导航栏 */
.main-sidebar {
  width: 260px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--border-light);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
  height: 100%;
  box-shadow: var(--shadow-sm);
}

.main-sidebar.collapsed {
  width: 80px;
}

.sidebar-content {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--spacing-md) 0;
}

.sidebar-menu {
  border: none;
  background: transparent;
  width: 100%;
}

.sidebar-menu :deep(.el-menu-item) {
  margin: 0 var(--spacing-md) var(--spacing-xs);
  border-radius: var(--border-radius-md);
  height: 48px;
  line-height: 48px;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: var(--bg-tertiary);
  color: var(--primary-color);
  transform: translateX(4px);
  border-color: var(--border-light);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  font-weight: 600;
  box-shadow: var(--shadow-md);
  border-color: transparent;
}

.sidebar-menu :deep(.el-sub-menu) {
  margin: 0 var(--spacing-md) var(--spacing-xs);
}

.sidebar-menu :deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  border-radius: var(--border-radius-md);
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: var(--bg-tertiary);
  color: var(--primary-color);
  border-color: var(--border-light);
}

.sidebar-menu :deep(.el-sub-menu.is-active .el-sub-menu__title) {
  color: var(--primary-color);
  font-weight: 600;
}

.sidebar-menu :deep(.el-menu-item-group__title) {
  padding: var(--spacing-md) var(--spacing-lg);
  color: var(--text-tertiary);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sidebar-menu :deep(.el-icon) {
  margin-right: var(--spacing-sm);
  font-size: 18px;
}

/* 自定义滚动条样式 */
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: var(--primary-color);
}

/* 主内容区域 */
.main-content {
  flex: 1;
  background: var(--bg-primary);
  overflow: auto;
  position: relative;
}

.content-wrapper {
  padding: 16px;  /* 减少 padding，从 24px 减少到 16px */
  min-height: calc(100vh - 70px);
  width: 100%;
  height: calc(100vh - 70px);
  overflow: auto;
  /* 移除 max-width 限制，让内容占满整个可用空间 */
  /* max-width: 1400px; */
  /* margin: 0 auto; */
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-sidebar {
    width: 240px;
  }
  
  .content-wrapper {
    padding: var(--spacing-lg);
  }
}

@media (max-width: 768px) {
  .main-header {
    padding: 0 var(--spacing-md);
    height: 60px;
  }
  
  .logo h1 {
    font-size: 18px;
  }
  
  .breadcrumb {
    display: none;
  }
  
  .header-actions {
    gap: var(--spacing-xs);
  }
  
  .action-btn {
    width: 36px;
    height: 36px;
  }
  
  .user-info {
    display: none;
  }
  
  .main-sidebar {
    position: fixed;
    left: 0;
    top: 60px;
    height: calc(100vh - 60px);
    z-index: 999;
    transform: translateX(-100%);
    transition: transform var(--transition-normal);
    width: 260px;
  }
  
  .main-sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .content-wrapper {
    padding: var(--spacing-md);
    min-height: calc(100vh - 60px);
  }
}

@media (max-width: 480px) {
  .main-header {
    padding: 0 var(--spacing-sm);
  }
  
  .logo-icon {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .logo h1 {
    font-size: 16px;
  }
  
  .content-wrapper {
    padding: var(--spacing-sm);
  }
}

/* 动画效果 */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.main-content {
  animation: fadeInUp 0.6s ease-out;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu) {
  animation: slideInRight 0.3s ease-out;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .main-header {
    background: rgba(30, 30, 30, 0.95);
    border-bottom-color: var(--border-dark);
  }
  
  .main-sidebar {
    background: rgba(30, 30, 30, 0.95);
    border-right-color: var(--border-dark);
  }
  
  .sidebar-toggle-btn,
  .action-btn,
  .user-dropdown {
    background: var(--bg-dark);
    border-color: var(--border-dark);
  }
  
  .sidebar-toggle-btn:hover,
  .action-btn:hover {
    background: var(--primary-color);
  }
  
  .user-dropdown:hover {
    background: var(--bg-secondary-dark);
  }
}
</style>
