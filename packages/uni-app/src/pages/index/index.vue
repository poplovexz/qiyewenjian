<template>
  <view class="home-container">
    <!-- 用户欢迎 -->
    <view class="welcome-section">
      <text class="welcome-text">欢迎回来</text>
      <text class="user-name">{{ userName }}</text>
    </view>

    <!-- 统计卡片 -->
    <view class="stat-cards">
      <view class="stat-card pending">
        <text class="stat-value">{{ stats.pending }}</text>
        <text class="stat-label">待处理</text>
      </view>
      <view class="stat-card progress">
        <text class="stat-value">{{ stats.inProgress }}</text>
        <text class="stat-label">进行中</text>
      </view>
      <view class="stat-card completed">
        <text class="stat-value">{{ stats.completed }}</text>
        <text class="stat-label">已完成</text>
      </view>
    </view>

    <!-- 快捷入口 -->
    <view class="quick-actions">
      <view class="section-title">快捷入口</view>
      <view class="action-grid">
        <view class="action-item" @click="goTasks">
          <view class="action-icon task-icon">📋</view>
          <text class="action-text">我的任务</text>
        </view>
        <view class="action-item" @click="goOrders">
          <view class="action-icon order-icon">📦</view>
          <text class="action-text">工单管理</text>
        </view>
        <view class="action-item" @click="goStats">
          <view class="action-icon stat-icon">📊</view>
          <text class="action-text">统计报表</text>
        </view>
        <view class="action-item" @click="goProfile">
          <view class="action-icon profile-icon">👤</view>
          <text class="action-text">个人中心</text>
        </view>
      </view>
    </view>

    <!-- 最近任务 -->
    <view class="recent-tasks">
      <view class="section-title">最近任务</view>
      <view v-for="task in recentTasks" :key="task.id" class="task-item" @click="goTaskDetail(task.id)">
        <view class="task-info">
          <text class="task-name">{{ task.name }}</text>
          <text class="task-customer">{{ task.customerName }}</text>
        </view>
        <text class="task-status" :class="task.status">{{ getStatusText(task.status) }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const userName = ref('张三')

const stats = reactive({
  pending: 5,
  inProgress: 3,
  completed: 20
})

const recentTasks = ref([
  { id: 1, name: '月度记账服务', customerName: '张三公司', status: 'pending' },
  { id: 2, name: '年度审计', customerName: '李四企业', status: 'in_progress' },
  { id: 3, name: '税务申报', customerName: '王五集团', status: 'completed' }
])

const getStatusText = (status: string) => {
  const map: Record<string, string> = { pending: '待处理', in_progress: '进行中', completed: '已完成' }
  return map[status] || status
}

const goTasks = () => uni.switchTab({ url: '/pages/tasks/index' })
const goOrders = () => uni.navigateTo({ url: '/pages/orders/index' })
const goStats = () => uni.navigateTo({ url: '/pages/stats/index' })
const goProfile = () => uni.switchTab({ url: '/pages/profile/index' })
const goTaskDetail = (id: number) => uni.navigateTo({ url: `/pages/tasks/detail?id=${id}` })
</script>

<style lang="scss" scoped>
.home-container { min-height: 100vh; background: #f5f5f5; padding-bottom: 120rpx; }
.welcome-section { background: linear-gradient(135deg, #1989fa 0%, #07c160 100%); padding: 60rpx 40rpx; color: #fff;
  .welcome-text { font-size: 28rpx; opacity: 0.9; }
  .user-name { font-size: 44rpx; font-weight: bold; margin-top: 10rpx; display: block; }
}
.stat-cards { display: flex; padding: 20rpx; margin-top: -40rpx;
  .stat-card { flex: 1; background: #fff; border-radius: 16rpx; padding: 30rpx; margin: 0 10rpx; text-align: center; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
    .stat-value { font-size: 48rpx; font-weight: bold; }
    .stat-label { font-size: 24rpx; color: #999; margin-top: 10rpx; display: block; }
    &.pending .stat-value { color: #fa8c16; }
    &.progress .stat-value { color: #1890ff; }
    &.completed .stat-value { color: #52c41a; }
  }
}
.section-title { font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }
.quick-actions { background: #fff; margin: 20rpx; border-radius: 16rpx; padding: 30rpx;
  .action-grid { display: flex; flex-wrap: wrap; }
  .action-item { width: 25%; text-align: center; padding: 20rpx 0;
    .action-icon { font-size: 48rpx; margin-bottom: 10rpx; }
    .action-text { font-size: 26rpx; color: #666; }
  }
}
.recent-tasks { background: #fff; margin: 20rpx; border-radius: 16rpx; padding: 30rpx;
  .task-item { display: flex; justify-content: space-between; align-items: center; padding: 24rpx 0; border-bottom: 1rpx solid #f5f5f5;
    &:last-child { border-bottom: none; }
    .task-info { .task-name { font-size: 30rpx; color: #333; display: block; } .task-customer { font-size: 24rpx; color: #999; margin-top: 8rpx; display: block; } }
    .task-status { font-size: 24rpx; padding: 8rpx 16rpx; border-radius: 8rpx;
      &.pending { background: #fff7e6; color: #fa8c16; }
      &.in_progress { background: #e6f7ff; color: #1890ff; }
      &.completed { background: #f6ffed; color: #52c41a; }
    }
  }
}
</style>
