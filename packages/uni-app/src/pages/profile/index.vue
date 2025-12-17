<template>
  <view class="profile-container">
    <!-- 用户信息卡片 -->
    <view class="user-card">
      <image class="avatar" src="/static/avatar.png" mode="aspectFill" />
      <view class="user-info">
        <text class="name">{{ userInfo.name }}</text>
        <text class="role">{{ userInfo.role }}</text>
      </view>
    </view>
    
    <!-- 统计数据 -->
    <view class="stat-card">
      <view class="stat-item">
        <text class="stat-value">{{ stats.total }}</text>
        <text class="stat-label">总任务</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ stats.completed }}</text>
        <text class="stat-label">已完成</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ stats.pending }}</text>
        <text class="stat-label">待处理</text>
      </view>
    </view>
    
    <!-- 菜单列表 -->
    <view class="menu-list">
      <view class="menu-item" @click="goPage('/pages/settings/index')">
        <text class="menu-label">系统设置</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/about/index')">
        <text class="menu-label">关于我们</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="handleLogout">
        <text class="menu-label logout">退出登录</text>
        <text class="menu-arrow">></text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const userInfo = reactive({
  name: '张三',
  role: '服务人员'
})

const stats = reactive({
  total: 28,
  completed: 20,
  pending: 8
})

const goPage = (url: string) => {
  uni.navigateTo({ url })
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        // TODO: 清除登录状态
        uni.reLaunch({ url: '/pages/login/index' })
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.profile-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.user-card {
  display: flex;
  align-items: center;
  padding: 60rpx 40rpx;
  background: linear-gradient(135deg, #1989fa 0%, #07c160 100%);
  
  .avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    border: 4rpx solid #fff;
  }
  
  .user-info {
    margin-left: 30rpx;
    
    .name {
      font-size: 36rpx;
      color: #fff;
      font-weight: bold;
    }
    
    .role {
      font-size: 26rpx;
      color: rgba(255, 255, 255, 0.8);
      margin-top: 10rpx;
    }
  }
}

.stat-card {
  display: flex;
  background: #ffffff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 30rpx 0;
  
  .stat-item {
    flex: 1;
    text-align: center;
    
    .stat-value {
      font-size: 44rpx;
      font-weight: bold;
      color: #1989fa;
    }
    
    .stat-label {
      font-size: 24rpx;
      color: #999;
      margin-top: 10rpx;
      display: block;
    }
  }
}

.menu-list {
  background: #ffffff;
  margin: 20rpx;
  border-radius: 16rpx;
  
  .menu-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 36rpx 30rpx;
    border-bottom: 1rpx solid #f5f5f5;
    
    &:last-child {
      border-bottom: none;
    }
    
    .menu-label {
      font-size: 30rpx;
      color: #333;
      
      &.logout {
        color: #ff4d4f;
      }
    }
    
    .menu-arrow {
      font-size: 28rpx;
      color: #ccc;
    }
  }
}
</style>

