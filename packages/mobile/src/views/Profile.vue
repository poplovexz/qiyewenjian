<template>
  <div class="profile-container">
    <van-nav-bar title="个人中心" fixed placeholder />

    <div class="user-card">
      <van-cell-group inset>
        <van-cell>
          <template #title>
            <div class="user-info">
              <van-icon name="user-circle-o" size="60" />
              <div class="user-details">
                <div class="user-name">{{ userStore.userInfo?.xingming || '未登录' }}</div>
                <div class="user-username">{{ userStore.userInfo?.yonghu_ming }}</div>
              </div>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <div class="statistics-card">
      <van-cell-group inset title="我的统计">
        <van-grid :column-num="3" :border="false">
          <van-grid-item icon="todo-list-o" :text="`待处理\n${statistics.pending_count}`" />
          <van-grid-item icon="clock-o" :text="`进行中\n${statistics.in_progress_count}`" />
          <van-grid-item icon="checked" :text="`已完成\n${statistics.completed_count}`" />
        </van-grid>
      </van-cell-group>
    </div>

    <!-- 角色和权限信息 -->
    <div class="role-permission-card">
      <van-cell-group inset title="角色与权限">
        <van-cell title="我的角色" :value="roleText" />
        <van-cell
          title="我的权限"
          :value="`${userStore.permissions.length} 项`"
          is-link
          @click="showPermissions = true"
        />
      </van-cell-group>
    </div>

    <div class="menu-list">
      <van-cell-group inset title="功能菜单">
        <van-cell title="我的任务" is-link @click="router.push('/tasks')" icon="todo-list-o" />
        <van-cell title="工单列表" is-link @click="router.push('/orders')" icon="orders-o" />
        <van-cell
          v-permission="['office:baoxiao:approve', 'office:qingjia:approve']"
          title="待我审批"
          is-link
          @click="router.push('/approvals')"
          icon="passed"
        />
        <van-cell title="修改密码" is-link @click="router.push('/profile/change-password')" icon="lock" />
      </van-cell-group>
    </div>

    <!-- 权限列表弹出层 -->
    <van-popup v-model:show="showPermissions" position="bottom" round :style="{ height: '60%' }">
      <div class="permission-popup">
        <div class="popup-header">
          <h3>我的权限列表</h3>
          <van-icon name="cross" @click="showPermissions = false" />
        </div>
        <div class="permission-list">
          <van-empty v-if="userStore.permissions.length === 0" description="暂无权限" />
          <div v-else class="permission-items">
            <div
              v-for="(perm, index) in userStore.permissions"
              :key="index"
              class="permission-item"
            >
              <van-icon name="shield-o" color="#667eea" />
              <span>{{ perm }}</span>
            </div>
          </div>
        </div>
      </div>
    </van-popup>

    <div class="logout-button">
      <van-button block type="danger" @click="handleLogout">退出登录</van-button>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { useUserStore } from '@/stores/user'
import { getTaskItemStatistics } from '@/api/task'
import type { TaskItemStatistics } from '@/types/task'

const router = useRouter()
const userStore = useUserStore()
const active = ref(3)
const showPermissions = ref(false)

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

// 角色文本
const roleText = computed(() => {
  if (!userStore.roles || userStore.roles.length === 0) {
    return '暂无角色'
  }
  return userStore.roles.join(', ')
})

const loadStatistics = async () => {
  try {
    const res = await getTaskItemStatistics()
    statistics.value = res
  } catch (error) {
    console.error('Load statistics error:', error)
  }
}

const handleLogout = async () => {
  try {
    await showConfirmDialog({
      title: '确认',
      message: '确定要退出登录吗？'
    })

    userStore.logout()
    showToast({ message: '已退出登录', type: 'success' })
    router.push('/login')
  } catch (error) {
    // 用户取消
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 60px;
}

.user-card {
  margin-top: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 20px 0;
}

.user-details {
  margin-left: 16px;
}

.user-name {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 4px;
}

.user-username {
  font-size: 14px;
  color: #969799;
}

.statistics-card {
  margin-top: 16px;
}

.menu-list {
  margin-top: 16px;
}

.role-permission-card {
  margin-top: 16px;
}

.logout-button {
  margin: 20px 16px;
}

/* 权限弹出层样式 */
.permission-popup {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebedf0;
}

.popup-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.permission-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.permission-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.permission-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f7f8fa;
  border-radius: 8px;
  font-size: 14px;
  color: #323233;
}
</style>

