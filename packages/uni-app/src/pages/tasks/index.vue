<template>
  <view class="tasks-container">
    <!-- 状态筛选 -->
    <view class="filter-bar">
      <view
        v-for="item in statusList"
        :key="item.value"
        class="filter-item"
        :class="{ active: currentStatus === item.value }"
        @click="changeStatus(item.value)"
      >
        {{ item.label }}
        <text v-if="getStatusCount(item.value) > 0" class="filter-count">{{ getStatusCount(item.value) }}</text>
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
      <view v-if="loading && tasks.length === 0" class="loading-tip">
        <text>加载中...</text>
      </view>

      <view v-for="task in filteredTasks" :key="task.id" class="task-card" @click="goDetail(task.id)">
        <view class="task-header">
          <text class="task-name">{{ task.chanpin_mingcheng || task.buzou_mingcheng || '任务项' }}</text>
          <text class="task-status" :class="task.xiangmu_zhuangtai">{{ getStatusText(task.xiangmu_zhuangtai) }}</text>
        </view>
        <view class="task-info">
          <text class="info-item">客户：{{ task.kehu_mingcheng || '未知' }}</text>
          <text class="info-item">工单：{{ task.gongdan_bianhao || '-' }}</text>
        </view>
        <view class="task-meta">
          <text v-if="task.jihua_gongshi" class="meta-item">计划：{{ task.jihua_gongshi }}h</text>
          <text v-if="task.shiji_gongshi" class="meta-item">实际：{{ task.shiji_gongshi }}h</text>
          <text v-if="task.kaishi_shijian" class="meta-item">开始：{{ formatDate(task.kaishi_shijian) }}</text>
        </view>
      </view>

      <view v-if="!loading && filteredTasks.length === 0" class="empty-tip">
        <text>暂无任务</text>
      </view>

      <view v-if="hasMore && !loading" class="load-more" @click="onLoadMore">
        <text>加载更多</text>
      </view>

      <view v-if="loadingMore" class="loading-tip">
        <text>加载中...</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { getMyTasks, getTaskStatistics } from '@/api/task'
import { TASK_STATUS_MAP } from '@/constants'
import dayjs from 'dayjs'

const currentStatus = ref('all')
const refreshing = ref(false)
const loading = ref(false)
const loadingMore = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)

interface TaskItemData {
  id: string
  chanpin_mingcheng?: string
  buzou_mingcheng?: string
  kehu_mingcheng?: string
  gongdan_bianhao?: string
  xiangmu_zhuangtai: string
  jihua_gongshi?: number
  shiji_gongshi?: number
  kaishi_shijian?: string
  jieshu_shijian?: string
}

const tasks = ref<TaskItemData[]>([])
const statistics = ref({ total: 0, pending: 0, in_progress: 0, completed: 0, skipped: 0 })

const statusList = [
  { label: '全部', value: 'all' },
  { label: '待处理', value: 'pending' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' }
]

// 计算属性：根据状态筛选任务
const filteredTasks = computed(() => {
  if (currentStatus.value === 'all') return tasks.value
  return tasks.value.filter(t => t.xiangmu_zhuangtai === currentStatus.value)
})

const hasMore = computed(() => tasks.value.length < total.value)

const getStatusText = (status: string) => TASK_STATUS_MAP[status]?.label || status

const getStatusCount = (status: string) => {
  if (status === 'all') return statistics.value.total
  return (statistics.value as Record<string, number>)[status] || 0
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return dayjs(dateStr).format('MM-DD HH:mm')
}

// 加载任务列表
const loadTasks = async (reset = false) => {
  if (reset) {
    page.value = 1
    tasks.value = []
  }

  loading.value = reset
  loadingMore.value = !reset

  try {
    const params: Record<string, any> = { page: page.value, pageSize }
    if (currentStatus.value !== 'all') {
      params.xiangmu_zhuangtai = currentStatus.value
    }

    const data = await getMyTasks(params)
    const items = data.items || []
    total.value = data.total || 0

    if (reset) {
      tasks.value = items
    } else {
      tasks.value.push(...items)
    }
  } catch (error) {
    console.error('加载任务失败:', error)
    // 开发环境 Mock 数据
    if (import.meta.env.DEV && reset) {
      tasks.value = [
        { id: '1', chanpin_mingcheng: '月度记账服务', kehu_mingcheng: '张三公司', gongdan_bianhao: 'GD202412001', xiangmu_zhuangtai: 'pending', jihua_gongshi: 2 },
        { id: '2', buzou_mingcheng: '年度审计报告', kehu_mingcheng: '李四企业', gongdan_bianhao: 'GD202412002', xiangmu_zhuangtai: 'in_progress', jihua_gongshi: 4, kaishi_shijian: '2024-12-15T09:00:00' },
        { id: '3', chanpin_mingcheng: '税务申报', kehu_mingcheng: '王五集团', gongdan_bianhao: 'GD202412003', xiangmu_zhuangtai: 'completed', jihua_gongshi: 1, shiji_gongshi: 1.5 }
      ]
      total.value = 3
    }
  } finally {
    loading.value = false
    loadingMore.value = false
    refreshing.value = false
  }
}

// 加载统计
const loadStatistics = async () => {
  try {
    const data = await getTaskStatistics()
    Object.assign(statistics.value, data)
  } catch (error) {
    if (import.meta.env.DEV) {
      statistics.value = { total: 28, pending: 5, in_progress: 3, completed: 20, skipped: 0 }
    }
  }
}

const changeStatus = (status: string) => {
  if (currentStatus.value === status) return
  currentStatus.value = status
  loadTasks(true)
}

const goDetail = (id: string) => {
  uni.navigateTo({ url: `/pages/tasks/detail?id=${id}` })
}

const onRefresh = async () => {
  refreshing.value = true
  await Promise.all([loadTasks(true), loadStatistics()])
}

const onLoadMore = () => {
  if (loadingMore.value || !hasMore.value) return
  page.value++
  loadTasks(false)
}

// 监听首页传来的筛选事件
const handleFilterEvent = (status: string) => {
  currentStatus.value = status
  loadTasks(true)
}

onMounted(() => {
  loadTasks(true)
  loadStatistics()
  uni.$on('filterTaskStatus', handleFilterEvent)
})

onUnmounted(() => {
  uni.$off('filterTaskStatus', handleFilterEvent)
})
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
  position: sticky;
  top: 0;
  z-index: 10;

  .filter-item {
    flex: 1;
    text-align: center;
    padding: 16rpx 0;
    font-size: 28rpx;
    color: #666;
    position: relative;

    &.active {
      color: #1989fa;
      font-weight: bold;
    }

    .filter-count {
      font-size: 20rpx;
      color: #fff;
      background: #ff4d4f;
      padding: 2rpx 10rpx;
      border-radius: 20rpx;
      margin-left: 6rpx;
      vertical-align: middle;
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
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.03);

  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;

    .task-name {
      font-size: 32rpx;
      font-weight: bold;
      color: #333;
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .task-status {
      font-size: 24rpx;
      padding: 8rpx 16rpx;
      border-radius: 8rpx;
      margin-left: 16rpx;
      flex-shrink: 0;

      &.pending { background: #fff7e6; color: #fa8c16; }
      &.in_progress { background: #e6f7ff; color: #1890ff; }
      &.completed { background: #f6ffed; color: #52c41a; }
      &.skipped { background: #f5f5f5; color: #999; }
    }
  }

  .task-info {
    margin-bottom: 12rpx;
    .info-item {
      font-size: 26rpx;
      color: #666;
      margin-right: 30rpx;
    }
  }

  .task-meta {
    display: flex;
    flex-wrap: wrap;
    .meta-item {
      font-size: 24rpx;
      color: #999;
      margin-right: 20rpx;
      background: #f5f5f5;
      padding: 4rpx 12rpx;
      border-radius: 6rpx;
    }
  }
}

.loading-tip, .empty-tip, .load-more {
  text-align: center;
  padding: 40rpx 0;
  color: #999;
  font-size: 28rpx;
}

.load-more {
  color: #1989fa;
}
</style>

