<template>
  <div class="home-container">
    <van-nav-bar title="工作台" fixed placeholder>
      <template #right>
        <van-icon name="bell" size="20" :badge="3" />
      </template>
    </van-nav-bar>

    <!-- 用户信息卡片 -->
    <div class="user-card">
      <div class="user-avatar">
        <van-image
          round
          width="60"
          height="60"
          :src="userStore.userInfo?.avatar || 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'"
        />
      </div>
      <div class="user-details">
        <div class="user-name">{{ userStore.userInfo?.xingming || '未登录' }}</div>
        <div class="user-role">{{ userStore.userInfo?.yonghu_ming || '员工' }}</div>
      </div>
      <van-icon name="arrow" color="#999" />
    </div>

    <!-- 任务统计卡片 -->
    <div class="statistics-card">
      <div class="card-title">
        <van-icon name="chart-trending-o" />
        <span>任务统计</span>
      </div>
      <div class="stats-grid">
        <div class="stat-item stat-pending">
          <div class="stat-value">{{ statistics.pending_count }}</div>
          <div class="stat-label">待处理</div>
        </div>
        <div class="stat-item stat-progress">
          <div class="stat-value">{{ statistics.in_progress_count }}</div>
          <div class="stat-label">进行中</div>
        </div>
        <div class="stat-item stat-completed">
          <div class="stat-value">{{ statistics.completed_count }}</div>
          <div class="stat-label">已完成</div>
        </div>
        <div class="stat-item stat-total">
          <div class="stat-value">{{ statistics.total_count }}</div>
          <div class="stat-label">总任务</div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="action-section">
      <div class="section-title">快捷操作</div>
      <div class="action-grid">
        <div class="action-item" @click="router.push('/office/reimbursement/create')">
          <div class="action-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <van-icon name="balance-list-o" size="24" color="#fff" />
          </div>
          <div class="action-label">申请报销</div>
        </div>
        <div class="action-item" @click="router.push('/office/leave/create')">
          <div class="action-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <van-icon name="calendar-o" size="24" color="#fff" />
          </div>
          <div class="action-label">申请请假</div>
        </div>
        <div class="action-item" @click="router.push('/tasks')">
          <div class="action-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <van-icon name="todo-list-o" size="24" color="#fff" />
          </div>
          <div class="action-label">我的任务</div>
        </div>
        <div class="action-item" @click="router.push('/orders')">
          <div class="action-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <van-icon name="orders-o" size="24" color="#fff" />
          </div>
          <div class="action-label">工单列表</div>
        </div>
      </div>
    </div>

    <!-- 办公管理 -->
    <div class="menu-section">
      <div class="section-title">办公管理</div>
      <div class="menu-card">
        <div class="menu-item" @click="router.push('/office/reimbursement')">
          <div class="menu-icon">
            <van-icon name="balance-o" size="20" color="#667eea" />
          </div>
          <div class="menu-content">
            <div class="menu-title">我的报销</div>
            <div class="menu-desc">查看报销记录</div>
          </div>
          <van-icon name="arrow" color="#c8c9cc" />
        </div>
        <van-divider :style="{ margin: '0' }" />
        <div class="menu-item" @click="router.push('/office/leave')">
          <div class="menu-icon">
            <van-icon name="records" size="20" color="#f5576c" />
          </div>
          <div class="menu-content">
            <div class="menu-title">我的请假</div>
            <div class="menu-desc">查看请假记录</div>
          </div>
          <van-icon name="arrow" color="#c8c9cc" />
        </div>
      </div>
    </div>

    <van-tabbar v-model="active" fixed placeholder>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="todo-list-o" to="/tasks">任务</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/orders">工单</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getTaskItemStatistics } from '@/api/task'
import type { TaskItemStatistics } from '@/types/task'

const router = useRouter()
const userStore = useUserStore()
const active = ref(0)

const statistics = ref<TaskItemStatistics>({
  total_count: 0,
  pending_count: 0,
  in_progress_count: 0,
  completed_count: 0,
  skipped_count: 0,
  total_jihua_gongshi: 0,
  total_shiji_gongshi: 0,
  avg_completion_rate: 0
})

const loadStatistics = async () => {
  try {
    console.log('📊 Loading statistics...')
    console.log('🔐 Current user token:', userStore.token ? userStore.token.substring(0, 30) + '...' : 'NO TOKEN')
    console.log('👤 Current user info:', userStore.userInfo)
    const res = await getTaskItemStatistics()
    console.log('✅ Statistics loaded:', res)
    statistics.value = res
  } catch (error) {
    console.error('❌ Load statistics error:', error)
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    })
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f2f5 0%, #ffffff 100%);
  padding-bottom: 70px;
}

/* 用户卡片 */
.user-card {
  margin: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.user-avatar {
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  color: #fff;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.user-role {
  font-size: 13px;
  opacity: 0.9;
}

/* 统计卡片 */
.statistics-card {
  margin: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #323233;
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-item {
  text-align: center;
  padding: 16px 8px;
  border-radius: 12px;
  background: #f7f8fa;
}

.stat-pending {
  background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%);
}

.stat-progress {
  background: linear-gradient(135deg, #fff8e5 0%, #ffe5cc 100%);
}

.stat-completed {
  background: linear-gradient(135deg, #e5fff5 0%, #ccffe5 100%);
}

.stat-total {
  background: linear-gradient(135deg, #e5f5ff 0%, #cce5ff 100%);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #323233;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #646566;
}

/* 快捷操作 */
.action-section,
.menu-section {
  margin: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
  margin-bottom: 12px;
  padding-left: 4px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.action-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.action-item:active .action-icon {
  transform: scale(0.95);
}

.action-label {
  font-size: 13px;
  color: #646566;
  text-align: center;
}

/* 菜单卡片 */
.menu-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.menu-item:active {
  background-color: #f7f8fa;
}

.menu-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #f7f8fa;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-content {
  flex: 1;
}

.menu-title {
  font-size: 15px;
  font-weight: 500;
  color: #323233;
  margin-bottom: 4px;
}

.menu-desc {
  font-size: 12px;
  color: #969799;
}

/* 底部导航栏美化 */
:deep(.van-tabbar) {
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
}

:deep(.van-tabbar-item--active) {
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
}
</style>

