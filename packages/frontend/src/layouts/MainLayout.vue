<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="main-header">
      <div class="header-left">
        <div class="logo">
          <h1>代理记账营运内部系统</h1>
        </div>
      </div>
      
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-dropdown">
            <el-avatar :size="32" :src="userInfo?.avatar">
              {{ userInfo?.xingming?.charAt(0) || 'U' }}
            </el-avatar>
            <span class="username">{{ userInfo?.xingming || '用户' }}</span>
            <el-icon class="el-icon--right">
              <arrow-down />
            </el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人资料</el-dropdown-item>
              <el-dropdown-item command="settings">系统设置</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主体内容区域 -->
    <div class="main-body">
      <!-- 侧边导航栏 -->
      <aside class="main-sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-toggle" @click="toggleSidebar">
          <el-icon>
            <expand v-if="sidebarCollapsed" />
            <fold v-else />
          </el-icon>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          :collapse="sidebarCollapsed"
          :router="true"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
        >
          <el-menu-item index="/dashboard">
            <el-icon><house /></el-icon>
            <template #title>工作台</template>
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
          
          <el-sub-menu index="contract">
            <template #title>
              <el-icon><document /></el-icon>
              <span>合同管理</span>
            </template>
            <el-menu-item index="/contracts">合同列表</el-menu-item>
            <el-menu-item index="/contract-templates">合同模板</el-menu-item>
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
            <el-menu-item index="/invoices">发票管理</el-menu-item>
            <el-menu-item index="/payments">收付款管理</el-menu-item>
            <el-menu-item index="/reports">财务报表</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </aside>

      <!-- 主内容区域 -->
      <main class="main-content">
        <div class="content-wrapper">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/modules/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  Expand,
  Fold,
  House,
  User,
  UserFilled,
  Document,
  ShoppingCart,
  List,
  Money
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

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中...')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中...')
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
}

/* 顶部导航栏 */
.main-header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 1000;
}

.header-left .logo h1 {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: #606266;
}

/* 主体内容区域 */
.main-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 侧边导航栏 */
.main-sidebar {
  width: 200px;
  background: #304156;
  transition: width 0.3s;
  position: relative;
  overflow: hidden;
}

.main-sidebar.collapsed {
  width: 64px;
}

.sidebar-toggle {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 24px;
  height: 24px;
  background: #409eff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1001;
  color: white;
  font-size: 12px;
}

.sidebar-menu {
  border: none;
  height: 100%;
  padding-top: 50px;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  background: #f0f2f5;
  overflow: auto;
}

.content-wrapper {
  padding: 20px;
  min-height: calc(100vh - 100px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-sidebar {
    position: fixed;
    left: 0;
    top: 60px;
    height: calc(100vh - 60px);
    z-index: 999;
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  
  .main-sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .header-left .logo h1 {
    font-size: 16px;
  }
}
</style>
