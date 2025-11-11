<template>
  <div class="home-container">
    <van-nav-bar title="首页" fixed placeholder />

    <div class="user-info">
      <van-cell-group inset>
        <van-cell :title="userStore.userInfo?.xingming || '未登录'" :label="userStore.userInfo?.yonghu_ming" />
      </van-cell-group>
    </div>

    <div class="statistics">
      <van-cell-group inset title="任务统计">
        <van-grid :column-num="2" :border="false">
          <van-grid-item icon="todo-list-o" :text="`待处理: ${statistics.pending_count}`" />
          <van-grid-item icon="clock-o" :text="`进行中: ${statistics.in_progress_count}`" />
          <van-grid-item icon="checked" :text="`已完成: ${statistics.completed_count}`" />
          <van-grid-item icon="bar-chart-o" :text="`总任务: ${statistics.total_count}`" />
        </van-grid>
      </van-cell-group>
    </div>

    <div class="quick-actions">
      <van-cell-group inset title="快捷入口">
        <van-cell title="我的任务" is-link @click="router.push('/tasks')" icon="todo-list-o" />
        <van-cell title="工单列表" is-link @click="router.push('/orders')" icon="orders-o" />
        <van-cell title="个人中心" is-link @click="router.push('/profile')" icon="user-o" />
      </van-cell-group>
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
    const res = await getTaskItemStatistics()
    statistics.value = res
  } catch (error) {
    console.error('Load statistics error:', error)
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 60px;
}

.user-info {
  margin-top: 16px;
}

.statistics {
  margin-top: 16px;
}

.quick-actions {
  margin-top: 16px;
}
</style>

