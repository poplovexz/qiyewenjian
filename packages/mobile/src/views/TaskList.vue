<template>
  <div class="task-list-container">
    <van-nav-bar title="我的任务" fixed placeholder />

    <van-tabs v-model:active="activeTab" @change="onTabChange">
      <van-tab title="全部" name="all" />
      <van-tab title="待处理" name="pending" />
      <van-tab title="进行中" name="in_progress" />
      <van-tab title="已完成" name="completed" />
    </van-tabs>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div v-for="item in taskList" :key="item.id" class="task-item" @click="goToDetail(item.id)">
          <van-cell-group inset>
            <van-cell>
              <template #title>
                <div class="task-title">
                  <span>{{ item.renwu_mingcheng }}</span>
                  <van-tag :type="getStatusType(item.xiangmu_zhuangtai)">
                    {{ getStatusText(item.xiangmu_zhuangtai) }}
                  </van-tag>
                </div>
              </template>
              <template #label>
                <div class="task-info">
                  <div>工单：{{ item.gongdan.gongdan_bianhao }}</div>
                  <div>客户：{{ item.kehu?.kehu_mingcheng || '-' }}</div>
                  <div>计划工时：{{ item.jihua_gongshi }}小时</div>
                  <div v-if="item.shiji_gongshi">实际工时：{{ item.shiji_gongshi }}小时</div>
                </div>
              </template>
            </van-cell>
          </van-cell-group>
        </div>

        <van-empty v-if="!loading && taskList.length === 0" description="暂无任务" />
      </van-list>
    </van-pull-refresh>

    <van-tabbar v-model="tabbarActive" fixed placeholder>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="todo-list-o" to="/tasks">任务</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/orders">工单</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getMyTaskItems } from '@/api/task'
import type { TaskItem, TaskItemStatus } from '@/types/task'

const router = useRouter()

const activeTab = ref('all')
const tabbarActive = ref(1)
const taskList = ref<TaskItem[]>([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)
const pageSize = 20

const onLoad = async () => {
  try {
    const params: any = {
      page: page.value,
      size: pageSize
    }

    if (activeTab.value !== 'all') {
      params.xiangmu_zhuangtai = activeTab.value
    }

    const res = await getMyTaskItems(params)

    if (page.value === 1) {
      taskList.value = res.items
    } else {
      taskList.value.push(...res.items)
    }

    loading.value = false

    if (taskList.value.length >= res.total) {
      finished.value = true
    } else {
      page.value++
    }
  } catch (error) {
    console.error('Load tasks error:', error)
    loading.value = false
  }
}

const onRefresh = () => {
  page.value = 1
  finished.value = false
  taskList.value = []
  refreshing.value = false
  onLoad()
}

const onTabChange = () => {
  page.value = 1
  finished.value = false
  taskList.value = []
  onLoad()
}

const goToDetail = (id: string) => {
  router.push(`/tasks/${id}`)
}

const getStatusType = (status: TaskItemStatus) => {
  const typeMap: Record<TaskItemStatus, string> = {
    pending: 'warning',
    in_progress: 'primary',
    completed: 'success',
    skipped: 'default'
  }
  return typeMap[status] || 'default'
}

const getStatusText = (status: TaskItemStatus) => {
  const textMap: Record<TaskItemStatus, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
    skipped: '已跳过'
  }
  return textMap[status] || status
}
</script>

<style scoped>
.task-list-container {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 60px;
}

.task-item {
  margin-top: 12px;
  cursor: pointer;
}

.task-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.task-info {
  margin-top: 8px;
  font-size: 13px;
  color: #969799;
  line-height: 1.6;
}
</style>

