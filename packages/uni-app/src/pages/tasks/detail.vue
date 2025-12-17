<template>
  <view class="detail-container">
    <view class="detail-card">
      <view class="card-header">
        <text class="title">{{ task.name }}</text>
        <text class="status" :class="task.status">{{ getStatusText(task.status) }}</text>
      </view>
      
      <view class="info-list">
        <view class="info-item">
          <text class="label">客户名称</text>
          <text class="value">{{ task.customerName }}</text>
        </view>
        <view class="info-item">
          <text class="label">截止日期</text>
          <text class="value">{{ task.deadline }}</text>
        </view>
        <view class="info-item">
          <text class="label">任务描述</text>
          <text class="value">{{ task.description }}</text>
        </view>
      </view>
    </view>
    
    <!-- 操作按钮 -->
    <view class="action-bar">
      <button v-if="task.status === 'pending'" class="btn primary" @click="startTask">
        开始任务
      </button>
      <button v-if="task.status === 'in_progress'" class="btn success" @click="completeTask">
        完成任务
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const task = ref({
  id: 1,
  name: '月度记账服务',
  customerName: '张三公司',
  deadline: '2024-12-20',
  status: 'pending',
  description: '为客户提供月度记账服务，包括凭证录入、账簿登记等工作。'
})

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成'
  }
  return map[status] || status
}

const startTask = () => {
  task.value.status = 'in_progress'
  uni.showToast({ title: '任务已开始', icon: 'success' })
}

const completeTask = () => {
  task.value.status = 'completed'
  uni.showToast({ title: '任务已完成', icon: 'success' })
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const id = (currentPage as any).options?.id
  // TODO: 根据 id 获取任务详情
})
</script>

<style lang="scss" scoped>
.detail-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20rpx;
  padding-bottom: 150rpx;
}

.detail-card {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 30rpx;
    border-bottom: 1rpx solid #eee;
    
    .title {
      font-size: 36rpx;
      font-weight: bold;
      color: #333;
    }
    
    .status {
      font-size: 24rpx;
      padding: 8rpx 16rpx;
      border-radius: 8rpx;
      
      &.pending { background: #fff7e6; color: #fa8c16; }
      &.in_progress { background: #e6f7ff; color: #1890ff; }
      &.completed { background: #f6ffed; color: #52c41a; }
    }
  }
  
  .info-list {
    padding-top: 30rpx;
    
    .info-item {
      display: flex;
      margin-bottom: 30rpx;
      
      .label {
        width: 160rpx;
        font-size: 28rpx;
        color: #999;
      }
      
      .value {
        flex: 1;
        font-size: 28rpx;
        color: #333;
      }
    }
  }
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  background: #ffffff;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
  
  .btn {
    width: 100%;
    height: 90rpx;
    border-radius: 10rpx;
    font-size: 32rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.primary { background: #1989fa; color: #fff; }
    &.success { background: #07c160; color: #fff; }
  }
}
</style>

