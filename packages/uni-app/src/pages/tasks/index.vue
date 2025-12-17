<template>
  <view class="tasks-container">
    <!-- 状态筛选 -->
    <view class="filter-bar">
      <view
        v-for="item in statusList"
        :key="item.value"
        class="filter-item"
        :class="{ active: currentStatus === item.value }"
        @click="currentStatus = item.value"
      >
        {{ item.label }}
      </view>
    </view>
    
    <!-- 任务列表 -->
    <scroll-view
      class="task-list"
      scroll-y
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
    >
      <view v-for="task in tasks" :key="task.id" class="task-card" @click="goDetail(task.id)">
        <view class="task-header">
          <text class="task-name">{{ task.name }}</text>
          <text class="task-status" :class="task.status">{{ getStatusText(task.status) }}</text>
        </view>
        <view class="task-info">
          <text class="info-item">客户：{{ task.customerName }}</text>
          <text class="info-item">截止：{{ task.deadline }}</text>
        </view>
      </view>
      
      <view v-if="tasks.length === 0" class="empty-tip">
        暂无任务
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const currentStatus = ref('all')
const refreshing = ref(false)

const statusList = [
  { label: '全部', value: 'all' },
  { label: '待处理', value: 'pending' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' }
]

// 模拟任务数据
const tasks = ref([
  { id: 1, name: '月度记账服务', customerName: '张三公司', deadline: '2024-12-20', status: 'pending' },
  { id: 2, name: '年度审计', customerName: '李四企业', deadline: '2024-12-25', status: 'in_progress' },
  { id: 3, name: '税务申报', customerName: '王五集团', deadline: '2024-12-18', status: 'completed' }
])

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成'
  }
  return map[status] || status
}

const goDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/tasks/detail?id=${id}` })
}

const onRefresh = async () => {
  refreshing.value = true
  // TODO: 刷新数据
  setTimeout(() => {
    refreshing.value = false
  }, 1000)
}

const onLoadMore = () => {
  // TODO: 加载更多
}
</script>

<style lang="scss" scoped>
.tasks-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.filter-bar {
  display: flex;
  background: #ffffff;
  padding: 20rpx;
  
  .filter-item {
    flex: 1;
    text-align: center;
    padding: 16rpx 0;
    font-size: 28rpx;
    color: #666;
    
    &.active {
      color: #1989fa;
      font-weight: bold;
    }
  }
}

.task-list {
  height: calc(100vh - 180rpx);
  padding: 20rpx;
}

.task-card {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  
  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
    
    .task-name {
      font-size: 32rpx;
      font-weight: bold;
      color: #333;
    }
    
    .task-status {
      font-size: 24rpx;
      padding: 8rpx 16rpx;
      border-radius: 8rpx;
      
      &.pending { background: #fff7e6; color: #fa8c16; }
      &.in_progress { background: #e6f7ff; color: #1890ff; }
      &.completed { background: #f6ffed; color: #52c41a; }
    }
  }
  
  .task-info {
    .info-item {
      font-size: 26rpx;
      color: #999;
      margin-right: 30rpx;
    }
  }
}

.empty-tip {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
  font-size: 28rpx;
}
</style>

