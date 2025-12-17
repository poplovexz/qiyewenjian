<template>
  <view class="home-container">
    <!-- 用户欢迎 -->
    <view class="welcome-section">
      <text class="welcome-text">欢迎回来</text>
      <text class="user-name">{{ userName }}</text>
    </view>

    <!-- 统计卡片 -->
    <view class="stat-cards">
      <view class="stat-card pending" @click="goTasksWithStatus('pending')">
        <text class="stat-value">{{ stats.pending }}</text>
        <text class="stat-label">待处理</text>
      </view>
      <view class="stat-card progress" @click="goTasksWithStatus('in_progress')">
        <text class="stat-value">{{ stats.in_progress }}</text>
        <text class="stat-label">进行中</text>
      </view>
      <view class="stat-card completed" @click="goTasksWithStatus('completed')">
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
      <view class="section-header">
        <text class="section-title">最近任务</text>
        <text class="section-more" @click="goTasks">查看全部 ></text>
      </view>
      <view v-if="loading" class="loading-tip">加载中...</view>
      <view v-else-if="recentTasks.length === 0" class="empty-tip">暂无任务</view>
      <view v-else v-for="task in recentTasks" :key="task.id" class="task-item" @click="goTaskDetail(task.id)">
        <view class="task-info">
          <text class="task-name">{{ task.chanpin_mingcheng || task.buzou_mingcheng || '任务项' }}</text>
          <text class="task-customer">{{ task.kehu_mingcheng || '未知客户' }}</text>
        </view>
        <text class="task-status" :class="task.xiangmu_zhuangtai">{{ getStatusText(task.xiangmu_zhuangtai) }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getTaskStatistics, getMyTasks } from '@/api/task'
import { TASK_STATUS_MAP } from '@/constants'

const userStore = useUserStore()
const userName = ref('')
const loading = ref(false)

const stats = reactive({
  total: 0,
  pending: 0,
  in_progress: 0,
  completed: 0,
  skipped: 0
})

interface TaskItemData {
  id: string
  chanpin_mingcheng?: string
  buzou_mingcheng?: string
  kehu_mingcheng?: string
  xiangmu_zhuangtai: string
}

const recentTasks = ref<TaskItemData[]>([])

const getStatusText = (status: string) => {
  return TASK_STATUS_MAP[status]?.label || status
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const data = await getTaskStatistics()
    Object.assign(stats, data)
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 开发环境使用 Mock 数据
    if (import.meta.env.DEV) {
      Object.assign(stats, { total: 28, pending: 5, in_progress: 3, completed: 20, skipped: 0 })
    }
  }
}

// 加载最近任务
const loadRecentTasks = async () => {
  loading.value = true
  try {
    const data = await getMyTasks({ page: 1, pageSize: 5 })
    recentTasks.value = data.items || []
  } catch (error) {
    console.error('加载任务列表失败:', error)
    // 开发环境 Mock 数据
    if (import.meta.env.DEV) {
      recentTasks.value = [
        { id: '1', chanpin_mingcheng: '月度记账服务', kehu_mingcheng: '张三公司', xiangmu_zhuangtai: 'pending' },
        { id: '2', buzou_mingcheng: '年度审计', kehu_mingcheng: '李四企业', xiangmu_zhuangtai: 'in_progress' },
        { id: '3', chanpin_mingcheng: '税务申报', kehu_mingcheng: '王五集团', xiangmu_zhuangtai: 'completed' }
      ]
    }
  } finally {
    loading.value = false
  }
}

const goTasks = () => uni.switchTab({ url: '/pages/tasks/index' })
const goTasksWithStatus = (status: string) => {
  uni.switchTab({ url: '/pages/tasks/index' })
  // 通过事件或全局状态传递筛选条件
  uni.$emit('filterTaskStatus', status)
}
const goOrders = () => uni.showToast({ title: '功能开发中', icon: 'none' })
const goStats = () => uni.showToast({ title: '功能开发中', icon: 'none' })
const goProfile = () => uni.switchTab({ url: '/pages/profile/index' })
const goTaskDetail = (id: string) => uni.navigateTo({ url: `/pages/tasks/detail?id=${id}` })

onMounted(() => {
  // 恢复登录状态
  userStore.restoreLogin()
  userName.value = userStore.userName || '用户'

  // 加载数据
  loadStatistics()
  loadRecentTasks()
})
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
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx;
  .section-title { font-size: 32rpx; font-weight: bold; color: #333; }
  .section-more { font-size: 26rpx; color: #1989fa; }
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
  .loading-tip, .empty-tip { text-align: center; padding: 40rpx 0; color: #999; font-size: 28rpx; }
  .task-item { display: flex; justify-content: space-between; align-items: center; padding: 24rpx 0; border-bottom: 1rpx solid #f5f5f5;
    &:last-child { border-bottom: none; }
    .task-info { .task-name { font-size: 30rpx; color: #333; display: block; } .task-customer { font-size: 24rpx; color: #999; margin-top: 8rpx; display: block; } }
    .task-status { font-size: 24rpx; padding: 8rpx 16rpx; border-radius: 8rpx;
      &.pending { background: #fff7e6; color: #fa8c16; }
      &.in_progress { background: #e6f7ff; color: #1890ff; }
      &.completed { background: #f6ffed; color: #52c41a; }
      &.skipped { background: #f5f5f5; color: #999; }
    }
  }
}
</style>
