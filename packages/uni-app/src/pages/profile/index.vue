<template>
  <view class="profile-container">
    <!-- 用户信息卡片 -->
    <view class="user-card">
      <image class="avatar" :src="userInfo.avatar || '/static/avatar.png'" mode="aspectFill" />
      <view class="user-info">
        <text class="name">{{ userInfo.name || '用户' }}</text>
        <text class="role">{{ userInfo.role || '服务人员' }}</text>
      </view>
      <view class="edit-btn" @click="goPage('/pages/profile/edit')">
        <text>编辑</text>
      </view>
    </view>

    <!-- 统计数据 -->
    <view class="stat-card">
      <view class="stat-item" @click="goTasksWithStatus('all')">
        <text class="stat-value">{{ stats.total }}</text>
        <text class="stat-label">总任务</text>
      </view>
      <view class="stat-item" @click="goTasksWithStatus('completed')">
        <text class="stat-value">{{ stats.completed }}</text>
        <text class="stat-label">已完成</text>
      </view>
      <view class="stat-item" @click="goTasksWithStatus('pending')">
        <text class="stat-value">{{ stats.pending }}</text>
        <text class="stat-label">待处理</text>
      </view>
      <view class="stat-item" @click="goTasksWithStatus('in_progress')">
        <text class="stat-value">{{ stats.in_progress }}</text>
        <text class="stat-label">进行中</text>
      </view>
    </view>

    <!-- 菜单列表 -->
    <view class="menu-list">
      <view class="menu-item" @click="goPage('/pages/password/index')">
        <view class="menu-icon">🔐</view>
        <text class="menu-label">修改密码</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/settings/index')">
        <view class="menu-icon">⚙️</view>
        <text class="menu-label">系统设置</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goPage('/pages/about/index')">
        <view class="menu-icon">ℹ️</view>
        <text class="menu-label">关于我们</text>
        <text class="menu-arrow">></text>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-section">
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </view>

    <!-- 版本信息 -->
    <view class="version-info">
      <text>版本 v{{ appVersion }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getTaskStatistics } from '@/api/task'
import { appConfig } from '@/utils/config'

const userStore = useUserStore()
const appVersion = appConfig.version

const userInfo = reactive({
  name: '',
  role: '',
  avatar: ''
})

const stats = reactive({
  total: 0,
  completed: 0,
  pending: 0,
  in_progress: 0
})

// 加载用户信息
const loadUserInfo = () => {
  userStore.restoreLogin()
  const info = userStore.userInfo
  if (info) {
    userInfo.name = info.name || info.username || '用户'
    userInfo.role = info.role || '服务人员'
    userInfo.avatar = info.avatar || ''
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const data = await getTaskStatistics()
    Object.assign(stats, data)
  } catch (error) {
    if (import.meta.env.DEV) {
      Object.assign(stats, { total: 28, completed: 20, pending: 5, in_progress: 3 })
    }
  }
}

const goPage = (url: string) => {
  uni.showToast({ title: '功能开发中', icon: 'none' })
  // uni.navigateTo({ url })
}

const goTasksWithStatus = (status: string) => {
  uni.switchTab({ url: '/pages/tasks/index' })
  uni.$emit('filterTaskStatus', status)
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
        uni.reLaunch({ url: '/pages/login/index' })
      }
    }
  })
}

onMounted(() => {
  loadUserInfo()
  loadStatistics()
})
</script>

<style lang="scss" scoped>
.profile-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 120rpx;
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
    flex: 1;
    margin-left: 30rpx;

    .name {
      font-size: 36rpx;
      color: #fff;
      font-weight: bold;
      display: block;
    }

    .role {
      font-size: 26rpx;
      color: rgba(255, 255, 255, 0.8);
      margin-top: 10rpx;
      display: block;
    }
  }

  .edit-btn {
    background: rgba(255, 255, 255, 0.2);
    padding: 12rpx 24rpx;
    border-radius: 30rpx;

    text {
      font-size: 24rpx;
      color: #fff;
    }
  }
}

.stat-card {
  display: flex;
  background: #ffffff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 30rpx 0;
  margin-top: -30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);

  .stat-item {
    flex: 1;
    text-align: center;

    .stat-value {
      font-size: 40rpx;
      font-weight: bold;
      color: #1989fa;
      display: block;
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
    align-items: center;
    padding: 36rpx 30rpx;
    border-bottom: 1rpx solid #f5f5f5;

    &:last-child {
      border-bottom: none;
    }

    .menu-icon {
      font-size: 36rpx;
      margin-right: 20rpx;
    }

    .menu-label {
      flex: 1;
      font-size: 30rpx;
      color: #333;
    }

    .menu-arrow {
      font-size: 28rpx;
      color: #ccc;
    }
  }
}

.logout-section {
  margin: 40rpx 20rpx;

  .logout-btn {
    width: 100%;
    height: 90rpx;
    background: #fff;
    color: #ff4d4f;
    font-size: 32rpx;
    border-radius: 16rpx;
    border: 1rpx solid #ff4d4f;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.version-info {
  text-align: center;
  padding: 30rpx 0;

  text {
    font-size: 24rpx;
    color: #c0c4cc;
  }
}
</style>

