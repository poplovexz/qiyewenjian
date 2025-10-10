<template>
  <div class="dashboard-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section animate-fade-in-down">
      <div class="welcome-content">
        <div class="welcome-text animate-fade-in-left animate-delay-200">
          <h1 class="welcome-title">
            欢迎回来，{{ userInfo?.xingming || userInfo?.yonghu_ming || '用户' }}！
          </h1>
          <p class="welcome-subtitle">
            今天是 {{ currentDate }}，祝您工作愉快
          </p>
        </div>
        <div class="welcome-avatar animate-scale-in-bounce animate-delay-500">
          <div class="avatar-circle">
            {{ (userInfo?.xingming || userInfo?.yonghu_ming || 'U').charAt(0) }}
          </div>
          <div class="status-indicator"></div>
        </div>
      </div>
      <div class="weather-widget animate-fade-in-right animate-delay-300 hover-scale">
        <div class="weather-icon animate-pulse">☀️</div>
        <div class="weather-info">
          <span class="temperature">22°C</span>
          <span class="weather-desc">晴朗</span>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        :icon="User"
        label="登录次数"
        :value="userInfo?.denglu_cishu || 0"
        variant="primary"
        trend="+12%"
        trend-type="up"
        description="本月登录活跃度"
        animated
        class="animate-fade-in-up animate-delay-100 hover-lift"
      />

      <StatCard
        :icon="Star"
        label="拥有角色"
        :value="userRoles.length"
        variant="success"
        trend="0%"
        trend-type="stable"
        description="当前分配角色数量"
        animated
        class="animate-fade-in-up animate-delay-200 hover-lift"
      />

      <StatCard
        :icon="Key"
        label="拥有权限"
        :value="userPermissions.length"
        variant="warning"
        trend="+5%"
        trend-type="up"
        description="可访问功能权限"
        animated
        class="animate-fade-in-up animate-delay-300 hover-lift"
      />

      <StatCard
        :icon="CircleCheck"
        label="账户状态"
        :value="getStatusText(userInfo?.zhuangtai)"
        variant="info"
        trend="正常"
        trend-type="stable"
        description="当前账户运行状态"
        animated
        class="animate-fade-in-up animate-delay-400 hover-lift"
      />
    </div>

    <!-- 主要内容区域 -->
      <div class="main-content grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="content-left">
        <!-- 快捷操作 -->
        <ModernCard
          title="快捷操作"
          subtitle="常用功能快速访问"
          variant="glass"
          :hoverable="true"
          :elevated="true"
          class="animate-fade-in-left animate-delay-700 hover-scale"
        >
          <div class="quick-actions-grid">
            <div 
              v-if="hasPermission('user:read')"
              class="action-item"
              @click="$router.push('/users')"
            >
              <div class="action-icon primary">
                <el-icon><User /></el-icon>
              </div>
              <div class="action-content">
                <div class="action-title">用户管理</div>
                <div class="action-desc">管理系统用户</div>
              </div>
            </div>

            <div class="action-item" @click="$router.push('/customers')">
              <div class="action-icon success">
                <el-icon><UserFilled /></el-icon>
              </div>
              <div class="action-content">
                <div class="action-title">客户管理</div>
                <div class="action-desc">管理客户信息</div>
              </div>
            </div>

            <div class="action-item" @click="$router.push('/contracts')">
              <div class="action-icon warning">
                <el-icon><Document /></el-icon>
              </div>
              <div class="action-content">
                <div class="action-title">合同管理</div>
                <div class="action-desc">管理合同文档</div>
              </div>
            </div>

            <div class="action-item" @click="$router.push('/orders')">
              <div class="action-icon info">
                <el-icon><ShoppingCart /></el-icon>
              </div>
              <div class="action-content">
                <div class="action-title">订单管理</div>
                <div class="action-desc">处理订单信息</div>
              </div>
            </div>

            <div class="action-item" @click="$router.push('/finance/dashboard')">
              <div class="action-icon error">
                <el-icon><Money /></el-icon>
              </div>
              <div class="action-content">
                <div class="action-title">财务管理</div>
                <div class="action-desc">财务数据分析</div>
              </div>
            </div>

            <div class="action-item" @click="$router.push('/tasks')">
              <div class="action-icon secondary">
                <el-icon><List /></el-icon>
              </div>
              <div class="action-content">
                <div class="action-title">任务管理</div>
                <div class="action-desc">跟踪任务进度</div>
              </div>
            </div>
          </div>
        </ModernCard>

        <!-- 最近活动 -->
        <ModernCard
          title="最近活动"
          subtitle="系统操作记录"
          variant="glass"
          :hoverable="true"
          :elevated="true"
          class="animate-fade-in-right animate-delay-700 hover-scale"
        >
          <div class="activity-list">
            <div class="activity-item">
              <div class="activity-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="activity-content">
                <div class="activity-title">登录系统</div>
                <div class="activity-time">{{ formatDate(userInfo?.zuihou_denglu) }}</div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="activity-content">
                <div class="activity-title">查看合同列表</div>
                <div class="activity-time">2小时前</div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon">
                <el-icon><UserFilled /></el-icon>
              </div>
              <div class="activity-content">
                <div class="activity-title">更新客户信息</div>
                <div class="activity-time">3小时前</div>
              </div>
            </div>
          </div>
        </ModernCard>
      </div>

      <div class="content-right">
        <!-- 个人信息卡片 -->
        <ModernCard
          title="个人信息"
          variant="glass"
          :hoverable="true"
          :elevated="true"
          class="animate-fade-in-up animate-delay-1000 hover-lift"
        >
          <div class="profile-header">
            <div class="profile-avatar">
              {{ (userInfo?.xingming || userInfo?.yonghu_ming || 'U').charAt(0) }}
            </div>
            <div class="profile-info">
              <h3>{{ userInfo?.xingming || userInfo?.yonghu_ming || '用户' }}</h3>
              <p>系统管理员</p>
            </div>
          </div>
          <div class="profile-details">
            <div class="detail-item">
              <span class="detail-label">用户名</span>
              <span class="detail-value">{{ userInfo?.yonghu_ming || '未设置' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">邮箱</span>
              <span class="detail-value">{{ userInfo?.youxiang || '未设置' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">手机</span>
              <span class="detail-value">{{ userInfo?.shouji || '未设置' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">最后登录</span>
              <span class="detail-value">{{ formatDate(userInfo?.zuihou_denglu) }}</span>
            </div>
          </div>
        </ModernCard>

        <!-- 权限信息卡片 -->
        <ModernCard
          title="权限信息"
          subtitle="角色与权限详情"
          variant="glass"
          hoverable
          elevated
          class="animate-fade-in-left animate-delay-1000 hover-lift"
        >
          <div class="permissions-content">
            <div class="roles-section">
              <div class="section-title">
                <el-icon><Star /></el-icon>
                <span>角色列表</span>
              </div>
              <div class="roles-list">
                <div v-for="role in userRoles" :key="role" class="role-tag">
                  {{ role }}
                </div>
                <div v-if="userRoles.length === 0" class="no-data">
                  <el-icon><Warning /></el-icon>
                  <span>暂无角色</span>
                </div>
              </div>
            </div>
            
            <div class="permissions-section">
              <div class="section-title">
                <el-icon><Key /></el-icon>
                <span>权限列表</span>
              </div>
              <div class="permissions-list">
                <div v-for="permission in userPermissions.slice(0, 6)" :key="permission" class="permission-tag">
                  {{ permission }}
                </div>
                <div v-if="userPermissions.length > 6" class="more-permissions">
                  +{{ userPermissions.length - 6 }} 更多
                </div>
                <div v-if="userPermissions.length === 0" class="no-data">
                  <el-icon><Warning /></el-icon>
                  <span>暂无权限</span>
                </div>
              </div>
            </div>
          </div>
        </ModernCard>

        <!-- 系统状态卡片 -->
        <ModernCard
          title="系统状态"
          subtitle="服务运行状态"
          variant="glass"
          hoverable
          elevated
          class="animate-fade-in-right animate-delay-1000 hover-lift"
        >
          <div class="status-list">
            <div class="status-item">
              <div class="status-indicator online"></div>
              <span class="status-label">数据库服务</span>
              <span class="status-value">正常</span>
            </div>
            <div class="status-item">
              <div class="status-indicator online"></div>
              <span class="status-label">API服务</span>
              <span class="status-value">正常</span>
            </div>
            <div class="status-item">
              <div class="status-indicator warning"></div>
              <span class="status-label">缓存服务</span>
              <span class="status-value">警告</span>
            </div>
          </div>
        </ModernCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { 
  User, 
  UserFilled, 
  Document, 
  Star, 
  Key, 
  CircleCheck, 
  ShoppingCart, 
  Money, 
  List,
  Warning
} from '@element-plus/icons-vue'
import StatCard from '@/components/ui/StatCard.vue'
import ModernCard from '@/components/ui/ModernCard.vue'
import ModernButton from '@/components/ui/ModernButton.vue'

// 组合式函数
const { userInfo, userRoles, userPermissions, hasPermission } = useAuth()

// 计算属性
const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 方法
const formatDate = (dateString?: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusText = (status?: string) => {
  switch (status) {
    case '1':
    case 'active':
      return '正常'
    case '0':
    case 'inactive':
      return '禁用'
    default:
      return '未知'
  }
}
</script>

<style scoped>
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  --warning-gradient: linear-gradient(135deg, #f9ca24 0%, #f0932b 100%);
  --info-gradient: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
  --error-gradient: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
  --text-primary: #2d3748;
  --text-secondary: #718096;
  --bg-glass: rgba(255, 255, 255, 0.95);
  --shadow-soft: 0 8px 32px rgba(0, 0, 0, 0.1);
  --shadow-hover: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.dashboard-container {
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.dashboard-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
  pointer-events: none;
}

/* 欢迎区域 */
.welcome-section {
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: var(--shadow-soft);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 8px 0;
}

.welcome-subtitle {
  color: var(--text-secondary);
  font-size: 16px;
  margin: 0;
}

.welcome-avatar {
  position: relative;
}

.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.status-indicator {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 16px;
  height: 16px;
  background: #10b981;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.weather-widget {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.5);
  padding: 16px 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.weather-icon {
  font-size: 24px;
}

.weather-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.temperature {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.weather-desc {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.trend-text {
  font-weight: 500;
  margin-top: 4px;
}

.trend-up {
  color: #10b981;
}

.trend-down {
  color: #ef4444;
}

.trend-stable {
  color: var(--text-secondary);
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
  position: relative;
  z-index: 1;
}

.content-left,
.content-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 快速操作卡片 */
.quick-actions-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-soft);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.card-header {
  margin-bottom: 20px;
}

.card-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.card-subtitle {
  color: var(--text-secondary);
  font-size: 14px;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.action-item {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-item:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  flex-shrink: 0;
}

.action-icon.primary {
  background: var(--primary-gradient);
}

.action-icon.success {
  background: var(--success-gradient);
}

.action-icon.warning {
  background: var(--warning-gradient);
}

.action-icon.info {
  background: var(--info-gradient);
}

.action-icon.error {
  background: var(--error-gradient);
}

.action-icon.secondary {
  background: var(--info-gradient);
}

.action-content {
  flex: 1;
}

.action-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.action-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 最近活动 */

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.activity-item:hover {
  background: rgba(255, 255, 255, 0.8);
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  color: white;
  font-size: 14px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.activity-time {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 个人信息卡片 */

.profile-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.profile-avatar {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.profile-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.profile-info p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.profile-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

/* 权限信息卡片 */

.permissions-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.roles-list,
.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.role-tag {
  background: var(--primary-gradient);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.permission-tag {
  background: var(--success-gradient);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.more-permissions {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.no-data {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-style: italic;
}

/* 系统状态卡片 */

.status-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: relative;
}

.status-indicator.online {
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

.status-indicator.warning {
  background: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
}

.status-indicator.offline {
  background: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

.status-label {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.status-value {
  font-size: 12px;
  font-weight: 500;
  color: #10b981;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }
  
  .welcome-section {
    padding: 20px;
  }
  
  .welcome-content {
    flex-direction: column;
    gap: 16px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .action-item {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-section,
.stats-grid,
.main-content {
  animation: fadeInUp 0.6s ease-out;
}

.stats-grid {
  animation-delay: 0.1s;
}

.main-content {
  animation-delay: 0.2s;
}
</style>
